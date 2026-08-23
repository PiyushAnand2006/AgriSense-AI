"""Disease information schemas."""

from app.schemas.common import CamelModel

SOURCE_NOTE = "Educational information — not verified agricultural guidance. Consult local agricultural officers."


class DiseaseKnowledge(CamelModel):
    """Educational knowledge attached to a disease. Demo-grade content."""

    symptoms: list[str] = []
    recommended_action: str = ""
    treatment: str = ""
    organic_alternatives: str = ""
    prevention: list[str] = []
    source_note: str = SOURCE_NOTE


class DiseaseOut(CamelModel):
    """A disease catalog entry served by the information service."""

    id: str  # slug e.g. "leaf-rust"
    name: str
    crop_ids: list[str] = []  # crops commonly affected
    knowledge: DiseaseKnowledge
