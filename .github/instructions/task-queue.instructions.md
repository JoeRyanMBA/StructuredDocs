---
description: "Use when adding background jobs, async tasks, long-running operations, or working with Redis task queue in StructuredDocs. Covers task enqueueing, fallback to sync, error handling, and job monitoring."
name: "StructuredDocs Task Queue Patterns"
applyTo: "backend/routes/import*.py,backend/routes/publications.py,backend/services/**.py"
---
# Task Queue & Background Job Patterns

StructuredDocs uses Redis + RQ (Redis Queue) for background jobs. If Redis is unavailable, tasks fall back to synchronous execution.

## When to Use Task Queue

- Long-running operations (document import, PDF generation, email sending)
- Bulk operations (publish multiple topics, export publication)
- Tasks that should not block HTTP request/response
- Operations that may fail and need retry logic

## Enqueueing a Task

```python
from backend.extensions import task_queue

# Enqueue a background job
job = task_queue.enqueue(
    'path.to.function',  # Function to call (string path)
    args=(arg1, arg2),    # Positional arguments
    kwargs={'key': 'value'},  # Keyword arguments
    job_timeout=3600,     # Max runtime in seconds
    result_ttl=500,       # How long to keep result
)

# Return job ID to client (for polling/status checks)
return {'job_id': job.id, 'status': 'queued'}
```

## Synchronous Fallback

If Redis is unavailable:
```python
try:
    job = task_queue.enqueue(my_function, args=(data,))
except Exception:
    # Fallback to sync execution
    result = my_function(data)
    return {'status': 'completed', 'result': result}
```

## Task Function Example

```python
# backend/tasks.py
def import_document(document_id, project_id):
    """Long-running import task."""
    from backend.app import create_app
    from backend.models import Document, Project
    
    app = create_app()
    with app.app_context():
        try:
            doc = Document.query.get(document_id)
            project = Project.query.get(project_id)
            
            # Perform import logic
            import_result = do_import(doc, project)
            
            # Update document status
            doc.status = 'imported'
            db.session.commit()
            
            return {'success': True, 'result': import_result}
        except Exception as e:
            current_app.logger.exception(f"Import failed: {e}")
            db.session.rollback()
            return {'success': False, 'error': str(e)}
```

## Polling for Job Status

Frontend can poll for job status:
```python
@bp.get('/jobs/<job_id>')
@jwt_required()
def get_job_status(job_id):
    """Get background job status."""
    job = task_queue.fetch_job(job_id)
    
    if not job:
        return {'error': 'Job not found'}, 404
    
    return {
        'id': job.id,
        'status': job.get_status(),  # 'queued', 'started', 'finished', 'failed'
        'progress': job.meta.get('progress', 0),
        'result': job.result if job.is_finished else None,
        'error': str(job.exc_info) if job.is_failed else None,
    }
```

## Task Monitoring

Check task queue status:
```bash
# From repo root
python -c "
from backend.extensions import task_queue
connection = task_queue.connection
print('Queue connection:', connection.ping())

# Get job count (if using standard RQ)
from rq import Queue
q = Queue(connection=connection)
print('Pending jobs:', len(q))
"
```

## Error Handling in Tasks

Always:
- Wrap in try/except
- Log exceptions with `current_app.logger.exception(...)`
- Rollback database session on error
- Return structured result (success/error dict)

```python
def safe_long_task(data):
    try:
        result = do_work(data)
        db.session.commit()
        return {'success': True, 'result': result}
    except Exception as e:
        current_app.logger.exception(f"Task failed: {e}")
        db.session.rollback()
        return {'success': False, 'error': str(e)}
```

## Common Task Patterns

### Document Import
```python
# Enqueue from route handler
job = task_queue.enqueue('backend.tasks.import_document', args=(doc_id, project_id))
return {'job_id': job.id, 'status': 'queued'}

# Frontend polls /api/jobs/<job_id> until complete
```

### PDF Generation
```python
# Enqueue for large/complex publications
job = task_queue.enqueue('backend.tasks.generate_publication_pdf', args=(pub_id,))

# Once done, PDF stored in database or S3
# Frontend can download when ready
```

### Email Sending
```python
# Queue email for review notification
job = task_queue.enqueue('backend.tasks.send_review_email', 
                        kwargs={'topic_id': topic_id, 'reviewer_email': email})
```

## Configuration

**Environment variables:**
- `REDIS_URL`: Redis connection string (defaults to `localhost:6379`)
- `REDIS_DB`: Database number (default `0`)
- `RQ_RESULT_TTL`: How long to keep completed job results (seconds)

If Redis unavailable:
- Tasks execute synchronously
- No retry logic available
- Consider scaling up single instance or adding retry middleware

## Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| Jobs queued but not running | Redis worker not started | Run `rq worker` in separate terminal |
| "Job lost" / Job disappears | Worker crashed or job timeout | Check logs, increase `job_timeout` |
| Sync fallback too slow | All tasks falling back to sync | Check Redis connection, restart Redis |
| Database locks during task | Task not using app context | Ensure task calls `db.session.commit()` or rollback |
| Task result not retrievable | Result TTL expired | Increase `RQ_RESULT_TTL` or fetch immediately |

## Files to Check

- `backend/extensions.py` — task_queue initialization and config
- `backend/tasks.py` (if exists) — background job definitions
- `backend/routes/*.py` — where tasks are enqueued
- [docs/README.md](../../docs/README.md) — deployment guide (background job setup)

## Related Patterns

- Import pipeline (uses task queue for document processing): [.github/skills/debug-import-pipeline.md](../skills/debug-import-pipeline.md)
- PDF export (may use task queue for large publications): [.github/skills/debug-pdf-export.md](../skills/debug-pdf-export.md)

**Read:** [.github/instructions/backend.instructions.md](./backend.instructions.md) for route patterns
