# Skill: Debug Import Pipeline Issues

This skill guides you through diagnosing and fixing problems in the document import flow (Word, HTML, Markdown → Project/Collection/Topic hierarchy).

## When to Use

- Documents not importing or importing with missing content
- Hierarchical structure (Project → Collection → Topic) not parsing correctly from headings
- Images embedded in imported documents not displaying
- Import pipeline errors or timeouts
- Document preview showing incorrectly

## Quick Diagnosis

### Is the Import Service Running?
```bash
# Check if Redis is available
redis-cli ping  # Should return PONG

# Check task queue status
python -c "from backend.extensions import task_queue; print(task_queue.connection.ping())"
```

### Check Import Handler Logs
Import logic starts in `backend/routes/import_handler.py`:
- Route: `POST /api/imports` 
- Accepts file upload and creates an async task
- Falls back to sync if Redis unavailable
- Logs to `current_app.logger`

### Enable Debug Logging
Set environment variable: `FLASK_DEBUG=1`
Then check logs for:
- Pandoc conversion errors (Word imports depend on `pandoc` binary)
- Image extraction/rewriting problems
- Heading parser output
- Database write failures

## Diagnosis Workflow

### 1. Verify Pandoc Installation (Word Imports)
```bash
pandoc --version
# Should output version info; if missing, install: apt-get install pandoc
```

### 2. Check for Heading Parser Issues
- Word/HTML files must have proper heading hierarchy (H1, H2, H3)
- Markdown must use `#`, `##`, `###` syntax
- The parser in `backend/services/` (or `import_handler.py`) extracts headings into the hierarchy
- **Read:** [docs/import-guide.md](../../docs/import-guide.md)

### 3. Trace Image Handling
Images are extracted and:
- Rewritten with new URLs
- Stored in S3-compatible or local filesystem storage
- Referenced in the content via image tags

Common issues:
- Missing image storage config → falls back to local `instance/` folder
- Broken image URLs after rewriting → check `backend/routes/import_handler.py` image rewrite logic
- Image storage unreachable → check S3 credentials and CORS

**Check file:** `backend/routes/import_handler.py` (image extraction and rewriting)  
**Check config:** `backend/pdf_config.py` and environment variables for storage location

### 4. Test Import in Isolation
```python
# From repo root:
python -c "
from backend.app import create_app
app = create_app()
with app.app_context():
    # Manually test import service
    from backend.services import import_service  # or similar
    # Call import function with test document
"
```

### 5. Check Database State After Failed Import
```bash
# Check if rows were partially created/rolled back
python -c "
from backend.app import create_app
from backend.models import Project, Collection, Topic
app = create_app()
with app.app_context():
    print('Projects:', Project.query.count())
    print('Collections:', Collection.query.count())
    print('Topics:', Topic.query.count())
"
```

### 6. Review Import Logs
- Check for `current_app.logger.exception(...)` output
- Look for Pandoc errors (stderr from subprocess)
- Verify file paths and storage access

## Common Issues & Fixes

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| "Pandoc not found" | Pandoc binary not installed | Run `apt-get install pandoc` |
| Hierarchical structure wrong | Headings don't follow H1 → H2 → H3 pattern | Verify heading levels in source document |
| Images missing/broken URLs | Image rewriting failed or storage unreachable | Check storage config, CORS, and log output |
| Import hangs or times out | Redis unavailable or sync fallback overloaded | Check Redis connection, consider async processing |
| Content corrupted or truncated | Encoding or streaming error | Check file encoding (UTF-8) and file size limits |
| Import partially succeeds | Database rollback on error | Review logs for validation errors in models |

## Files to Check

| File | Purpose |
|------|---------|
| `backend/routes/import_handler.py` | Main import entry point; handles file upload, creates async task |
| `backend/services/` | May contain import logic for different file types (Word, Markdown, HTML) |
| `docs/import-guide.md` | User-facing import guide with examples and troubleshooting |
| `backend/models.py` | Check `Project`, `Collection`, `Topic` schema for validation |
| `backend/pdf_config.py` | Storage configuration (S3 or local filesystem) |
| `.env` or environment variables | Check import-related configs (pandoc path, storage URL, etc.) |

## Test Import E2E
```bash
# 1. Start backend
python -m gunicorn "backend.app:create_app()" -b 0.0.0.0:8080

# 2. Start frontend or use curl
curl -X POST http://localhost:8080/api/imports \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -F "file=@test_document.docx"

# 3. Check logs for errors
# 4. Verify Project/Collection/Topic structure created in database
```

## Migration Considerations

If you modify import behavior:
1. Existing imported documents should not break
2. Add migration-safe tests (check `backend/**/test*.py` for patterns)
3. Use `.env` or admin settings for feature flags, not hardcoded logic
4. Test with real-world documents (Word, HTML, Markdown variants)

**Read:** [.github/instructions/migrations.instructions.md](../../.github/instructions/migrations.instructions.md)
