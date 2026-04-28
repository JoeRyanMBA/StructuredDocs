---
description: "Use when editing Flask backend routes, SQLAlchemy models, Alembic migrations, import pipeline code, review token logic, publication exports, or other Python server code in backend/. Covers blueprint registration, JSON response patterns, and migration-safe schema changes."
name: "StructuredDocs Backend"
applyTo: "backend/**/*.py"
---
# StructuredDocs Backend Guidelines

- Start from the owning surface: route behavior in `backend/routes/`, app wiring in `backend/app.py`, shared extension instances in `backend/extensions.py`, model shape in `backend/models.py`, and export or PDF logic in `backend/services/` plus `backend/pdf_config.py`.
- Import `db`, `jwt`, `limiter`, `redis_conn`, and `task_queue` from `backend/extensions.py`; do not create duplicate extension instances.
- New backend resources should follow the existing Blueprint pattern and be registered through the blueprint map in `backend/app.py`.
- Keep API handlers JSON-first. On write failures, log with `current_app.logger.exception(...)` when practical, call `db.session.rollback()`, and return an error payload with an appropriate status.
- If an API response shape changes, update the model `to_dict()` serializer or the local serialization path deliberately instead of patching response fields ad hoc.
- New database columns should keep existing rows valid with a `server_default` when needed, and schema changes should ship with an Alembic migration.
- Prefer archival via boolean `archived` flags over hard deletes unless the surrounding feature already uses true deletion.
- Protected routes use `@jwt_required()`, and `get_jwt_identity()` returns the integer user id.
- Long-running work should go through `task_queue.enqueue(...)`; the app can fall back to synchronous execution when Redis is unavailable.
- For route-registration or HTML-instead-of-JSON bugs, check `ENABLE_BLUEPRINTS`, `SKIP_BLUEPRINTS`, `.enable_blueprints`, and the blueprint map in `backend/app.py`.
- Import pipeline changes usually start in `backend/routes/import_handler.py`; Word imports depend on `pandoc`, extracted media handling, and image-reference rewriting.
- Review access bugs should be traced through `ReviewToken.is_valid()` in `backend/models.py` before changing route logic.
- Publication export changes should be checked in `backend/routes/publications.py`, `backend/services/pdf_generator.py`, and `backend/pdf_config.py`; keep HTML compatible with the existing PDF sanitization path.
