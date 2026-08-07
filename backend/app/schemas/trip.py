import uuid
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class TravelTripRequirementRead(BaseModel):
    id: uuid.UUID
    requirement: str
    sort_order: int

    model_config = {"from_attributes": True}


class TravelTripMemberPublicRead(BaseModel):
    user_id: uuid.UUID
    name: str
    picture_url: str | None = None
    role: str
    status: str
    joined_at: datetime

    model_config = {"from_attributes": True}


class TravelTripParticipantRead(BaseModel):
    user_id: uuid.UUID
    name: str
    email: EmailStr
    picture_url: str | None = None
    role: str
    status: str
    joined_at: datetime

    model_config = {"from_attributes": True}


class TravelTripCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    origin: str = Field(..., min_length=2, max_length=255)
    destination: str = Field(..., min_length=2, max_length=255)

    start_at: datetime
    end_at: datetime

    meeting_point: str | None = Field(default=None, max_length=255)
    transport: str | None = Field(default=None, max_length=100)

    estimated_cost_min_bdt: float | None = Field(default=None, ge=0)
    estimated_cost_max_bdt: float | None = Field(default=None, ge=0)

    description: str | None = None
    itinerary: str | None = None

    max_members: int = Field(default=5, ge=2, le=50)

    communication_platform: str | None = Field(default="Email / BCC Draft", max_length=50)
    communication_note: str | None = None

    requirements: list[str] = Field(default_factory=list)


class TravelTripUpdate(BaseModel):
    title: str | None = None
    origin: str | None = None
    destination: str | None = None

    start_at: datetime | None = None
    end_at: datetime | None = None

    meeting_point: str | None = None
    transport: str | None = None

    estimated_cost_min_bdt: float | None = Field(default=None, ge=0)
    estimated_cost_max_bdt: float | None = Field(default=None, ge=0)

    description: str | None = None
    itinerary: str | None = None

    max_members: int | None = Field(default=None, ge=2, le=50)

    communication_platform: str | None = None
    communication_note: str | None = None

    requirements: list[str] | None = None


class TravelTripRead(BaseModel):
    id: uuid.UUID
    creator_id: uuid.UUID
    creator_name: str
    creator_picture_url: str | None = None
    title: str
    origin: str
    destination: str
    start_at: datetime
    end_at: datetime
    transport: str | None = None
    estimated_cost_min_bdt: float | None = None
    estimated_cost_max_bdt: float | None = None
    max_members: int
    joined_members_count: int
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class TravelTripDetailRead(BaseModel):
    id: uuid.UUID
    creator_id: uuid.UUID
    creator_name: str
    creator_picture_url: str | None = None
    title: str
    origin: str
    destination: str
    start_at: datetime
    end_at: datetime
    meeting_point: str | None = None
    transport: str | None = None
    estimated_cost_min_bdt: float | None = None
    estimated_cost_max_bdt: float | None = None
    description: str | None = None
    itinerary: str | None = None
    max_members: int
    joined_members_count: int
    status: str
    communication_platform: str | None = None
    communication_note: str | None = None

    requirements: list[TravelTripRequirementRead] = Field(default_factory=list)
    members: list[TravelTripMemberPublicRead] = Field(default_factory=list)

    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class EmailDraftRead(BaseModel):
    trip_id: uuid.UUID
    trip_title: str
    bcc_emails: list[EmailStr] = Field(default_factory=list)
    subject: str
    body: str
    mailto_url: str
