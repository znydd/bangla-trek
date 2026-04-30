import uuid
from datetime import datetime
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .community_entry import CommunityEntry
    from .user import User

class NomadMetric(Base):
    __tablename__ = "nomad_metrics"
    __table_args__ = (
        UniqueConstraint("entry_id", "user_id", name="uq_nomad_metrics_entry_user"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    entry_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("community_entries.id"), nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    carrier: Mapped[str] = mapped_column(String(50), nullable=False)
    signal_strength: Mapped[str] = mapped_column(String(20), nullable=False)
    safety_rating: Mapped[int] = mapped_column(Integer, nullable=False)
    bkash_available: Mapped[bool] = mapped_column(Boolean, nullable=False)
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    entry: Mapped["CommunityEntry"] = relationship("CommunityEntry")
    user: Mapped["User"] = relationship("User")