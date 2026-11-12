"""Remove the unused scope option from variable definitions.

Revision ID: 20261112_remove_variable_scope
Revises: 20260319_last_accessed_at, 20260826_add_branding_template_to_publications
Create Date: 2026-11-12
"""
from alembic import op
import sqlalchemy as sa


revision = '20261112_remove_variable_scope'
down_revision = (
    '20260319_last_accessed_at',
    '20260826_add_branding_template_to_publications',
)
branch_labels = None
depends_on = None


def upgrade():
    inspector = sa.inspect(op.get_bind())
    if 'variables' in inspector.get_table_names() and any(
        column.get('name') == 'scope'
        for column in inspector.get_columns('variables')
    ):
        op.drop_column('variables', 'scope')
        if op.get_bind().dialect.name == 'postgresql':
            op.execute('DROP TYPE IF EXISTS variable_scope_enum')


def downgrade():
    inspector = sa.inspect(op.get_bind())
    if 'variables' in inspector.get_table_names() and not any(
        column.get('name') == 'scope'
        for column in inspector.get_columns('variables')
    ):
        op.add_column(
            'variables',
            sa.Column(
                'scope',
                sa.Enum('global', 'collection', name='variable_scope_enum'),
                server_default='global',
                nullable=False,
            ),
        )
