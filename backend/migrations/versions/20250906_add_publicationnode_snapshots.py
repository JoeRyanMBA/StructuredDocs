"""
Add title_snapshot and content_snapshot to publication_nodes for variable substitution snapshot
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20250906_add_publicationnode_snapshots'
down_revision = 'var_implementation_stub'
branch_labels = None
depends_on = None

def upgrade():
    columns = {c['name'] for c in sa.inspect(op.get_bind()).get_columns('publication_nodes')}
    if 'title_snapshot' not in columns:
        op.add_column('publication_nodes', sa.Column('title_snapshot', sa.String(length=200), nullable=True))
    if 'content_snapshot' not in columns:
        op.add_column('publication_nodes', sa.Column('content_snapshot', sa.Text(), nullable=True))

def downgrade():
    op.drop_column('publication_nodes', 'title_snapshot')
    op.drop_column('publication_nodes', 'content_snapshot')
