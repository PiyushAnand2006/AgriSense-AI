"""Crop catalog and farmer crop (planting) models."""

import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


def _uuid() -> str:
    return uuid.uuid4().hex


class Crop(Base):
    """Central crop catalog. Adding a new crop is a data change, not a code change."""

    __tablename__ = "crops"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)  # slug e.g. "wheat"
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    season: Mapped[str] = mapped_column(String(10), nullable=False, index=True)  # RABI | ZAID
    scientific_name: Mapped[str | None] = mapped_column(String(120))
    description: Mapped[str] = mapped_column(String(600), default="")
    image_url: Mapped[str] = mapped_column(String(300), default="")
    growing_period_days: Mapped[int | None] = mapped_column(Integer)  # typical sowing->harvest span
    sowing_window: Mapped[str | None] = mapped_column(String(80), default="")  # e.g. "Oct-Nov"
    harvest_window: Mapped[str | None] = mapped_column(String(80), default="")  # e.g. "Mar-Apr"
    supported: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class FarmerCrop(Base):
    """A crop a specific farmer is growing / has grown."""

    __tablename__ = "farmer_crops"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    crop_id: Mapped[str] = mapped_column(ForeignKey("crops.id"), nullable=False)
    season: Mapped[str] = mapped_column(String(10), nullable=False)
    planting_date: Mapped[date | None] = mapped_column(Date)
    expected_harvest_date: Mapped[date | None] = mapped_column(Date)
    farm_size: Mapped[float | None] = mapped_column()  # acres
    location: Mapped[str | None] = mapped_column(String(160))
    status: Mapped[str] = mapped_column(String(12), default="ACTIVE", index=True)  # ACTIVE | HARVESTED | ARCHIVED
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
