"""add description to tags

Revision ID: d6e7f8a3b4c5
Revises: d5e6f7a2b3c4
Create Date: 2026-03-12 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'd6e7f8a3b4c5'
down_revision = 'd5e6f7a2b3c4'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    cols = [c['name'] for c in inspector.get_columns('tags')]
    if 'description' not in cols:
        op.add_column('tags', sa.Column('description', sa.Text(), nullable=True))


def downgrade():
    op.drop_column('tags', 'description')
