# Review Workflow - Quick Reference Card

## Current Single-Topic Workflow
```
RequestReviewModal.vue
├─ Topic: Required (1 only)
├─ Reviewer: Required (1 only)  
├─ Priority: Optional
├─ Due Date: Optional
├─ Message: Optional
└─ Submit → POST /api/reviews/request → Creates 1 Review
            → Create ReviewToken (expires due_date + 7 days)
            → Send email via email_service.send_review_notification()
```

## Email Template Structure
```
Subject: Review Request: {topic_title} (Topic #{id})

Body (HTML + Text):
  Hello {reviewer_name},
  
  Topic #{topic_id}: {title}
  Priority: {priority}
  Due Date: {formatted_date}
  Message from Author: {message}
  
  [Start Review Button] → /review/{token}
```

## Reviewer Access Flow
```
Email received with /review/{token}
    ↓
GET /api/review/{token}
    ├─ Validate token (not expired, not used up)
    ├─ Return: topic content + feedback items + token info
    └─ Increment access_count
    ↓
Reviewer provides feedback
    ↓
POST /api/review/{token}/feedback
    ├─ Validate token again
    ├─ Create ReviewFeedback items
    ├─ Update Review status → completed
    ├─ Mark ReviewToken → used_at
    └─ Return success
    ↓
Author views feedback in ReviewFeedbackView.vue
```

## Sequential Review (Multiple Reviewers, 1 Topic)
```
SequentialReviewModal.vue
├─ Topic: Required (1 only)
├─ Add multiple reviewers in order
├─ Configure auto-advance & pause behavior
└─ Submit → Creates ReviewSequence + N Reviews
            → First Review starts
            → On completion, auto-creates next Review
            → Topic updated after each approval
```

## Database Quick Lookup
| Table | Key Fields | Purpose |
|-------|-----------|---------|
| `reviews` | topic_id, reviewer_id, requested_by, status, priority, sequence_id | Core review records |
| `review_tokens` | token, review_id, expires_at, access_count | External reviewer access |
| `review_feedback` | review_id, feedback_type, original_text, suggested_text, priority | Structured feedback |
| `review_sequences` | topic_id, status | Multi-step review orchestration |
| `review_sequence_steps` | sequence_id, position, reviewer_id | Individual steps in sequence |

## API Endpoints (All Single-Topic)
```
POST   /api/reviews/request                    - Create 1 review
POST   /api/reviews/{id}/start                 - Mark started
POST   /api/reviews/{id}/submit                - Submit completed review
POST   /api/reviews/{id}/follow-up             - Send reminder email
GET    /api/reviews/                           - List all
GET    /api/reviews/{id}                       - Details
GET    /api/reviews/reviewers                  - Available reviewers
GET    /api/reviews/pending                    - Filter pending
GET    /api/reviews/my-reviews?requester_id=X - Filter by requester
GET    /api/reviews/topic/{id}/reviews        - All reviews for topic
GET    /api/reviews/stats                     - Aggregated stats
GET    /api/review/{token}                    - Reviewer view (no auth)
POST   /api/review/{token}/feedback           - Submit feedback (no auth)
GET    /api/reviews/{id}/feedback             - Get feedback (auth)
```

## Frontend Components Location
```
/frontend/src/
├─ views/
│  ├─ ReviewsDashboard.vue        → Combined reviews table with search/filter
│  ├─ IncorporateFeedback.vue     → Completed reviews needing author action
│  ├─ ReviewFeedbackView.vue      → Word-level diff + per-item accept/reject
│  └─ BulkReviewPortal.vue        → Reviewer portal for bulk reviews (no auth)
├─ components/
│  ├─ ReviewDiffEditor.vue        → Word-level diff with Accept All / Reject All
│  ├─ RequestReviewModal.vue      → Single-topic review request
│  ├─ BulkRequestReviewModal.vue  → Multi-topic review request (≥2 topics)
│  ├─ SequentialReviewModal.vue   → Multi-step reviewer queue (same topic)
│  └─ ReviewPortal.vue            → Single-topic reviewer portal (no auth)
└─ api/
   └─ reviews.js                   → API methods (single + bulk)
```

## Email Service Key Methods
```python
# backend/utils/email_service.py

send_review_notification(
    reviewer_email,
    reviewer_name, 
    topic_title,
    topic_id,
    author_message,
    due_date,
    priority,
    review_token
)
→ Calls: _create_review_email_html() + _create_review_email_text()
→ Sends via self._send_email()

send_review_reminder(
    reviewer_email,
    reviewer_name,
    topic_title,
    due_date,
    review_token,
    is_follow_up=False
)
→ For overdue or manual follow-ups
```

## Token Security Model
```
ReviewToken fields:
├─ token (VARCHAR 64, unique, cryptographically secure)
├─ review_id (FK to reviews)
├─ reviewer_email
├─ expires_at (due_date + 7 days)
├─ accessed_at (first access timestamp)
├─ used_at (when feedback submitted)
├─ is_active (can be deactivated)
├─ access_count (current accesses)
└─ max_access_count (default 10, configurable)

Validation rules (ReviewToken.is_valid()):
✓ is_active == true
✓ not expired
✓ access_count < max_access_count
```

## Data Flow: Create → Email → Feedback
```
1. User clicks "Send for Review"
   ↓
2. RequestReviewModal opens (topic as prop)
   ↓
3. Select reviewer + priority + due_date + message
   ↓
4. Click "Request Review"
   ↓
5. POST /api/reviews/request
   ├─ Validate topic & reviewer
   ├─ Create Review record (status='pending')
   ├─ Create ReviewToken
   ├─ Call email_service.send_review_notification()
   │  ├─ Format HTML email
   │  ├─ Format text email
   │  └─ Send via SMTP/email provider
   ├─ Set Review.email_delivery_unavailable = true/false
   └─ Return {success, review}
   ↓
6. Reviewer receives email
   ↓
7. Clicks /review/{token} link
   ↓
8. Browser sends GET /api/review/{token}
   ├─ Validate token
   ├─ Return topic content + feedback_items + token_info
   └─ Increment access_count
   ↓
9. Reviewer fills feedback form
   ├─ General comments
   ├─ Text edits (original → suggested)
   ├─ Priority & impact ratings
   └─ Overall recommendation
   ↓
10. Click "Submit Feedback"
    ↓
11. POST /api/review/{token}/feedback
    ├─ Validate token
    ├─ Create ReviewFeedback items
    ├─ Update Review status='completed'
    ├─ Update ReviewToken used_at
    └─ Return {success, feedback_items_count}
    ↓
12. Author views feedback in ReviewFeedbackView.vue
    ├─ GET /api/reviews/{id}/feedback
    ├─ Display feedback items
    ├─ Can respond to each item
    └─ Track status (pending/accepted/rejected/modified)
```

## Bulk Review Endpoints
```
POST /api/reviews/bulk-request              (create ReviewBatch + N reviews + token + email)
GET  /api/bulk-review/<token>               (reviewer portal: all topics + progress)
POST /api/bulk-review/<token>/review/<id>/feedback  (submit feedback for one topic)
GET  /api/bulk-review/<token>/status        (per-topic completion state)
```

---

**For detailed analysis**: See `REVIEW_WORKFLOW_ANALYSIS.md`
**For overview**: See `REVIEW_SUMMARY.md`
