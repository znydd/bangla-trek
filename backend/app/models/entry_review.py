import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from .community_entry import CommunityEntry
    from .entry_review_photo import EntryReviewPhoto
    from .itinerary import Itinerary, ItineraryActivity
    from .user import User


class EntryReview(Base):
    __tablename__ = "entry_reviews"
    __table_args__ = (
        UniqueConstraint("entry_id", "user_id", name="uq_entry_reviews_entry_user"),
        CheckConstraint(
            "rating >= 1 AND rating <= 5", name="ck_entry_reviews_rating_range"
        ),
        CheckConstraint(
            "travel_style IN ('budget', 'luxury', 'adventure', 'family')",
            name="ck_entry_reviews_travel_style",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    entry_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("community_entries.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )

    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    travel_style: Mapped[str] = mapped_column(String(20), nullable=False)
    actual_cost_bdt: Mapped[float | None] = mapped_column(Float, nullable=True)
    time_spent_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    review_text: Mapped[str] = mapped_column(Text, nullable=False)

    itinerary_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("itineraries.id", ondelete="SET NULL"),
        nullable=True,
    )
    activity_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("itinerary_activities.id", ondelete="SET NULL"),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    entry: Mapped["CommunityEntry"] = relationship(
        "CommunityEntry", back_populates="reviews"
    )
    user: Mapped["User"] = relationship("User")
    itinerary: Mapped[Optional["Itinerary"]] = relationship("Itinerary")
    activity: Mapped[Optional["ItineraryActivity"]] = relationship(
        "ItineraryActivity"
    )
    photos: Mapped[List["EntryReviewPhoto"]] = relationship(
        "EntryReviewPhoto", back_populates="review", cascade="all, delete-orphan"
    )
