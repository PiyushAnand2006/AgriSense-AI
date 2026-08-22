"""Request correlation + structured request logging.

Every request carries an ``X-Request-ID``:

    Frontend (optional header)
        -> FastAPI (reuses or generates one)
            -> services / external clients (logs)
                -> response header X-Request-ID

Logged per request (never any credentials, tokens or API keys):

    request_id, method, path, status_code, duration_ms, user_id (when authed)
"""

import logging
import time
import uuid
from contextvars import ContextVar

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("agrisense.request")

request_id_ctx: ContextVar[str] = ContextVar("request_id", default="")
user_id_ctx: ContextVar[str] = ContextVar("user_id", default="")


def current_request_id() -> str:
    return request_id_ctx.get()


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex[:16]
        request_id_token = request_id_ctx.set(request_id)
        user_token = None
        start = time.perf_counter()

        try:
            response = await call_next(request)
        except Exception:
            duration_ms = round((time.perf_counter() - start) * 1000, 1)
            logger.exception(
                "request failed request_id=%s method=%s path=%s duration_ms=%s",
                request_id, request.method, request.url.path, duration_ms,
            )
            request_id_ctx.reset(request_id_token)
            raise

        duration_ms = round((time.perf_counter() - start) * 1000, 1)
        # get_current_user stores the authenticated user id on request.state.
        user_id = getattr(request.state, "user_id", "")
        if user_id:
            user_token = user_id_ctx.set(user_id)

        logger.info(
            "request request_id=%s method=%s path=%s status=%d duration_ms=%s user_id=%s",
            request_id, request.method, request.url.path, response.status_code,
            duration_ms, user_id or "-",
        )
        response.headers["X-Request-ID"] = request_id
        if user_token is not None:
            user_id_ctx.reset(user_token)
        request_id_ctx.reset(request_id_token)
        return response
