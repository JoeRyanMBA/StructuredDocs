# StructuredDocs Workspace Instructions

## Scope

StructuredDocs is a document management and knowledge-base platform built as a Vue 3 frontend plus a Flask backend. The core content hierarchy is Project -> Collection -> Topic, with document import, review workflows, and publication/export features layered on top.

## Build And Test

- Frontend dev: `cd frontend && npm install && npm run dev`
- Frontend build: `cd frontend && npm run build`
- Backend setup: `python -m venv .venv && source .venv/bin/activate && pip install -r backend/requirements.txt`
- Backend dev server from repo root: `python -m gunicorn "backend.app:create_app()" -b 0.0.0.0:8080`
- Run a focused backend test from repo root: `python -m pytest test_<file>.py`
- Example unit test: `python -m pytest test_hierarchical_parsing_logic.py`
- Integration tests may require the backend running separately; check the specific test file before running it.
- Frontend E2E: `npm run cy:run` or `npm run cy:modal-smoke`
- Docker full stack: `docker compose up --build`
- Migrations: `cd backend && flask db upgrade`

## Architecture

- Backend app factory and blueprint registration live in `backend/app.py`.
- Import all Flask extensions from `backend/extensions.py`; do not instantiate duplicate `db`, `jwt`, `limiter`, `redis_conn`, or `task_queue` objects elsewhere.
- SQLAlchemy models are centralized in `backend/models.py`; collection nesting is self-referential and topic ordering is stored through `collection_topic_tree.position`.
- Backend routes are split by resource under `backend/routes/`; each resource uses a Blueprint with `/api/...` prefixes.
- Frontend API access belongs in `frontend/src/api/`, reusable stateful logic in `frontend/src/composables/`, and page-level views in `frontend/src/pages/` or `frontend/src/views/`.
- Use the `@` alias for `frontend/src/` imports.

## Project Conventions

- New backend routes should follow existing Blueprint patterns and be registered through the blueprint map in `backend/app.py`.
- Route handlers should return JSON, log exceptions with `current_app.logger.exception(...)`, and roll back the session on write failures.
- Models are expected to expose `to_dict()` serializers used by the API layer.
- New database columns should include a `server_default` when needed to keep existing rows valid, and schema changes should ship with an Alembic migration.
- Archival is usually implemented with boolean `archived` flags rather than hard deletes.
- Protected backend routes use `@jwt_required()`, and `get_jwt_identity()` returns the integer user id.
- Long-running work should go through `task_queue.enqueue(...)`; the app can fall back to synchronous execution when Redis is unavailable.

## Agent-Critical Pitfalls

- `backend/app.py` can selectively register routes. Use `ENABLE_BLUEPRINTS=<comma-list>` for narrow startup and `SKIP_BLUEPRINTS=1` for migration-oriented startup.
- Startup behavior depends on repo-root assets such as `.enable_blueprints` and `frontend/dist/`; if those are missing, `create_app()` can enter an emergency fallback mode.
- Import pipeline work usually starts in `backend/routes/import_handler.py`; Word import handling depends on `pandoc` and image rewriting.
- Review token access bugs should be traced through `ReviewToken.is_valid()` in `backend/models.py`.
- Publication export and PDF rendering work should be checked in `backend/routes/publications.py`, `backend/services/pdf_generator.py`, and `backend/pdf_config.py`; HTML passed to ReportLab must stay compatible with the existing sanitization path.
- Image storage can target S3-compatible storage or local filesystem fallback depending on environment configuration.

## Reference Docs

- `README.md` for quick start, deployment overview, and environment templates.
- `docs/import-guide.md` for document import behavior and troubleshooting.
- `docs/REVIEW_WORKFLOW_GUIDE.md` for the review lifecycle and reviewer UX.
- `ARCHIVE_SYSTEM.md` for archival behavior.
- `docs/object-storage-setup.md` for S3-compatible object storage configuration.
- `docs/email-sending.md` for SMTP configuration.
- `docs/self-hosting.md` for deployment and hosting details.
