# Skill: Add Full-Stack Feature to StructuredDocs

This skill guides you through adding a complete feature that requires changes to both backend and frontend, including database schema updates.

## When to Use

- Adding a new user-facing feature (e.g., new collection property, workflow step, export format)
- Adding a new admin setting or configuration option
- Adding new API endpoints with supporting UI

## Workflow

### 1. Plan the Data Model

- Open `backend/models.py` and identify where the new data should live
- Determine if you need a new table, new columns on existing tables, or a new association
- Sketch the SQLAlchemy model and relationships
- **Read:** [.github/instructions/migrations.instructions.md](../../.github/instructions/migrations.instructions.md)

### 2. Create the Migration

- From repo root, run: `python -c "from backend.app import create_app; app = create_app(); app.app_context().push()" && cd backend && flask db migrate -m "Add <feature>"`
- Edit the generated migration in `backend/migrations/versions/` to ensure it's reversible and safe
- Include `server_default` for new columns to avoid breaking existing rows
- Test rollback: `flask db downgrade && flask db upgrade`

### 3. Update the Backend Model

- Add/modify the SQLAlchemy model in `backend/models.py`
- Add a `to_dict()` method or update the existing one to include new fields
- Add validation logic (use existing model patterns)

### 4. Add Backend Routes

- Create or modify route(s) in `backend/routes/<resource>.py`
- Import extensions from `backend/extensions.py` (not locally)
- Return JSON responses with proper error handling
- Protect routes with `@jwt_required()` if needed
- **Read:** [.github/instructions/backend.instructions.md](../../.github/instructions/backend.instructions.md)

### 5. Test Backend in Isolation

- Write unit tests in `test_<feature>.py` at repo root
- Write integration tests using the app fixture from `conftest.py`
- Run: `python -m pytest test_<feature>.py -v`
- **Read:** [.github/instructions/testing.instructions.md](../../.github/instructions/testing.instructions.md)

### 6. Update Frontend API Layer

- Create or modify `frontend/src/api/<resource>.js`
- Ensure field names match backend `to_dict()` output
- Handle errors and edge cases
- **Read:** [.github/instructions/frontend.instructions.md](../../.github/instructions/frontend.instructions.md)

### 7. Add Frontend Components/Pages

- Add Vue components to `frontend/src/components/`
- Add pages to `frontend/src/pages/` or `frontend/src/views/`
- Use composables in `frontend/src/composables/` for reusable logic
- Import API calls from `frontend/src/api/`
- Use `@` alias for imports

### 8. Test End-to-End

- Start backend: `python -m gunicorn "backend.app:create_app()" -b 0.0.0.0:8080`
- Start frontend: `cd frontend && npm run dev`
- Manually test the feature in the browser
- Run E2E tests: `npm run cy:run`
- Run frontend linter: `cd frontend && npm run lint`

### 9. Validation Checklist

- [ ] Migration is reversible and includes `server_default` for new columns
- [ ] Backend model has updated `to_dict()` method
- [ ] All new routes are tested and logged with `current_app.logger`
- [ ] Protected routes use `@jwt_required()` and `get_jwt_identity()`
- [ ] Frontend API wrapper matches backend schema
- [ ] No hardcoded configs—use environment variables or admin settings
- [ ] Long-running tasks go through `task_queue.enqueue()`
- [ ] All tests pass: `python -m pytest` and `npm run lint`

## Common Pitfalls

| Issue | Solution |
| --- | --- |
| Migration fails on existing rows | Forgot `server_default`—add it and re-run migration |
| API returns 404 or HTML | Check `backend/app.py` blueprint registration and `ENABLE_BLUEPRINTS` env |
| Frontend can't fetch data | Check CORS headers, proxy config in Vite, and backend CORS setup |
| Changes to `to_dict()` break existing code | Update consuming API wrappers and page components first |
| Long operations timeout | Use `task_queue.enqueue()` for background work |

## Files to Review

- Example model with relationships: `backend/models.py`
- Example routes pattern: `backend/routes/collections.py` or `backend/routes/topics.py`
- Example Vue page: `frontend/src/pages/Collections.vue`
- Example API wrapper: `frontend/src/api/collections.js`
- Example composable: `frontend/src/composables/useCollections.js` (if exists)
