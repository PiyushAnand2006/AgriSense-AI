"""Test configuration: isolated SQLite DB + authenticated client helpers."""

import os
import sys
import tempfile
import uuid
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

_TMP = tempfile.mkdtemp(prefix="agrisense-test-")
os.environ["DATABASE_URL"] = f"sqlite:///{_TMP}/test.db"
os.environ["UPLOAD_DIR"] = f"{_TMP}/uploads"
# Rate limits are raised for the suite (many tests register users through
# one client IP); the limiter itself is tested in isolation in test_system.
os.environ["RATE_LIMIT_AUTH"] = "1000"
os.environ["RATE_LIMIT_ASSISTANT"] = "1000"
os.environ["RATE_LIMIT_UPLOADS"] = "1000"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

# Fixture credential for throwaway test accounts (never a real secret).
TEST_PASSWORD = os.environ.get("AGRISENSE_TEST_PASSWORD", "Test-Passw0rd-Fixture")


@pytest.fixture(scope="session")
def client():
    from app.main import app

    with TestClient(app) as test_client:
        yield test_client


def register_user(client: TestClient) -> dict:
    email = f"farmer-{uuid.uuid4().hex[:10]}@example.com"
    response = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Test Farmer",
            "email": email,
            "password": TEST_PASSWORD,
            "village": "Baragaon",
            "district": "Varanasi",
            "state": "Uttar Pradesh",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


@pytest.fixture()
def auth(client):
    """A freshly registered user + Authorization headers."""
    payload = register_user(client)
    return {"token": payload["token"], "user": payload["user"], "headers": {"Authorization": f"Bearer {payload['token']}"}}


# Minimal valid 1x1 PNG for upload tests.
PNG_BYTES = bytes.fromhex(
    "89504e470d0a1a0a0000000d4948445200000001000000010806000000"
    "1f15c4890000000d49444154789c6360000002000100"
    "0521a10f0000000049454e44ae426082"
)
