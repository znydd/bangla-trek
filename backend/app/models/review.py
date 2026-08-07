import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from .place import Place
    from .user import User


class Review(Base):
    __tablename__ = "reviews"
    __table_args__ = (
        UniqueConstraint("place_id", "user_id", "visited_on", name="uq_reviews_place_user_visit"),
        CheckConstraint("rating >= 1 AND rating <= 5", name="ck_reviews_rating_range"),
        Index("ix_reviews_place_status", "place_id", "status"),
        Index("ix_reviews_user_status", "user_id", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    place_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("places.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="published", index=True
    )  # 'published', 'pending', 'hidden', 'removed'

    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    visited_on: Mapped[date] = mapped_column(Date, nullable=False)

    travel_style: Mapped[str | None] = mapped_column(String(50), nullable=True)
    group_type: Mapped[str | None] = mapped_column(String(50), nullable=True)  # Solo, Couple, Family, Friends
    group_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    starting_location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    actual_cost_bdt: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)

    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    travel_guide: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Observational Metrics
    crowd_level: Mapped[str | None] = mapped_column(String(50), nullable=True)
    access_difficulty: Mapped[str | None] = mapped_column(String(50), nullable=True)
    road_condition: Mapped[str | None] = mapped_column(String(50), nullable=True)
    safety: Mapped[str | None] = mapped_column(String(50), nullable=True)
    cleanliness: Mapped[str | None] = mapped_column(String(50), nullable=True)
    mobile_carrier: Mapped[str | None] = mapped_column(String(50), nullable=True)
    strongest_network: Mapped[str | None] = mapped_column(String(50), nullable=True)
    network_reliability: Mapped[str | None] = mapped_column(String(50), nullable=True)

    helpful_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    place: Mapped["Place"] = relationship("Place", back_populates="reviews")
    user: Mapped["User"] = relationship("User")
    payment_methods: Mapped[List["ReviewPaymentMethod"]] = relationship(
        "ReviewPaymentMethod", back_populates="review", cascade="all, delete-orphan"
    )
    media: Mapped[List["ReviewMedia"]] = relationship(
        "ReviewMedia", back_populates="review", cascade="all, delete-orphan"
    )
    helpful_votes: Mapped[List["ReviewHelpfulVote"]] = relationship(
        "ReviewHelpfulVote", back_populates="review", cascade="all, delete-orphan"
    )


class ReviewPaymentMethod(Base):
    __tablename__ = "review_payment_methods"
    __table_args__ = (
        UniqueConstraint("review_id", "payment_method", name="uq_review_payment_methods"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    review_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("reviews.id", ondelete="CASCADE"), nullable=False, index=True
    )
    payment_method: Mapped[str] = mapped_column(String(50), nullable=False)

    review: Mapped["Review"] = relationship("Review", back_populates="payment_methods")


class ReviewMedia(Base):
    __tablename__ = "review_media"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    review_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("reviews.id", ondelete="CASCADE"), nullable=False, index=True
    )
    media_type: Mapped[str] = mapped_column(String(20), nullable=False)  # 'photo', 'video_embed'
    url: Mapped[str] = mapped_column(String(2048), nullable=False)
    storage_public_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    platform: Mapped[str | None] = mapped_column(String(50), nullable=True)
    caption: Mapped[str | None] = mapped_column(String(500), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    moderation_status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="published"
    )

    review: Mapped["Review"] = relationship("Review", back_populates="media")


class ReviewHelpfulVote(Base):
    __tablename__ = "review_helpful_votes"
    __table_args__ = (
        UniqueConstraint("review_id", "user_id", name="uq_review_helpful_votes_review_user"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    review_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("reviews.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    review: Mapped["Review"] = relationship("Review", back_populates="helpful_votes")
    user: Mapped["User"] = relationship("User")
