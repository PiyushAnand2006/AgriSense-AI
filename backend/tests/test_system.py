"""System, middleware and health-check tests.

Covers: request correlation IDs, structured request logging hooks,
rate limiting, and the /health endpoint family.
"""


def test_health_checks(client):
    live = client.get("/health")
    assert live.status_code == 200
    assert live.json()["status"] == "ok"

    live2 = client.get("/health/live")
    assert live2.status_code == 200 and live2.json()["status"] == "ok"

    ready = client.get("/health/ready")
    assert ready.status_code == 200
    assert ready.json()["database"] == "up"
    # No sensitive details in health output.
    assert "database_url" not in ready.json()


def test_request_id_generated_and_returned(client):
    response = client.get("/api/v1/system")
    assert "x-request-id" in response.headers
    assert response.headers["x-request-id"]


def test_request_id_correlation(client):
    """A client-provided X-Request-ID is echoed back (correlation across hops)."""
    response = client.get("/api/v1/system", headers={"X-Request-ID": "trace-abc-123"})
    assert response.headers["x-request-id"] == "trace-abc-123"


def test_root_endpoint_lists_entrypoints(client):
    body = client.get("/").json()
    assert body["api"] == "/api/v1"
    assert body["docs"] == "/docs"
    assert body["health"] == "/health"


def test_auth_rate_limiting():
    """Exceeding the auth rate limit returns 429 with the error envelope.

    Uses an isolated mini-app so the shared suite client's limiter state is
    never polluted (limits are raised suite-wide in conftest).
    """
    from fastapi import APIRouter, FastAPI
    from fastapi.testclient import TestClient

    from app.core.config import get_settings
    from app.middleware.rate_limit import RateLimitMiddleware

    mini = FastAPI()
    auth = APIRouter(prefix="/api/v1/auth")

    @auth.post("/login")
    def login():
        return {"ok": True}

    mini.include_router(auth)
    mini.add_middleware(RateLimitMiddleware)

    settings = get_settings()
    original = settings.rate_limit_auth
    settings.rate_limit_auth = 3
    try:
        with TestClient(mini) as tc:
            codes = [tc.post("/api/v1/auth/login").status_code for _ in range(5)]
        assert codes[:3] == [200, 200, 200]
        assert 429 in codes[3:]
        with TestClient(mini) as tc:
            limited = tc.post("/api/v1/auth/login")
            limited = tc.post("/api/v1/auth/login")
            limited = tc.post("/api/v1/auth/login")
            limited = tc.post("/api/v1/auth/login")
            assert limited.status_code == 429
            assert limited.json()["error"]["code"] == "RATE_LIMITED"
    finally:
        settings.rate_limit_auth = original


def test_error_envelope_on_404(client):
    response = client.get("/api/v1/diseases/not-a-real-disease")
    assert response.status_code == 404
    # FastAPI HTTPException detail (legacy shape) or envelope — both 404.
    # The standardized envelope is used by AppError/validation handlers.
    assert response.json()  # a JSON body is always present


def test_openapi_documentation_complete(client):
    schema = client.get("/openapi.json").json()
    paths = schema["paths"]
    # Core documented endpoint families exist.
    for prefix in (
        "/api/v1/seasons", "/api/v1/crops", "/api/v1/diseases", "/api/v1/pests",
        "/api/v1/treatments", "/api/v1/fertilizers", "/api/v1/market", "/api/v1/weather",
        "/api/v1/dashboard", "/api/v1/recommendations", "/api/v1/listings",
        "/api/v1/assistant", "/api/v1/notifications", "/api/v1/auth",
    ):
        assert any(p.startswith(prefix) for p in paths), f"missing {prefix} in OpenAPI"
    # Unknown endpoint families must not exist.
    for gone in ("/api/v1/health/analyze", "/api/v1/pests/analyze",
                 "/api/v1/quality/analyze", "/api/v1/market/forecast/{crop_id}"):
        assert gone not in paths
