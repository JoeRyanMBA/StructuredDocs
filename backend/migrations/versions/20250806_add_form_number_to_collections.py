"""Add form_number field to collections table

Revision ID: 20250806_add_form_number
Revises: f9269827c2fc
Create Date: 2025-08-06 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20250806_add_form_number'
down_revision = 'bd57ab311365'
branch_labels = None
depends_on = None

def upgrade():
    # Add the form_number column
    with op.batch_alter_table('collections', schema=None) as batch_op:
        batch_op.add_column(sa.Column('form_number', sa.String(length=100), nullable=True))
    
    # Update existing collections with temporary form numbers
    # We'll make it nullable first, populate it, then make it required
    connection = op.get_bind()
    connection.execute(sa.text("""
        UPDATE collections 
        SET form_number = 'TEMP-' || CAST(id AS VARCHAR(10))
        WHERE form_number IS NULL
    """))
    
    # Now make the column NOT NULL and add unique constraint
    with op.batch_alter_table('collections', schema=None) as batch_op:
        batch_op.alter_column('form_number', nullable=False)
        batch_op.create_unique_constraint('uq_collections_form_number', ['form_number'])

def downgrade():
    with op.batch_alter_table('collections', schema=None) as batch_op:
        batch_op.drop_constraint('uq_collections_form_number', type_='unique')
        batch_op.drop_column('form_number')
