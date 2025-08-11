
"""add created_at and updated_at to collections"""

revision = '20250810_add_collection_timestamps'
down_revision = 'f2f2c9b34aae'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa

def upgrade():
    import datetime
    op.add_column('collections', sa.Column('created_at', sa.DateTime(), nullable=True))
    op.add_column('collections', sa.Column('updated_at', sa.DateTime(), nullable=True))
    # Set current timestamp for all existing rows
    now = datetime.datetime.utcnow().isoformat(sep=' ', timespec='seconds')
    op.execute(f"UPDATE collections SET created_at = '{now}', updated_at = '{now}'")
    # Make columns non-nullable
    with op.batch_alter_table('collections') as batch_op:
        batch_op.alter_column('created_at', nullable=False)
        batch_op.alter_column('updated_at', nullable=False)

def downgrade():
    op.drop_column('collections', 'created_at')
    op.drop_column('collections', 'updated_at')
