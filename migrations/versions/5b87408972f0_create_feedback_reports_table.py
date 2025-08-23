"""create feedback_reports table

Revision ID: 5b87408972f0
Revises: 
Create Date: 2025-08-23 21:22:24.709523

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5b87408972f0'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
       # Create feedback_reports table
       op.create_table(
              'feedback_reports',
              sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
              sa.Column('report_type', sa.String(length=32), nullable=False, server_default=sa.text("'other'")),
              sa.Column('page', sa.String(length=256), nullable=True),
              sa.Column('component', sa.String(length=256), nullable=True),
              sa.Column('user_contact', sa.String(length=256), nullable=True),
              sa.Column('message', sa.Text(), nullable=False),
              sa.Column('metadata_json', sa.Text(), nullable=True),
              sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
       )


def downgrade():
       # Drop feedback_reports table
       op.drop_table('feedback_reports')
