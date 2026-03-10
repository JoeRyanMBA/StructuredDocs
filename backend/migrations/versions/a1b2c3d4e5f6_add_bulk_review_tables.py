"""add bulk review tables

Revision ID: a1b2c3d4e5f6
Revises: f4b8d9a1c2e3
Create Date: 2026-03-10

"""
from alembic import op
import sqlalchemy as sa

revision = 'a1b2c3d4e5f6'
down_revision = 'f4b8d9a1c2e3'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'review_batches',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('requester_id', sa.Integer(), sa.ForeignKey('stakeholders.id'), nullable=True),
        sa.Column('reviewer_id', sa.Integer(), sa.ForeignKey('stakeholders.id'), nullable=False),
        sa.Column('priority', sa.Enum('low', 'medium', 'high', 'urgent', name='review_batch_priority'), nullable=False, server_default='medium'),
        sa.Column('due_date', sa.DateTime(), nullable=True),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('status', sa.Enum('pending', 'in_progress', 'completed', name='review_batch_status'), nullable=False, server_default='pending'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('email_delivery_unavailable', sa.Boolean(), nullable=False, server_default='0'),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'review_batch_tokens',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('token', sa.String(64), nullable=False),
        sa.Column('batch_id', sa.Integer(), sa.ForeignKey('review_batches.id'), nullable=False),
        sa.Column('reviewer_email', sa.String(120), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('accessed_at', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('access_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('max_access_count', sa.Integer(), nullable=False, server_default='100'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('token'),
    )
    op.create_index('ix_review_batch_tokens_token', 'review_batch_tokens', ['token'])

    op.add_column('reviews', sa.Column('batch_id', sa.Integer(), sa.ForeignKey('review_batches.id'), nullable=True))
    op.add_column('reviews', sa.Column('batch_position', sa.Integer(), nullable=True))
    op.create_index('ix_reviews_batch_id', 'reviews', ['batch_id'])


def downgrade():
    op.drop_index('ix_reviews_batch_id', table_name='reviews')
    op.drop_column('reviews', 'batch_position')
    op.drop_column('reviews', 'batch_id')
    op.drop_index('ix_review_batch_tokens_token', table_name='review_batch_tokens')
    op.drop_table('review_batch_tokens')
    op.drop_table('review_batches')
