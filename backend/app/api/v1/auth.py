"""Authentication endpoints."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.deps import get_current_user
from app.core.security import create_access_token, hash_password, verify_password
from app.db.session import get_db
from app.models.user import FarmerProfile, User
from app.schemas.auth import (
    AuthResponse,
    FarmerProfileOut,
    LoginRequest,
    ProfileUpdateRequest,
    RegisterRequest,
    UserOut,
)
from app.services.notification_service import notify

router = APIRouter(prefix="/auth", tags=["auth"])


def _user_out(db: Session, user: User) -> UserOut:
    profile = db.scalar(select(FarmerProfile).where(FarmerProfile.user_id == user.id))
    return UserOut(
        id=user.id,
        name=user.name,
        email=user.email,
        created_at=user.created_at,
        profile=FarmerProfileOut.model_validate(profile) if profile else None,
    )


def _auth_response(db: Session, user: User) -> AuthResponse:
    settings = get_settings()
    token = create_access_token(user.id)
    return AuthResponse(
        token=token,
        token_type="bearer",
        expires_in_days=settings.access_token_expire_days,
        user=_user_out(db, user),
    )


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.scalar(select(User).where(User.email == payload.email.lower()))
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="An account with this email already exists.")
    user = User(
        email=payload.email.lower(),
        name=payload.name.strip(),
        hashed_password=hash_password(payload.password),
        profile=FarmerProfile(
            village=payload.village,
            district=payload.district,
            state=payload.state,
        ),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    notify(
        db,
        user.id,
        type="SYSTEM",
        title="Welcome to AgriSense AI",
        message="Start by selecting your season and crop, then explore health analysis and market intelligence.",
    )
    return _auth_response(db, user)


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == payload.email.lower()))
    if user is None or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password.")
    return _auth_response(db, user)


@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)):
    # Tokens are stateless JWTs; the client discards the token on logout.
    return {"success": True, "message": "Logged out."}


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return _user_out(db, current_user)


@router.patch("/me", response_model=UserOut)
def update_me(
    payload: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = db.scalar(select(FarmerProfile).where(FarmerProfile.user_id == current_user.id))
    if profile is None:
        profile = FarmerProfile(user_id=current_user.id)
        db.add(profile)

    data = payload.model_dump(exclude_unset=True, by_alias=False)
    if "name" in data and data["name"]:
        current_user.name = data.pop("name")
    if "farm_size_acres" in data:
        profile.farm_size_acres = data.pop("farm_size_acres")
    for field, value in data.items():
        if value is not None:
            setattr(profile, field, value)

    db.commit()
    db.refresh(current_user)
    return _user_out(db, current_user)
