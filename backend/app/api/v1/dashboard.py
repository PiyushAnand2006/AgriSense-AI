"""Dashboard aggregation endpoints.

- GET /dashboard        aggregated crop + market + weather + notifications
- GET /dashboard/summary  alias kept for compatibility

One request powers the whole dashboard page. Non-critical source failures
are reported in ``warnings`` instead of failing the response.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.dashboard import DashboardSummary
from app.services.dashboard_service import build_dashboard

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


async def _summary(db: Session, user: User, cropId: str | None) -> DashboardSummary:
    try:
        return await build_dashboard(db, user, cropId)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc


@router.get("", response_model=DashboardSummary)
async def dashboard(
    cropId: str | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return await _summary(db, current_user, cropId)


@router.get("/summary", response_model=DashboardSummary)
async def dashboard_summary(
    cropId: str | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return await _summary(db, current_user, cropId)
