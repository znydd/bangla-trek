import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


# ── Request schemas ──


class ChatSendRequest(BaseModel):
    """Send a message to the AI chatbot to refine an itinerary."""

    itinerary_id: uuid.UUID
    message: str = Field(..., min_length=1, max_length=2000)


class SeasonalIntelRequest(BaseModel):
    """Request seasonal intelligence for a destination."""

    destination: str = Field(..., min_length=1, max_length=255)
    travel_month: Optional[int] = Field(None, ge=1, le=12)


# ── Response schemas ──


class ChatMessageRead(BaseModel):
    id: uuid.UUID
    itinerary_id: uuid.UUID
    role: str
    content: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UpdatedActivity(BaseModel):
    """An activity returned by the AI when it modifies the itinerary."""

    day_number: int
    start_time: str
    end_time: str
    title: str
    description: str
    estimated_cost: float
    location: str
    category: str
    community_entry_id: Optional[str] = None


class ChatResponse(BaseModel):
    """Response from the AI chatbot."""

    reply: str
    updated_activities: Optional[List[UpdatedActivity]] = None
    message: ChatMessageRead


class SeasonalWarning(BaseModel):
    """A seasonal warning or recommendation."""

    severity: str  # "info" | "warning" | "danger"
    title: str
    description: str
    recommended_months: Optional[List[str]] = None


class SeasonalIntelResponse(BaseModel):
    """Seasonal intelligence for a destination."""

    destination: str
    warnings: List[SeasonalWarning] = []
    best_months: List[str] = []
    current_season_summary: str = ""
