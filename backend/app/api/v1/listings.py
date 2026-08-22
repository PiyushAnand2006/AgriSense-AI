"""Farmer marketplace listing endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.crop import Crop
from app.models.listing import CropListing
from app.models.user import User
from app.schemas.common import Page
from app.schemas.listing import ListingCreate, ListingOut, ListingUpdate
from app.services.notification_service import notify

router = APIRouter(prefix="/listings", tags=["listings"])


def _listing_out(db: Session, listing: CropListing) -> ListingOut:
    crop = db.get(Crop, listing.crop_id)
    return ListingOut(
        id=listing.id,
        farmer_id=listing.farmer_id,
        farmer_name=listing.farmer_name,
        crop_id=listing.crop_id,
        crop_name=crop.name if crop else listing.crop_id,
        quantity=listing.quantity,
        unit=listing.unit,
        asking_price=listing.asking_price,
        quality_grade=listing.quality_grade,
        location=listing.location,
        status=listing.status,
        created_at=listing.created_at,
    )


@router.get("", response_model=Page[ListingOut])
def list_listings(
    search: str | None = None,
    cropId: str | None = None,
    grade: str | None = None,
    status_filter: str | None = "ACTIVE",
    maxPrice: float | None = Query(default=None, gt=0),
    sort: str = "newest",
    page: int = Query(default=1, ge=1),
    pageSize: int = Query(default=12, ge=1, le=50),
    db: Session = Depends(get_db),
):
    stmt = select(CropListing)
    if status_filter:
        stmt = stmt.where(CropListing.status == status_filter.upper())
    if cropId:
        stmt = stmt.where(CropListing.crop_id == cropId)
    if grade:
        stmt = stmt.where(CropListing.quality_grade == grade.upper())
    if maxPrice is not None:
        stmt = stmt.where(CropListing.asking_price <= maxPrice)
    if search:
        needle = f"%{search.lower()}%"
        stmt = stmt.join(Crop, Crop.id == CropListing.crop_id).where(
            or_(
                func.lower(Crop.name).like(needle),
                func.lower(CropListing.location).like(needle),
                func.lower(CropListing.farmer_name).like(needle),
            )
        )

    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0

    sorters = {
        "newest": CropListing.created_at.desc(),
        "price_asc": CropListing.asking_price.asc(),
        "price_desc": CropListing.asking_price.desc(),
        "quantity_desc": CropListing.quantity.desc(),
    }
    stmt = stmt.order_by(sorters.get(sort, sorters["newest"]))
    rows = list(db.scalars(stmt.offset((page - 1) * pageSize).limit(pageSize)))

    return Page[ListingOut](
        items=[_listing_out(db, row) for row in rows],
        total=total,
        page=page,
        page_size=pageSize,
    )


@router.post("", response_model=ListingOut, status_code=status.HTTP_201_CREATED)
def create_listing(
    payload: ListingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if db.get(Crop, payload.crop_id) is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unknown crop id.")
    listing = CropListing(
        farmer_id=current_user.id,
        farmer_name=current_user.name,
        crop_id=payload.crop_id,
        quantity=payload.quantity,
        unit=payload.unit,
        asking_price=payload.asking_price,
        quality_grade=payload.quality_grade,
        location=payload.location,
    )
    db.add(listing)
    db.commit()
    db.refresh(listing)
    notify(
        db,
        current_user.id,
        type="MARKETPLACE",
        title="Listing published",
        message=f"Your {payload.quantity} {payload.unit} listing is now visible in the marketplace.",
    )
    return _listing_out(db, listing)


@router.get("/{listing_id}", response_model=ListingOut)
def get_listing(listing_id: str, db: Session = Depends(get_db)):
    listing = db.get(CropListing, listing_id)
    if listing is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found.")
    return _listing_out(db, listing)


@router.patch("/{listing_id}", response_model=ListingOut)
def update_listing(
    listing_id: str,
    payload: ListingUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    listing = db.get(CropListing, listing_id)
    if listing is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found.")
    if listing.farmer_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only edit your own listings.")
    for field, value in payload.model_dump(exclude_unset=True, by_alias=False).items():
        setattr(listing, field, value)
    db.commit()
    db.refresh(listing)
    return _listing_out(db, listing)


@router.delete("/{listing_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_listing(
    listing_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    listing = db.get(CropListing, listing_id)
    if listing is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found.")
    if listing.farmer_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only delete your own listings.")
    db.delete(listing)
    db.commit()
