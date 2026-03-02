"""Add form_number to publications

Revision ID: add_form_number_to_publications
Revises: e5f6a1b2c3d4
Create Date: 2026-03-02
"""
from alembic import op
import sqlalchemy as sa

revision = 'add_form_number_to_publications'
down_revision = 'e5f6a1b2c3d4'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('publications', sa.Column('form_number', sa.String(length=100), nullable=True))


def downgrade():
    op.drop_column('publications', 'form_number')
