import uuid
from datetime import date, datetime
from pydantic import BaseModel, Field, field_validator


class ReviewMediaCreate(BaseModel):
    media_type: str = "photo"  # 'photo', 'video_embed'
    url: str
    storage_public_id: str | None = None
    platform: str | None = None
    caption: str | None = None
    sort_order: int = 0


class ReviewMediaRead(BaseModel):
    id: uuid.UUID
    media_type: str
    url: str
    storage_public_id: str | None = None
    platform: str | None = None
    caption: str | None = None
    sort_order: int = 0

    model_config = {"from_attributes": True}


class ReviewCreate(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    visited_on: date

    travel_style: str | None = None
    group_type: str | None = None
    group_size: int | None = Field(default=None, ge=1)
    starting_location: str | None = None
    actual_cost_bdt: float | None = Field(default=None, ge=0)

    title: str | None = None
    travel_guide: str | None = None

    crowd_level: str | None = None
    access_difficulty: str | None = None
    road_condition: str | None = None
    safety: str | None = None
    cleanliness: str | None = None
    mobile_carrier: str | None = None
    strongest_network: str | None = None
    network_reliability: str | None = None

    payment_methods: list[str] = Field(default_factory=list)
    media: list[ReviewMediaCreate] = Field(default_factory=list)


class ReviewUpdate(BaseModel):
    rating: int | None = Field(default=None, ge=1, le=5)
    visited_on: date | None = None

    travel_style: str | None = None
    group_type: str | None = None
    group_size: int | None = Field(default=None, ge=1)
    starting_location: str | None = None
    actual_cost_bdt: float | None = Field(default=None, ge=0)

    title: str | None = None
    travel_guide: str | None = None

    crowd_level: str | None = None
    access_difficulty: str | None = None
    road_condition: str | None = None
    safety: str | None = None
    cleanliness: str | None = None
    mobile_carrier: str | None = None
    strongest_network: str | None = None
    network_reliability: str | None = None

    payment_methods: list[str] | None = None


class ReviewUserRead(BaseModel):
    id: uuid.UUID
    name: str
    picture_url: str | None = None

    model_config = {"from_attributes": True}


class ReviewRead(BaseModel):
    id: uuid.UUID
    place_id: uuid.UUID
    user_id: uuid.UUID
    user: ReviewUserRead
    status: str

    rating: int
    visited_on: date

    travel_style: str | None = None
    group_type: str | None = None
    group_size: int | None = None
    starting_location: str | None = None
    actual_cost_bdt: float | None = None

    title: str | None = None
    travel_guide: str | None = None

    crowd_level: str | None = None
    access_difficulty: str | None = None
    road_condition: str | None = None
    safety: str | None = None
    cleanliness: str | None = None
    mobile_carrier: str | None = None
    strongest_network: str | None = None
    network_reliability: str | None = None

    helpful_count: int = 0
    is_helpful_by_me: bool = False
    payment_methods: list[str] = Field(default_factory=list)
    media: list[ReviewMediaRead] = Field(default_factory=list)

    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# Metric Aggregation Schemas
class DistributionOption(BaseModel):
    value: str
    count: int
    percentage: float


class MetricDistribution(BaseModel):
    total: int
    options: list[DistributionOption]


class CostRange(BaseModel):
    min: float | None = None
    max: float | None = None
    median: float | None = None


class ReviewSummaryRead(BaseModel):
    place_id: uuid.UUID
    total_reviews: int
    average_rating: float
    most_recent_visit: date | None = None
    most_common_travel_style: str | None = None
    average_group_size: float | None = None
    typical_access_difficulty: str | None = None
    most_reported_payment_method: str | None = None
    cost_range: CostRange

    rating_breakdown: MetricDistribution
    crowd_level: MetricDistribution
    access_difficulty: MetricDistribution
    road_condition: MetricDistribution
    safety: MetricDistribution
    cleanliness: MetricDistribution
    mobile_carrier: MetricDistribution
    network_reliability: MetricDistribution
    payment_methods: MetricDistribution
