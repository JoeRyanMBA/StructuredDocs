"""Merge migration heads

Revision ID: d6b286130912
Revises: 16afd4356602, 8c13f0f5bd21
Create Date: 2025-07-29 19:37:10.834741

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd6b286130912'
down_revision = ('16afd4356602', '8c13f0f5bd21')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
