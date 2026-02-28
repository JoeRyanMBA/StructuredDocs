"""add snippets table

Revision ID: a1b2c3d4e5f7
Revises: var_implementation_stub
Create Date: 2026-02-28

"""
from alembic import op
import sqlalchemy as sa

revision = 'a1b2c3d4e5f7'
down_revision = 'var_implementation_stub'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'snippets',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )


def downgrade():
    op.drop_table('snippets')
