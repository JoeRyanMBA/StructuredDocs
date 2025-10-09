# Database Migration Snippets

This folder contains dialect-specific snippets for adding snapshot columns to the `publication_nodes` table.

## PostgreSQL

```sql
ALTER TABLE publication_nodes
  ADD COLUMN IF NOT EXISTS title_snapshot VARCHAR(200);

ALTER TABLE publication_nodes
  ADD COLUMN IF NOT EXISTS content_snapshot TEXT;
```

## SQLite

SQLite does not support `IF NOT EXISTS` for `ADD COLUMN` prior to recent versions. However, adding a new column without existing constraints is allowed and will succeed if the column does not already exist. Use a guard query or migration tool (Alembic) to check existence before altering.

Example (conceptual; prefer Alembic/ORM migrations):

```sql
-- Check if column exists (via PRAGMA) and then run the ALTER
-- PRAGMA table_info('publication_nodes');
-- If 'title_snapshot' not present:
ALTER TABLE publication_nodes ADD COLUMN title_snapshot TEXT;
-- If 'content_snapshot' not present:
ALTER TABLE publication_nodes ADD COLUMN content_snapshot TEXT;
```

> Recommendation: Prefer using your ORM/alembic migrations to ensure portability and safety.
