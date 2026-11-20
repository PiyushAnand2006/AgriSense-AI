"""Secure image upload handling.

Rules enforced here:
- allow-list of JPEG / PNG / WEBP, verified by magic bytes (not just headers)
- hard size limit from settings (MAX_UPLOAD_MB)
- server-generated filenames only; user filenames are never trusted
- storage backends: Supabase Storage (absolute public URLs) when configured,
  otherwise the local uploads directory (dev/tests). Render's filesystem is
  ephemeral — files written locally are lost on every deploy/restart — so
  production deployments should configure Supabase Storage.
"""

import uuid
from pathlib import Path

import httpx
from fastapi import HTTPException, UploadFile, status

from app.core.config import Settings, get_settings

ALLOWED_TYPES: dict[str, str] = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}

# Sub-folder inside the storage bucket; keeps the bucket root tidy and makes
# per-purpose lifecycle/cleanup rules possible later.
_STORAGE_PREFIX = "health-records"


def _sniff_type(data: bytes) -> str | None:
    if data[:3] == b"\xff\xd8\xff":
        return "image/jpeg"
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return "image/png"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "image/webp"
    return None


def save_upload(file: UploadFile) -> str:
    """Validate and persist an uploaded image; return its URL."""
    settings = get_settings()
    limit = settings.max_upload_mb * 1024 * 1024

    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file type. Allowed: JPEG, PNG, WEBP.",
        )

    data = file.file.read(limit + 1)
    if len(data) > limit:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum {settings.max_upload_mb} MB.",
        )
    if not data:
        raise HTTPException(status_code=400, detail="Empty file.")

    sniffed = _sniff_type(data)
    if sniffed is None or sniffed != file.content_type:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="File content does not match an allowed image type (JPEG, PNG, WEBP).",
        )

    filename = f"{uuid.uuid4().hex}{ALLOWED_TYPES[sniffed]}"
    if settings.is_supabase_storage_configured:
        return _save_to_supabase(data, sniffed, filename, settings)
    return _save_to_local(data, filename, settings)


def _save_to_local(data: bytes, filename: str, settings: Settings) -> str:
    """Write to the local uploads dir; return the app-relative URL."""
    destination: Path = settings.upload_path / filename
    destination.write_bytes(data)
    return f"/uploads/{filename}"


def _save_to_supabase(data: bytes, content_type: str, filename: str, settings: Settings) -> str:
    """Upload to a public Supabase Storage bucket; return the public URL.

    Uses the service-role key server-side only. Failures raise 502 so a
    storage outage is visible to the farmer instead of silently writing to
    an ephemeral disk (which would lose the photo on the next deploy anyway).
    """
    base = settings.supabase_url.rstrip("/")
    bucket = settings.supabase_storage_bucket
    path = f"{_STORAGE_PREFIX}/{filename}"
    try:
        response = httpx.post(
            f"{base}/storage/v1/object/{bucket}/{path}",
            content=data,
            headers={
                "Authorization": f"Bearer {settings.supabase_storage_key}",
                "Content-Type": content_type,
                "x-upsert": "true",
            },
            timeout=30.0,
        )
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Image storage is temporarily unavailable. Please try again.",
        ) from exc
    if response.status_code >= 300:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Image storage rejected the upload. Please try again.",
        )
    return f"{base}/storage/v1/object/public/{bucket}/{path}"
