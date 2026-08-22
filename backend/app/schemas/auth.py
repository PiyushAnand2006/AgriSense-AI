"""Auth / user schemas."""

from datetime import datetime

from pydantic import EmailStr, Field

from app.schemas.common import CamelModel


class RegisterRequest(CamelModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    village: str | None = None
    district: str | None = None
    state: str | None = None


class LoginRequest(CamelModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class FarmerProfileOut(CamelModel):
    village: str | None = None
    district: str | None = None
    state: str | None = None
    phone: str | None = None
    language: str = "en"
    farm_size_acres: float | None = None


class UserOut(CamelModel):
    id: str
    name: str
    email: EmailStr
    created_at: datetime | None = None
    profile: FarmerProfileOut | None = None


class ProfileUpdateRequest(CamelModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    village: str | None = None
    district: str | None = None
    state: str | None = None
    phone: str | None = None
    language: str | None = None
    farm_size_acres: float | None = Field(default=None, ge=0)


class AuthResponse(CamelModel):
    token: str
    token_type: str = "bearer"
    expires_in_days: int
    user: UserOut
