"""Image storage backends: Supabase Storage when configured, local dir otherwise.

Render's filesystem is ephemeral, so production must store uploads in object
storage. These tests pin the contract of both backends (no real network: the
Supabase path is exercised through a mocked httpx.post).
"""

from pathlib import Path

import httpx

from app.core.config import get_settings
from tests.conftest import PNG_BYTES

API = "/api/v1/uploads"


def _upload(client, auth):
    return client.post(
        API,
        files={"file": ("leaf.png", PNG_BYTES, "image/png")},
        headers=auth["headers"],
    )


def _configure_supabase(monkeypatch) -> None:
    settings = get_settings()
    monkeypatch.setattr(settings, "supabase_url", "https://proj.supabase.co", raising=False)
    monkeypatch.setattr(settings, "supabase_storage_key", "test-service-key", raising=False)
    monkeypatch.setattr(settings, "supabase_storage_bucket", "crop-health", raising=False)


def test_local_fallback_when_storage_not_configured(client, auth, monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "supabase_url", "", raising=False)
    monkeypatch.setattr(settings, "supabase_storage_key", "", raising=False)

    response = _upload(client, auth)
    assert response.status_code == 200, response.text
    url = response.json()["url"]
    assert url.startswith("/uploads/") and url.endswith(".png")

    # The file really is on the local disk.
    assert (Path(get_settings().upload_path) / Path(url).name).exists()


def test_supabase_storage_upload_returns_public_url(client, auth, monkeypatch):
    _configure_supabase(monkeypatch)
    captured: dict = {}

    def fake_post(url, **kwargs):
        captured["url"] = url
        captured["kwargs"] = kwargs
        return httpx.Response(200, request=httpx.Request("POST", url))

    monkeypatch.setattr("app.core.files.httpx.post", fake_post)

    response = _upload(client, auth)
    assert response.status_code == 200, response.text
    url = response.json()["url"]

    assert url.startswith(
        "https://proj.supabase.co/storage/v1/object/public/crop-health/health-records/"
    )
    assert url.endswith(".png")
    assert captured["url"] == (
        "https://proj.supabase.co/storage/v1/object/crop-health/health-records/"
        + url.rsplit("/", 1)[1]
    )
    assert captured["kwargs"]["headers"]["Authorization"] == "Bearer test-service-key"
    assert captured["kwargs"]["headers"]["Content-Type"] == "image/png"

    # Nothing written to the (ephemeral) local disk when storage is configured.
    assert not (Path(get_settings().upload_path) / Path(url).name).exists()


def test_supabase_storage_rejection_maps_to_502(client, auth, monkeypatch):
    _configure_supabase(monkeypatch)
    monkeypatch.setattr(
        "app.core.files.httpx.post",
        lambda url, **kwargs: httpx.Response(500, request=httpx.Request("POST", url)),
    )
    response = _upload(client, auth)
    assert response.status_code == 502


def test_supabase_storage_network_error_maps_to_502(client, auth, monkeypatch):
    _configure_supabase(monkeypatch)

    def unreachable(url, **kwargs):
        raise httpx.ConnectError("connection refused")

    monkeypatch.setattr("app.core.files.httpx.post", unreachable)
    response = _upload(client, auth)
    assert response.status_code == 502
