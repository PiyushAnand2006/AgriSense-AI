"""Assistant external API hook.

The farmer assistant is rule-based by default. When ``ASSISTANT_API_URL`` is
configured, chat requests are forwarded to an external conversational API
(an LLM provider, a hosted assistant, ...) instead. The API key lives only in
backend configuration and is never exposed to the frontend.
"""

import logging
from typing import Any

from app.external.http_client import ExternalHttpClient

logger = logging.getLogger("agrisense.external.assistant")

SYSTEM_PROMPT = (
    "You are AgriSense, a helpful farming assistant for Indian farmers. "
    "Answer briefly and practically. You are informational support, not a "
    "replacement for local agricultural officers."
)


class AssistantClient:
    def __init__(self, base_url: str, api_key: str = "") -> None:
        self._http = ExternalHttpClient(base_url, api_key=api_key, service_name="assistant")

    @property
    def configured(self) -> bool:
        return bool(self._http.base_url)

    async def chat(self, message: str, history: list[dict[str, str]] | None = None) -> str:
        payload: dict[str, Any] = {
            "message": message,
            "system": SYSTEM_PROMPT,
        }
        if history:
            payload["history"] = history[-8:]  # bound prompt size
        response = await self._http.post("/chat", json=payload)
        return _extract_reply(response)


def _extract_reply(payload: Any) -> str:
    if isinstance(payload, dict):
        for key in ("reply", "response", "answer", "text", "message"):
            value = payload.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        choices = payload.get("choices")
        if isinstance(choices, list) and choices:
            content = choices[0].get("message", {}).get("content")
            if isinstance(content, str):
                return content.strip()
    if isinstance(payload, str) and payload.strip():
        return payload.strip()
    return ""


_assistant_client: AssistantClient | None = None


def get_assistant_client() -> AssistantClient:
    global _assistant_client  # noqa: PLW0603
    if _assistant_client is None:
        from app.core.config import get_settings

        settings = get_settings()
        _assistant_client = AssistantClient(settings.assistant_api_url, settings.assistant_api_key)
    return _assistant_client


def reset_assistant_client(client: AssistantClient | None = None) -> None:
    """Test seam: inject a mock client or reset the singleton."""
    global _assistant_client  # noqa: PLW0603
    _assistant_client = client
