"""add transit blueprints

Revision ID: b1e4f3a7c902
Revises: 944fb5489856
Create Date: 2026-04-17 01:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b1e4f3a7c902'
down_revision: Union[str, Sequence[str], None] = '944fb5489856'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('transit_blueprints',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('origin', sa.String(length=255), nullable=False),
        sa.Column('destination', sa.String(length=255), nullable=False),
        sa.Column('raw_description', sa.Text(), nullable=False),
        sa.Column('estimated_duration_mins', sa.Integer(), nullable=True),
        sa.Column('estimated_cost_bdt', sa.Float(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_transit_blueprints_user_id'), 'transit_blueprints', ['user_id'], unique=False)

    op.create_table('transit_blueprint_steps',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('blueprint_id', sa.UUID(), nullable=False),
        sa.Column('step_number', sa.Integer(), nullable=False),
        sa.Column('instruction', sa.Text(), nullable=False),
        sa.Column('mode', sa.String(length=30), nullable=False),
        sa.Column('estimated_duration_mins', sa.Integer(), nullable=True),
        sa.Column('estimated_cost_bdt', sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(['blueprint_id'], ['transit_blueprints.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_transit_blueprint_steps_blueprint_id'), 'transit_blueprint_steps', ['blueprint_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_transit_blueprint_steps_blueprint_id'), table_name='transit_blueprint_steps')
    op.drop_table('transit_blueprint_steps')
    op.drop_index(op.f('ix_transit_blueprints_user_id'), table_name='transit_blueprints')
    op.drop_table('transit_blueprints')
