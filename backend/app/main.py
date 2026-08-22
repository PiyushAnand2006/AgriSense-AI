"""FastAPI application entrypoint.

Run locally:
    uvicorn app.main:app --reload --port 8000

Middleware stack (outermost first):
    CORS -> RequestContext (X-Request-ID + structured logs) -> RateLimit
Error handlers translate AppError subclasses into the standard
{"error": {"code", "message", "requestId"}} envelope without leaking stack
traces.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import inspect as sqla_inspect

from app import __version__
from app.api.router import api_router
from app.core.config import get_settings
from app.core.errors import AppError
from app.db.session import engine, init_db
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.request_context import RequestContextMiddleware, current_request_id

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("agrisense")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield
    from app.core.cache import close_cache

    await close_cache()


app = FastAPI(
    title="AgriSense AI API",
    version=__version__,
    description=(
        "REST API-driven agricultural information and decision-support platform. "
        "The backend acts as the central API orchestration layer: it owns the "
        "database, integrates external weather/mandi APIs, normalizes their "
        "responses and serves a standardized REST contract to the frontend."
    ),
    lifespan=lifespan,
)

settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(RequestContextMiddleware)

# --- Centralized error handling ------------------------------------------------


def _error_response(status_code: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": message,
                "requestId": current_request_id(),
            }
        },
    )


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    logger.warning(
        "app_error code=%s status=%d service=%s detail=%s",
        exc.code, exc.status_code, exc.service or "-", exc.detail,
    )
    return _error_response(exc.status_code, exc.code, exc.detail)


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    first = exc.errors()[0] if exc.errors() else {}
    loc = ".".join(str(part) for part in first.get("loc", []) if part != "body")
    message = first.get("msg", "Request validation failed.")
    if loc:
        message = f"{loc}: {message}"
    return _error_response(422, "VALIDATION_ERROR", message)


@app.exception_handler(Exception)
async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("unhandled error on %s %s", request.method, request.url.path)
    return _error_response(500, "INTERNAL_ERROR", "An unexpected error occurred.")


# --- Routes ---------------------------------------------------------------------

app.include_router(api_router, prefix="/api/v1")
app.mount("/uploads", StaticFiles(directory=str(settings.upload_path)), name="uploads")


@app.get("/")
def root():
    return {
        "app": "AgriSense AI API",
        "version": __version__,
        "docs": "/docs",
        "api": "/api/v1",
        "health": "/health",
    }


# --- Health checks (no auth, no sensitive details) --------------------------------


@app.get("/health")
def health():
    """Liveness: the process is up and serving."""
    return {"status": "ok", "version": __version__}


@app.get("/health/live")
def health_live():
    return {"status": "ok"}


@app.get("/health/ready")
def health_ready():
    """Readiness: dependencies (database) are reachable."""
    try:
        with engine.connect() as connection:
            # A metadata read doubles as a connectivity round-trip.
            sqla_inspect(connection).get_table_names()
        return {"status": "ok", "database": "up"}
    except Exception as exc:  # noqa: BLE001 — readiness must never crash
        logger.warning("readiness check failed: %s", exc)
        return JSONResponse(
            status_code=503,
            content={"status": "degraded", "database": "down"},
        )
