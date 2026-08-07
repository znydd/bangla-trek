"""create places and reviews tables

Revision ID: f1a2b3c4d5e6
Revises: e1a2b3c4d5e6
Create Date: 2026-08-07 16:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'f1a2b3c4d5e6'
down_revision: Union[str, Sequence[str], None] = 'e1a2b3c4d5e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Places table
    op.create_table(
        'places',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('slug', sa.String(length=255), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('normalized_name', sa.String(length=255), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('summary', sa.String(length=500), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('source_type', sa.String(length=20), server_default='community', nullable=False),
        sa.Column('status', sa.String(length=20), server_default='draft', nullable=False),
        sa.Column('created_by', sa.UUID(), nullable=True),
        sa.Column('approved_by', sa.UUID(), nullable=True),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('duplicate_of_place_id', sa.UUID(), nullable=True),
        sa.Column('village', sa.String(length=255), nullable=True),
        sa.Column('upazila', sa.String(length=255), nullable=True),
        sa.Column('district', sa.String(length=255), nullable=True),
        sa.Column('division', sa.String(length=255), nullable=True),
        sa.Column('nearest_hub', sa.String(length=255), nullable=True),
        sa.Column('latitude', sa.Float(), nullable=True),
        sa.Column('longitude', sa.Float(), nullable=True),
        sa.Column('best_season', sa.String(length=255), nullable=True),
        sa.Column('suggested_duration', sa.String(length=255), nullable=True),
        sa.Column('guide_requirement', sa.String(length=255), nullable=True),
        sa.Column('budget_min_bdt', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('budget_max_bdt', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('highlights', postgresql.ARRAY(sa.String()), server_default='{}', nullable=False),
        sa.Column('know_before_you_go', postgresql.ARRAY(sa.String()), server_default='{}', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['approved_by'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['duplicate_of_place_id'], ['places.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_places_slug', 'places', ['slug'], unique=True)
    op.create_index('ix_places_status', 'places', ['status'], unique=False)
    op.create_index('ix_places_category', 'places', ['category'], unique=False)
    op.create_index('ix_places_normalized_name', 'places', ['normalized_name'], unique=False)
    op.create_index('ix_places_upazila', 'places', ['upazila'], unique=False)
    op.create_index('ix_places_district', 'places', ['district'], unique=False)
    op.create_index('ix_places_status_category', 'places', ['status', 'category'], unique=False)
    op.create_index('ix_places_district_upazila', 'places', ['district', 'upazila'], unique=False)

    # 2. Place Aliases
    op.create_table(
        'place_aliases',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('place_id', sa.UUID(), nullable=False),
        sa.Column('alias', sa.String(length=255), nullable=False),
        sa.Column('normalized_alias', sa.String(length=255), nullable=False),
        sa.ForeignKeyConstraint(['place_id'], ['places.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_place_aliases_place_id', 'place_aliases', ['place_id'], unique=False)
    op.create_index('ix_place_aliases_normalized_alias', 'place_aliases', ['normalized_alias'], unique=False)

    # 3. Place Tags
    op.create_table(
        'place_tags',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('place_id', sa.UUID(), nullable=False),
        sa.Column('tag', sa.String(length=50), nullable=False),
        sa.ForeignKeyConstraint(['place_id'], ['places.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_place_tags_place_id', 'place_tags', ['place_id'], unique=False)
    op.create_index('ix_place_tags_tag', 'place_tags', ['tag'], unique=False)

    # 4. Place Media
    op.create_table(
        'place_media',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('place_id', sa.UUID(), nullable=False),
        sa.Column('uploaded_by', sa.UUID(), nullable=True),
        sa.Column('media_type', sa.String(length=20), nullable=False),
        sa.Column('url', sa.String(length=2048), nullable=False),
        sa.Column('storage_public_id', sa.String(length=255), nullable=True),
        sa.Column('platform', sa.String(length=50), nullable=True),
        sa.Column('caption', sa.String(length=500), nullable=True),
        sa.Column('sort_order', sa.Integer(), server_default='0', nullable=False),
        sa.Column('moderation_status', sa.String(length=20), server_default='approved', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['place_id'], ['places.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['uploaded_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_place_media_place_id', 'place_media', ['place_id'], unique=False)

    # 5. Reviews
    op.create_table(
        'reviews',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('place_id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('status', sa.String(length=20), server_default='published', nullable=False),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.Column('visited_on', sa.Date(), nullable=False),
        sa.Column('travel_style', sa.String(length=50), nullable=True),
        sa.Column('group_type', sa.String(length=50), nullable=True),
        sa.Column('group_size', sa.Integer(), nullable=True),
        sa.Column('starting_location', sa.String(length=255), nullable=True),
        sa.Column('actual_cost_bdt', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('title', sa.String(length=255), nullable=True),
        sa.Column('travel_guide', sa.Text(), nullable=True),
        sa.Column('crowd_level', sa.String(length=50), nullable=True),
        sa.Column('access_difficulty', sa.String(length=50), nullable=True),
        sa.Column('road_condition', sa.String(length=50), nullable=True),
        sa.Column('safety', sa.String(length=50), nullable=True),
        sa.Column('cleanliness', sa.String(length=50), nullable=True),
        sa.Column('mobile_carrier', sa.String(length=50), nullable=True),
        sa.Column('strongest_network', sa.String(length=50), nullable=True),
        sa.Column('network_reliability', sa.String(length=50), nullable=True),
        sa.Column('helpful_count', sa.Integer(), server_default='0', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint('rating >= 1 AND rating <= 5', name='ck_reviews_rating_range'),
        sa.ForeignKeyConstraint(['place_id'], ['places.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('place_id', 'user_id', 'visited_on', name='uq_reviews_place_user_visit')
    )
    op.create_index('ix_reviews_place_id', 'reviews', ['place_id'], unique=False)
    op.create_index('ix_reviews_user_id', 'reviews', ['user_id'], unique=False)
    op.create_index('ix_reviews_status', 'reviews', ['status'], unique=False)
    op.create_index('ix_reviews_place_status', 'reviews', ['place_id', 'status'], unique=False)
    op.create_index('ix_reviews_user_status', 'reviews', ['user_id', 'status'], unique=False)

    # 6. Review Payment Methods
    op.create_table(
        'review_payment_methods',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('review_id', sa.UUID(), nullable=False),
        sa.Column('payment_method', sa.String(length=50), nullable=False),
        sa.ForeignKeyConstraint(['review_id'], ['reviews.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('review_id', 'payment_method', name='uq_review_payment_methods')
    )
    op.create_index('ix_review_payment_methods_review_id', 'review_payment_methods', ['review_id'], unique=False)

    # 7. Review Media
    op.create_table(
        'review_media',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('review_id', sa.UUID(), nullable=False),
        sa.Column('media_type', sa.String(length=20), nullable=False),
        sa.Column('url', sa.String(length=2048), nullable=False),
        sa.Column('storage_public_id', sa.String(length=255), nullable=True),
        sa.Column('platform', sa.String(length=50), nullable=True),
        sa.Column('caption', sa.String(length=500), nullable=True),
        sa.Column('sort_order', sa.Integer(), server_default='0', nullable=False),
        sa.Column('moderation_status', sa.String(length=20), server_default='published', nullable=False),
        sa.ForeignKeyConstraint(['review_id'], ['reviews.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_review_media_review_id', 'review_media', ['review_id'], unique=False)

    # 8. Review Helpful Votes
    op.create_table(
        'review_helpful_votes',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('review_id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['review_id'], ['reviews.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('review_id', 'user_id', name='uq_review_helpful_votes_review_user')
    )
    op.create_index('ix_review_helpful_votes_review_id', 'review_helpful_votes', ['review_id'], unique=False)
    op.create_index('ix_review_helpful_votes_user_id', 'review_helpful_votes', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_table('review_helpful_votes')
    op.drop_table('review_media')
    op.drop_table('review_payment_methods')
    op.drop_table('reviews')
    op.drop_table('place_media')
    op.drop_table('place_tags')
    op.drop_table('place_aliases')
    op.drop_table('places')
