"""Sell / hold decision-support schemas (transparent rule-based engine).

This is a decision-support rule, not financial advice. The engine compares
recorded market trends against storage costs using documented thresholds.
"""

from pydantic import Field

from app.schemas.common import CamelModel

DISCLAIMER = "Decision-support rule based on recorded mandi trends — not financial advice."


class SellHoldRequest(CamelModel):
    crop_id: str
    market_id: str | None = None
    quantity: float = Field(gt=0, le=100000)
    storage_days: int = Field(ge=1, le=180)
    storage_cost: float | None = Field(default=None, ge=0)  # total cost override
    risk_tolerance: str = Field(default="MEDIUM", pattern="^(LOW|MEDIUM|HIGH)$")


class SellHoldResult(CamelModel):
    recommendation: str  # SELL | HOLD
    reason: str
    current_price: float
    trend: str  # UPWARD | DOWNWARD | FLAT
    trend_change_pct: float
    projected_price: float  # trend extrapolation, clearly labelled
    storage_cost: float
    expected_additional_return: float
    risk: str  # LOW | MEDIUM | HIGH
    crop_id: str = ""
    crop_name: str = ""
    market_id: str = ""
    market_name: str = ""
    quantity: float = 0
    storage_days: int = 0
    disclaimer: str = DISCLAIMER
