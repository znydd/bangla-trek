import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


# ── Facility schemas ──


class EmergencyFacilityRead(BaseModel):
    id: uuid.UUID
    name: str
    facility_type: str
    address: str
    district: str
    latitude: float
    longitude: float
    phone_number: Optional[str] = None
    notes: Optional[str] = None
    distance_km: Optional[float] = None  # computed from user location

    model_config = ConfigDict(from_attributes=True)


class EmergencyFacilityListResponse(BaseModel):
    items: List[EmergencyFacilityRead]
    total: int


# ── Phrase schemas ──


class EmergencyPhraseRead(BaseModel):
    id: str
    english: str
    bengali: str
    romanized: str


class EmergencyPhraseCategoryRead(BaseModel):
    category: str
    phrases: List[EmergencyPhraseRead]


# ── Translation schemas ──


class TranslateRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=1000)
    dialect: Optional[str] = Field(
        None,
        description="Target dialect: sylheti, chittagonian, barisali, rangpuri, or standard (default)",
    )


class TranslateResponse(BaseModel):
    original_text: str
    bengali: str
    romanized: str
    dialect: str
    dialect_text: Optional[str] = None
    dialect_romanized: Optional[str] = None
