import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class PollOptionBase(BaseModel):
    title: str
    description: Optional[str] = None


class PollOptionCreate(PollOptionBase):
    pass


class PollOptionRead(PollOptionBase):
    id: uuid.UUID
    poll_id: uuid.UUID
    vote_count: int = 0
    has_voted: bool = False

    model_config = ConfigDict(from_attributes=True)


class PollCreate(BaseModel):
    title: str
    category: str
    options: List[PollOptionCreate]


class PollRead(BaseModel):
    id: uuid.UUID
    trip_id: uuid.UUID
    creator_id: uuid.UUID
    title: str
    category: str
    is_open: bool
    created_at: datetime
    
    # extra data
    creator_name: str
    options: List[PollOptionRead]
    total_votes: int = 0

    model_config = ConfigDict(from_attributes=True)


class PollVoteCreate(BaseModel):
    option_id: uuid.UUID
