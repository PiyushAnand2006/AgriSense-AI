"""Market intelligence endpoints.

- GET /markets               mandi catalog (cached)
- GET /prices                normalized price board with filter/sort/pagination
- GET /prices/{crop_id}      normalized price history for one crop
- GET /trends/{crop_id}      rule-computed trend summary (not a forecast)

All responses follow the normalized internal structure (min/max/modal price,
unit, source) regardless of whether the data came from the external mandi
API or the local database.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.crop import Crop
from app.schemas.market import (
    MarketOut,
    MarketTrend,
    PriceHistory,
    PricePoint,
    PriceSummary,
)
from app.services.market_service import (
    DEFAULT_MARKET_ID,
    compute_trends,
    get_current_price,
    get_history,
    latest_per_combo,
    list_markets_cached,
    prices_source,
    resolve_market,
    trend_direction,
)

router = APIRouter(prefix="/market", tags=["market"])


def _resolve_market_or_503(db: Session, market_id: str | None):
    try:
        return resolve_market(db, market_id)
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)
        ) from exc


@router.get("/markets", response_model=list[MarketOut])
async def list_markets(db: Session = Depends(get_db)):
    markets = await list_markets_cached(db)
    return [MarketOut.model_validate(m) for m in markets]


@router.get("/prices", response_model=list[PriceSummary])
async def price_board(
    cropId: str | None = None,
    marketId: str | None = None,
    state: str | None = None,
    search: str | None = None,
    sort: str = Query(default="name", pattern="^(name|price_asc|price_desc|change_desc)$"),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Latest normalized price per crop x market with change + trends."""
    source = await prices_source()
    summaries: list[PriceSummary] = []
    for price, crop, market in latest_per_combo(db):
        if cropId and crop.id != cropId:
            continue
        if marketId and market.id != marketId:
            continue
        if state and market.state.lower() != state.lower():
            continue
        if search:
            needle = search.lower()
            if not any(
                needle in s for s in (crop.name.lower(), market.name.lower(), market.city.lower())
            ):
                continue
        history = get_history(db, crop.id, market.id, days=31)
        previous = history[-2].modal_price if len(history) >= 2 else price.modal_price
        change = round(price.modal_price - previous, 1)
        change_pct = round((change / previous) * 100, 2) if previous else 0.0
        trends = compute_trends(history)
        summaries.append(
            PriceSummary(
                crop_id=crop.id,
                crop_name=crop.name,
                market_id=market.id,
                market_name=market.name,
                current_price=price.modal_price,
                min_price=price.min_price,
                max_price=price.max_price,
                modal_price=price.modal_price,
                previous_price=previous,
                change=change,
                change_pct=change_pct,
                trend7d=trends["trend7d"],
                trend14d=trends["trend14d"],
                trend30d=trends["trend30d"],
                last_updated=price.price_date,
                source=source,
            )
        )

    sorters = {
        "price_asc": lambda s: s.current_price,
        "price_desc": lambda s: -s.current_price,
        "change_desc": lambda s: -s.change_pct,
        "name": lambda s: (s.crop_name.lower(), s.market_name.lower()),
    }
    summaries.sort(key=sorters[sort])
    start = (page - 1) * limit
    return summaries[start : start + limit]


@router.get("/prices/{crop_id}", response_model=PriceHistory)
async def price_history(
    crop_id: str,
    marketId: str | None = None,
    days: int = Query(default=90, ge=7, le=365),
    db: Session = Depends(get_db),
):
    crop = db.get(Crop, crop_id)
    if crop is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Crop not found.")
    market = _resolve_market_or_503(db, marketId)
    history = get_history(db, crop.id, market.id, days=days)
    if not history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No price data for this crop/market."
        )
    trends = compute_trends(history)
    source = await prices_source()
    return PriceHistory(
        crop_id=crop.id,
        crop_name=crop.name,
        market_id=market.id,
        market_name=market.name,
        current_price=history[-1].modal_price,
        history=[
            PricePoint(date=p.price_date, min_price=p.min_price, max_price=p.max_price, modal_price=p.modal_price)
            for p in history
        ],
        trends=trends,
        source=source,
    )


@router.get("/trends/{crop_id}", response_model=MarketTrend)
async def market_trend(
    crop_id: str,
    marketId: str | None = None,
    days: int = Query(default=30, ge=7, le=120),
    db: Session = Depends(get_db),
):
    """Trend computed from recorded mandi prices — not a forecast."""
    crop = db.get(Crop, crop_id)
    if crop is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Crop not found.")
    market = _resolve_market_or_503(db, marketId)
    history = get_history(db, crop.id, market.id, days=days)
    if not history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No price data for this crop/market."
        )
    trends = compute_trends(history)
    current = history[-1].modal_price
    start_price = history[0].modal_price
    change_pct = round((current - start_price) / start_price * 100, 2) if start_price else 0.0
    return MarketTrend(
        crop_id=crop.id,
        crop_name=crop.name,
        market_id=market.id,
        market_name=market.name,
        days=len(history),
        current_price=current,
        start_price=start_price,
        change=round(current - start_price, 1),
        change_pct=change_pct,
        direction=trend_direction(change_pct).replace("UPWARD", "UP").replace("DOWNWARD", "DOWN"),
        trend7d=trends["trend7d"],
        trend14d=trends["trend14d"],
        trend30d=trends["trend30d"],
        history=[
            PricePoint(date=p.price_date, min_price=p.min_price, max_price=p.max_price, modal_price=p.modal_price)
            for p in history
        ],
    )
