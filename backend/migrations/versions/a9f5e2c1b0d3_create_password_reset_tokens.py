"""create password_reset_tokens table

Revision ID: a9f5e2c1b0d3
Revises: e43f15c67e8b
Create Date: 2025-08-27 19:10:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a9f5e2c1b0d3'
down_revision = 'e43f15c67e8b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'password_reset_tokens',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('token', sa.String(length=64), nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('token_type', sa.Enum('setup', 'reset', name='token_type'), nullable=False, server_default='reset'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('used_at', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('TRUE')),
        sa.Column('created_by_admin', sa.Boolean(), nullable=False, server_default=sa.text('FALSE')),
        sa.UniqueConstraint('token', name='uq_password_reset_tokens_token')
    )
    op.create_index('ix_password_reset_tokens_token', 'password_reset_tokens', ['token'], unique=True)


def downgrade() -> None:
    op.drop_index('ix_password_reset_tokens_token', table_name='password_reset_tokens')
    op.drop_table('password_reset_tokens')
    # Drop enum type on PostgreSQL if desired
    try:
        op.execute("DROP TYPE IF EXISTS token_type")
    except Exception:
        pass
