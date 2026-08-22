"""Treatment information endpoints (educational guidance — no ML, no dosages).

- GET /treatments                        all treatments
- GET /treatments/{treatment_id}         treatment detail

Treatments scoped to a disease/pest live in their own routers:
- GET /diseases/{disease_id}/treatments
- GET /pests/{pest_id}/treatments
"""

from fastapi import APIRouter, HTTPException, status

from app.schemas.treatment import TreatmentOut
from app.services.knowledge import get_treatment, list_treatments

router = APIRouter(prefix="/treatments", tags=["treatments"])


def _treatment_out(entry: dict) -> TreatmentOut:
    return TreatmentOut.model_validate(entry)


@router.get("", response_model=list[TreatmentOut])
def list_all():
    return [_treatment_out(t) for t in list_treatments()]


@router.get("/{treatment_id}", response_model=TreatmentOut)
def treatment_detail(treatment_id: str):
    entry = get_treatment(treatment_id)
    if entry is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Treatment not found."
        )
    return _treatment_out(entry)
