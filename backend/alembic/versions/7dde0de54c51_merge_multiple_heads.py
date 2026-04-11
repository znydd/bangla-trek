"""merge multiple heads

Revision ID: 7dde0de54c51
Revises: 6ec4420a4f83, 944fb5489856
Create Date: 2026-04-11 07:00:53.548882

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7dde0de54c51'
down_revision: Union[str, Sequence[str], None] = ('6ec4420a4f83', '944fb5489856')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
