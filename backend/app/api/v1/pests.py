"""Pest information endpoints (information service).

- GET /pests                       all known pests
- GET /pests/{pest_id}             pest detail
- GET /pests/{pest_id}/treatments  educational treatment guidance
- GET /crops/{crop_id}/pests       common pests for a crop (crops router)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.crop import Crop
from app.schemas.pest import PestKnowledge, PestOut
from app.schemas.treatment import TreatmentOut
from app.services.knowledge import get_pest, list_pests, pests_for_crop, treatments_for_pest

router = APIRouter(prefix="/pests", tags=["pests"])


def _pest_out(entry: dict) -> PestOut:
    return PestOut(
        id=entry["id"],
        name=entry["name"],
        crop_ids=entry["crop_ids"],
        knowledge=PestKnowledge.model_validate(entry["knowledge"]),
    )


@router.get("", response_model=list[PestOut])
def list_all(cropId: str | None = None, db: Session = Depends(get_db)):
    """All pests, optionally filtered by crop id."""
    if cropId:
        crop = db.get(Crop, cropId)
        if crop is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Crop not found.")
        return [_pest_out(e) for e in pests_for_crop(cropId)]
    return [_pest_out(e) for e in list_pests()]


@router.get("/{pest_id}", response_model=PestOut)
def pest_detail(pest_id: str):
    entry = get_pest(pest_id)
    if entry is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Pest not found."
        )
    return _pest_out(entry)


@router.get("/{pest_id}/treatments", response_model=list[TreatmentOut])
def pest_treatments(pest_id: str):
    treatments = treatments_for_pest(pest_id)
    if not treatments:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Pest not found."
        )
    return [TreatmentOut.model_validate(t) for t in treatments]
