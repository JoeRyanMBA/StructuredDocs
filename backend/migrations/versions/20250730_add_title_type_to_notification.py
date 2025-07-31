"""
Add title and type fields to Notification model

Revision ID: 20250730_add_title_type_to_notification
Revises: 6e3967447e3d
Create Date: 2025-07-31 10:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20250730_add_title_type_to_notification'
down_revision = '6e3967447e3d'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('notifications', sa.Column('title', sa.String(length=128), nullable=False, server_default=''))
    op.add_column('notifications', sa.Column('type', sa.String(length=32), nullable=False, server_default='global'))

def downgrade():
    op.drop_column('notifications', 'title')
    op.drop_column('notifications', 'type')
