import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from app.db.base_class import Base

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False, index=True)
    type = Column(String(50), nullable=False)  # group_join, travel_overlap, reminder, poll_result
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    link_url = Column(String(500), nullable=True) # Direct link to the trip/itinerary
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
