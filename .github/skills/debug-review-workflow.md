# Skill: Debug Review Workflow Issues

This skill guides you through diagnosing and fixing problems in the review and approval workflow, including reviewer access, feedback collection, and review state tracking.

## When to Use

- Reviewers can't access review links or get 403/401 errors
- Review feedback not showing or getting lost
- Review status not updating correctly
- Review tokens expiring prematurely or not working at all
- Email notifications for reviews not being sent

## Quick Diagnosis

### Is Review Enabled?

Check `backend/app.py` blueprint registration. The review routes should be active:
```bash
python -c "
from backend.app import create_app
app = create_app()
# List all registered routes
for rule in app.url_map.iter_rules():
    if '/review' in rule.rule:
        print(rule)
"
```

### Check Review Token Validity

All review access goes through `ReviewToken.is_valid()` in `backend/models.py`:
- Token must not be expired
- Token must be linked to a valid Topic/Feedback
- Token must belong to an active (non-archived) resource
- **Read:** Check the `ReviewToken` model for all validation rules

## Diagnosis Workflow

### 1. Understand Review State Flow

Review workflow lifecycle:
1. Topic created and assigned reviewers
2. Review tokens generated for external reviewers (no account needed)
3. Reviewers access via token link (e.g., `/review/<token>`)
4. Feedback collected inline or as comments
5. Approval status tracked and workflow progresses
6. Topic published once approved

**Read:** [docs/REVIEW_WORKFLOW_GUIDE.md](../../docs/REVIEW_WORKFLOW_GUIDE.md)

### 2. Verify Review Token Generation

Tokens are created when:
- A Topic is put into review
- External reviewers are assigned
- Time-limited link is generated (e.g., 7 days by default)

Check the database:
```bash
python -c "
from backend.app import create_app
from backend.models import ReviewToken
app = create_app()
with app.app_context():
    token = ReviewToken.query.first()
    print(f'Token: {token.token}')
    print(f'Expires: {token.expires_at}')
    print(f'Valid: {token.is_valid()}')
    print(f'Topic: {token.topic_id if token else None}')
"
```

### 3. Test Review Access Flow

```bash
# 1. Generate a review link for a topic
# Use the admin UI or API endpoint to create review

# 2. Try accessing the review page with the token
# Example (in browser): http://localhost:3000/review/abc123xyz
#   - Should show review interface without login
#   - Should show feedback collection UI
#   - Should allow inline comments

# 3. Check logs for token validation errors
# Look for: "Token invalid", "Token expired", "Topic not found"
```

### 4. Check Email Notifications

Review notifications are sent via:
- SMTP config (check `.env` and `docs/email-sending.md`)
- Email queue in `backend/extensions.py` task_queue
- Route handler for sending (likely in `backend/routes/reviews.py` or similar)

**Test email setup:**
```bash
python -c "
from backend.extensions import task_queue
# If Redis is available, task_queue will queue emails
# Otherwise, falls back to sync sending
print('Task queue connection:', task_queue.connection.ping())
"
```

### 5. Check Feedback Persistence

Feedback should be stored in database and linked to:
- Specific Topic (or Feedback record)
- Reviewer (via ReviewToken or User account)
- Comment/inline location in content

Verify in database:
```bash
python -c "
from backend.app import create_app
from backend.models import Feedback  # or similar model
app = create_app()
with app.app_context():
    feedback = Feedback.query.first()
    print(f'Feedback: {feedback}')
    print(f'Topic: {feedback.topic_id}')
    print(f'Reviewer: {feedback.reviewer_id}')
"
```

### 6. Trace Review Status Updates

Review approval status usually flows through:
- `Topic.review_status` field (enum: pending, in_review, approved, rejected)
- Approval counts or explicit approvals per reviewer
- Workflow rules for advancement (e.g., all reviewers must approve)

**Check file:** `backend/models.py` for `Topic`, `ReviewToken`, `Feedback` schema

## Common Issues & Fixes

| Symptom | Likely Cause | Fix |
| --- |--------------|-----|
| "Invalid review token" / 403 on review link | Token expired or not found | Check `ReviewToken.expires_at`, regenerate link |
| Reviewer can't see feedback | Feedback not linked to token/topic correctly | Check Feedback model relationships and database state |
| Review email not sent | SMTP config missing or queue failure | Check `.env` for SMTP settings, verify email service |
| Review status stuck | Workflow logic not advancing state | Check approval count logic in route handler |
| Reviewer can edit content | Permissions not enforced on endpoint | Check `@jwt_required()` and permission checks in routes |
| Review link works but shows 404 | Frontend route not configured | Check `frontend/src/pages/` for `/review/:token` page |

## Files to Check

| File | Purpose |
| --- |---------|
| `backend/models.py` | `ReviewToken`, `Feedback`, `Topic` schema and `is_valid()` method |
| `backend/routes/reviews.py` (or similar) | Review-related API endpoints |
| `frontend/src/pages/Review.vue` (or similar) | Review access UI for reviewers |
| `frontend/src/api/reviews.js` (or similar) | API wrappers for review endpoints |
| `docs/REVIEW_WORKFLOW_GUIDE.md` | User documentation for review lifecycle |
| `.env` | SMTP configuration for email notifications |

## Test Review E2E

### Without Authentication (External Reviewer)

```bash
# 1. Get a valid review token from admin UI or API
# 2. Access review page in frontend with token
http://localhost:3000/review/<token>
# 3. Should show review UI without login
# 4. Should allow adding feedback
```

### With Authentication (Internal Reviewer)

```bash
# 1. Login as internal user
# 2. Check dashboard or review list
# 3. Access review from list (no token needed)
# 4. Provide approval/feedback
# 5. Check status update
```

### Admin / Supervisor View

- Should see review progress
- Should see all feedback
- Should be able to move topic through workflow

## Debug Tips

1. **Enable request logging:** `FLASK_DEBUG=1` shows all requests/responses
2. **Check browser network tab:** See API calls and responses for review endpoints
3. **Review database state:** Query `ReviewToken`, `Feedback`, `Topic` directly
4. **Check email logs:** If using external email service, check its logs
5. **Trace token validation:** Add debug logging to `ReviewToken.is_valid()` temporarily

## Related Topics

- [docs/REVIEW_WORKFLOW_GUIDE.md](../../docs/REVIEW_WORKFLOW_GUIDE.md) — user guide
- [backend/models.py](../../backend/models.py) — review data model
- [docs/email-sending.md](../../docs/email-sending.md) — SMTP setup

**Read:** [.github/instructions/backend.instructions.md](../../.github/instructions/backend.instructions.md) for route patterns
