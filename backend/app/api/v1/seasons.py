"""Season endpoints — database-driven, never hard-coded in the frontend.

- GET /seasons               list seasons
- GET /seasons/{season}      season detail
- GET /seasons/{season}/crops  crops for a season
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.crop import Crop
from app.schemas.crop import CropOut
from app.schemas.seasons import SeasonCropsOut, SeasonOut
from app.services.knowledge import SEASONS

router = APIRouter(prefix="/seasons", tags=["seasons"])


def _season_out(season_id: str) -> SeasonOut:
    meta = SEASONS.get(season_id)
    if meta is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Unknown season '{season_id}'. Available: {', '.join(SEASONS)}",
        )
    return SeasonOut(id=season_id, name=meta["name"], label=meta["label"])


@router.get("", response_model=list[SeasonOut])
def list_seasons(db: Session = Depends(get_db)):
    """Seasons that actually have crops registered in the catalog."""
    present = {c.season.lower() for c in db.scalars(select(Crop))}
    return [_season_out(sid) for sid in SEASONS if sid in present]


@router.get("/{season_id}", response_model=SeasonOut)
def season_detail(season_id: str, db: Session = Depends(get_db)):
    return _season_out(season_id.lower())


@router.get("/{season_id}/crops", response_model=SeasonCropsOut)
def season_crops(season_id: str, db: Session = Depends(get_db)):
    season = _season_out(season_id.lower())
    crops = list(
        db.scalars(
            select(Crop).where(Crop.season == season_id.upper()).order_by(Crop.name)
        )
    )
    return SeasonCropsOut(season=season, crops=[CropOut.model_validate(c) for c in crops])
