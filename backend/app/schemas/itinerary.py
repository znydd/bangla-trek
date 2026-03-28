import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


# ── Request schemas ──


class ItineraryGenerateRequest(BaseModel):
    destination: str = Field(..., min_length=1, max_length=255)
    duration_days: int = Field(..., ge=1, le=14)
    budget: float = Field(..., gt=0)
    travel_style: str = Field(..., pattern="^(budget|comfort|luxury)$")
    interests: List[str] = Field(default=[])
    group_type: str = Field(..., pattern="^(solo|couple|family|friends)$")


# ── Response schemas ──


class ActivityRead(BaseModel):
    id: uuid.UUID
    day_number: int
    start_time: str
    end_time: str
    title: str
    description: str
    estimated_cost: float
    location: str
    category: str
    community_entry_id: Optional[uuid.UUID] = None

    model_config = ConfigDict(from_attributes=True)


class ItineraryRead(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    destination: str
    duration_days: int
    budget: float
    travel_style: str
    interests: List[str]
    group_type: str
    created_at: datetime
    updated_at: datetime
    activities: List[ActivityRead] = []

    model_config = ConfigDict(from_attributes=True)


class ItineraryListItem(BaseModel):
    id: uuid.UUID
    destination: str
    duration_days: int
    budget: float
    travel_style: str
    group_type: str
    created_at: datetime
    activity_count: int = 0

    model_config = ConfigDict(from_attributes=True)
