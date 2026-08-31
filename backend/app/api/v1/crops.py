"""Crop catalog + farmer crop (planting) endpoints.

- GET    /crops                     catalog (filter by season/search)
- GET    /crops/mine                the authenticated farmer's plantings
- GET    /crops/{crop_id}           catalog detail (slug ids like "wheat")
- POST   /crops                     add a planting for the farmer
- PATCH  /crops/{id}                update one of the farmer's plantings (uuid)
- DELETE /crops/{id}                remove one of the farmer's plantings (uuid)
- GET    /crops/{crop_id}/diseases  common diseases for the crop
- GET    /crops/{crop_id}/pests     common pests for the crop
- GET    /crops/{crop_id}/treatments  educational treatment guidance
- GET    /crops/{crop_id}/fertilizers fertilizer catalog for the crop
- POST   /crops/{crop_id}/records   log a farmer-observed disease/pest record
- GET    /crops/{crop_id}/records   list the farmer's records for the crop
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.analysis import HealthRecord
from app.models.crop import Crop, FarmerCrop
from app.models.user import User
from app.schemas.crop import CropOut, FarmerCropCreate, FarmerCropOut, FarmerCropUpdate
from app.schemas.disease import DiseaseKnowledge, DiseaseOut
from app.schemas.fertilizer import FertilizerInfoOut
from app.schemas.health_record import HealthRecordCreate, HealthRecordOut
from app.schemas.pest import PestKnowledge, PestOut
from app.schemas.treatment import TreatmentOut
from app.services.knowledge import (
    diseases_for_crop,
    fertilizers_for_crop,
    pests_for_crop,
    treatments_for_crop,
)
from app.services.notification_service import notify

router = APIRouter(prefix="/crops", tags=["crops"])


def _farmer_crop_out(db: Session, planting: FarmerCrop) -> FarmerCropOut:
    crop = db.get(Crop, planting.crop_id)
    return FarmerCropOut(
        id=planting.id,
        crop_id=planting.crop_id,
        crop=CropOut.model_validate(crop) if crop else None,
        season=planting.season,
        planting_date=planting.planting_date,
        expected_harvest_date=planting.expected_harvest_date,
        farm_size=planting.farm_size,
        location=planting.location,
        status=planting.status,
        created_at=planting.created_at,
    )


def _get_planting(db: Session, user: User, planting_id: str) -> FarmerCrop:
    planting = db.get(FarmerCrop, planting_id)
    if planting is None or planting.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Crop planting not found.")
    return planting


def _get_catalog_crop(db: Session, crop_id: str) -> Crop:
    crop = db.get(Crop, crop_id)
    if crop is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Crop not found.")
    return crop


# --- Catalog + plantings ------------------------------------------------------


@router.get("", response_model=list[CropOut])
def list_catalog(season: str | None = None, search: str | None = None, db: Session = Depends(get_db)):
    stmt = select(Crop).order_by(Crop.season, Crop.name)
    if season:
        stmt = stmt.where(Crop.season == season.upper())
    crops = list(db.scalars(stmt))
    if search:
        needle = search.lower()
        crops = [c for c in crops if needle in c.name.lower() or needle in c.id.lower()]
    return [CropOut.model_validate(c) for c in crops]


@router.get("/mine", response_model=list[FarmerCropOut])
def my_crops(
    status_filter: str | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    stmt = (
        select(FarmerCrop)
        .where(FarmerCrop.user_id == current_user.id)
        .order_by(FarmerCrop.created_at.desc())
    )
    if status_filter:
        stmt = stmt.where(FarmerCrop.status == status_filter.upper())
    return [_farmer_crop_out(db, p) for p in db.scalars(stmt)]


@router.get("/{crop_id}", response_model=CropOut)
def catalog_detail(crop_id: str, db: Session = Depends(get_db)):
    return CropOut.model_validate(_get_catalog_crop(db, crop_id))


@router.post("", response_model=FarmerCropOut, status_code=status.HTTP_201_CREATED)
def create_planting(
    payload: FarmerCropCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    crop = db.get(Crop, payload.crop_id)
    if crop is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unknown crop id.")
    planting = FarmerCrop(
        user_id=current_user.id,
        crop_id=crop.id,
        season=crop.season,
        planting_date=payload.planting_date,
        expected_harvest_date=payload.expected_harvest_date,
        farm_size=payload.farm_size,
        location=payload.location,
    )
    db.add(planting)
    db.commit()
    db.refresh(planting)
    return _farmer_crop_out(db, planting)


@router.patch("/{planting_id}", response_model=FarmerCropOut)
def update_planting(
    planting_id: str,
    payload: FarmerCropUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    planting = _get_planting(db, current_user, planting_id)
    data = payload.model_dump(exclude_unset=True, by_alias=False)
    for field, value in data.items():
        setattr(planting, field, value)
    db.commit()
    db.refresh(planting)
    return _farmer_crop_out(db, planting)


@router.delete("/{planting_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_planting(
    planting_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    planting = _get_planting(db, current_user, planting_id)
    db.delete(planting)
    db.commit()


# --- Crop-scoped information sub-resources --------------------------------------


@router.get("/{crop_id}/diseases", response_model=list[DiseaseOut])
def crop_diseases(crop_id: str, db: Session = Depends(get_db)):
    crop = _get_catalog_crop(db, crop_id)
    return [
        DiseaseOut(
            id=e["id"], name=e["name"], crop_ids=e["crop_ids"],
            knowledge=DiseaseKnowledge.model_validate(e["knowledge"]),
        )
        for e in diseases_for_crop(crop.id)
    ]


@router.get("/{crop_id}/pests", response_model=list[PestOut])
def crop_pests(crop_id: str, db: Session = Depends(get_db)):
    crop = _get_catalog_crop(db, crop_id)
    return [
        PestOut(
            id=e["id"], name=e["name"], crop_ids=e["crop_ids"],
            knowledge=PestKnowledge.model_validate(e["knowledge"]),
        )
        for e in pests_for_crop(crop.id)
    ]


@router.get("/{crop_id}/treatments", response_model=list[TreatmentOut])
def crop_treatments(crop_id: str, db: Session = Depends(get_db)):
    crop = _get_catalog_crop(db, crop_id)
    return [TreatmentOut.model_validate(t) for t in treatments_for_crop(crop.id)]


@router.get("/{crop_id}/fertilizers", response_model=list[FertilizerInfoOut])
def crop_fertilizers(crop_id: str, db: Session = Depends(get_db)):
    crop = _get_catalog_crop(db, crop_id)
    return [FertilizerInfoOut.model_validate(f) for f in fertilizers_for_crop(crop.id)]


# --- Farmer-logged health records -------------------------------------------------


def _record_out(record: HealthRecord, crop_name: str) -> HealthRecordOut:
    return HealthRecordOut(
        id=record.id,
        crop_id=record.crop_id,
        crop_name=crop_name,
        record_type=record.record_type,
        name=record.name,
        severity=record.severity,
        image_url=record.image_url,
        notes=record.notes,
        created_at=record.created_at,
    )


@router.get("/{crop_id}/records", response_model=list[HealthRecordOut])
def list_records(
    crop_id: str,
    recordType: str | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    crop = _get_catalog_crop(db, crop_id)
    stmt = (
        select(HealthRecord)
        .where(HealthRecord.user_id == current_user.id, HealthRecord.crop_id == crop.id)
        .order_by(HealthRecord.created_at.desc())
        .limit(50)
    )
    if recordType:
        stmt = stmt.where(HealthRecord.record_type == recordType.upper())
    return [_record_out(r, crop.name) for r in db.scalars(stmt)]


@router.post("/{crop_id}/records", response_model=HealthRecordOut, status_code=status.HTTP_201_CREATED)
def create_record(
    crop_id: str,
    payload: HealthRecordCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    crop = _get_catalog_crop(db, crop_id)
    record = HealthRecord(
        user_id=current_user.id,
        crop_id=crop.id,
        record_type=payload.record_type.upper(),
        name=payload.name.strip(),
        severity=payload.severity.upper(),
        image_url=payload.image_url,
        notes=payload.notes,
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    notify(
        db,
        current_user.id,
        type="ANALYSIS",
        title="Health record logged",
        message=f"{crop.name}: {payload.record_type.lower()} observation '{payload.name}' "
                f"recorded ({payload.severity.lower()} severity).",
    )
    return _record_out(record, crop.name)


@router.delete("/{crop_id}/records/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_record(
    crop_id: str,
    record_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    crop = _get_catalog_crop(db, crop_id)
    record = db.scalar(
        select(HealthRecord).where(
            HealthRecord.id == record_id,
            HealthRecord.user_id == current_user.id,
            HealthRecord.crop_id == crop.id,
        )
    )
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Health record not found.")
    db.delete(record)
    db.commit()
    return None
