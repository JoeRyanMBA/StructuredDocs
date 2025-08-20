"""add_division_to_stakeholders

Revision ID: 87eeb4c4233f
Revises: b95a3c29dcb3
Create Date: 2025-08-16 14:29:22.793130

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '87eeb4c4233f'
down_revision = 'b95a3c29dcb3'
branch_labels = None
depends_on = None


def upgrade():
    # Add division column to stakeholders table
    op.add_column('stakeholders', sa.Column('division', sa.String(200), nullable=True))


def downgrade():
    # Remove division column from stakeholders table
    op.drop_column('stakeholders', 'division')
