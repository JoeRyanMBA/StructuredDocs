# StructuredDocs — Copilot Instructions

## What This App Is

StructuredDocs is a document management and knowledge-base platform. Users organize content into a **Project → Collection → Topic** hierarchy. Topics contain rich HTML content (edited via TinyMCE/Quill), can be reviewed externally via tokenized links, and published as PDFs. Word/HTML/Markdown documents can be imported and parsed into this hierarchy automatically.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Vue 3, Vite, Bootstrap 5, TinyMCE 6, Quill 2, Axios |
| Backend | Python 3.11, Flask, SQLAlchemy ORM |
| Database | PostgreSQL (production), SQLite (development) |
| Auth | Flask-JWT-Extended (JWT bearer tokens) |
| Background jobs | Redis + RQ |
| Rate limiting | Flask-Limiter (Redis-backed in prod, in-memory fallback) |
| Storage | AWS S3 / DigitalOcean Spaces (images) |
| Email | SendGrid or SMTP |

---

## Commands

### Frontend (in `frontend/`)
```bash
npm run dev       # Vite dev server on :5173 (proxies /api → localhost:8080)
npm run build     # Production build to frontend/dist/
```

### Backend (from repo root)
```bash
python -m pytest test_<file>.py                     # Run a single test file
python -m pytest test_hierarchical_parsing_logic.py # Example: standalone unit test (no server needed)
python -m pytest test_integration.py               # Integration tests (requires running backend on :5050)
python -m gunicorn "backend.app:create_app()" -b 0.0.0.0:8080  # Run backend
```

### E2E / Cypress (from repo root)
```bash
npm run cy:open                        # Interactive Cypress runner
npm run cy:run                         # Headless all specs
npm run cy:modal-smoke                 # Single smoke spec
```

### Full stack (Docker)
```bash
docker compose up --build              # API on :8080, nginx frontend on :3000
```

### Database migrations
```bash
cd backend && flask db upgrade         # Apply Alembic migrations
# Or trigger at container startup with env: RUN_DB_MIGRATIONS=1
```

---

## Architecture

### Backend (`backend/`)

- **`app.py`** — Flask app factory (`create_app()`). Initialises extensions, registers blueprints, and serves `frontend/dist/` for the SPA fallback.
- **`extensions.py`** — Single source for all extension instances (`db`, `migrate`, `jwt`, `limiter`, `redis_conn`, `task_queue`). Import from here, not from individual libraries.
- **`models.py`** — All SQLAlchemy models in one file. Key hierarchy: `Project` → `Collection` (self-referential, nestable) → `Topic`. Topic ordering within a collection is managed via the `collection_topic_tree` pivot table with a `position` column.
- **`routes/`** — One Blueprint file per resource. Each blueprint registers itself with `url_prefix='/api/<resource>'`.

### Frontend (`frontend/src/`)

- **`api/`** — Axios wrappers; all API calls go through here.
- **`components/`** — Reusable Vue 3 SFCs.
- **`pages/` / `views/`** — Page-level components wired up by Vue Router.
- **`composables/`** — Vue 3 composition-API hooks (shared stateful logic).
- `@` alias resolves to `frontend/src/`.

### Request Flow

1. Browser → Vite dev proxy (dev) or Vercel → DigitalOcean (prod)
2. Flask blueprint handles route → queries SQLAlchemy models → returns JSON
3. JWT bearer token required on protected routes (`@jwt_required()`)

---

## Key Conventions

### Adding a new backend route
1. Create `backend/routes/<resource>.py` with a Blueprint and `url_prefix='/api/<resource>'`.
2. Register it in the `blueprint_map` dict inside `app.py`'s `create_app()`.
3. All routes return JSON; use `current_app.logger.exception(...)` on errors, roll back with `db.session.rollback()`, and return `{'error': str(e)}` with the appropriate HTTP status.

### Models
- Every model has a `to_dict()` method used by routes to serialise to JSON.
- Soft-delete / archival is done with a boolean `archived` column (not hard deletes).
- New columns must have a `server_default` so that existing rows aren't broken; add an Alembic migration.

### Authentication
- `@jwt_required()` from Flask-JWT-Extended protects routes.
- `get_jwt_identity()` returns the current user's `id` (integer).
- Roles: `author`, `reviewer`, `admin` (defined as a SQLAlchemy `Enum`).
- Review tokens (`ReviewToken` model) grant external reviewers time-limited access without a full account.

### Environment / Config
- Secrets live in `.env` (repo root) and `backend/.env.email`. Neither file is committed.
- `app.py` loads both via `load_env_file()` at startup (python-dotenv with `override=False`).
- Key vars: `DATABASE_URL`, `JWT_SECRET_KEY`, `SECRET_KEY`, `SPACES_*` / `AWS_*` for storage, `SENDGRID_API_KEY` or SMTP vars for email.
- `SKIP_BLUEPRINTS=1` — start Flask without registering routes (useful during migrations).
- `ENABLE_BLUEPRINTS=<comma-list>` — register only named blueprints (useful for lightweight startup).

