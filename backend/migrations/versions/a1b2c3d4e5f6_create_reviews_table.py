"""create reviews table

Revision ID: a1b2c3d4e5f6
Revises: 87eeb4c4233f
Create Date: 2025-08-27 16:10:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '87eeb4c4233f'
branch_labels = None
depends_on = None


def upgrade():
    # Create enums if needed by using sa.Enum in column definitions
    op.create_table(
        'reviews',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('topic_id', sa.Integer(), sa.ForeignKey('topics.id'), nullable=False),
        sa.Column('requested_by', sa.Integer(), sa.ForeignKey('stakeholders.id'), nullable=False),
        sa.Column('reviewer_id', sa.Integer(), sa.ForeignKey('stakeholders.id'), nullable=False),
        sa.Column('status', sa.Enum('pending', 'in_progress', 'completed', 'declined', name='review_status'), nullable=False, server_default='pending'),
        sa.Column('priority', sa.Enum('low', 'medium', 'high', 'urgent', name='review_priority'), nullable=False, server_default='medium'),
        sa.Column('requested_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('due_date', sa.DateTime(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('feedback', sa.Text(), nullable=True),
        sa.Column('recommendation', sa.Enum('approve', 'approve_with_changes', 'reject', 'needs_more_info', name='review_recommendation'), nullable=True),
        sa.Column('review_notes', sa.Text(), nullable=True),
        sa.Column('author_message', sa.Text(), nullable=True),
        sa.Column('edited_content', sa.Text(), nullable=True),
    )


def downgrade():
    op.drop_table('reviews')
