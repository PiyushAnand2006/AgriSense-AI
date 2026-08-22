"""Image upload endpoint (validated, UUID-named, stored in uploads dir)."""

from fastapi import APIRouter, Depends, UploadFile
from pydantic import BaseModel

from app.core.deps import get_current_user
from app.core.files import save_upload
from app.models.user import User

router = APIRouter(prefix="/uploads", tags=["uploads"])


class UploadResult(BaseModel):
    url: str


@router.post("", response_model=UploadResult)
def upload_image(file: UploadFile, current_user: User = Depends(get_current_user)):
    url = save_upload(file)
    return UploadResult(url=url)
