import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class BuddyMatchSuggestion(BaseModel):
    """A suggested buddy match with overlap details."""

    matched_user_id: uuid.UUID
    matched_user_name: str
    matched_user_picture_url: Optional[str] = None

    # Match details
    match_score: float = Field(..., ge=0.0, le=1.0)
    common_interests: List[str] = []
    common_destinations: List[str] = []

    # Source of match
    match_source: str = Field(
        ..., description="Source of match: itinerary, group_trip, or location"
    )

    model_config = ConfigDict(from_attributes=True)


class BuddyMatchRead(BaseModel):
    """Full buddy match record."""

    id: uuid.UUID
    user_id: uuid.UUID
    matched_user_id: uuid.UUID

    # Matched user info
    matched_user_name: str
    matched_user_picture_url: Optional[str] = None

    # Match details
    match_score: float
    common_interests: List[str] = []
    common_destinations: List[str] = []
    status: str  # suggested | pending | accepted | rejected | blocked

    # Timestamps
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BuddyMatchAction(BaseModel):
    """Action to take on a buddy match."""

    action: str = Field(
        ..., pattern="^(accept|reject|block)$"
    )  # accept | reject | block


class BuddyMatchList(BaseModel):
    """List of buddy matches with pagination."""

    items: List[BuddyMatchRead]
    total: int
    page: int
    per_page: int
    total_pages: int


class BuddyDiscoveryFilters(BaseModel):
    """Filters for discovering potential buddies."""

    destination: Optional[str] = None
    interest: Optional[str] = None
    min_match_score: float = Field(0.1, ge=0.0, le=1.0)
    limit: int = Field(20, ge=1, le=100)
