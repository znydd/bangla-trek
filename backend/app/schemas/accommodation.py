import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


# ── Response schemas ──


class AccommodationPhotoRead(BaseModel):
    id: uuid.UUID
    url: str
    public_id: str
    caption: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class AccommodationRead(BaseModel):
    """Single accommodation (community entry of type hotel/guesthouse/homestay)."""

    id: uuid.UUID
    user_id: uuid.UUID
    category: str  # hotel, guesthouse, homestay
    name: str
    location: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    price_range: str
    amenities: List[str] = []
    travel_tips: Optional[str] = None
    tags: List[str] = []
    created_at: datetime
    updated_at: datetime

    photos: List[AccommodationPhotoRead] = []

    # Populated by service layer
    author_name: str
    author_picture_url: Optional[str] = None
    distance_km: Optional[float] = None  # distance from reference point

    model_config = ConfigDict(from_attributes=True)


class AccommodationListResponse(BaseModel):
    items: List[AccommodationRead]
    total: int
    page: int
    per_page: int
    total_pages: int


# ── AI recommendation schemas ──


class AIAccommodationRecommendation(BaseModel):
    """A single AI-generated accommodation recommendation."""

    accommodation_id: str
    name: str
    category: str
    price_range: str
    location: str
    reasoning: str  # LLM-generated explanation
    estimated_cost_per_night: float
    travel_convenience_score: int = Field(
        ..., ge=1, le=10, description="1-10 score for travel convenience"
    )
    cost_benefit_summary: str


class AIRecommendationsResponse(BaseModel):
    """Response containing AI-generated accommodation recommendations."""

    recommendations: List[AIAccommodationRecommendation]
    summary: str  # Overall LLM summary/reasoning
    itinerary_id: uuid.UUID
