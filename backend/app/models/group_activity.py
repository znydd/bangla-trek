import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from .group_trip import GroupTrip
    from .user import User


class GroupActivity(Base):
    """Activity feed for a group trip."""

    __tablename__ = "group_activities"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    trip_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("group_trips.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )

    activity_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # e.g., "join", "leave", "poll_created", "voted", "itinerary_linked"
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    
    # Store arbitrary metadata (e.g., poll_id, option_text)
    metadata_json: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    trip: Mapped["GroupTrip"] = relationship("GroupTrip")
    user: Mapped["User"] = relationship("User")
