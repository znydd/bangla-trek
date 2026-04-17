import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


# ── Request schemas ──


class TransitBlueprintStepCreate(BaseModel):
    """A single step when the user manually defines steps."""
    step_number: int = Field(..., ge=1)
    instruction: str = Field(..., min_length=1)
    mode: str = Field(..., pattern="^(bus|cng|walking|rickshaw|train|launch|boat|ferry|auto|bike|car|mixed|other)$")
    estimated_duration_mins: Optional[int] = Field(None, ge=0)
    estimated_cost_bdt: Optional[float] = Field(None, ge=0)


class TransitBlueprintCreate(BaseModel):
    origin: str = Field(..., min_length=1, max_length=255)
    destination: str = Field(..., min_length=1, max_length=255)
    raw_description: str = Field(..., min_length=10)
    estimated_duration_mins: Optional[int] = Field(None, ge=0)
    estimated_cost_bdt: Optional[float] = Field(None, ge=0)
    notes: Optional[str] = None


class ParsePreviewRequest(BaseModel):
    """Send raw text to the LLM for structured parsing without saving."""
    raw_description: str = Field(..., min_length=10)
    origin: Optional[str] = None
    destination: Optional[str] = None


# ── Response schemas ──


class TransitBlueprintStepRead(BaseModel):
    id: uuid.UUID
    step_number: int
    instruction: str
    mode: str
    estimated_duration_mins: Optional[int] = None
    estimated_cost_bdt: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)


class TransitBlueprintRead(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    origin: str
    destination: str
    raw_description: str
    estimated_duration_mins: Optional[int] = None
    estimated_cost_bdt: Optional[float] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    steps: List[TransitBlueprintStepRead] = []

    # Populated by service layer
    author_name: str
    author_picture_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class TransitBlueprintListItem(BaseModel):
    id: uuid.UUID
    origin: str
    destination: str
    estimated_duration_mins: Optional[int] = None
    estimated_cost_bdt: Optional[float] = None
    step_count: int = 0
    created_at: datetime

    # Populated by service layer
    author_name: str
    author_picture_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class TransitBlueprintListResponse(BaseModel):
    items: List[TransitBlueprintListItem]
    total: int
    page: int
    per_page: int
    total_pages: int


class ParsedStepPreview(BaseModel):
    """A single parsed step from the LLM preview (not yet saved)."""
    step_number: int
    instruction: str
    mode: str
    estimated_duration_mins: Optional[int] = None
    estimated_cost_bdt: Optional[float] = None


class ParsePreviewResponse(BaseModel):
    """LLM-parsed steps returned for preview before final save."""
    steps: List[ParsedStepPreview]
    total_estimated_duration_mins: Optional[int] = None
    total_estimated_cost_bdt: Optional[float] = None
