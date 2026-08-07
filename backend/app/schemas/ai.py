import uuid
from datetime import datetime
from pydantic import BaseModel, Field


class AIConversationCreate(BaseModel):
    title: str | None = Field(default="New Conversation", max_length=255)


class AIConversationRead(BaseModel):
    id: uuid.UUID
    title: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AIPlaceContextRead(BaseModel):
    place_id: uuid.UUID
    slug: str
    name: str
    category: str
    district: str | None = None
    upazila: str | None = None
    added_at: datetime

    model_config = {"from_attributes": True}


class AIMessageRead(BaseModel):
    id: uuid.UUID
    conversation_id: uuid.UUID
    role: str
    content: str
    model: str | None = None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class AIConversationDetailRead(BaseModel):
    id: uuid.UUID
    title: str
    context_places: list[AIPlaceContextRead] = Field(default_factory=list)
    messages: list[AIMessageRead] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AIMessageCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=4000)
