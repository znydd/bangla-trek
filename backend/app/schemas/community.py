import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, HttpUrl


class VideoEmbedBase(BaseModel):
    url: str
    platform: str # youtube, facebook, tiktok


class VideoEmbedCreate(VideoEmbedBase):
    pass


class VideoEmbedRead(VideoEmbedBase):
    id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)


class PhotoRead(BaseModel):
    id: uuid.UUID
    url: str
    public_id: str
    caption: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class CommunityEntryBase(BaseModel):
    category: str
    name: str
    location: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    price_range: str
    amenities: List[str] = []
    travel_tips: Optional[str] = None
    tags: List[str] = []


class CommunityEntryCreate(CommunityEntryBase):
    video_embeds: List[VideoEmbedCreate] = []


class CommunityEntryUpdate(BaseModel):
    category: Optional[str] = None
    name: Optional[str] = None
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    price_range: Optional[str] = None
    amenities: Optional[List[str]] = None
    travel_tips: Optional[str] = None
    tags: Optional[List[str]] = None
    video_embeds: Optional[List[VideoEmbedCreate]] = None


class CommunityEntryRead(CommunityEntryBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    
    photos: List[PhotoRead] = []
    video_embeds: List[VideoEmbedRead] = []
    
    # These will be populated by the service layer via join
    author_name: str
    author_picture_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class CommunityMapPoint(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    location: str
    latitude: float
    longitude: float
    category: str
    tags: List[str] = []
    author_name: str
    author_picture_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class PaginatedResponse(BaseModel):
    total: int
    page: int
    per_page: int
    total_pages: int


class CommunityEntryList(PaginatedResponse):
    items: List[CommunityEntryRead]
