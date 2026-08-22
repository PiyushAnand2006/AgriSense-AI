"""Dashboard aggregation service.

One request -> backend gathers crop, market, weather and notification data
in parallel. Partial failures of non-critical sources (weather, market) are
collected into ``warnings`` instead of failing the whole response:

    {"crop": {...}, "market": {...}, "weather": null,
     "notifications": [...], "warnings": ["Weather service unavailable"]}
"""

import logging
from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.errors import ExternalServiceError
from app.models.analysis import HealthRecord, SellHoldRecommendation
from app.models.crop import Crop, FarmerCrop
from app.models.user import Notification, User
from app.schemas.dashboard import DashboardSummary, HealthScorePoint
from app.schemas.health_record import HealthRecordOut
from app.schemas.market import MarketTrend
from app.services.market_service import (
    DEFAULT_MARKET_ID,
    compute_trends,
    get_current_price,
    get_history,
    trend_direction,
)
from app.services.weather_service import get_weather

logger = logging.getLogger("agrisense.dashboard")

_SEVERITY_SCORE = {"LOW": 90, "MODERATE": 74, "HIGH": 55}


def _score_label(score: float) -> str:
    if score >= 90:
        return "Excellent"
    if score >= 75:
        return "Good"
    if score >= 60:
        return "Watch"
    return "Critical"


def _resolve_crop(db: Session, user: User, crop_id: str | None) -> Crop | None:
    if crop_id:
        return db.get(Crop, crop_id)
    planting = db.scalars(
        select(FarmerCrop)
        .where(FarmerCrop.user_id == user.id, FarmerCrop.status == "ACTIVE")
        .order_by(FarmerCrop.created_at.desc())
        .limit(1)
    ).first()
    if planting:
        return db.get(Crop, planting.crop_id)
    return db.get(Crop, "wheat") or db.scalars(select(Crop).limit(1)).first()


def _health_snapshot(db: Session, user: User, crop: Crop):
    records = list(
        db.scalars(
            select(HealthRecord)
            .where(HealthRecord.user_id == user.id, HealthRecord.crop_id == crop.id)
            .order_by(HealthRecord.created_at.desc())
            .limit(12)
        )
    )
    latest = records[0] if records else None
    score = _SEVERITY_SCORE.get(latest.severity, 85) if latest else 96
    history = [
        HealthScorePoint(
            date=r.created_at.date() if r.created_at else date.today(),
            score=_SEVERITY_SCORE.get(r.severity, 85),
            name=r.name,
            severity=r.severity,
        )
        for r in reversed(records)
    ]
    latest_out = (
        HealthRecordOut(
            id=latest.id,
            crop_id=latest.crop_id,
            crop_name=crop.name,
            record_type=latest.record_type,
            name=latest.name,
            severity=latest.severity,
            image_url=latest.image_url,
            notes=latest.notes,
            created_at=latest.created_at,
        )
        if latest
        else None
    )
    return score, history, latest_out


async def build_dashboard(db: Session, user: User, crop_id: str | None = None) -> DashboardSummary:
    crop = _resolve_crop(db, user, crop_id)
    if crop is None:
        raise LookupError("No crops available")

    warnings: list[str] = []

    # Local, always-available sources (database).
    health_score, health_history, latest_record = _health_snapshot(db, user, crop)

    latest_price = get_current_price(db, crop.id, DEFAULT_MARKET_ID)
    market_price = latest_price.modal_price if latest_price else 0.0
    market_trend = None
    if latest_price:
        history = get_history(db, crop.id, DEFAULT_MARKET_ID, days=30)
        trends = compute_trends(history)
        change = round(market_price - history[0].modal_price, 1) if history else 0.0
        change_pct = trends["trend30d"]
        market_trend = MarketTrend(
            crop_id=crop.id,
            crop_name=crop.name,
            market_id=DEFAULT_MARKET_ID,
            market_name="Azadpur Mandi" if DEFAULT_MARKET_ID == "delhi-azadpur" else DEFAULT_MARKET_ID,
            days=len(history),
            current_price=round(market_price, 1),
            start_price=round(history[0].modal_price, 1) if history else round(market_price, 1),
            change=change,
            change_pct=change_pct,
            direction=trend_direction(change_pct).replace("UPWARD", "UP").replace("DOWNWARD", "DOWN"),
            trend7d=trends["trend7d"],
            trend14d=trends["trend14d"],
            trend30d=trends["trend30d"],
            history=[],
        )

    last_recommendation = db.scalars(
        select(SellHoldRecommendation)
        .where(
            SellHoldRecommendation.user_id == user.id,
            SellHoldRecommendation.crop_id == crop.id,
        )
        .order_by(SellHoldRecommendation.created_at.desc())
        .limit(1)
    ).first()

    unread_notifications = db.scalar(
        select(func.count())
        .select_from(Notification)
        .where(Notification.user_id == user.id, Notification.is_read.is_(False))
    ) or 0

    # Non-critical external source: weather. Runs concurrently with nothing
    # else pending; failure degrades to a warning rather than an error.
    weather = None
    weather_source = None
    try:
        weather_response = await get_weather()
        weather = weather_response.today
        weather_source = weather_response.source
        if weather_response.source == "weather-local":
            warnings.append("Weather service unavailable — showing local seasonal estimate.")
    except ExternalServiceError:
        warnings.append("Weather service unavailable")

    from app.schemas.crop import CropOut

    return DashboardSummary(
        crop=CropOut.model_validate(crop),
        season=crop.season,
        health_score=health_score,
        health_score_label=_score_label(health_score),
        latest_record=latest_record,
        market_id=DEFAULT_MARKET_ID,
        market_name="Azadpur Mandi" if DEFAULT_MARKET_ID == "delhi-azadpur" else DEFAULT_MARKET_ID,
        market_price=round(market_price, 1),
        market_trend=market_trend,
        recommendation=last_recommendation.recommendation if last_recommendation else None,
        recommendation_risk=last_recommendation.risk if last_recommendation else None,
        expected_additional_return=(
            last_recommendation.expected_additional_return if last_recommendation else None
        ),
        health_history=health_history,
        weather=weather,
        weather_source=weather_source,
        unread_notifications=unread_notifications,
        warnings=warnings,
    )
