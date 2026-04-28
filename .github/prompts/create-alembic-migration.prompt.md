---
description: "Create an Alembic migration for a StructuredDocs schema change. Use when adding or altering models, introducing new columns or tables, or adjusting enum and data shape with reversible upgrade and downgrade steps."
name: "Create Alembic Migration"
argument-hint: "Describe the model/schema change, existing-row constraints, and expected upgrade/downgrade behavior"
agent: "backend-specialist"
---
Create or update an Alembic migration for the schema change described in this chat input.

Requirements:
- Align migration changes with the corresponding model update in `backend/models.py`.
- Keep existing rows safe and valid; use defaults and staged data-shape changes when needed.
- Implement clear reversible `upgrade()` and `downgrade()` paths.
- Follow existing migration style in `backend/migrations/versions/`.
- Call out any manual data backfill or operator action explicitly if unavoidable.
- Validate with the narrowest practical check after editing.

Useful references:
- [backend/models.py](../../backend/models.py)
- [backend/migrations/env.py](../../backend/migrations/env.py)
- [backend/migrations/versions](../../backend/migrations/versions)
- [README.md](../../README.md)
