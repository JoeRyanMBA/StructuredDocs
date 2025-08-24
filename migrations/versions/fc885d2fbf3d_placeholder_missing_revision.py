"""placeholder migration to satisfy missing revision fc885d2fbf3d

Revision ID: fc885d2fbf3d
Revises: 32f0391eff6b
Create Date: 2025-08-23 22:40:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fc885d2fbf3d'
down_revision = '32f0391eff6b'
branch_labels = None
depends_on = None


def upgrade():
    # placeholder: no schema changes
    pass


def downgrade():
    # placeholder: no schema changes
    pass
