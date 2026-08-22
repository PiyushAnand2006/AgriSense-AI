"""Season schemas (database-driven, never hard-coded in the frontend)."""

from app.schemas.common import CamelModel
from app.schemas.crop import CropOut


class SeasonOut(CamelModel):
    id: str  # slug e.g. "rabi"
    name: str  # "Rabi"
    label: str  # short description, e.g. "Winter (Oct-Mar)"


class SeasonCropsOut(CamelModel):
    season: SeasonOut
    crops: list[CropOut]
