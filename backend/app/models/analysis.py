"""Farmer-logged crop health records and sell/hold recommendation records.

Health records are observations the farmer logs (disease/pest seen in the
field, optionally with a photo). No server-side inference happens — the
earlier ML analysis tables were removed with the ML layer.
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


def _uuid() -> str:
    return uuid.uuid4().hex


class HealthRecord(Base):
    """A farmer-logged disease/pest observation for one crop."""

    __tablename__ = "health_records"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    crop_id: Mapped[str] = mapped_column(ForeignKey("crops.id"), index=True, nullable=False)
    record_type: Mapped[str] = mapped_column(String(10), nullable=False)  # DISEASE | PEST
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    severity: Mapped[str] = mapped_column(String(12), nullable=False)  # LOW | MODERATE | HIGH
    image_url: Mapped[str] = mapped_column(String(300), default="")
    notes: Mapped[str] = mapped_column(String(600), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), index=True)


class SellHoldRecommendation(Base):
    """Persisted output of the rule-based sell/hold decision engine."""

    __tablename__ = "sell_hold_recommendations"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    crop_id: Mapped[str] = mapped_column(ForeignKey("crops.id"), nullable=False)
    market_id: Mapped[str] = mapped_column(String(40), nullable=False)
    quantity: Mapped[float] = mapped_column(nullable=False)
    storage_days: Mapped[int] = mapped_column(Integer, nullable=False)
    recommendation: Mapped[str] = mapped_column(String(6), nullable=False)  # SELL | HOLD
    current_price: Mapped[float] = mapped_column(nullable=False)
    projected_price: Mapped[float] = mapped_column(nullable=False)
    trend: Mapped[str] = mapped_column(String(10), nullable=False)  # UPWARD | DOWNWARD | FLAT
    trend_change_pct: Mapped[float] = mapped_column(nullable=False)
    storage_cost: Mapped[float] = mapped_column(nullable=False)
    expected_additional_return: Mapped[float] = mapped_column(nullable=False)
    risk: Mapped[str] = mapped_column(String(10), nullable=False)  # LOW | MEDIUM | HIGH
    reason: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), index=True)
