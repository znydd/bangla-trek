import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict


# ── Activity Schemas ──


class GroupActivityRead(BaseModel):
    id: uuid.UUID
    trip_id: uuid.UUID
    user_id: uuid.UUID
    activity_type: str
    description: str
    metadata_json: Optional[Dict[str, Any]] = None
    created_at: datetime
    
    # Joined info
    user_name: Optional[str] = None
    user_picture_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# ── Poll Schemas ──


class PollOptionCreate(BaseModel):
    text: str
    image_url: Optional[str] = None
    itinerary_activity_id: Optional[uuid.UUID] = None


class PollCreate(BaseModel):
    title: str
    description: Optional[str] = None
    options: List[PollOptionCreate]


class PollOptionRead(BaseModel):
    id: uuid.UUID
    poll_id: uuid.UUID
    text: str
    image_url: Optional[str] = None
    itinerary_activity_id: Optional[uuid.UUID] = None
    vote_count: int = 0
    is_voted_by_me: bool = False

    model_config = ConfigDict(from_attributes=True)


class PollRead(BaseModel):
    id: uuid.UUID
    trip_id: uuid.UUID
    creator_id: uuid.UUID
    title: str
    description: Optional[str] = None
    is_active: bool
    created_at: datetime
    creator_name: Optional[str] = None
    
    options: List[PollOptionRead] = []
    total_votes: int = 0
    my_vote_option_id: Optional[uuid.UUID] = None

    model_config = ConfigDict(from_attributes=True)


# ── Collaboration Request Schemas ──


class ItineraryLinkRequest(BaseModel):
    itinerary_id: uuid.UUID
