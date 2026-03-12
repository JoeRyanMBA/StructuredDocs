"""add description to tags

Revision ID: a1b2c3d4e5f6
Revises: f4b8d9a1c2e3
Create Date: 2026-03-12 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'a1b2c3d4e5f6'
down_revision = 'f4b8d9a1c2e3'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('tags', sa.Column('description', sa.Text(), nullable=True))


def downgrade():
    op.drop_column('tags', 'description')
