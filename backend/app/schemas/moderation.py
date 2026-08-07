import uuid
from datetime import datetime
from typing import Any, Dict
from pydantic import BaseModel, Field
from app.schemas.place import PlaceDetailRead
from app.schemas.review import ReviewRead


class ModerationApproveRequest(BaseModel):
    notes: str | None = None


class ModerationRejectRequest(BaseModel):
    reason: str = Field(..., min_length=3, max_length=1000)


class ModerationRequestChangesRequest(BaseModel):
    reason: str = Field(..., min_length=3, max_length=1000)


class ModerationMergeRequest(BaseModel):
    target_canonical_place_id: uuid.UUID
    reason: str = Field(..., min_length=3, max_length=1000)


class ModerationActionRead(BaseModel):
    id: uuid.UUID
    entity_type: str
    entity_id: uuid.UUID
    action: str
    performed_by: uuid.UUID
    performer_name: str | None = None
    reason: str | None = None
    meta_data: Dict[str, Any] | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class PendingSubmissionRead(BaseModel):
    place: PlaceDetailRead
    submitter_name: str | None = None
    submitter_email: str | None = None
    initial_review: ReviewRead | None = None

    model_config = {"from_attributes": True}
