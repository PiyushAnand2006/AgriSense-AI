"""Crop catalog and farmer crop schemas."""

from datetime import date, datetime

from pydantic import Field

from app.schemas.common import CamelModel


class CropOut(CamelModel):
    id: str
    name: str
    season: str
    scientific_name: str | None = None
    image_url: str = ""
    description: str = ""
    growing_period_days: int | None = None
    sowing_window: str | None = None
    harvest_window: str | None = None
    supported: bool = True


class FarmerCropCreate(CamelModel):
    crop_id: str
    planting_date: date | None = None
    expected_harvest_date: date | None = None
    farm_size: float | None = Field(default=None, ge=0)
    location: str | None = None


class FarmerCropUpdate(CamelModel):
    planting_date: date | None = None
    expected_harvest_date: date | None = None
    farm_size: float | None = Field(default=None, ge=0)
    location: str | None = None
    status: str | None = Field(default=None, pattern="^(ACTIVE|HARVESTED|ARCHIVED)$")


class FarmerCropOut(CamelModel):
    id: str
    crop_id: str
    crop: CropOut | None = None
    season: str
    planting_date: date | None = None
    expected_harvest_date: date | None = None
    farm_size: float | None = None
    location: str | None = None
    status: str
    created_at: datetime | None = None
