"""add audit_logs table

Revision ID: d4e5f6a1b2c3
Revises: f4b8d9a1c2e3
Create Date: 2025-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'd4e5f6a1b2c3'
down_revision = 'f4b8d9a1c2e3'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if 'audit_logs' not in inspector.get_table_names():
        op.create_table(
            'audit_logs',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
            sa.Column('action', sa.String(50), nullable=False),
            sa.Column('resource_type', sa.String(100), nullable=False),
            sa.Column('resource_id', sa.Integer(), nullable=True),
            sa.Column('details', sa.Text(), nullable=True),
            sa.Column('ip_address', sa.String(45), nullable=True),
            sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        )
        op.create_index('ix_audit_logs_user_id', 'audit_logs', ['user_id'])
        op.create_index('ix_audit_logs_resource', 'audit_logs', ['resource_type', 'resource_id'])
        op.create_index('ix_audit_logs_created_at', 'audit_logs', ['created_at'])


def downgrade():
    op.drop_index('ix_audit_logs_created_at', 'audit_logs')
    op.drop_index('ix_audit_logs_resource', 'audit_logs')
    op.drop_index('ix_audit_logs_user_id', 'audit_logs')
    op.drop_table('audit_logs')
