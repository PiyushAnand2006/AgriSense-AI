"""Centralized application error types.

The error handlers registered in ``app.main`` translate these into the
standard wire format:

    {"error": {"code": "...", "message": "...", "requestId": "..."}}

Internal stack traces are never exposed to clients.
"""

from typing import Any


class AppError(Exception):
    """Base class for application errors with a stable machine-readable code."""

    status_code = 500
    code = "INTERNAL_ERROR"

    def __init__(self, detail: str = "", *, service: str = "", context: dict[str, Any] | None = None) -> None:
        super().__init__(detail)
        self.detail = detail or self.default_message
        self.service = service
        self.context = context or {}

    @property
    def default_message(self) -> str:
        return "An unexpected error occurred."


class ExternalServiceError(AppError):
    """A third-party API failed after retries (timeout / 5xx / network)."""

    status_code = 503
    code = "EXTERNAL_SERVICE_UNAVAILABLE"

    @property
    def default_message(self) -> str:
        return "An external service is temporarily unavailable."


class ExternalServiceTimeout(AppError):
    """A third-party API timed out."""

    status_code = 504
    code = "EXTERNAL_SERVICE_TIMEOUT"

    @property
    def default_message(self) -> str:
        return "An external service took too long to respond."


class UpstreamBadResponseError(AppError):
    """A third-party API returned a payload we could not validate/normalize."""

    status_code = 502
    code = "EXTERNAL_SERVICE_BAD_RESPONSE"

    @property
    def default_message(self) -> str:
        return "An external service returned an unexpected response."


class NotFoundError(AppError):
    status_code = 404
    code = "NOT_FOUND"

    @property
    def default_message(self) -> str:
        return "Resource not found."


class ValidationError(AppError):
    status_code = 422
    code = "VALIDATION_ERROR"

    @property
    def default_message(self) -> str:
        return "Request validation failed."
