"""Market (mandi) and daily market price models.

Rows follow the normalized mandi structure: min / max / modal price per
quintal per day, mirroring AGMARKNET-style feeds.
"""

from datetime import date

from sqlalchemy import Date, Float, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Market(Base):
    __tablename__ = "markets"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)  # slug e.g. "delhi-azadpur"
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    city: Mapped[str] = mapped_column(String(120), nullable=False)
    state: Mapped[str] = mapped_column(String(120), nullable=False)


class MarketPrice(Base):
    __tablename__ = "market_prices"
    __table_args__ = (
        UniqueConstraint("crop_id", "market_id", "price_date", name="uq_price_per_day"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    crop_id: Mapped[str] = mapped_column(
        ForeignKey("crops.id", ondelete="CASCADE"), index=True, nullable=False
    )
    market_id: Mapped[str] = mapped_column(
        ForeignKey("markets.id", ondelete="CASCADE"), index=True, nullable=False
    )
    price_date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    modal_price: Mapped[float] = mapped_column(nullable=False)  # INR per quintal
    min_price: Mapped[float] = mapped_column(nullable=False, server_default="0")
    max_price: Mapped[float] = mapped_column(nullable=False, server_default="0")
