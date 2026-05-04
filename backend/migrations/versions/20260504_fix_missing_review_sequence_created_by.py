"""Repair missing review_sequences.created_by column.

Revision ID: 20260504_seq_created_by
Revises: a9f5e2c1b0d3
Create Date: 2026-05-04
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260504_seq_created_by'
down_revision = 'a9f5e2c1b0d3'
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
    dialect = bind.dialect.name

    if 'review_sequences' not in inspector.get_table_names():
        return

    if not _has_column(inspector, 'review_sequences', 'created_by'):
        op.add_column('review_sequences', sa.Column('created_by', sa.Integer(), nullable=True))

        # Backfill from existing sequence reviews where possible.
        if dialect == 'postgresql':
            op.execute(
                """
                UPDATE review_sequences rs
                SET created_by = sub.requested_by
                FROM (
                  SELECT sequence_id, MIN(requested_by) AS requested_by
                  FROM reviews
                  WHERE sequence_id IS NOT NULL AND requested_by IS NOT NULL
                  GROUP BY sequence_id
                ) AS sub
                WHERE rs.id = sub.sequence_id
                  AND rs.created_by IS NULL
                """
            )
        else:
            op.execute(
                """
                UPDATE review_sequences
                SET created_by = (
                  SELECT r.requested_by
                  FROM reviews r
                  WHERE r.sequence_id = review_sequences.id
                    AND r.requested_by IS NOT NULL
                  ORDER BY r.id ASC
                  LIMIT 1
                )
                WHERE created_by IS NULL
                """
            )

        # Final fallback so rows remain queryable even if reviews are missing.
        op.execute(
            """
            UPDATE review_sequences
            SET created_by = (
              SELECT s.id
              FROM stakeholders s
              ORDER BY s.id ASC
              LIMIT 1
            )
            WHERE created_by IS NULL
            """
        )

    # Re-inspect after potential add_column.
    inspector = sa.inspect(bind)
    if _has_column(inspector, 'review_sequences', 'created_by') and not _has_fk_on_column(inspector, 'review_sequences', 'created_by'):
        try:
            op.create_foreign_key(
                'fk_review_sequences_created_by_stakeholders',
                'review_sequences',
                'stakeholders',
                ['created_by'],
                ['id']
            )
        except Exception:
            # Keep migration non-destructive on environments with nonstandard constraints.
            pass


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if 'review_sequences' not in inspector.get_table_names():
        return

    if _has_column(inspector, 'review_sequences', 'created_by'):
        for fk in inspector.get_foreign_keys('review_sequences'):
            constrained = fk.get('constrained_columns') or []
            if 'created_by' in constrained and fk.get('name'):
                op.drop_constraint(fk['name'], 'review_sequences', type_='foreignkey')

        op.drop_column('review_sequences', 'created_by')
