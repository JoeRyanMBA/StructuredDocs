# StructuredDocs Review Workflow - Quick Summary

## 5 Key Questions Answered

### 1️⃣ How are reviews currently created?

**Single at a time**: One request = one topic + one reviewer
- User selects 1 topic → Opens modal → Selects 1 reviewer → Creates 1 Review record
- **Endpoint**: `POST /api/reviews/request`
- **Sequential reviews**: Can add multiple reviewers to same topic (in queue), but each requires separate setup

**NO bulk creation endpoint exists** - must repeat for each topic-reviewer pair

---

### 2️⃣ How are review emails sent?

**Per-topic emails**: 
- 1 email per review (not per batch)
- Subject: `"Review Request: {topic_title} (Topic #{id})"`
- Contains: topic info, priority, due_date, message from author
- Includes secure token URL: `/review/{token}` 
- Called immediately when Review created via `email_service.send_review_notification()`

**No batch/digest emails** - each reviewer gets individual email per topic

---

### 3️⃣ Are there bulk review endpoints or UI?

**❌ NO**
- No `/api/reviews/batch` endpoint
- No `/api/reviews/request-multiple` endpoint
- No `BulkReviewModal` component
- No batch tracking UI
- No reviewer dashboard showing all assigned reviews

**Only single-topic workflows exist**

---

### 4️⃣ What does the reviewer experience look like?

**One link per topic**:
- Reviewer receives email with unique token: `/review/{token}`
- That token gives access to ONLY that one topic
- View topic content + existing feedback
- Submit feedback via form (structured: comments, text edits, suggestions)
- **Can't navigate** between topics with same token
- Each topic = separate email + separate link + separate browser tab

**No reviewer dashboard** - no way to see all assigned reviews in one place without logging in

---

### 5️⃣ What frontend UI exists?

**Frontend Components**:
- `ReviewsDashboard.vue` - Main review management dashboard
- `RequestReviewModal.vue` - Single-topic review request form
- `SequentialReviewModal.vue` - Multi-step reviewer queue (same topic)
- `ReviewFeedbackView.vue` - Viewing feedback from reviewers
- `ReviewCard.vue` - Card component in dashboard

**API Methods** (reviews.js):
- `requestReview()` - Create single review
- `getReviewers()` - Get available reviewers
- `getPendingReviews()` - Get pending reviews
- `submitReview()` - Submit completed review

**No bulk methods exist**

---

## Data Model

```
reviews (single topic-reviewer pair per row)
  ├─ topic_id, reviewer_id, requested_by
  ├─ status, priority, due_date
  ├─ feedback, recommendation
  └─ sequence_id (optional, for sequential reviews)

review_tokens (external access)
  ├─ token (unique per review)
  ├─ review_id (binds to 1 review)
  └─ expires_at, access_count limits

review_feedback (structured comments)
  ├─ review_id (N items per review)
  ├─ type: general_comment, text_edit, etc.
  ├─ section targeting (section_title, page_number, etc.)
  └─ priority, impact, author_response

review_sequences (for multi-reviewer same topic)
  ├─ Defines sequence of reviewers
  └─ Auto-advances after each approval
```

---

## What's Missing for Bulk Review Feature

| Component | Status | Gap |
|-----------|--------|-----|
| **Multi-topic request** | ❌ Missing | API + UI for selecting multiple topics |
| **Batch tracking** | ❌ Missing | DB table + progress endpoints + UI |
| **Reviewer dashboard** | ❌ Missing | View all assigned reviews in one place |
| **Email aggregation** | ❌ Missing | Digest email or batch notification |
| **Bulk feedback** | ❌ Missing | Accept all changes at once |
| **Topic navigation** | ❌ Missing | See related reviews from same batch |
| **Templates** | ❌ Missing | Save/reuse review configurations |

---

## Email Flow (Current)

```
User requests review
  ↓
Review created in DB
  ↓
ReviewToken created (unique per review)
  ↓
email_service.send_review_notification() called
  ├─ Format HTML email
  ├─ Format text email  
  ├─ Send via SendGrid
  └─ Log delivery status
  
Reviewer receives email
  ↓
Click /review/{token} link
  ↓
GET /api/review/{token} - fetch review content
  ↓
View topic + provide feedback
  ↓
POST /api/review/{token}/feedback - submit feedback
  ↓
Review marked completed
```

---

## Database Files Location

- **Models**: `/workspaces/StructuredDocs/backend/models.py` (lines 1107-1450)
- **Endpoints**: `/workspaces/StructuredDocs/backend/routes/reviews.py` (626 lines)
- **Token handling**: `/workspaces/StructuredDocs/backend/routes/review_tokens.py` (293 lines)
- **Email templates**: `/workspaces/StructuredDocs/backend/utils/email_service.py` (lines 633-715)

---

## Implementation Path (Phases)

### Phase 1: MVP Bulk (1-2 weeks)
- Add `POST /api/reviews/batch` endpoint
- Create `RequestBulkReviewModal.vue` (topic multi-select)
- Add ReviewBatch DB table
- Send reviews in async job

### Phase 2: Batch Tracking (1-2 weeks)  
- Progress endpoints
- BatchProgressTracker UI
- Cancel batch functionality

### Phase 3: Reviewer Dashboard (2 weeks)
- `GET /api/reviews/my-assigned` endpoint
- ReviewerDashboard.vue component
- Filter + search interface

### Phase 4: Advanced (3-4 weeks)
- Email aggregation
- Parallel reviewers
- Templates
- Bulk feedback incorporation

---

## Key Insights

1. **Current system is optimized for single-topic reviews** - all components assume 1 topic → 1 reviewer
2. **Sequential reviews work but are topic-scoped** - multiple reviewers for SAME topic, not multiple topics
3. **Email is per-topic** - no batching, no digest emails
4. **Reviewer experience is fragmented** - each topic requires separate link + email
5. **Schema is ready for bulk** - just need batch_id FK + ReviewBatch table
6. **Token system prevents reviewer dashboard** - tokens are topic-specific, not user-scoped

---

## Files to Read

- **Full Analysis**: `/workspaces/StructuredDocs/REVIEW_WORKFLOW_ANALYSIS.md` (742 lines)
- **Implementation Roadmap**: `/workspaces/StructuredDocs/BULK_REVIEW_TODO.md` (extensive code examples)
- **This Summary**: `/workspaces/StructuredDocs/REVIEW_SUMMARY.md` (you are here)

