import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import DateTime, Float, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from .user import User


class BuddyMatch(Base):
    """Stores buddy match records with interest and destination overlap."""

    __tablename__ = "buddy_matches"
    __table_args__ = (
        UniqueConstraint("user_id", "matched_user_id", name="uq_buddy_match_pair"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    # The user who initiated/owns this match record
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )

    # The matched buddy user
    matched_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )

    # Match score (0.0 to 1.0) based on interest and destination overlap
    match_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    # Common interests shared between users
    common_interests: Mapped[List[str]] = mapped_column(
        ARRAY(String), nullable=False, default=[]
    )

    # Common destinations (from itineraries or group trips)
    common_destinations: Mapped[List[str]] = mapped_column(
        ARRAY(String), nullable=False, default=[]
    )

    # Match status
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="suggested"
    )  # suggested | pending | accepted | rejected | blocked

    # Who initiated the match request (for pending/accepted status)
    initiated_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])
    matched_user: Mapped["User"] = relationship("User", foreign_keys=[matched_user_id])
