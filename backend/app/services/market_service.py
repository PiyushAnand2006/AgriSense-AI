"""Market service — price queries, normalization, trends and external feed.

Data flow for every price request:

    route -> market_service
               -> cache (short TTL)
               -> mandi client (external API, when configured)
                    or database (seeded reference data)
               -> normalize -> standardized response

The frontend only ever sees the normalized structure (cropId, marketName,
minPrice, maxPrice, modalPrice, unit, source) regardless of the origin.
"""

import logging
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.cache import MARKET_METADATA_TTL, cache_key, get_cache
from app.external.mandi_client import SOURCE_MANDI_API, SOURCE_MANDI_DB
from app.models.crop import Crop
from app.models.market import Market, MarketPrice

logger = logging.getLogger("agrisense.market")

DEFAULT_MARKET_ID = "delhi-azadpur"


# --- Reference lookups --------------------------------------------------------


def get_crop(db: Session, crop_id: str) -> Crop | None:
    return db.get(Crop, crop_id)


def get_market(db: Session, market_id: str) -> Market | None:
    return db.get(Market, market_id)


def list_markets(db: Session) -> list[Market]:
    """Market metadata is stable — cached aggressively."""
    return list(db.scalars(select(Market).order_by(Market.name)))


async def list_markets_cached(db: Session) -> list[Market]:
    cache = await get_cache()
    key = cache_key("markets")
    cached = await cache.get(key)
    if cached is not None:
        return [Market(**row) for row in cached]
    markets = list_markets(db)
    await cache.set(
        key,
        [{"id": m.id, "name": m.name, "city": m.city, "state": m.state} for m in markets],
        ttl=MARKET_METADATA_TTL,
    )
    return markets


def resolve_market(db: Session, market_id: str | None) -> Market:
    market = db.get(Market, market_id or DEFAULT_MARKET_ID)
    if market is None:
        market = db.scalars(select(Market).order_by(Market.id)).first()
    if market is None:
        raise LookupError("No market data available.")
    return market


# --- Price history (database source) -------------------------------------------


def get_history(db: Session, crop_id: str, market_id: str, days: int = 90) -> list[MarketPrice]:
    start = date.toordinal(date.today()) - days + 1
    stmt = (
        select(MarketPrice)
        .where(
            MarketPrice.crop_id == crop_id,
            MarketPrice.market_id == market_id,
        )
        .order_by(MarketPrice.price_date.desc())
        .limit(days)
    )
    rows = list(db.scalars(stmt))
    rows.reverse()
    # Keep only rows within the window (seeded data always ends today).
    return [r for r in rows if r.price_date.toordinal() >= start]


def get_current_price(db: Session, crop_id: str, market_id: str) -> MarketPrice | None:
    stmt = (
        select(MarketPrice)
        .where(MarketPrice.crop_id == crop_id, MarketPrice.market_id == market_id)
        .order_by(MarketPrice.price_date.desc())
        .limit(1)
    )
    return db.scalars(stmt).first()


def latest_per_combo(db: Session) -> list[tuple[MarketPrice, Crop, Market]]:
    """Latest price row for every crop x market combination."""
    stmt = (
        select(MarketPrice, Crop, Market)
        .join(Crop, Crop.id == MarketPrice.crop_id)
        .join(Market, Market.id == MarketPrice.market_id)
        .order_by(MarketPrice.price_date.desc())
    )
    seen: set[tuple[str, str]] = set()
    results: list[tuple[MarketPrice, Crop, Market]] = []
    for price, crop, market in db.execute(stmt):
        key = (crop.id, market.id)
        if key in seen:
            continue
        seen.add(key)
        results.append((price, crop, market))
    return results


# --- Trend computation (rule-based, not a forecast) ------------------------------


def _pct_change(newer: float, older: float) -> float:
    if older == 0:
        return 0.0
    return round((newer - older) / older * 100, 2)


def compute_trends(history: list[MarketPrice]) -> dict[str, float]:
    """Percentage change over 7/14/30-day windows vs the latest price."""
    latest = history[-1].modal_price if history else 0.0

    def change_over(n: int) -> float:
        if len(history) > n and history[-n - 1].modal_price:
            return _pct_change(latest, history[-n - 1].modal_price)
        return 0.0

    return {"trend7d": change_over(7), "trend14d": change_over(14), "trend30d": change_over(30)}


def trend_direction(change_pct: float) -> str:
    if change_pct > 1.0:
        return "UPWARD"
    if change_pct < -1.0:
        return "DOWNWARD"
    return "FLAT"


# --- External feed integration ---------------------------------------------------


async def fetch_external_prices(crop_name: str | None, market_name: str | None) -> list[dict] | None:
    """Try the configured mandi API; return normalized rows or None.

    Raises ExternalServiceError upward when the provider fails after retries
    so routes can translate it into 502/503/504 responses.
    """
    from app.external.mandi_client import get_mandi_client

    client = get_mandi_client()
    if not client.configured:
        return None
    rows = await client.fetch_prices(commodity=crop_name, market=market_name, limit=50)
    return [row.model_dump(mode="json") for row in rows]


async def prices_source(crop_name: str | None = None, market_name: str | None = None) -> str:
    """Which source will price data come from (used in response metadata)."""
    from app.external.mandi_client import get_mandi_client

    client = get_mandi_client()
    if not client.configured:
        return SOURCE_MANDI_DB
    return SOURCE_MANDI_API
