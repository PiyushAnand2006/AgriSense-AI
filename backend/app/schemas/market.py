"""Market price schemas — normalized internal structure.

Every price the API serves uses this shape regardless of where the data came
from (external mandi API or local database). The ``source`` field makes the
origin explicit; the frontend only ever consumes this standardized format.
"""

from datetime import date

from app.schemas.common import CamelModel

PRICE_UNIT = "quintal"


class MarketOut(CamelModel):
    id: str
    name: str
    city: str
    state: str


class PricePoint(CamelModel):
    date: date
    min_price: float = 0.0
    max_price: float = 0.0
    modal_price: float
    unit: str = PRICE_UNIT


class PriceSummary(CamelModel):
    """Latest normalized price + computed change for one crop x market."""

    crop_id: str
    crop_name: str
    market_id: str
    market_name: str
    current_price: float  # modal price (kept for display convenience)
    min_price: float
    max_price: float
    modal_price: float
    unit: str = PRICE_UNIT
    previous_price: float
    change: float
    change_pct: float
    trend7d: float
    trend14d: float
    trend30d: float
    last_updated: date
    source: str  # "mandi-api" | "mandi-db"


class PriceHistory(CamelModel):
    crop_id: str
    crop_name: str
    market_id: str
    market_name: str
    current_price: float
    history: list[PricePoint]
    trends: dict[str, float]
    source: str = "mandi-db"


class MarketTrend(CamelModel):
    """Rule-computed trend summary over recent history (not a forecast)."""

    crop_id: str
    crop_name: str
    market_id: str
    market_name: str
    days: int
    current_price: float
    start_price: float
    change: float
    change_pct: float
    direction: str  # UP | DOWN | FLAT
    trend7d: float
    trend14d: float
    trend30d: float
    history: list[PricePoint] = []
    note: str = "Trend computed from recorded mandi prices — not a price forecast."