### Background Jobs
- Long-running work (email sends, image processing) is dispatched via `task_queue.enqueue(fn, ...)` from `backend/extensions.py`.
- Worker is started separately: `python -m backend.worker`.
- If Redis is unavailable, the app falls back to synchronous execution.

### Image Storage
- Images are uploaded to S3/Spaces and stored by URL reference in the database.
- Local dev can use the filesystem fallback (images stored under `instance/`).
- `SPACES_BUCKET`, `SPACES_ENDPOINT`, `SPACES_KEY`, `SPACES_SECRET` configure the object store.

---

## Import Pipeline

Document imports go through a **staged review** flow before Topics are created.

**Entry points** (`backend/routes/import_handler.py`, blueprint prefix `/api/import`):
- `POST /api/import/upload` — accepts a `.docx` or `.html` file upload
- `POST /api/import/markdown` — accepts raw Markdown

**Processing steps:**
1. **Conversion** — Word files are converted to Markdown via `pandoc` (spawned as a subprocess). Embedded images are extracted to a temp directory by pandoc's `--extract-media` flag.
2. **Image storage** — `ImageHandler` picks up extracted images, uploads them to S3/Spaces, and rewrites Markdown image references to use the stored URLs.
3. **Hierarchy parsing** — `_parse_hierarchical_structure_with_images()` walks the Markdown headings (`#` / `##` / `###` …) and builds a tree of `ImportItem` rows. Word heading styles are normalised to levels by `detect_heading_level_from_style()` (handles variants like "SC Heading 2", "Heading Level 3", etc.).
4. **Staging** — An `ImportDocument` is created with `status='staging'`, `review_step='pending'`. The import items are viewable at `GET /api/import/staging/<id>`.

**Review and commit:**
- `POST /api/import/staging/<id>/sme_approve` → advances `review_step` to `'sme_approved'`
- `POST /api/import/staging/<id>/commit` → creates `Topic` records from the staged `ImportItem` tree, sets `ImportDocument.status='approved'`
- `POST /api/import/staging/<id>/reject` → sets `status='rejected'`
- `POST /api/import/staging/<id>/reprocess` → re-runs parsing without re-uploading the file

**Models involved:** `ImportDocument`, `ImportItem`, `ImportImage`, `ImportLink`

---

## Review Token Workflow

Provides **external reviewers** (non-account holders) access to a specific topic via a signed URL.

**Core flow:**
1. An author creates a review via `POST /api/reviews/request`, linking a `Topic` to an internal `reviewer_id`. `Review.status` starts as `'pending'`.
2. `POST /api/reviews/<id>/start` → `status='in_progress'`.
3. `POST /api/reviews/<id>/generate-token` → creates a `ReviewToken` record using `secrets.token_urlsafe(32)`. Default expiry is 30 days; `max_access_count` defaults to 10. Returns a `review_url` of the form `/review/<token>` and a pre-filled email template body.
4. The external reviewer opens `/review/<token>` → frontend calls `GET /api/review/<token>`. The backend validates expiry and `access_count < max_access_count`, then increments `access_count`.
5. Reviewer submits inline feedback via `POST /api/review/<token>/feedback` → creates `ReviewFeedback` rows (`status` one of `'pending'`, `'accepted'`, `'rejected'`, `'modified'`).
6. Author responds to individual items via `PUT /api/feedback/<id>/respond`.
7. `POST /api/reviews/<id>/submit` → marks the review complete; the topic status is updated to `'approved'` or `'revisions_requested'`.

**Models involved:** `Review`, `ReviewToken`, `ReviewFeedback`

**Token validation** is done by `ReviewToken.is_valid()` on the model instance — check there first when debugging access errors.

---

## Publication & Export

A **Publication** is an ordered, named snapshot of selected Topics assembled for distribution.

**Workflow:**
1. `POST /api/publications` — create a new Publication (title, description).
2. `POST /api/publications/<id>/nodes` — save the topic tree. Each `PublicationNode` stores `title_snapshot` and `content_snapshot` (frozen copies of topic title/content at save time, so edits to the live topic don't affect the publication).
3. Export or preview:

| Endpoint | Output |
|---|---|
| `GET /api/publications/<id>/export/pdf?format=<type>` | PDF download via ReportLab |
| `GET /api/publications/<id>/export/mobile-kb` | Self-contained HTML knowledge base |
| `GET /api/publications/<id>/preview/mobile-kb` | Same HTML, inline preview |

**PDF generation** (`generate_pdf()` in `publications.py`):
- Uses `BackgroundImageDocTemplate` (ReportLab `BaseDocTemplate` subclass) with separate page templates for title page, TOC (roman numerals), and content pages.
- `format` query param selects a config class from `backend/pdf_config.py`: `default` → `PDFConfig`, `corporate` → `CorporateConfig`, `academic` → `AcademicConfig`, `compact` → `CompactConfig`, `organization` → `OrganizationConfig`.
- HTML content in topic snapshots is sanitised by `_pdf_sanitize_text()` before passing to ReportLab (strips unsupported tags, fixes mis-nested bold/italic, escapes stray `&`). Run content through this function whenever adding new HTML-to-PDF rendering.
- An optional background image (watermark/cover) is passed via `background_image` query param.

**Models involved:** `Publication`, `PublicationNode`
