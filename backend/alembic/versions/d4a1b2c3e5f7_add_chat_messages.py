"""add chat_messages table

Revision ID: d4a1b2c3e5f7
Revises: f3f9e2847c48
Create Date: 2026-04-17 19:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "d4a1b2c3e5f7"
down_revision: Union[str, Sequence[str], None] = ("f3f9e2847c48", "add_buddy_matches_table", "b1e4f3a7c902", "c3a9d2e5f108")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "chat_messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "itinerary_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("itineraries.id", ondelete="CASCADE"),
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
        sa.Column("role", sa.String(10), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )


def downgrade() -> None:
    op.drop_table("chat_messages")
