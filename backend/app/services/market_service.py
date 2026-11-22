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
from datetime import date, timedelta

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


# Daily in-process cache for the bulk history fetch — same criteria as
# latest_per_combo: identical for every user, changes only at the daily seed
# rollover, so it is keyed by calendar date (+ window length).
_history_bulk_cache: dict[tuple[str, int], dict[tuple[str, str], list[MarketPrice]]] = {}


def _compute_history_bulk(db: Session, days: int) -> dict[tuple[str, str], list[MarketPrice]]:
    """Trailing `days` of prices for every crop x market combo, one indexed
    range query (uq_price_per_day leads with crop_id, market_id), grouped
    oldest-first per combo — same ordering contract as get_history()."""
    start = date.today() - timedelta(days=days - 1)
    stmt = (
        select(MarketPrice)
        .where(MarketPrice.price_date >= start)
        .order_by(MarketPrice.crop_id, MarketPrice.market_id, MarketPrice.price_date)
    )
    bulk: dict[tuple[str, str], list[MarketPrice]] = {}
    for price in db.scalars(stmt):
        bulk.setdefault((price.crop_id, price.market_id), []).append(price)
    return bulk


def get_history_bulk(db: Session, days: int = 31) -> dict[tuple[str, str], list[MarketPrice]]:
    """Bulk history with the daily cache applied.

    Replaces the price board's old per-combo get_history() loop — an N+1 that
    cost one DB round trip (~150ms across regions) per combo, ~26s per page
    load — with one indexed range query per day.
    """
    today = date.today().isoformat()
    cached = _history_bulk_cache.get((today, days))
    if cached is None:
        cached = _compute_history_bulk(db, days)
        _history_bulk_cache.clear()  # drop stale dates
        _history_bulk_cache[(today, days)] = cached
    # Shallow copy: callers cannot mutate the cached dict itself.
    return dict(cached)


def get_current_price(db: Session, crop_id: str, market_id: str) -> MarketPrice | None:
    stmt = (
        select(MarketPrice)
        .where(MarketPrice.crop_id == crop_id, MarketPrice.market_id == market_id)
        .order_by(MarketPrice.price_date.desc())
        .limit(1)
    )
    return db.scalars(stmt).first()


# --- Latest price per crop x market (daily in-process cache) ---------------------

# latest_per_combo() scans the whole market_prices table and de-duplicates it
# in Python, but its result is identical for every user and only changes when
# the daily seed rolls prices over (calendar date) or the process restarts, so
# the result is cached in-process, keyed by calendar date. Never cache
# user-specific data here. Detached ORM instances are fine to hand out because
# callers only read loaded column attributes.
_latest_combo_cache: dict[str, list[tuple[MarketPrice, Crop, Market]]] = {}


def _compute_latest_per_combo(db: Session) -> list[tuple[MarketPrice, Crop, Market]]:
    """Newest price row for every crop x market combo.

    Derived from today's rows via the bulk range query (the seed guarantees
    every combo has a row for the current date after boot), so instead of a
    whole-table scan + Python de-duplication we pay one single-day indexed
    query plus two tiny catalog lookups.
    """
    today_rows = _compute_history_bulk(db, days=1)
    crops = {crop.id: crop for crop in db.scalars(select(Crop))}
    markets = {market.id: market for market in db.scalars(select(Market))}
    results: list[tuple[MarketPrice, Crop, Market]] = []
    for (crop_id, market_id), rows in today_rows.items():
        crop = crops.get(crop_id)
        market = markets.get(market_id)
        if rows and crop is not None and market is not None:
            results.append((rows[-1], crop, market))
    return results


def latest_per_combo(db: Session) -> list[tuple[MarketPrice, Crop, Market]]:
    """Latest price row for every crop x market combination (cached per day)."""
    today = date.today().isoformat()
    cached = _latest_combo_cache.get(today)
    if cached is None:
        cached = _compute_latest_per_combo(db)
        _latest_combo_cache.clear()  # drop stale dates
        _latest_combo_cache[today] = cached
    # Hand out a copy so callers cannot mutate the cached list.
    return list(cached)


def clear_latest_combo_cache() -> None:
    """Drop the cached combos (used by tests and future invalidation hooks)."""
    _latest_combo_cache.clear()


def clear_market_caches() -> None:
    """Drop both daily market caches (tests and future invalidation hooks)."""
    _latest_combo_cache.clear()
    _history_bulk_cache.clear()


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
