import uuid
from pydantic import BaseModel, Field

class NomadMetricSubmit(BaseModel):
    entry_id: uuid.UUID
    carrier: str = Field(..., pattern="^(GP|Robi|Banglalink|Teletalk)$")
    signal_strength: str = Field(..., pattern="^(No Signal|2G|3G|4G|5G)$")
    safety_rating: int = Field(..., ge=1, le=5)
    bkash_available: bool

class CarrierSignal(BaseModel):
    carrier: str
    signal: str
    votes: int

class NomadMetricSummary(BaseModel):
    entry_id: uuid.UUID
    avg_safety_rating: float | None
    bkash_available_pct: int
    signal_by_carrier: list[CarrierSignal]
    has_submitted: bool = False