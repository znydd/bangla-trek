import uuid
from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class TransitFareContributionCreate(BaseModel):
    origin: str = Field(..., min_length=1, max_length=255)
    destination: str = Field(..., min_length=1, max_length=255)
    mode: str = Field(..., pattern="^(cng|bus|train)$")
    fare_bdt: float = Field(..., ge=0)
    min_fare_bdt: Optional[float] = Field(default=None, ge=0)
    max_fare_bdt: Optional[float] = Field(default=None, ge=0)
    notes: Optional[str] = Field(default=None, max_length=2000)
    source_type: str = Field(default="observed", pattern="^(observed|quoted|booked)$")
    travel_date: Optional[date] = None


class TransitFareContributionRead(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    origin: str
    destination: str
    mode: str
    fare_bdt: float
    min_fare_bdt: Optional[float] = None
    max_fare_bdt: Optional[float] = None
    notes: Optional[str] = None
    source_type: str
    travel_date: Optional[date] = None
    submitted_at: datetime

    author_name: str
    author_picture_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class TransitFareContributionList(BaseModel):
    items: List[TransitFareContributionRead]
    total: int
    page: int
    per_page: int
    total_pages: int


class TransitFareModeEstimate(BaseModel):
    mode: str
    median_fare_bdt: Optional[float] = None
    submission_count: int
    recent_submission_count: int
    min_fare_bdt: Optional[float] = None
    max_fare_bdt: Optional[float] = None
    last_updated_at: Optional[datetime] = None
    sample_window_days: Optional[int] = None
    is_low_data: bool
    used_all_time_fallback: bool


class TransitFareEstimateResponse(BaseModel):
    origin: str
    destination: str
    estimates: List[TransitFareModeEstimate]


class BookingLink(BaseModel):
    id: str
    label: str
    url: str


class BookingLinksResponse(BaseModel):
    items: List[BookingLink]
