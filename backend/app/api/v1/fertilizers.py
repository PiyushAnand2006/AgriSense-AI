"""Fertilizer information + guidance endpoints (rule-based, no ML).

- GET  /fertilizers                 fertilizer category catalog
- GET  /fertilizers/{id}            catalog detail
- GET  /crops/{crop_id}/fertilizers crop-scoped catalog (crops router)
- POST /fertilizer-guidance         validated rule-based guidance
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.crop import Crop
from app.models.user import User
from app.schemas.fertilizer import (
    FertilizerGuidanceRequest,
    FertilizerGuidanceResult,
    FertilizerInfoOut,
)
from app.services.knowledge import get_fertilizer, get_fertilizer_guidance, list_fertilizers

router = APIRouter(prefix="/fertilizers", tags=["fertilizers"])

guidance_router = APIRouter(prefix="/fertilizer-guidance", tags=["fertilizers"])


def _info_out(entry: dict) -> FertilizerInfoOut:
    return FertilizerInfoOut.model_validate(entry)


@router.get("", response_model=list[FertilizerInfoOut])
def list_catalog():
    return [_info_out(f) for f in list_fertilizers()]


@router.get("/{fertilizer_id}", response_model=FertilizerInfoOut)
def fertilizer_detail(fertilizer_id: str):
    entry = get_fertilizer(fertilizer_id)
    if entry is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Fertilizer not found."
        )
    return _info_out(entry)


@guidance_router.post("", response_model=FertilizerGuidanceResult)
def fertilizer_guidance(
    payload: FertilizerGuidanceRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    crop = db.get(Crop, payload.crop_id)
    if crop is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unknown crop id.")

    guidance = get_fertilizer_guidance(
        crop.name, payload.growth_stage.upper(), payload.soil_condition.upper(), payload.npk
    )
    return FertilizerGuidanceResult(
        crop=crop.name,
        growth_stage=payload.growth_stage.upper(),
        soil_condition=payload.soil_condition.upper(),
        recommended_category=guidance["recommended_category"],
        recommended_fertilizer_id=guidance["recommended_fertilizer_id"],
        application_timing=guidance["application_timing"],
        soil_note=guidance["soil_note"],
        guidance=guidance["guidance"],
    )
