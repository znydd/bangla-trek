import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import (
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
    from .user import User


class TravelTrip(Base):
    __tablename__ = "travel_trips"
    __table_args__ = (
        Index("ix_travel_trips_status_dates", "status", "start_at"),
        Index("ix_travel_trips_destination", "destination"),
        Index("ix_travel_trips_origin", "origin"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    creator_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)

    origin: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    destination: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    start_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    meeting_point: Mapped[str | None] = mapped_column(String(255), nullable=True)
    transport: Mapped[str | None] = mapped_column(String(100), nullable=True)

    estimated_cost_min_bdt: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    estimated_cost_max_bdt: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)

    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    itinerary: Mapped[str | None] = mapped_column(Text, nullable=True)

    max_members: Mapped[int] = mapped_column(Integer, nullable=False, default=5)

    communication_platform: Mapped[str | None] = mapped_column(String(50), nullable=True)
    communication_note: Mapped[str | None] = mapped_column(Text, nullable=True)

    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="scheduled", index=True
    )  # 'scheduled', 'full', 'cancelled', 'completed'

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    creator: Mapped["User"] = relationship("User")
    requirements: Mapped[List["TravelTripRequirement"]] = relationship(
        "TravelTripRequirement", back_populates="trip", cascade="all, delete-orphan"
    )
    members: Mapped[List["TravelTripMember"]] = relationship(
        "TravelTripMember", back_populates="trip", cascade="all, delete-orphan"
    )


class TravelTripRequirement(Base):
    __tablename__ = "travel_trip_requirements"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    trip_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("travel_trips.id", ondelete="CASCADE"), nullable=False, index=True
    )
    requirement: Mapped[str] = mapped_column(String(255), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    trip: Mapped["TravelTrip"] = relationship("TravelTrip", back_populates="requirements")


class TravelTripMember(Base):
    __tablename__ = "travel_trip_members"
    __table_args__ = (
        UniqueConstraint("trip_id", "user_id", name="uq_travel_trip_members_trip_user"),
        Index("ix_travel_trip_members_user_status", "user_id", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    trip_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("travel_trips.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="member")  # 'organizer', 'member'
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="joined")  # 'joined', 'left', 'removed'

    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    left_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    trip: Mapped["TravelTrip"] = relationship("TravelTrip", back_populates="members")
    user: Mapped["User"] = relationship("User")
