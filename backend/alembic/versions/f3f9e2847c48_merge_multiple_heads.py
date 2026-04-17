"""merge multiple heads

Revision ID: f3f9e2847c48
Revises: 6ec4420a4f83, 944fb5489856
Create Date: 2026-04-16 20:35:17.616763

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f3f9e2847c48'
down_revision: Union[str, Sequence[str], None] = ('6ec4420a4f83', '944fb5489856')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
