import uuid
from datetime import datetime
from pydantic import BaseModel, Field


class PlaceMediaRead(BaseModel):
    id: uuid.UUID
    media_type: str
    url: str
    storage_public_id: str | None = None
    platform: str | None = None
    caption: str | None = None
    sort_order: int = 0

    model_config = {"from_attributes": True}


class PlaceAliasRead(BaseModel):
    id: uuid.UUID
    alias: str

    model_config = {"from_attributes": True}


class PlaceTagRead(BaseModel):
    id: uuid.UUID
    tag: str

    model_config = {"from_attributes": True}


class PlaceCardRead(BaseModel):
    id: uuid.UUID
    slug: str
    name: str
    category: str
    summary: str
    district: str | None = None
    upazila: str | None = None
    village: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    best_season: str | None = None
    suggested_duration: str | None = None
    budget_min_bdt: float | None = None
    budget_max_bdt: float | None = None
    average_rating: float = 0.0
    review_count: int = 0
    primary_image_url: str | None = None
    tags: list[str] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class PlaceDetailRead(BaseModel):
    id: uuid.UUID
    slug: str
    name: str
    category: str
    summary: str
    description: str | None = None
    source_type: str
    status: str

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
    budget_min_bdt: float | None = None
    budget_max_bdt: float | None = None

    highlights: list[str] = Field(default_factory=list)
    know_before_you_go: list[str] = Field(default_factory=list)

    average_rating: float = 0.0
    review_count: int = 0

    aliases: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    media: list[PlaceMediaRead] = Field(default_factory=list)

    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
