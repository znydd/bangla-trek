import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from .user import User


class TransitBlueprint(Base):
    __tablename__ = "transit_blueprints"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )

    origin: Mapped[str] = mapped_column(String(255), nullable=False)
    destination: Mapped[str] = mapped_column(String(255), nullable=False)
    raw_description: Mapped[str] = mapped_column(Text, nullable=False)
    estimated_duration_mins: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True
    )
    estimated_cost_bdt: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    user: Mapped["User"] = relationship("User")
    steps: Mapped[List["TransitBlueprintStep"]] = relationship(
        "TransitBlueprintStep",
        back_populates="blueprint",
        cascade="all, delete-orphan",
        order_by="TransitBlueprintStep.step_number",
    )


class TransitBlueprintStep(Base):
    __tablename__ = "transit_blueprint_steps"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    blueprint_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("transit_blueprints.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    step_number: Mapped[int] = mapped_column(Integer, nullable=False)
    instruction: Mapped[str] = mapped_column(Text, nullable=False)
    mode: Mapped[str] = mapped_column(
        String(30), nullable=False
    )  # bus, cng, walking, rickshaw, train, launch, boat, etc.
    estimated_duration_mins: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True
    )
    estimated_cost_bdt: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True
    )

    # Relationships
    blueprint: Mapped["TransitBlueprint"] = relationship(
        "TransitBlueprint", back_populates="steps"
    )
