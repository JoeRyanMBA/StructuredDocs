# StructuredDocs Agent Guide

This document helps AI agents choose the right specialist and approach for StructuredDocs development tasks.

## Specialist Agents

### Backend Specialist

**Use for:** Flask routes, SQLAlchemy models, Alembic migrations, Python server code  
**Key files:** `backend/app.py`, `backend/models.py`, `backend/routes/`, `backend/extensions.py`, `backend/services/`  
**Detailed guidance:** See [.github/instructions/backend.instructions.md](.github/instructions/backend.instructions.md)

Common tasks:

- Adding or modifying API routes (JSON responses, error handling, auth checks)
- Changing database schema with migrations
- Import pipeline work (`backend/routes/import_handler.py`)
- Review token logic (`ReviewToken.is_valid()` in models)
- Publication/PDF export changes

### Frontend-Only Work

**Use for:** Vue pages, components, composables, API wrappers  
**Key files:** `frontend/src/api/`, `frontend/src/components/`, `frontend/src/composables/`, `frontend/src/pages/`, `frontend/src/views/`  
**Detailed guidance:** See [.github/instructions/frontend.instructions.md](.github/instructions/frontend.instructions.md)

Common tasks:

- New Vue components or page layouts
- Composable logic for client-side state
- API wrapper updates
- UI/UX changes

### Test & Validation

**Use for:** pytest fixtures, backend API regression tests, E2E validation  
**Test locations:** `test_*.py` (root level), `backend/**/test*.py`, `e2e/`, `cypress/`  
**Detailed guidance:** See [.github/instructions/testing.instructions.md](.github/instructions/testing.instructions.md)

Common tasks:

- Writing focused unit or integration tests
- Validating new schema changes with existing-row safety
- E2E test updates for UI flows

### Explore Agent

**Use for:** Codebase research, architecture questions, quick discovery  
**Specify:** Desired thoroughness (quick, medium, or thorough)

Use when:

- You need to understand how a feature works before implementing
- You're investigating a bug and need to trace call paths
- You need a quick inventory of related files or patterns

## Workflow Recommendations

### Adding a New Feature (Full Stack)

1. **Explore** – understand existing patterns in both frontend and backend
2. **Backend Specialist** – add routes, models, and migrations
3. **Frontend** work – add components and API wrappers
4. **Test** – write unit tests, run integration tests, validate E2E

### Schema Changes

1. Read [.github/instructions/migrations.instructions.md](.github/instructions/migrations.instructions.md)
2. Use **Backend Specialist** to create reversible migrations
3. Update models and routes
4. Use **Test** agent to validate existing rows stay valid

### Debugging Issues

1. **Explore** – identify where the bug likely originates
2. Choose the specialist (Backend/Frontend) based on symptoms
3. **Test** – add regression tests to prevent recurrence

### Import or Review Pipeline Changes

1. **Backend Specialist** – most import and review logic lives in `backend/routes/import_handler.py` and review token validation
2. Check [docs/import-guide.md](docs/import-guide.md) and [docs/REVIEW_WORKFLOW_GUIDE.md](docs/REVIEW_WORKFLOW_GUIDE.md)
3. Use **Test** to validate new behavior with existing data

### PDF/Publication Export Issues

1. **Backend Specialist** – check `backend/routes/publications.py`, `backend/services/pdf_generator.py`, and `backend/pdf_config.py`
2. Watch for HTML sanitization compatibility (ReportLab constraints)
3. Test with **Test** agent to ensure output quality

## Common Pitfalls & Debugging

| Issue | Where to Check | Specialist |
| --- | --- | --- |
| Routes not loading, `404` on API calls | `backend/app.py` blueprint map, `.enable_blueprints`, `ENABLE_BLUEPRINTS` env | Backend |
| Images not displaying after import | `backend/routes/import_handler.py`, check image URLs and storage config | Backend |
| Frontend can't fetch data | `frontend/src/api/`, proxy config, CORS headers | Frontend or Backend |
| Database migration fails on existing rows | Missing `server_default`, rollback logic in migration | Backend Specialist (Migrations) |
| Review links not working | `ReviewToken.is_valid()` in `backend/models.py` | Backend |
| PDF export cuts off content | HTML sanitization path, ReportLab constraints in `backend/pdf_config.py` | Backend |

## Specialized Skills

These skills provide deep guidance for specific workflows and problem domains:

- [.github/skills/add-full-stack-feature.md](.github/skills/add-full-stack-feature.md) – Step-by-step guide for adding a complete feature (backend + frontend + migrations)
- [.github/skills/debug-import-pipeline.md](.github/skills/debug-import-pipeline.md) – Diagnosing and fixing document import issues
- [.github/skills/debug-review-workflow.md](.github/skills/debug-review-workflow.md) – Fixing review access, tokens, and approval flows
- [.github/skills/debug-pdf-export.md](.github/skills/debug-pdf-export.md) – Troubleshooting PDF generation and publication exports

## Detailed Instruction Guides

These augment the core instructions with patterns for specific domains:

- [.github/instructions/validation-error-handling.instructions.md](.github/instructions/validation-error-handling.instructions.md) – Database validation, transaction safety, error responses
- [.github/instructions/task-queue.instructions.md](.github/instructions/task-queue.instructions.md) – Background jobs, Redis task queue, async patterns
- [.github/instructions/image-handling.instructions.md](.github/instructions/image-handling.instructions.md) – Image storage, S3/local filesystem, URL rewriting
- [.github/instructions/frontend-state.instructions.md](.github/instructions/frontend-state.instructions.md) – Vue 3 composables, reactive state, API integration

## Core Documentation Links

- [README.md](README.md) – Quick start and tech stack
- [docs/README.md](docs/README.md) – Documentation hub (imports, reviews, deployment, etc.)
- [.github/instructions/backend.instructions.md](.github/instructions/backend.instructions.md) – Backend patterns and conventions
- [.github/instructions/frontend.instructions.md](.github/instructions/frontend.instructions.md) – Frontend patterns and conventions
- [.github/instructions/migrations.instructions.md](.github/instructions/migrations.instructions.md) – Safe migration patterns
- [.github/instructions/testing.instructions.md](.github/instructions/testing.instructions.md) – Test structure and fixtures
- [CONTRIBUTING.md](CONTRIBUTING.md) – Development workflow and code style
- [docs/import-guide.md](docs/import-guide.md) – Document import behavior
- [docs/REVIEW_WORKFLOW_GUIDE.md](docs/REVIEW_WORKFLOW_GUIDE.md) – Review lifecycle
- [ARCHIVE_SYSTEM.md](ARCHIVE_SYSTEM.md) – Archival design
