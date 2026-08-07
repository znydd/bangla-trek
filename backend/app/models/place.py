import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from .user import User
    from .review import Review


class Place(Base):
    __tablename__ = "places"
    __table_args__ = (
        Index("ix_places_status_category", "status", "category"),
        Index("ix_places_district_upazila", "district", "upazila"),
        Index("ix_places_normalized_name", "normalized_name"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    slug: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    normalized_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    summary: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    source_type: Mapped[str] = mapped_column(
        String(20), nullable=False, default="community"
    )  # 'admin' or 'community'
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="draft", index=True
    )  # 'draft', 'pending', 'changes_requested', 'approved', 'rejected', 'merged', 'archived'

    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    approved_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    approved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    duplicate_of_place_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("places.id", ondelete="SET NULL"), nullable=True
    )

    # Location
    village: Mapped[str | None] = mapped_column(String(255), nullable=True)
    upazila: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    district: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    division: Mapped[str | None] = mapped_column(String(255), nullable=True)
    nearest_hub: Mapped[str | None] = mapped_column(String(255), nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Travel Facts
    best_season: Mapped[str | None] = mapped_column(String(255), nullable=True)
    suggested_duration: Mapped[str | None] = mapped_column(String(255), nullable=True)
    guide_requirement: Mapped[str | None] = mapped_column(String(255), nullable=True)
    budget_min_bdt: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    budget_max_bdt: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)

    highlights: Mapped[List[str]] = mapped_column(ARRAY(String), nullable=False, default=[])
    know_before_you_go: Mapped[List[str]] = mapped_column(ARRAY(String), nullable=False, default=[])

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    creator: Mapped[Optional["User"]] = relationship("User", foreign_keys=[created_by])
    approver: Mapped[Optional["User"]] = relationship("User", foreign_keys=[approved_by])
    aliases: Mapped[List["PlaceAlias"]] = relationship(
        "PlaceAlias", back_populates="place", cascade="all, delete-orphan"
    )
    tags: Mapped[List["PlaceTag"]] = relationship(
        "PlaceTag", back_populates="place", cascade="all, delete-orphan"
    )
    media: Mapped[List["PlaceMedia"]] = relationship(
        "PlaceMedia", back_populates="place", cascade="all, delete-orphan"
    )
    reviews: Mapped[List["Review"]] = relationship(
        "Review", back_populates="place", cascade="all, delete-orphan"
    )


class PlaceAlias(Base):
    __tablename__ = "place_aliases"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    place_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("places.id", ondelete="CASCADE"), nullable=False, index=True
    )
    alias: Mapped[str] = mapped_column(String(255), nullable=False)
    normalized_alias: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    place: Mapped["Place"] = relationship("Place", back_populates="aliases")


class PlaceTag(Base):
    __tablename__ = "place_tags"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    place_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("places.id", ondelete="CASCADE"), nullable=False, index=True
    )
    tag: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    place: Mapped["Place"] = relationship("Place", back_populates="tags")


class PlaceMedia(Base):
    __tablename__ = "place_media"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    place_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("places.id", ondelete="CASCADE"), nullable=False, index=True
    )
    uploaded_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    media_type: Mapped[str] = mapped_column(String(20), nullable=False)  # 'photo', 'video_embed'
    url: Mapped[str] = mapped_column(String(2048), nullable=False)
    storage_public_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    platform: Mapped[str | None] = mapped_column(String(50), nullable=True)  # YouTube, Facebook, TikTok
    caption: Mapped[str | None] = mapped_column(String(500), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    moderation_status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="approved"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    place: Mapped["Place"] = relationship("Place", back_populates="media")
    uploader: Mapped[Optional["User"]] = relationship("User")
