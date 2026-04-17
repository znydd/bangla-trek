"""add transit fare contributions

Revision ID: 9f71b3e6aa10
Revises: 2d9b7c0f4a61
Create Date: 2026-04-17 18:05:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9f71b3e6aa10"
down_revision: Union[str, Sequence[str], None] = "2d9b7c0f4a61"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "transit_fare_contributions",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("origin", sa.String(length=255), nullable=False),
        sa.Column("destination", sa.String(length=255), nullable=False),
        sa.Column("mode", sa.String(length=20), nullable=False),
        sa.Column("fare_bdt", sa.Float(), nullable=False),
        sa.Column("min_fare_bdt", sa.Float(), nullable=True),
        sa.Column("max_fare_bdt", sa.Float(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("source_type", sa.String(length=20), nullable=False),
        sa.Column("travel_date", sa.Date(), nullable=True),
        sa.Column(
            "submitted_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("fare_bdt >= 0", name="ck_transit_fares_fare_non_negative"),
        sa.CheckConstraint(
            "(min_fare_bdt IS NULL OR min_fare_bdt >= 0)",
            name="ck_transit_fares_min_non_negative",
        ),
        sa.CheckConstraint(
            "(max_fare_bdt IS NULL OR max_fare_bdt >= 0)",
            name="ck_transit_fares_max_non_negative",
        ),
        sa.CheckConstraint(
            "(min_fare_bdt IS NULL OR max_fare_bdt IS NULL OR min_fare_bdt <= max_fare_bdt)",
            name="ck_transit_fares_min_lte_max",
        ),
        sa.CheckConstraint(
            "mode IN ('cng', 'bus', 'train')",
            name="ck_transit_fares_mode",
        ),
        sa.CheckConstraint(
            "source_type IN ('observed', 'quoted', 'booked')",
            name="ck_transit_fares_source_type",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_transit_fare_contributions_user_id"),
        "transit_fare_contributions",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_transit_fare_contributions_submitted_at"),
        "transit_fare_contributions",
        ["submitted_at"],
        unique=False,
    )
    op.create_index(
        "ix_transit_fares_route_mode_submitted",
        "transit_fare_contributions",
        ["origin", "destination", "mode", "submitted_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_transit_fares_route_mode_submitted",
        table_name="transit_fare_contributions",
    )
    op.drop_index(
        op.f("ix_transit_fare_contributions_submitted_at"),
        table_name="transit_fare_contributions",
    )
    op.drop_index(
        op.f("ix_transit_fare_contributions_user_id"),
        table_name="transit_fare_contributions",
    )
    op.drop_table("transit_fare_contributions")
