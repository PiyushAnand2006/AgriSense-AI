"""Fertilizer information + guidance schemas (rule-based, no ML)."""

from pydantic import Field

from app.schemas.common import CamelModel

SOURCE_NOTE = "Educational information — not verified agricultural guidance. Base final doses on a soil test."


class FertilizerInfoOut(CamelModel):
    """A fertilizer category entry in the crop guidance catalog."""

    id: str  # slug e.g. "npk-basal"
    name: str
    category: str  # BALANCED | NITROGEN | PHOSPHORUS_POTASSIUM | POTASSIUM | MICRONUTRIENT | NONE
    growth_stages: list[str] = []  # stages where this category is relevant
    guidance: str
    source_note: str = SOURCE_NOTE


class FertilizerGuidanceRequest(CamelModel):
    crop_id: str
    growth_stage: str = Field(pattern="^(SOWING|VEGETATIVE|FLOWERING|GRAIN_FILLING|FRUITING|HARVEST_READY)$")
    soil_condition: str = Field(pattern="^(LOAMY|SANDY|CLAY|SALINE|BLACK)$")
    npk: str | None = None  # optional free-form soil note e.g. "low nitrogen"


class FertilizerGuidanceResult(CamelModel):
    crop: str
    growth_stage: str
    soil_condition: str
    recommended_category: str
    recommended_fertilizer_id: str
    application_timing: str
    soil_note: str = ""
    guidance: str
    source_note: str = SOURCE_NOTE
