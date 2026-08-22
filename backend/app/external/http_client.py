"""Shared async HTTP client for all outbound third-party requests.

Every external integration (weather, mandi, assistant) goes through
``ExternalHttpClient`` so the cross-cutting concerns are implemented once:

* configurable timeout
* bounded retries with backoff for transient failures (5xx / network errors)
* structured latency logging per outbound call
* consistent ``ExternalServiceError`` signalling for the error middleware

Services never build raw ``httpx`` calls themselves.
"""

import asyncio
import logging
from typing import Any

import httpx

from app.core.errors import ExternalServiceError

logger = logging.getLogger("agrisense.external")

DEFAULT_TIMEOUT_SECONDS = 8.0
MAX_RETRIES = 2
RETRY_BACKOFF_SECONDS = 0.4


class ExternalHttpClient:
    """Thin httpx wrapper adding timeout, retry and logging for one base URL."""

    def __init__(
        self,
        base_url: str,
        *,
        api_key: str = "",
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
        service_name: str = "external",
        headers: dict[str, str] | None = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._service_name = service_name
        default_headers = {"Accept": "application/json"}
        if api_key:
            default_headers["Authorization"] = f"Bearer {api_key}"
        if headers:
            default_headers.update(headers)
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            timeout=timeout,
            headers=default_headers,
            follow_redirects=True,
        )

    @property
    def base_url(self) -> str:
        return self._base_url

    async def get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        return await self._request("GET", path, params=params)

    async def post(self, path: str, *, json: Any = None) -> Any:
        return await self._request("POST", path, json=json)

    async def aclose(self) -> None:
        await self._client.aclose()

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any = None,
    ) -> Any:
        """Perform the request with retries; return parsed JSON body.

        Raises ``ExternalServiceError`` on timeouts, network failures and
        (after retries) unsuccessful status codes.
        """
        url = httpx.URL(path, params=params)
        last_error: Exception | None = None

        for attempt in range(1, MAX_RETRIES + 2):
            try:
                logger.info(
                    "external call service=%s method=%s url=%s attempt=%d",
                    self._service_name, method, url, attempt,
                )
                response = await self._client.request(method, path, params=params, json=json)
                if response.status_code >= 500:
                    raise httpx.HTTPStatusError(
                        f"upstream returned {response.status_code}",
                        request=response.request,
                        response=response,
                    )
                response.raise_for_status()
                logger.info(
                    "external ok service=%s status=%d", self._service_name, response.status_code
                )
                return response.json()

            except httpx.TimeoutException as exc:
                last_error = exc
                logger.warning(
                    "external timeout service=%s url=%s attempt=%d",
                    self._service_name, url, attempt,
                )
            except httpx.HTTPError as exc:
                last_error = exc
                logger.warning(
                    "external error service=%s url=%s attempt=%d error=%s",
                    self._service_name, url, attempt, exc,
                )

            if attempt <= MAX_RETRIES:
                await asyncio.sleep(RETRY_BACKOFF_SECONDS * attempt)

        raise ExternalServiceError(
            service=self._service_name,
            detail=f"{self._service_name} service is temporarily unavailable.",
        ) from last_error
