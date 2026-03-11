# StructuredDocs Review Workflow - Quick Summary

## 5 Key Questions Answered

### 1️⃣ How are reviews currently created?

**Single-topic or bulk**: Reviews can be created one at a time or in bulk (multiple topics to one reviewer in a single email).

- **Single**: User selects 1 topic → Opens modal → Selects 1 reviewer → Creates 1 Review record
  - **Endpoint**: `POST /api/reviews/request`
- **Bulk**: User selects ≥2 topics → Opens bulk modal → Selects 1 reviewer → Creates a `ReviewBatch` + N Review records + one shared token
  - **Endpoint**: `POST /api/reviews/bulk-request`
- **Sequential reviews**: Can add multiple reviewers to same topic (in queue), each reviewer is automatically notified when the previous completes

---

### 2️⃣ How are review emails sent?

**Per-review or per-batch emails**:
- **Single review**: 1 email per review
  - Subject: `"Review Request: {topic_title} (Topic #{id})"`
  - Contains: topic info, priority, due_date, message from author
  - Includes secure token URL: `/review/{token}`
- **Bulk review**: 1 email per batch (N topics, one link)
  - Subject: `"Review Request: {N} Topics Assigned for Review"`
  - Contains: numbered list of topic titles + single portal link: `/bulk-review/{token}`
- Sent immediately when Review/ReviewBatch is created

---

### 3️⃣ Are there bulk review endpoints or UI?

**✅ YES — implemented**
- `POST /api/reviews/bulk-request` — creates a `ReviewBatch` + N reviews + shared token + sends one email
- `GET /api/bulk-review/<token>` — reviewer portal: all topics with progress bar + prev/next navigation
- `POST /api/bulk-review/<token>/review/<id>/feedback` — per-topic feedback submission
- `GET /api/bulk-review/<token>/status` — per-topic completion state
- `BulkRequestReviewModal.vue` — select ≥2 topics, pick reviewer, configure and send
- `BulkReviewPortal.vue` — reviewer-facing portal with WYSIWYG editor and view toggle

---

### 4️⃣ What does the reviewer experience look like?

**Single-topic review**: Reviewer gets one email → one token link → `/review/{token}` for that topic only.

**Bulk review portal**: Reviewer gets one email → one token link → `/bulk-review/{token}`. The portal shows all assigned topics with a progress bar and prev/next navigation. Each topic has a WYSIWYG editor for inline edits plus a structured feedback form. Completed topics show a checkmark.

Both flows: reviewer leaves inline feedback (comments, text edits, recommendations), submits, and sees a confirmation screen.

---

### 5️⃣ What frontend UI exists?

**Frontend Components**:
- `ReviewsDashboard.vue` — Combined reviews table with search, filter, and status badges
- `IncorporateFeedback.vue` — Filtered list of completed reviews needing author action
- `ReviewFeedbackView.vue` — Word-level diff (accept/reject individual changes) + per-item feedback responses; Update Topic saves everything and returns topic to `draft`
- `ReviewDiffEditor.vue` — Word-level diff component; Accept All / Reject All or toggle individual segments
- `RequestReviewModal.vue` — Single-topic review request form
- `BulkRequestReviewModal.vue` — Multi-topic review request (≥2 topics, one reviewer, one email)
- `BulkReviewPortal.vue` — Reviewer-facing bulk review portal with WYSIWYG editor and progress tracking
- `SequentialReviewModal.vue` — Multi-step reviewer queue (same topic, ordered reviewers)
- `ReviewPortal.vue` — Single-topic reviewer portal (accessed via token link)

**API Methods** (reviews.js):
- `requestReview()` — Create single review
- `requestBulkReview()` — Create bulk review batch
- `getReviews()` — List all reviews
- `getReviewers()` — Get available reviewers
- `getPendingReviews()` — Get pending reviews
- `submitReview()` — Submit completed review
- `getBulkReview(token)` — Get bulk review portal data
- `submitBulkTopicFeedback(token, reviewId, data)` — Submit feedback for one topic in a batch

---

## Data Model

```
reviews (one topic-reviewer pair per row)
  ├─ topic_id, reviewer_id, requested_by
  ├─ status, priority, due_date
  ├─ feedback, recommendation, edited_content
  ├─ sequence_id (optional, for sequential reviews)
  └─ batch_id, batch_position (optional, for bulk reviews)

review_batches (groups N reviews for one reviewer)
  ├─ reviewer_id, requester_id
  ├─ status (pending / in_progress / completed)
  └─ priority, due_date, message

review_batch_tokens (portal access for bulk reviews)
  ├─ token (unique, shared across all topics in batch)
  ├─ batch_id
  └─ expires_at, access_count limits

review_tokens (external access for single reviews)
  ├─ token (unique per review)
  ├─ review_id (binds to 1 review)
  └─ expires_at, access_count limits

review_feedback (structured comments)
  ├─ review_id (N items per review)
  ├─ type: general_comment, text_edit, etc.
  ├─ section targeting (section_title, page_number, etc.)
  └─ priority, impact, author_response, status (pending/accepted/rejected/modified)

review_sequences (for multi-reviewer same topic)
  ├─ Defines sequence of reviewers
  └─ Auto-advances after each approval
```

---

## Email Flow

**Single review:**
```
POST /api/reviews/request
  ↓ Review + ReviewToken created
  ↓ email_service.send_review_notification()
Reviewer receives email → clicks /review/{token}
  ↓ GET /api/review/{token}
  ↓ POST /api/review/{token}/feedback
Review marked completed → topic status updated
```

**Bulk review:**
```
POST /api/reviews/bulk-request
  ↓ ReviewBatch + N Reviews + ReviewBatchToken created
  ↓ email_service.send_bulk_review_notification()
Reviewer receives email → clicks /bulk-review/{token}
  ↓ GET /api/bulk-review/{token}
  ↓ POST /api/bulk-review/{token}/review/{id}/feedback (per topic)
All topics reviewed → batch marked completed
```

---

## Database Files Location

- **Models**: `backend/models.py`
- **Single-review endpoints**: `backend/routes/reviews.py`
- **Bulk-review endpoints**: `backend/routes/bulk_reviews.py`
- **Token handling**: `backend/routes/review_tokens.py`
- **Email templates**: `backend/utils/email_service.py`

---

## Key Insights

1. **Both single-topic and bulk workflows are supported** — use bulk when sending the same reviewer multiple topics at once
2. **Sequential reviews are topic-scoped** — multiple reviewers for the SAME topic in order
3. **Feedback incorporation uses word-level diff** — `ReviewDiffEditor` shows reviewer edits as accept/reject toggles; `Update Topic` saves and returns the topic to `draft`
4. **Topic status is the source of truth** — `revisions_requested` means feedback awaits incorporation; `draft` means the author has incorporated changes (or is still writing)
5. **Tokens are scoped** — single-review tokens (`/review/{token}`) give access to one topic; batch tokens (`/bulk-review/{token}`) give access to the full portal for all topics in the batch

---

## Files to Read

- **Full Analysis**: `REVIEW_WORKFLOW_ANALYSIS.md`
- **This Summary**: `REVIEW_SUMMARY.md` (you are here)

