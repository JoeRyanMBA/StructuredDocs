"""Add archived column to projects

Revision ID: add_archived_projects_20250930
Revises: b95a3c29dcb3
Create Date: 2025-09-30
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_archived_projects_20250930'
down_revision = 'b95a3c29dcb3'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('projects', sa.Column('archived', sa.Boolean(), nullable=False, server_default='0'))
    # Ensure existing rows default
    op.execute("UPDATE projects SET archived = 0 WHERE archived IS NULL;")


def downgrade():
    op.drop_column('projects', 'archived')
