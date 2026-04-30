import uuid
from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class ReviewPhotoRead(BaseModel):
    id: uuid.UUID
    url: str
    public_id: str
    caption: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EntryReviewBase(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    travel_style: str = Field(..., pattern="^(budget|luxury|adventure|family)$")
    actual_cost_bdt: Optional[float] = Field(default=None, ge=0)
    time_spent_minutes: Optional[int] = Field(default=None, ge=0)
    review_text: str = Field(..., min_length=1)
    itinerary_id: Optional[uuid.UUID] = None
    activity_id: Optional[uuid.UUID] = None


class EntryReviewCreate(EntryReviewBase):
    pass


class EntryReviewUpdate(BaseModel):
    rating: Optional[int] = Field(default=None, ge=1, le=5)
    travel_style: Optional[str] = Field(
        default=None, pattern="^(budget|luxury|adventure|family)$"
    )
    actual_cost_bdt: Optional[float] = Field(default=None, ge=0)
    time_spent_minutes: Optional[int] = Field(default=None, ge=0)
    review_text: Optional[str] = Field(default=None, min_length=1)
    itinerary_id: Optional[uuid.UUID] = None
    activity_id: Optional[uuid.UUID] = None


class EntryReviewRead(EntryReviewBase):
    id: uuid.UUID
    entry_id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    photos: List[ReviewPhotoRead] = []

    author_name: str
    author_picture_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ReviewStyleSummary(BaseModel):
    travel_style: str
    count: int


class ReviewSummary(BaseModel):
    average_rating: Optional[float] = None
    review_count: int
    breakdown: Dict[int, int]
    by_travel_style: List[ReviewStyleSummary]


class EntryReviewList(BaseModel):
    items: List[EntryReviewRead]
    total: int
    page: int
    per_page: int
    total_pages: int
    summary: ReviewSummary
    my_review_id: Optional[uuid.UUID] = None
