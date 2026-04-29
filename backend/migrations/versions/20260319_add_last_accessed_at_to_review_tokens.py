"""add last_accessed_at to review_tokens and review_batch_tokens

Revision ID: 20260319_last_accessed_at
Revises: 20260316_add_last_seen_to_users, 20260316_notif_fields, add_form_number_to_publications, 20251209_fix_project_stakeholder_role_enum, add_import_links_20251004, 20250906_add_publicationnode_snapshots, a1b2c3d4e5f7, a9f5e2c1b0d3, c3d4e5f6a7b8, d6e7f8a3b4c5
Create Date: 2026-03-19 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260319_last_accessed_at'
down_revision = (
    '20260316_add_last_seen_to_users',
    '20260316_notif_fields',
    'add_form_number_to_publications',
    '20251209_fix_project_stakeholder_role_enum',
    'add_import_links_20251004',
    '20250906_add_publicationnode_snapshots',
    'a1b2c3d4e5f7',
    'a9f5e2c1b0d3',
    'c3d4e5f6a7b8',
    'd6e7f8a3b4c5',
)
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'review_tokens',
        sa.Column('last_accessed_at', sa.DateTime(), nullable=True)
    )
    op.add_column(
        'review_batch_tokens',
        sa.Column('last_accessed_at', sa.DateTime(), nullable=True)
    )


def downgrade():
    op.drop_column('review_tokens', 'last_accessed_at')
    op.drop_column('review_batch_tokens', 'last_accessed_at')
