"""Marketplace listing schemas."""

from datetime import datetime

from pydantic import Field

from app.schemas.common import CamelModel


class ListingCreate(CamelModel):
    crop_id: str
    quantity: float = Field(gt=0, le=100000)
    unit: str = Field(default="quintal", max_length=16)
    asking_price: float = Field(gt=0)
    quality_grade: str | None = Field(default=None, pattern="^(A|B|C)$")
    location: str | None = Field(default=None, max_length=160)


class ListingUpdate(CamelModel):
    quantity: float | None = Field(default=None, gt=0)
    asking_price: float | None = Field(default=None, gt=0)
    quality_grade: str | None = Field(default=None, pattern="^(A|B|C)$")
    location: str | None = Field(default=None, max_length=160)
    status: str | None = Field(default=None, pattern="^(ACTIVE|SOLD|EXPIRED)$")


class ListingOut(CamelModel):
    id: str
    farmer_id: str
    farmer_name: str = ""
    crop_id: str
    crop_name: str = ""
    quantity: float
    unit: str
    asking_price: float
    quality_grade: str | None = None
    location: str | None = None
    status: str
    created_at: datetime | None = None
