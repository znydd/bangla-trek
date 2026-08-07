"""add email_verified and deleted_at to users

Revision ID: e1a2b3c4d5e6
Revises: 8b351b619903, f3f9e2847c48
Create Date: 2026-08-07 16:05:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e1a2b3c4d5e6'
down_revision: Union[str, Sequence[str], None] = ('8b351b619903', 'f3f9e2847c48', '7e18976465c2')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'users',
        sa.Column('email_verified', sa.Boolean(), server_default=sa.text('false'), nullable=False)
    )
    op.add_column(
        'users',
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True)
    )


def downgrade() -> None:
    op.drop_column('users', 'deleted_at')
    op.drop_column('users', 'email_verified')
