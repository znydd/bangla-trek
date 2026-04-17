"""dummy for missing rev

Revision ID: 7dde0de54c51
Revises: afe87c85f3c1
Create Date: 2026-04-10 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "7dde0de54c51"
down_revision: Union[str, None] = "afe87c85f3c1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    pass

def downgrade() -> None:
    pass
