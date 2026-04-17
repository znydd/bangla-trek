import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


UserTravelStatus = Literal["traveling", "planning", "offline"]


class UserLocationUpsert(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    status: UserTravelStatus = "traveling"
    message: str | None = Field(default=None, max_length=280)


class UserLocationRead(BaseModel):
    user_id: uuid.UUID
    latitude: float
    longitude: float
    status: str | None
    message: str | None
    updated_at: datetime | None

    model_config = {"from_attributes": True}


class UserLocationPoint(UserLocationRead):
    user_name: str | None = None
    user_picture_url: str | None = None

