"""Fix project_stakeholder role enum collision

Revision ID: 20251209_fix_project_stakeholder_role_enum
Revises: f1e2d3c4b5a6
Create Date: 2025-12-09 15:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20251209_fix_project_stakeholder_role_enum'
down_revision = 'f1e2d3c4b5a6'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    dialect = bind.dialect.name

    if dialect == 'postgresql':
        # Create new enum with distinct name
        op.execute("""
            DO $$ BEGIN
                CREATE TYPE project_stakeholder_role AS ENUM ('project_manager', 'subject_matter_expert', 'reviewer', 'stakeholder', 'sponsor');
            EXCEPTION
                WHEN duplicate_object THEN null;
            END $$;
        """)
        
        # Alter the project_stakeholders.role column to use the new enum
        op.execute("""
            ALTER TABLE project_stakeholders 
            ALTER COLUMN role TYPE project_stakeholder_role 
            USING role::text::project_stakeholder_role;
        """)
        
        # Drop the old enum constraint if it's not used by stakeholders anymore
        # Note: We can't drop it yet because it's still used by stakeholders table


def downgrade():
    # This is a one-way migration - downgrade would require manual intervention
    pass
