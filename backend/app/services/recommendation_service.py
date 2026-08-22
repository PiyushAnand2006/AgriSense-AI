"""Sell / Hold decision-support engine — transparent rules, no ML.

The backend exclusively owns this logic; the frontend never computes a
recommendation. Inputs:

* current modal price (recorded mandi data)
* recent trend (7/14/30-day percentage change over recorded history)
* quantity + storage duration
* storage cost (explicit or default estimate)
* farmer's risk tolerance

Rules (documented, deterministic — see docs/api-pipeline.md):

1. Project the price over the storage window by extrapolating the recent
   trend (capped at ±20% so a hot streak never promises the moon).
2. expected_return = projected_price - current_price - storage_cost
3. HOLD if expected_return exceeds the risk-specific threshold, else SELL:
       LOW risk    -> +2.0% of current price
       MEDIUM risk -> +0.5%
       HIGH risk   ->  0.0%
4. Risk label reflects storage horizon and trend flatness.

This is decision support, not financial advice.
"""

import logging

from sqlalchemy.orm import Session

from app.models.analysis import SellHoldRecommendation
from app.models.user import User
from app.schemas.recommendation import DISCLAIMER, SellHoldRequest, SellHoldResult
from app.services.market_service import (
    compute_trends,
    get_crop,
    get_current_price,
    get_history,
    get_market,
    resolve_market,
    trend_direction,
)
from app.services.notification_service import notify

logger = logging.getLogger("agrisense.recommendation")

DEFAULT_STORAGE_COST_PER_DAY = 7.0  # demo value, INR per quintal per day

# Minimum expected net gain (as % of current price) required to HOLD.
_HOLD_THRESHOLD = {"LOW": 2.0, "MEDIUM": 0.5, "HIGH": 0.0}

# Cap on trend extrapolation over the storage window (fraction of price).
_MAX_PROJECTION_SWING = 0.20


def _first_market(db: Session):
    return resolve_market(db, None)


def _projected_price(current: float, daily_trend_pct: float, days: int) -> float:
    """Extrapolate the recent trend over the storage window, capped ±20%."""
    projected = current * (1.0 + daily_trend_pct / 100.0 * days)
    swing = current * _MAX_PROJECTION_SWING
    return round(max(current - swing, min(current + swing, projected)), 1)


def compute_sell_hold(db: Session, user: User, request: SellHoldRequest) -> SellHoldResult:
    crop = get_crop(db, request.crop_id)
    if crop is None:
        raise ValueError("Unknown crop")

    market = get_market(db, request.market_id) if request.market_id else _first_market(db)
    if market is None:
        raise ValueError("Unknown market")

    latest = get_current_price(db, crop.id, market.id)
    if latest is None:
        raise ValueError("No price data for this crop/market")

    history = get_history(db, crop.id, market.id, days=90)
    trends = compute_trends(history)
    trend_pct = trends["trend7d"] if trends["trend7d"] != 0 else trends["trend14d"]
    direction = trend_direction(trend_pct)

    current_price = latest.modal_price
    storage_cost = (
        request.storage_cost
        if request.storage_cost is not None
        else DEFAULT_STORAGE_COST_PER_DAY * request.storage_days
    )
    projected_price = _projected_price(current_price, trend_pct / 7.0, request.storage_days)

    expected_return = round(projected_price - current_price - storage_cost, 1)
    expected_return_pct = (expected_return / current_price * 100) if current_price else 0.0

    threshold = _HOLD_THRESHOLD[request.risk_tolerance]
    decision = "HOLD" if expected_return_pct > threshold else "SELL"

    # Risk reflects horizon length and trend flatness.
    if request.storage_days > 30:
        risk = "HIGH"
    elif request.storage_days > 14:
        risk = "MEDIUM"
    else:
        risk = "LOW"
    if abs(expected_return_pct) < 1.0:
        risk = "HIGH" if risk != "LOW" else "MEDIUM"

    if decision == "HOLD":
        reason = (
            f"Recent {crop.name} trend is {direction.lower()} ({trend_pct:+.1f}% over the last week) "
            f"and the projected price over {request.storage_days} days (₹{projected_price:,.0f}/quintal) "
            f"covers the ₹{storage_cost:,.0f} storage cost with an expected additional return of "
            f"₹{expected_return:,.0f}/quintal — above your {request.risk_tolerance.lower()}-risk threshold."
        )
    else:
        reason = (
            f"Recent {crop.name} trend is {direction.lower()} ({trend_pct:+.1f}% over the last week). "
            f"The projected price over {request.storage_days} days (₹{projected_price:,.0f}/quintal) does "
            f"not cover the ₹{storage_cost:,.0f} storage cost beyond your {request.risk_tolerance.lower()}-risk "
            f"threshold — selling now locks in ₹{current_price:,.0f}/quintal."
        )

    record = SellHoldRecommendation(
        user_id=user.id,
        crop_id=crop.id,
        market_id=market.id,
        quantity=request.quantity,
        storage_days=request.storage_days,
        recommendation=decision,
        current_price=current_price,
        projected_price=projected_price,
        trend=direction,
        trend_change_pct=trend_pct,
        storage_cost=round(storage_cost, 1),
        expected_additional_return=expected_return,
        risk=risk,
        reason=reason,
    )
    db.add(record)
    db.commit()

    notify(
        db,
        user.id,
        type="RECOMMENDATION",
        title=f"Sell/Hold recommendation: {decision}",
        message=f"{crop.name} @ {market.name}: {decision} — trend {direction.lower()}, risk {risk.lower()}.",
    )

    return SellHoldResult(
        recommendation=decision,
        reason=reason,
        current_price=current_price,
        trend=direction,
        trend_change_pct=trend_pct,
        projected_price=projected_price,
        storage_cost=round(storage_cost, 1),
        expected_additional_return=expected_return,
        risk=risk,
        crop_id=crop.id,
        crop_name=crop.name,
        market_id=market.id,
        market_name=market.name,
        quantity=request.quantity,
        storage_days=request.storage_days,
        disclaimer=DISCLAIMER,
    )


def recommendation_history(db: Session, user: User, limit: int = 10) -> list[SellHoldResult]:
    from sqlalchemy import select

    from app.models.crop import Crop
    from app.models.market import Market

    records = list(
        db.scalars(
            select(SellHoldRecommendation)
            .where(SellHoldRecommendation.user_id == user.id)
            .order_by(SellHoldRecommendation.created_at.desc())
            .limit(min(limit, 30))
        )
    )
    results = []
    for r in records:
        crop = db.get(Crop, r.crop_id)
        market = db.get(Market, r.market_id)
        results.append(
            SellHoldResult(
                recommendation=r.recommendation,
                reason=r.reason,
                current_price=r.current_price,
                trend=r.trend,
                trend_change_pct=r.trend_change_pct,
                projected_price=r.projected_price,
                storage_cost=r.storage_cost,
                expected_additional_return=r.expected_additional_return,
                risk=r.risk,
                crop_id=r.crop_id,
                crop_name=crop.name if crop else r.crop_id,
                market_id=r.market_id,
                market_name=market.name if market else r.market_id,
                quantity=r.quantity,
                storage_days=r.storage_days,
                disclaimer=DISCLAIMER,
            )
        )
    return results
