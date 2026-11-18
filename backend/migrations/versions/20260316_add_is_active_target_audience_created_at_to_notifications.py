"""add is_active, target_audience, created_at to notifications

Revision ID: 20260316_notif_fields
Revises: 
Create Date: 2026-03-16
"""
from alembic import op
import sqlalchemy as sa

revision = '20260316_notif_fields'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    columns = {c['name'] for c in sa.inspect(op.get_bind()).get_columns('notifications')}
    if 'is_active' not in columns:
        op.add_column('notifications', sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'))
    if 'target_audience' not in columns:
        op.add_column('notifications', sa.Column('target_audience', sa.String(64), nullable=True))
    if 'created_at' not in columns:
        op.add_column('notifications', sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.func.now()))


def downgrade():
    op.drop_column('notifications', 'created_at')
    op.drop_column('notifications', 'target_audience')
    op.drop_column('notifications', 'is_active')
