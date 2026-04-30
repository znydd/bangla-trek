import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import DateTime, Float, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from .user import User
    from .entry_photo import EntryPhoto
    from .entry_review import EntryReview
    from .entry_video_embed import EntryVideoEmbed


class CommunityEntry(Base):
    __tablename__ = "community_entries"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    
    category: Mapped[str] = mapped_column(String(20), nullable=False) # attraction, hotel, etc.
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    location: Mapped[str] = mapped_column(String(500), nullable=False)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    price_range: Mapped[str] = mapped_column(String(20), nullable=False) # budget, mid_range, etc.
    
    amenities: Mapped[List[str]] = mapped_column(ARRAY(String), nullable=False, default=[])
    travel_tips: Mapped[str | None] = mapped_column(Text, nullable=True)
    tags: Mapped[List[str]] = mapped_column(ARRAY(String), nullable=False, default=[]) # trending, hidden_gem
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    user: Mapped["User"] = relationship("User")
    photos: Mapped[List["EntryPhoto"]] = relationship(
        "EntryPhoto", back_populates="entry", cascade="all, delete-orphan"
    )
    video_embeds: Mapped[List["EntryVideoEmbed"]] = relationship(
        "EntryVideoEmbed", back_populates="entry", cascade="all, delete-orphan"
    )
    reviews: Mapped[List["EntryReview"]] = relationship(
        "EntryReview", back_populates="entry", cascade="all, delete-orphan"
    )
