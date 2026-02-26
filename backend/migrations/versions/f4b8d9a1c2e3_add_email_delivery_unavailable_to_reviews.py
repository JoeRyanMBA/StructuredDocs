"""add email_delivery_unavailable to reviews

Revision ID: f4b8d9a1c2e3
Revises: ceac11c5e665
Create Date: 2026-02-26 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f4b8d9a1c2e3'
down_revision = 'ceac11c5e665'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'reviews',
        sa.Column('email_delivery_unavailable', sa.Boolean(), nullable=False, server_default=sa.text('0'))
    )


def downgrade():
    op.drop_column('reviews', 'email_delivery_unavailable')
