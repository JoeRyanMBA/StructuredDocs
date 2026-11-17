"""Add import_links table

Revision ID: add_import_links_20251004
Revises: add_archived_projects_20250930
Create Date: 2025-10-04
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_import_links_20251004'
down_revision = 'add_archived_projects_20250930'
branch_labels = None
depends_on = None

def upgrade():
    if sa.inspect(op.get_bind()).has_table('import_links'):
        return
    # Create import_links table
    link_type = sa.Enum('form', 'document', 'website', 'policy', 'procedure', 'regulation', 'other', name='link_type_enum')
    if op.get_bind().dialect.name == 'postgresql':
        from sqlalchemy.dialects.postgresql import ENUM
        link_type = ENUM(*link_type.enums, name=link_type.name, create_type=False)
        link_type.create(op.get_bind(), checkfirst=True)
    op.create_table('import_links',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('document_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('url', sa.String(length=512), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('link_type', link_type, nullable=False),
        sa.Column('is_internal', sa.Boolean(), nullable=False),
        sa.Column('context', sa.Text(), nullable=True),
        sa.Column('position_in_document', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['document_id'], ['import_documents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('import_links')