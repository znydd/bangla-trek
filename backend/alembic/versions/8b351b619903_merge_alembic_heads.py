"""merge alembic heads

Revision ID: 8b351b619903
Revises: add_buddy_matches_table, b1e4f3a7c902, c3a9d2e5f108
Create Date: 2026-04-17 15:26:40.088021

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8b351b619903'
down_revision: Union[str, Sequence[str], None] = ('add_buddy_matches_table', 'b1e4f3a7c902', 'c3a9d2e5f108')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
