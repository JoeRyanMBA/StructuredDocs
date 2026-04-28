---
description: "Use when creating or editing Alembic migrations, changing SQLAlchemy schema, or adding backend columns or tables in StructuredDocs. Covers reversible migration style, existing-row safety, and coordination with backend/models.py."
name: "StructuredDocs Migrations"
applyTo: "backend/migrations/**/*.py"
---
# StructuredDocs Migration Guidelines

- Keep migrations aligned with the model change in `backend/models.py`; do not land schema-only drift without the corresponding application update.
- New columns should keep existing rows valid. Use `server_default` in the model when needed, and make the migration safe for already-populated tables.
- Prefer reversible migrations with explicit `upgrade()` and `downgrade()` steps.
- Match the existing Alembic file style in `backend/migrations/versions/`, including clear revision metadata and direct `op.add_column`, `op.create_table`, or related operations.
- Be careful with enum or data-shape changes that can affect existing rows; stage them deliberately rather than combining destructive changes into one step.
- After changing schema, update or add the narrowest relevant backend test or regression check when feasible.
