"""merge nomad_metrics and itinerary branches

Revision ID: 815b1f28c96e
Revises: 6c5f4a1d8e21, afe87c85f3c1
Create Date: 2026-04-10 15:50:11.555022

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '815b1f28c96e'
down_revision: Union[str, Sequence[str], None] = ('6c5f4a1d8e21', 'afe87c85f3c1')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
