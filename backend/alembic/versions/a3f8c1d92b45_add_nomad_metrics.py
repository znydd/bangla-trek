"""add nomad metrics

Revision ID: a3f8c1d92b45
Revises: 561d3d12166a
Create Date: 2026-03-28 02:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'a3f8c1d92b45'
down_revision: Union[str, Sequence[str], None] = '561d3d12166a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('nomad_metrics',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('entry_id', sa.UUID(), nullable=False),
    sa.Column('carrier', sa.String(length=50), nullable=False),
    sa.Column('signal_strength', sa.String(length=20), nullable=False),
    sa.Column('safety_rating', sa.Integer(), nullable=False),
    sa.Column('bkash_available', sa.Boolean(), nullable=False),
    sa.Column('submitted_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['entry_id'], ['community_entries.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_nomad_metrics_entry_id'), 'nomad_metrics', ['entry_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_nomad_metrics_entry_id'), table_name='nomad_metrics')
    op.drop_table('nomad_metrics')
