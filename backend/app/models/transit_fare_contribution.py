import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from .user import User


class TransitFareContribution(Base):
    __tablename__ = "transit_fare_contributions"
    __table_args__ = (
        CheckConstraint(
            "fare_bdt >= 0",
            name="ck_transit_fares_fare_non_negative",
        ),
        CheckConstraint(
            "min_fare_bdt IS NULL OR min_fare_bdt >= 0",
            name="ck_transit_fares_min_non_negative",
        ),
        CheckConstraint(
            "max_fare_bdt IS NULL OR max_fare_bdt >= 0",
            name="ck_transit_fares_max_non_negative",
        ),
        CheckConstraint(
            "min_fare_bdt IS NULL OR max_fare_bdt IS NULL OR min_fare_bdt <= max_fare_bdt",
            name="ck_transit_fares_min_lte_max",
        ),
        CheckConstraint(
            "mode IN ('cng', 'bus', 'train')",
            name="ck_transit_fares_mode",
        ),
        CheckConstraint(
            "source_type IN ('observed', 'quoted', 'booked')",
            name="ck_transit_fares_source_type",
        ),
        Index(
            "ix_transit_fares_route_mode_submitted",
            "origin",
            "destination",
            "mode",
            "submitted_at",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )

    origin: Mapped[str] = mapped_column(String(255), nullable=False)
    destination: Mapped[str] = mapped_column(String(255), nullable=False)
    mode: Mapped[str] = mapped_column(String(20), nullable=False)

    fare_bdt: Mapped[float] = mapped_column(Float, nullable=False)
    min_fare_bdt: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    max_fare_bdt: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source_type: Mapped[str] = mapped_column(
        String(20), nullable=False, default="observed"
    )
    travel_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )

    user: Mapped["User"] = relationship("User")
