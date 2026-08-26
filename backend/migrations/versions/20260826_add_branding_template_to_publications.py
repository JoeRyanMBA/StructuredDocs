"""Store the branding template selected when a publication is created.

Revision ID: 20260826_add_branding_template_to_publications
Revises: 20260520_add_source_collection_to_publications
Create Date: 2026-08-26
"""

from alembic import op
import sqlalchemy as sa


revision = '20260826_add_branding_template_to_publications'
down_revision = '20260520_add_source_collection_to_publications'
branch_labels = None
depends_on = None


def upgrade():
    inspector = sa.inspect(op.get_bind())
    if 'publications' in inspector.get_table_names() and not any(
        column.get('name') == 'branding_template_name'
        for column in inspector.get_columns('publications')
    ):
        op.add_column('publications', sa.Column('branding_template_name', sa.String(length=120), nullable=True))


def downgrade():
    inspector = sa.inspect(op.get_bind())
    if 'publications' in inspector.get_table_names() and any(
        column.get('name') == 'branding_template_name'
        for column in inspector.get_columns('publications')
    ):
        op.drop_column('publications', 'branding_template_name')