"""Dashboard aggregate schema.

One request -> backend gathers crop, market, weather and notification data.
Partial failures of non-critical sources are reported in ``warnings`` instead
of failing the whole response.
"""

from datetime import date

from app.schemas.common import CamelModel
from app.schemas.crop import CropOut
from app.schemas.health_record import HealthRecordOut
from app.schemas.market import MarketTrend
from app.schemas.weather import WeatherDay


class HealthScorePoint(CamelModel):
    date: date
    score: float
    name: str | None = None  # observed disease/pest name
    severity: str | None = None


class DashboardSummary(CamelModel):
    crop: CropOut
    season: str
    health_score: float
    health_score_label: str
    latest_record: HealthRecordOut | None = None
    market_id: str
    market_name: str
    market_price: float
    market_source: str = "mandi-db"
    market_trend: MarketTrend | None = None
    recommendation: str | None = None
    recommendation_risk: str | None = None
    expected_additional_return: float | None = None
    health_history: list[HealthScorePoint] = []
    weather: WeatherDay | None = None
    weather_source: str | None = None
    unread_notifications: int = 0
    warnings: list[str] = []  # e.g. "Weather service unavailable"
