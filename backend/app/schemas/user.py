import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserRead(BaseModel):
    id: uuid.UUID
    google_id: str
    email: EmailStr
    name: str
    picture_url: str | None
    role: str
    is_active: bool
    email_verified: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None

    model_config = {"from_attributes": True}


class DevLoginRequest(BaseModel):
    email: EmailStr = "dev@example.com"
    name: str = "Dev User"
    role: str = "user"


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead

