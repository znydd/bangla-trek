from sqlalchemy import Column, Float, ForeignKey, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.db.base import Base

class UserLocation(Base):
    __tablename__ = "user_locations"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    status = Column(String, default="traveling")
    message = Column(String, nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), default=func.now())