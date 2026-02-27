"""add entity_tags table

Revision ID: a1b2c3d4e5f6
Revises: f4b8d9a1c2e3
Create Date: 2026-02-27

"""
from alembic import op
import sqlalchemy as sa

revision = 'a1b2c3d4e5f6'
down_revision = 'f4b8d9a1c2e3'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'entity_tags',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('entity_type', sa.String(50), nullable=False),
        sa.Column('entity_id', sa.Integer(), nullable=False),
        sa.Column('tag_id', sa.Integer(), sa.ForeignKey('tags.id', ondelete='CASCADE'), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint('entity_type', 'entity_id', 'tag_id', name='uq_entity_tag'),
    )
    op.create_index('ix_entity_tags_lookup', 'entity_tags', ['entity_type', 'entity_id'])


def downgrade():
    op.drop_index('ix_entity_tags_lookup', table_name='entity_tags')
    op.drop_table('entity_tags')
