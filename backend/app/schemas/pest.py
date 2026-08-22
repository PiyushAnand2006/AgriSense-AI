"""Pest information schemas (API-based, no ML)."""

from app.schemas.common import CamelModel

SOURCE_NOTE = "Educational information — not verified agricultural guidance. Consult local agricultural officers."


class PestKnowledge(CamelModel):
    symptoms: list[str] = []
    recommended_action: str = ""
    treatment: str = ""
    organic_alternatives: str = ""
    prevention: list[str] = []
    source_note: str = SOURCE_NOTE


class PestOut(CamelModel):
    id: str  # slug e.g. "aphid"
    name: str
    crop_ids: list[str] = []  # crops commonly affected
    knowledge: PestKnowledge
