"""add collaboration tables

Revision ID: e5b2c3d4f6a7
Revises: d4a1b2c3e5f7
Create Date: 2026-04-17 19:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "e5b2c3d4f6a7"
down_revision: Union[str, Sequence[str], None] = ("d4a1b2c3e5f7", "7dde0de54c51")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add itinerary_id to group_trips
    op.add_column(
        "group_trips",
        sa.Column("itinerary_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        "fk_group_trips_itinerary",
        "group_trips",
        "itineraries",
        ["itinerary_id"],
        ["id"],
    )
    op.create_index(
        "ix_group_trips_itinerary_id", "group_trips", ["itinerary_id"], unique=False
    )

    # 2. Add group_activities table
    op.create_table(
        "group_activities",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "trip_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("group_trips.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
            nullable=False,
            index=True,
        ),
        sa.Column("activity_type", sa.String(50), nullable=False),
        sa.Column("description", sa.String(500), nullable=False),
        sa.Column("metadata_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )

    # 3. Add polls table
    op.create_table(
        "polls",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "trip_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("group_trips.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "creator_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
            nullable=False,
        ),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )

    # 4. Add poll_options table
    op.create_table(
        "poll_options",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "poll_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("polls.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("text", sa.String(255), nullable=False),
        sa.Column("image_url", sa.String(500), nullable=True),
        sa.Column(
            "itinerary_activity_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("itinerary_activities.id"),
            nullable=True,
        ),
    )

    # 5. Add poll_votes table
    op.create_table(
        "poll_votes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "poll_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("polls.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "poll_option_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("poll_options.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
        sa.UniqueConstraint("poll_id", "user_id", name="uq_user_poll_vote"),
    )


def downgrade() -> None:
    op.drop_table("poll_votes")
    op.drop_table("poll_options")
    op.drop_table("polls")
    op.drop_table("group_activities")
    op.drop_index("ix_group_trips_itinerary_id", table_name="group_trips")
    op.drop_constraint("fk_group_trips_itinerary", "group_trips", type_="foreignkey")
    op.drop_column("group_trips", "itinerary_id")
