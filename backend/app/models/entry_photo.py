import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from .community_entry import CommunityEntry


class EntryPhoto(Base):
    __tablename__ = "entry_photos"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    entry_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("community_entries.id"), nullable=False, index=True
    )
    
    url: Mapped[str] = mapped_column(String(2048), nullable=False)
    public_id: Mapped[str] = mapped_column(String(500), nullable=False) # Cloudinary public_id
    caption: Mapped[str | None] = mapped_column(String(500), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationship
    entry: Mapped["CommunityEntry"] = relationship("CommunityEntry", back_populates="photos")
