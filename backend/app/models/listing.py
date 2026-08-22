"""Farmer marketplace crop listing model."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


def _uuid() -> str:
    return uuid.uuid4().hex


class CropListing(Base):
    __tablename__ = "crop_listings"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_uuid)
    farmer_id: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    farmer_name: Mapped[str] = mapped_column(String(120), default="")
    crop_id: Mapped[str] = mapped_column(String(40), index=True, nullable=False)
    quantity: Mapped[float] = mapped_column(nullable=False)
    unit: Mapped[str] = mapped_column(String(16), default="quintal")
    asking_price: Mapped[float] = mapped_column(nullable=False)  # INR per unit
    quality_grade: Mapped[str | None] = mapped_column(String(4))
    location: Mapped[str | None] = mapped_column(String(160))
    status: Mapped[str] = mapped_column(String(10), default="ACTIVE", index=True)  # ACTIVE | SOLD | EXPIRED
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
