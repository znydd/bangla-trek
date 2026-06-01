import uuid
from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, model_validator


class GroupTripCreate(BaseModel):
    title: str
    destination: str
    description: Optional[str] = None
    start_date: date
    end_date: date
    visibility: str = "private"  # public | private

    @model_validator(mode="after")
    def validate_dates(self):
        if self.end_date < self.start_date:
            raise ValueError("end_date must be on or after start_date")
        if self.visibility not in ("public", "private"):
            raise ValueError("visibility must be 'public' or 'private'")
        return self


class GroupTripUpdate(BaseModel):
    title: Optional[str] = None
    destination: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    visibility: Optional[str] = None


class MemberRead(BaseModel):
    user_id: uuid.UUID
    name: str
    picture_url: Optional[str] = None
    role: str
    joined_at: datetime

    model_config = ConfigDict(from_attributes=True)


class GroupTripRead(BaseModel):
    id: uuid.UUID
    creator_id: uuid.UUID
    title: str
    destination: str
    description: Optional[str] = None
    start_date: date
    end_date: date
    visibility: str
    invite_code: str
    member_count: int = 0
    itinerary_id: Optional[uuid.UUID] = None
    created_at: datetime

    # Creator info
    creator_name: str
    creator_picture_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class GroupTripDetail(GroupTripRead):
    members: List[MemberRead] = []


class GroupTripList(BaseModel):
    items: List[GroupTripRead]
    total: int
    page: int
    per_page: int
    total_pages: int


class GroupTripPreview(BaseModel):
    """Basic info shown to someone deciding whether to join via invite link."""
    id: uuid.UUID
    title: str
    destination: str
    description: Optional[str] = None
    start_date: date
    end_date: date
    visibility: str
    member_count: int = 0
    itinerary_id: Optional[uuid.UUID] = None
    creator_name: str
    creator_picture_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class OverlappingTrip(BaseModel):
    id: uuid.UUID
    title: str
    destination: str
    description: Optional[str] = None
    start_date: date
    end_date: date
    visibility: str
    member_count: int = 0
    itinerary_id: Optional[uuid.UUID] = None
    creator_name: str
    creator_picture_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
