"""add last_seen to users

Revision ID: 20260316_add_last_seen_to_users
Revises:
Create Date: 2026-03-16
"""
from alembic import op
import sqlalchemy as sa

revision = '20260316_add_last_seen_to_users'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    columns = {c['name'] for c in sa.inspect(op.get_bind()).get_columns('users')}
    if 'last_seen' not in columns:
        op.add_column('users', sa.Column('last_seen', sa.DateTime(), nullable=True))


def downgrade():
    op.drop_column('users', 'last_seen')
