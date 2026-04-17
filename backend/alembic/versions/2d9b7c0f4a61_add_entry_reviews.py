"""add entry reviews

Revision ID: 2d9b7c0f4a61
Revises: 8b351b619903
Create Date: 2026-04-17 16:05:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "2d9b7c0f4a61"
down_revision: Union[str, Sequence[str], None] = "8b351b619903"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "entry_reviews",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("entry_id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("travel_style", sa.String(length=20), nullable=False),
        sa.Column("actual_cost_bdt", sa.Float(), nullable=True),
        sa.Column("time_spent_minutes", sa.Integer(), nullable=True),
        sa.Column("review_text", sa.Text(), nullable=False),
        sa.Column("itinerary_id", sa.UUID(), nullable=True),
        sa.Column("activity_id", sa.UUID(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "rating >= 1 AND rating <= 5",
            name="ck_entry_reviews_rating_range",
        ),
        sa.CheckConstraint(
            "travel_style IN ('budget', 'luxury', 'adventure', 'family')",
            name="ck_entry_reviews_travel_style",
        ),
        sa.ForeignKeyConstraint(
            ["activity_id"], ["itinerary_activities.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["entry_id"], ["community_entries.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["itinerary_id"], ["itineraries.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("entry_id", "user_id", name="uq_entry_reviews_entry_user"),
    )
    op.create_index(
        op.f("ix_entry_reviews_entry_id"),
        "entry_reviews",
        ["entry_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_entry_reviews_user_id"),
        "entry_reviews",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        "ix_entry_reviews_travel_style",
        "entry_reviews",
        ["travel_style"],
        unique=False,
    )

    op.create_table(
        "entry_review_photos",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("review_id", sa.UUID(), nullable=False),
        sa.Column("url", sa.String(length=2048), nullable=False),
        sa.Column("public_id", sa.String(length=500), nullable=False),
        sa.Column("caption", sa.String(length=500), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["review_id"], ["entry_reviews.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_entry_review_photos_review_id"),
        "entry_review_photos",
        ["review_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        op.f("ix_entry_review_photos_review_id"),
        table_name="entry_review_photos",
    )
    op.drop_table("entry_review_photos")
    op.drop_index("ix_entry_reviews_travel_style", table_name="entry_reviews")
    op.drop_index(op.f("ix_entry_reviews_user_id"), table_name="entry_reviews")
    op.drop_index(op.f("ix_entry_reviews_entry_id"), table_name="entry_reviews")
    op.drop_table("entry_reviews")
