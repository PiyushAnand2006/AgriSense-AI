"""Sell / Hold decision-support endpoints (rule-based engine)."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.recommendation import SellHoldRequest, SellHoldResult
from app.services.recommendation_service import compute_sell_hold, recommendation_history

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.post("/sell-hold", response_model=SellHoldResult)
def sell_hold(
    payload: SellHoldRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return compute_sell_hold(db, current_user, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/history", response_model=list[SellHoldResult])
def history(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return recommendation_history(db, current_user, limit)
