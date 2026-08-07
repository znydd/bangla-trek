import uuid
from datetime import datetime
from pydantic import BaseModel, Field
from app.schemas.place import PlaceMediaRead
from app.schemas.review import ReviewCreate, ReviewRead


class DuplicateCheckMatch(BaseModel):
    id: uuid.UUID
    slug: str
    name: str
    category: str
    district: str | None = None
    upazila: str | None = None
    status: str
    match_reason: str


class DuplicateCheckResponse(BaseModel):
    query: str
    has_exact_match: bool
    matches: list[DuplicateCheckMatch] = Field(default_factory=list)


class PlaceDraftCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    category: str
    summary: str = Field(..., max_length=500)
    description: str | None = None

    village: str | None = None
    upazila: str | None = None
    district: str | None = None
    division: str | None = None
    nearest_hub: str | None = None
    latitude: float | None = None
    longitude: float | None = None

    best_season: str | None = None
    suggested_duration: str | None = None
    guide_requirement: str | None = None
    budget_min_bdt: float | None = Field(default=None, ge=0)
    budget_max_bdt: float | None = Field(default=None, ge=0)

    highlights: list[str] = Field(default_factory=list)
    know_before_you_go: list[str] = Field(default_factory=list)
    aliases: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)


class PlaceDraftUpdate(BaseModel):
    name: str | None = None
    category: str | None = None
    summary: str | None = None
    description: str | None = None

    village: str | None = None
    upazila: str | None = None
    district: str | None = None
    division: str | None = None
    nearest_hub: str | None = None
    latitude: float | None = None
    longitude: float | None = None

    best_season: str | None = None
    suggested_duration: str | None = None
    guide_requirement: str | None = None
    budget_min_bdt: float | None = Field(default=None, ge=0)
    budget_max_bdt: float | None = Field(default=None, ge=0)

    highlights: list[str] | None = None
    know_before_you_go: list[str] | None = None
    aliases: list[str] | None = None
    tags: list[str] | None = None


class PlaceSubmissionSubmit(BaseModel):
    initial_review: ReviewCreate | None = None


class UserContributionRead(BaseModel):
    id: uuid.UUID
    slug: str
    name: str
    category: str
    summary: str
    status: str
    district: str | None = None
    upazila: str | None = None
    created_at: datetime
    updated_at: datetime
    initial_review: ReviewRead | None = None
    media: list[PlaceMediaRead] = Field(default_factory=list)

    model_config = {"from_attributes": True}
