import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from .community_entry import CommunityEntry


class EntryVideoEmbed(Base):
    __tablename__ = "entry_video_embeds"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    entry_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("community_entries.id"), nullable=False, index=True
    )
    
    url: Mapped[str] = mapped_column(String(2048), nullable=False)
    platform: Mapped[str] = mapped_column(String(20), nullable=False) # youtube, facebook, tiktok

    # Relationship
    entry: Mapped["CommunityEntry"] = relationship("CommunityEntry", back_populates="video_embeds")
