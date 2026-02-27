"""Add variable substitution tables

Revision ID: add_variables_tables
Revises: b95a3c29dcb3
Create Date: 2025-09-06
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'var_implementation_stub'
down_revision = 'b95a3c29dcb3'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'variables',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(length=120), nullable=False),
        sa.Column('slug', sa.String(length=120), nullable=False, unique=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('scope', sa.Enum('global', 'collection', name='variable_scope_enum'), server_default='global', nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    )

    op.create_table(
        'variable_values',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('variable_id', sa.Integer(), sa.ForeignKey('variables.id', ondelete='CASCADE'), nullable=False),
        sa.Column('value', sa.String(length=500), nullable=False),
        sa.Column('is_default', sa.Boolean(), server_default='0', nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.UniqueConstraint('variable_id', 'value', name='uq_variable_value')
    )

    op.create_table(
        'collection_variable_selections',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('collection_id', sa.Integer(), sa.ForeignKey('collections.id', ondelete='CASCADE'), nullable=False),
        sa.Column('variable_id', sa.Integer(), sa.ForeignKey('variables.id', ondelete='CASCADE'), nullable=False),
        sa.Column('variable_value_id', sa.Integer(), sa.ForeignKey('variable_values.id', ondelete='SET NULL'), nullable=True),
        sa.Column('locked', sa.Boolean(), server_default='0', nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.UniqueConstraint('collection_id', 'variable_id', name='uq_collection_variable')
    )


def downgrade():
    op.drop_table('collection_variable_selections')
    op.drop_table('variable_values')
    op.drop_table('variables')
    op.execute("DROP TYPE IF EXISTS variable_scope_enum")
