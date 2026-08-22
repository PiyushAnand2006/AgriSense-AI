"""Daily weather snapshot model (mock provider fills this for now)."""

from datetime import date

from sqlalchemy import Date, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class WeatherSnapshot(Base):
    __tablename__ = "weather_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    snapshot_date: Mapped[date] = mapped_column(Date, unique=True, index=True, nullable=False)
    temperature_c: Mapped[float] = mapped_column(nullable=False)
    humidity_pct: Mapped[float] = mapped_column(nullable=False)
    rain_probability: Mapped[float] = mapped_column(nullable=False)
    wind_kph: Mapped[float] = mapped_column(nullable=False)
    condition: Mapped[str] = mapped_column(String(40), nullable=False)  # Sunny | Cloudy | Rain | ...
