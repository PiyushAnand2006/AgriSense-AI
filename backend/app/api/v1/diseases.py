"""Disease information endpoints (information service — no ML).

- GET /diseases                       all known diseases
- GET /diseases/{disease_id}          disease detail (symptoms, management, prevention)
- GET /diseases/{disease_id}/treatments  educational treatment guidance
- GET /crops/{crop_id}/diseases       common diseases for a crop (crops router)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.crop import Crop
from app.schemas.disease import DiseaseKnowledge, DiseaseOut
from app.schemas.treatment import TreatmentOut
from app.services.knowledge import diseases_for_crop, get_disease, list_diseases, treatments_for_disease

router = APIRouter(prefix="/diseases", tags=["diseases"])


def _disease_out(entry: dict) -> DiseaseOut:
    return DiseaseOut(
        id=entry["id"],
        name=entry["name"],
        crop_ids=entry["crop_ids"],
        knowledge=DiseaseKnowledge.model_validate(entry["knowledge"]),
    )


@router.get("", response_model=list[DiseaseOut])
def list_all(cropId: str | None = None, db: Session = Depends(get_db)):
    """All diseases, optionally filtered by crop id."""
    if cropId:
        crop = db.get(Crop, cropId)
        if crop is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Crop not found.")
        return [_disease_out(e) for e in diseases_for_crop(cropId)]
    return [_disease_out(e) for e in list_diseases()]


@router.get("/{disease_id}", response_model=DiseaseOut)
def disease_detail(disease_id: str):
    entry = get_disease(disease_id)
    if entry is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Disease not found."
        )
    return _disease_out(entry)


@router.get("/{disease_id}/treatments", response_model=list[TreatmentOut])
def disease_treatments(disease_id: str):
    treatments = treatments_for_disease(disease_id)
    if not treatments:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Disease not found."
        )
    return [TreatmentOut.model_validate(t) for t in treatments]
