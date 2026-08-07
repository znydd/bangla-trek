"""create travel_trips tables

Revision ID: f4a5b6c7d8e9
Revises: f3a4b5c6d7e8
Create Date: 2026-08-07 16:51:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'f4a5b6c7d8e9'
down_revision: Union[str, Sequence[str], None] = 'f3a4b5c6d7e8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. travel_trips
    op.create_table(
        'travel_trips',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('creator_id', sa.UUID(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('origin', sa.String(length=255), nullable=False),
        sa.Column('destination', sa.String(length=255), nullable=False),
        sa.Column('start_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('meeting_point', sa.String(length=255), nullable=True),
        sa.Column('transport', sa.String(length=100), nullable=True),
        sa.Column('estimated_cost_min_bdt', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('estimated_cost_max_bdt', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('itinerary', sa.Text(), nullable=True),
        sa.Column('max_members', sa.Integer(), server_default='5', nullable=False),
        sa.Column('communication_platform', sa.String(length=50), nullable=True),
        sa.Column('communication_note', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), server_default='scheduled', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['creator_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_travel_trips_creator_id', 'travel_trips', ['creator_id'], unique=False)
    op.create_index('ix_travel_trips_origin', 'travel_trips', ['origin'], unique=False)
    op.create_index('ix_travel_trips_destination', 'travel_trips', ['destination'], unique=False)
    op.create_index('ix_travel_trips_status', 'travel_trips', ['status'], unique=False)
    op.create_index('ix_travel_trips_status_dates', 'travel_trips', ['status', 'start_at'], unique=False)

    # 2. travel_trip_requirements
    op.create_table(
        'travel_trip_requirements',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('trip_id', sa.UUID(), nullable=False),
        sa.Column('requirement', sa.String(length=255), nullable=False),
        sa.Column('sort_order', sa.Integer(), server_default='0', nullable=False),
        sa.ForeignKeyConstraint(['trip_id'], ['travel_trips.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_travel_trip_requirements_trip_id', 'travel_trip_requirements', ['trip_id'], unique=False)

    # 3. travel_trip_members
    op.create_table(
        'travel_trip_members',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('trip_id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('role', sa.String(length=20), server_default='member', nullable=False),
        sa.Column('status', sa.String(length=20), server_default='joined', nullable=False),
        sa.Column('joined_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('left_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['trip_id'], ['travel_trips.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('trip_id', 'user_id', name='uq_travel_trip_members_trip_user')
    )
    op.create_index('ix_travel_trip_members_trip_id', 'travel_trip_members', ['trip_id'], unique=False)
    op.create_index('ix_travel_trip_members_user_id', 'travel_trip_members', ['user_id'], unique=False)
    op.create_index('ix_travel_trip_members_user_status', 'travel_trip_members', ['user_id', 'status'], unique=False)


def downgrade() -> None:
    op.drop_table('travel_trip_members')
    op.drop_table('travel_trip_requirements')
    op.drop_table('travel_trips')
