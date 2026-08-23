"""Farmer-logged crop health records.

Farmers observe a disease or pest in the field, optionally attach a photo
(via /uploads), and log the observation. No inference of any kind happens
server-side.
"""

from datetime import datetime

from pydantic import Field

from app.schemas.common import CamelModel


class HealthRecordCreate(CamelModel):
    record_type: str = Field(pattern="^(DISEASE|PEST)$")
    name: str = Field(min_length=2, max_length=120)  # observed disease/pest name
    severity: str = Field(default="LOW", pattern="^(LOW|MODERATE|HIGH)$")
    image_url: str = ""
    notes: str = Field(default="", max_length=600)


class HealthRecordOut(CamelModel):
    id: str
    crop_id: str
    crop_name: str = ""
    record_type: str  # DISEASE | PEST
    name: str
    severity: str  # LOW | MODERATE | HIGH
    image_url: str = ""
    notes: str = ""
    created_at: datetime | None = None
