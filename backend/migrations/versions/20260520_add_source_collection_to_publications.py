"""Add source_collection_id to publications.

Revision ID: 20260520_add_source_collection_to_publications
Revises: 20260504_fix_missing_review_sequence_created_by
Create Date: 2026-05-20
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260520_add_source_collection_to_publications'
down_revision = '20260504_fix_missing_review_sequence_created_by'
branch_labels = None
depends_on = None


def _has_column(inspector, table_name, column_name):
    return any(col.get('name') == column_name for col in inspector.get_columns(table_name))


def _has_fk_on_column(inspector, table_name, column_name):
    for fk in inspector.get_foreign_keys(table_name):
        constrained = fk.get('constrained_columns') or []
        if column_name in constrained:
            return True
    return False


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if 'publications' not in inspector.get_table_names():
        return

    if not _has_column(inspector, 'publications', 'source_collection_id'):
        op.add_column('publications', sa.Column('source_collection_id', sa.Integer(), nullable=True))

    # Backfill using current publish convention: publication.title == collection.name.
    op.execute(
        """
        UPDATE publications
        SET source_collection_id = (
          SELECT c.id
          FROM collections c
          WHERE c.name = publications.title
          ORDER BY c.id ASC
          LIMIT 1
        )
        WHERE source_collection_id IS NULL
        """
    )

    inspector = sa.inspect(bind)
    if _has_column(inspector, 'publications', 'source_collection_id') and not _has_fk_on_column(inspector, 'publications', 'source_collection_id'):
        try:
            op.create_foreign_key(
                'fk_publications_source_collection_id',
                'publications',
                'collections',
                ['source_collection_id'],
                ['id'],
                ondelete='SET NULL'
            )
        except Exception:
            # Keep migration non-destructive on environments with nonstandard constraints.
            pass


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if 'publications' not in inspector.get_table_names():
        return

    if _has_column(inspector, 'publications', 'source_collection_id'):
        for fk in inspector.get_foreign_keys('publications'):
            constrained = fk.get('constrained_columns') or []
            if 'source_collection_id' in constrained and fk.get('name'):
                op.drop_constraint(fk['name'], 'publications', type_='foreignkey')

        op.drop_column('publications', 'source_collection_id')
