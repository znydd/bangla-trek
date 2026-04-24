"""add group poll tables

Revision ID: e5b7c9d2a410
Revises: d370fa1a41a9
Create Date: 2026-04-24 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "e5b7c9d2a410"
down_revision: Union[str, Sequence[str], None] = "d370fa1a41a9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "group_activities",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("trip_id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("activity_type", sa.String(length=50), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=False),
        sa.Column("metadata_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["trip_id"], ["group_trips.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_group_activities_trip_id"),
        "group_activities",
        ["trip_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_group_activities_user_id"),
        "group_activities",
        ["user_id"],
        unique=False,
    )

    op.create_table(
        "polls",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("trip_id", sa.UUID(), nullable=False),
        sa.Column("creator_id", sa.UUID(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["creator_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["trip_id"], ["group_trips.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_polls_trip_id"), "polls", ["trip_id"], unique=False)

    op.create_table(
        "poll_options",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("poll_id", sa.UUID(), nullable=False),
        sa.Column("text", sa.String(length=255), nullable=False),
        sa.Column("image_url", sa.String(length=500), nullable=True),
        sa.Column("itinerary_activity_id", sa.UUID(), nullable=True),
        sa.ForeignKeyConstraint(
            ["itinerary_activity_id"],
            ["itinerary_activities.id"],
        ),
        sa.ForeignKeyConstraint(["poll_id"], ["polls.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_poll_options_poll_id"),
        "poll_options",
        ["poll_id"],
        unique=False,
    )

    op.create_table(
        "poll_votes",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("poll_id", sa.UUID(), nullable=False),
        sa.Column("poll_option_id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["poll_id"], ["polls.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["poll_option_id"],
            ["poll_options.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("poll_id", "user_id", name="uq_user_poll_vote"),
    )
    op.create_index(
        op.f("ix_poll_votes_poll_id"),
        "poll_votes",
        ["poll_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_poll_votes_poll_option_id"),
        "poll_votes",
        ["poll_option_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_poll_votes_user_id"),
        "poll_votes",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_poll_votes_user_id"), table_name="poll_votes")
    op.drop_index(op.f("ix_poll_votes_poll_option_id"), table_name="poll_votes")
    op.drop_index(op.f("ix_poll_votes_poll_id"), table_name="poll_votes")
    op.drop_table("poll_votes")
    op.drop_index(op.f("ix_poll_options_poll_id"), table_name="poll_options")
    op.drop_table("poll_options")
    op.drop_index(op.f("ix_polls_trip_id"), table_name="polls")
    op.drop_table("polls")
    op.drop_index(op.f("ix_group_activities_user_id"), table_name="group_activities")
    op.drop_index(op.f("ix_group_activities_trip_id"), table_name="group_activities")
    op.drop_table("group_activities")
