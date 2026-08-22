"""Secure image upload handling.

Rules enforced here:
- allow-list of JPEG / PNG / WEBP, verified by magic bytes (not just headers)
- hard size limit from settings (MAX_UPLOAD_MB)
- server-generated filenames only; user filenames are never trusted
- files are stored in a dedicated uploads directory outside source trees
"""

import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile, status

from app.core.config import get_settings

ALLOWED_TYPES: dict[str, str] = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}


def _sniff_type(data: bytes) -> str | None:
    if data[:3] == b"\xff\xd8\xff":
        return "image/jpeg"
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return "image/png"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "image/webp"
    return None


def save_upload(file: UploadFile) -> str:
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
    destination: Path = settings.upload_path / filename
    destination.write_bytes(data)
    return f"/uploads/{filename}"
