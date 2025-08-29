"""add role and can_review to stakeholders

Revision ID: f1e2d3c4b5a6
Revises: 07f342e56ae5
Create Date: 2025-08-27 16:45:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f1e2d3c4b5a6'
down_revision = '07f342e56ae5'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    dialect = bind.dialect.name

    # Add can_review first (simple boolean)
    op.add_column('stakeholders', sa.Column('can_review', sa.Boolean(), nullable=False, server_default='1'))

    # Add role column; on Postgres reuse existing enum type "stakeholder_role" created by project_stakeholders
    if dialect == 'postgresql':
        from sqlalchemy.dialects import postgresql
        role_enum = postgresql.ENUM(name='stakeholder_role', create_type=False)
        op.add_column('stakeholders', sa.Column('role', role_enum, nullable=False, server_default='stakeholder'))
    else:
        # Fallback generic enum/string for SQLite or others
        op.add_column(
            'stakeholders',
            sa.Column(
                'role',
                sa.Enum('author', 'reviewer', 'subject_matter_expert', 'stakeholder', 'admin', name='stakeholder_role'),
                nullable=False,
                server_default='stakeholder'
            )
        )


def downgrade():
    # Drop role then can_review
    op.drop_column('stakeholders', 'role')
    op.drop_column('stakeholders', 'can_review')
