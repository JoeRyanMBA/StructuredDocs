# Database utilities

Use the Alembic migrations in `backend/migrations/` for normal schema changes.
The scripts here are manual transfer, export, seed, or repair tools; they are
not part of the application startup path.

## Folders

- `repairs/` contains one-off Python schema repairs.
- `manual/` contains SQL snippets and manual operations.
- `transfer/` contains SQLite-to-PostgreSQL transfer tools.
- `export/` contains database export utilities.
- `seed_help_links.py` is a CLI for the help-link seed data.

Run Python tools from the repository root with module syntax, for example:

```bash
python -m scripts.database.repairs.fix_collections_archived_column
```

Review each script before use and confirm the selected database. Back up
production data before running repairs. In particular, `manual/clear_db.sql`
deletes application data and must not be run against production.
