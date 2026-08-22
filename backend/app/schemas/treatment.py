"""Treatment information schemas.

Treatments are educational guidance entries linked to diseases/pests. No
chemical dosages are provided — content is generically worded and clearly
labelled until a verified agricultural source is integrated.
"""

from app.schemas.common import CamelModel

SOURCE_NOTE = "Educational information — not verified agricultural guidance. Consult local agricultural officers."


class TreatmentOut(CamelModel):
    id: str  # slug e.g. "leaf-rust-treatment"
    target_type: str  # DISEASE | PEST
    target_name: str  # e.g. "Leaf Rust"
    recommended_action: str
    chemical_guidance: str  # generic, no dosages
    organic_alternatives: str
    prevention: list[str] = []
    source_note: str = SOURCE_NOTE
