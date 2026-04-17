"""add emergency facilities

Revision ID: c3a9d2e5f108
Revises: 944fb5489856
Create Date: 2026-04-17 12:53:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c3a9d2e5f108'
down_revision: Union[str, Sequence[str], None] = '944fb5489856'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('emergency_facilities',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('facility_type', sa.String(length=30), nullable=False),
        sa.Column('address', sa.Text(), nullable=False),
        sa.Column('district', sa.String(length=100), nullable=False),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.Column('phone_number', sa.String(length=50), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_emergency_facilities_facility_type'), 'emergency_facilities', ['facility_type'], unique=False)
    op.create_index(op.f('ix_emergency_facilities_district'), 'emergency_facilities', ['district'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_emergency_facilities_district'), table_name='emergency_facilities')
    op.drop_index(op.f('ix_emergency_facilities_facility_type'), table_name='emergency_facilities')
    op.drop_table('emergency_facilities')
