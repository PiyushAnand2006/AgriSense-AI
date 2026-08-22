"""Fixed-window per-IP rate limiting for sensitive API boundaries.

Applied to (limits are requests/minute/IP and are documented in docs/api.md):

* ``/api/v1/auth``        — registration/login brute-force protection
* ``/api/v1/assistant``   — each chat may hit an external/LLM API
* ``/api/v1/uploads``     — file uploads are expensive
"""

import time
from collections import defaultdict

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

_PREFIX_LIMITS: dict[str, tuple[str, int]] = {
    # path prefix -> (settings field, default limit)
    "/api/v1/auth": ("rate_limit_auth", 30),
    "/api/v1/assistant": ("rate_limit_assistant", 20),
    "/api/v1/uploads": ("rate_limit_uploads", 30),
}

WINDOW_SECONDS = 60.0


class RateLimitMiddleware(BaseHTTPMiddleware):
    """One shared fixed-window limiter keyed by (prefix, ip)."""

    def __init__(self, app) -> None:  # noqa: D107
        super().__init__(app)
        self._hits: dict[tuple[str, str], list[float]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        matched = next(
            (prefix for prefix in _PREFIX_LIMITS if request.url.path.startswith(prefix)),
            None,
        )
        if matched is not None:
            from app.core.config import get_settings

            settings = get_settings()
            field, default = _PREFIX_LIMITS[matched]
            limit = int(getattr(settings, field, default) or default)

            ip = request.client.host if request.client else "unknown"
            now = time.monotonic()
            key = (matched, ip)
            window = self._hits[key]
            self._hits[key] = [t for t in window if now - t < WINDOW_SECONDS]
            if len(self._hits[key]) >= limit:
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": {
                            "code": "RATE_LIMITED",
                            "message": "Too many requests. Please wait a minute and try again.",
                        }
                    },
                    headers={"Retry-After": str(int(WINDOW_SECONDS))},
                )
            self._hits[key].append(now)
        return await call_next(request)
