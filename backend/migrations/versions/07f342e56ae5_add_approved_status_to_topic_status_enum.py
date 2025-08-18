"""add approved status to topic status enum

Revision ID: 07f342e56ae5
Revises: ceac11c5e665
Create Date: 2025-08-17 21:22:21.222970

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '07f342e56ae5'
down_revision = 'ceac11c5e665'
branch_labels = None
depends_on = None


def upgrade():
    # SQLite doesn't support altering enums directly, so we'll recreate the topic_status constraint
    # First, drop the old constraint
    op.execute("DROP TABLE IF EXISTS topics_temp")
    
    # Create temporary table with new enum values
    op.execute("""
        CREATE TABLE topics_temp (
            id INTEGER PRIMARY KEY,
            title VARCHAR(200) NOT NULL,
            content TEXT,
            frontmatter TEXT,
            status VARCHAR(20) CHECK(status IN ('draft', 'pending_review', 'approved', 'published', 'rejected', 'archived')) NOT NULL DEFAULT 'draft',
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Copy data from old table
    op.execute("""
        INSERT INTO topics_temp (id, title, content, frontmatter, status, created_at, updated_at)
        SELECT id, title, content, frontmatter, status, created_at, updated_at FROM topics
    """)
    
    # Drop old table and rename temp table
    op.execute("DROP TABLE topics")
    op.execute("ALTER TABLE topics_temp RENAME TO topics")


def downgrade():
    # Reverse the process - remove 'approved' status
    op.execute("DROP TABLE IF EXISTS topics_temp")
    
    # Create temporary table without 'approved' status
    op.execute("""
        CREATE TABLE topics_temp (
            id INTEGER PRIMARY KEY,
            title VARCHAR(200) NOT NULL,
            content TEXT,
            frontmatter TEXT,
            status VARCHAR(20) CHECK(status IN ('draft', 'pending_review', 'published', 'rejected', 'archived')) NOT NULL DEFAULT 'draft',
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Copy data, converting 'approved' back to 'published'
    op.execute("""
        INSERT INTO topics_temp (id, title, content, frontmatter, status, created_at, updated_at)
        SELECT id, title, content, frontmatter, 
               CASE WHEN status = 'approved' THEN 'published' ELSE status END,
               created_at, updated_at 
        FROM topics
    """)
    
    # Drop old table and rename temp table
    op.execute("DROP TABLE topics")
    op.execute("ALTER TABLE topics_temp RENAME TO topics")
