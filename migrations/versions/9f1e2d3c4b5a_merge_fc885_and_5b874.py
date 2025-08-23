"""merge fc885d2fbf3d and 5b87408972f0

Revision ID: 9f1e2d3c4b5a
Revises: fc885d2fbf3d,5b87408972f0
Create Date: 2025-08-23 22:55:00.000000

This is a no-op merge migration created to reconcile parallel heads so Alembic
can produce a single linear history on the server. It intentionally performs
no schema changes.
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '9f1e2d3c4b5a'
down_revision = ('fc885d2fbf3d', '5b87408972f0')
branch_labels = None
depends_on = None


def upgrade():
    # no schema changes; this migration merges two heads
    pass


def downgrade():
    # no-op downgrade
    pass
