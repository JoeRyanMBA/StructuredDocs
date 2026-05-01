# StructuredDocs Review Workflow Analysis

## Executive Summary
StructuredDocs has a **single-topic, single-reviewer review system** with:
- Single review requests (1 topic → 1 reviewer at a time)
- Sequential multi-step review support (multiple reviewers in sequence)
- Secure token-based external reviewer access
- Structured feedback collection with text edits
- Email notifications for reviewers

**No bulk review features currently exist** - each review requires individual topic selection and reviewer assignment.

---

## 1. HOW REVIEWS ARE CURRENTLY CREATED

### Current Architecture
- **Model**: Single review per topic-reviewer pair
- **Approach**: Sequential single-topic workflow
- **Database**: 1 Review record = 1 topic + 1 reviewer assignment

### Creation Methods

#### A. Single Topic Review (Standard)
**Endpoint**: `POST /api/reviews/request` (JWT required)

**Request payload**:
```json
{
  "topic_id": 123,
  "reviewer_id": 456,
  "requested_by": 789,
  "priority": "medium|low|high|urgent",
  "message": "Please check for clarity",
  "due_date": "2025-03-15T00:00:00Z" (optional)
}
```

**Implementation** (backend/routes/reviews.py, lines 69-192):
1. Validates topic exists
2. Validates reviewer can review
3. Creates single Review record
4. Updates topic status to 'pending_review'
5. Creates ReviewToken for external access
6. Sends review notification email

**Frontend Component**: `RequestReviewModal.vue`
- Single topic selection (passed as prop)
- Single reviewer dropdown
- Single priority, due_date, message fields
- Submit creates ONE review

#### B. Sequential Multi-Step Review
**For same topic with multiple reviewers in sequence**

**Frontend Component**: `SequentialReviewModal.vue`
- Allows adding multiple reviewers in order
- Each reviewer reviews sequentially
- Creates ReviewSequence + individual Review records for each step

**How it works**:
1. Creates ReviewSequence record (topic_id, status='active')
2. For each reviewer, creates Review with sequence_id and sequence_position
3. First review starts immediately
4. On completion, auto-advances to next reviewer in sequence
5. Each reviewer only sees version after previous changes incorporated

**Models involved**:
- `ReviewSequence` (line 1377): Tracks multi-step review process
- `ReviewSequenceStep` (line 1412): Individual steps with reviewer assignments

### Key Limitation: NO BULK OPERATIONS
- ❌ Cannot request reviews for multiple topics at once
- ❌ Cannot send same topic to multiple reviewers in parallel
- ❌ Cannot batch operations via UI or API
- ❌ No `/api/reviews/request-bulk` endpoint
- ❌ No batch import/CSV functionality

**Current Workflow**:
```
User clicks "Send for Review" 
→ Opens RequestReviewModal 
→ Selects 1 topic 
→ Selects 1 reviewer 
→ Submits (creates 1 Review)
→ Repeat for each topic-reviewer pair
```

---

## 2. HOW REVIEW EMAILS ARE SENT

### Email Service Architecture
**File**: `backend/utils/email_service.py`

### Single-Topic Email Template
**Trigger**: When Review is created (`request_review()` endpoint, line 155)

**Email Method**: `send_review_notification()`
```python
def send_review_notification(self, reviewer_email, reviewer_name, topic_title, 
                           topic_id, author_message, due_date, priority, 
                           review_token, base_url=None)
```

**Email Content** (lines 633-715):

**Subject**: `"Review Request: {topic_title} (Topic #{topic_id})"`

**HTML Template** (line 646-673):
```html
Subject: Review Request: {topic_title} (Topic #{topic_id})

Hello {reviewer_name},

You have been requested to review the following document:

┌─────────────────────────────────────┐
│ Topic #{topic_id}: {topic_title}   │
│ Priority: {priority.title()}         │
│ Due Date: {formatted_due_date}       │
│ Message from Author: {author_message}│
└─────────────────────────────────────┘

[Start Review Button] → {review_url}

Please review and provide feedback.
```

**Text Template** (line 675-705):
- Same information in plain text
- Used as fallback

### Key Characteristics
- **Per-topic**: One email per review request
- **Per-reviewer**: Each reviewer gets individual email
- **Secure Link**: Unique token in URL: `/review/{token}`
- **No batching**: Each email sent individually
- **One email ≠ multiple topics**: No way to send "review 5 topics" in one email

### Email Delivery Tracking
- Field: `email_delivery_unavailable` (boolean on Review model)
- Set to `true` if email fails to send
- Logged but review still created

### Reminder Emails
**Trigger**: `POST /api/reviews/{review_id}/follow-up` endpoint (line 380)

**Method**: `send_review_reminder()`
- Sent when review overdue or manually triggered
- Same single-topic format
- Prefix: "Second Request:" for follow-ups

---

## 3. ARE THERE BULK REVIEW ENDPOINTS OR UI COMPONENTS?

### ❌ Bulk Review Endpoints: NONE

**Searched**:
- `backend/routes/reviews.py` (626 lines) - No bulk endpoints
- `frontend/src/api/reviews.js` - No bulk methods
- Database migrations - No bulk tables

**All review endpoints are single-topic**:
```
GET  /api/reviews/                           - List all reviews
GET  /api/reviews/<id>                       - Single review details
GET  /api/reviews/reviewers                  - List reviewers
POST /api/reviews/request                    - Request ONE review
POST /api/reviews/<id>/start                 - Start ONE review
POST /api/reviews/<id>/submit                - Submit ONE review
POST /api/reviews/<id>/follow-up             - Follow-up for ONE review
GET  /api/reviews/pending                    - Get pending reviews
GET  /api/reviews/my-reviews                 - Get my reviews (filter by requester)
GET  /api/reviews/topic/<id>/reviews         - Get all reviews for topic
GET  /api/reviews/stats                      - Stats (aggregated, not bulk)
```

### ❌ Bulk UI Components: NONE

**Reviewed components**:
- `RequestReviewModal.vue` - Single topic, single reviewer
- `SequentialReviewModal.vue` - Multiple reviewers (sequential), ONE topic
- `ReviewsDashboard.vue` - Viewing/managing reviews
- `ReviewFeedbackView.vue` - Viewing feedback

**All modals**:
- Take topic as prop (required: `{type: Object, required: true}`)
- Have single reviewer dropdown/selection
- Create single review on submit

### Dashboard Actions
```vue
<!-- ReviewsDashboard.vue line 64 -->
<button class="quick-action-card" @click="sendNewReview">
  <h3>Send for Review</h3>
</button>

// Implementation (line 340-342):
sendNewReview() {
  this.$router.push('/topics')  // Go to topics list
}
```

**Workflow**: User selects ONE topic from list, opens modal for that topic.

---

## 4. REVIEWER EXPERIENCE - SINGLE VS MULTIPLE TOPICS

### Current Reviewer Experience: ONE LINK PER TOPIC

**Access Method**: 
- Secure token URL: `{baseurl}/review/{token}`
- 32-character cryptographically secure token
- Stateless - no login required

**Per-Topic Limitation**:
```
Topic A → Email 1 → Token 1 → /review/token1
Topic B → Email 2 → Token 2 → /review/token2
Topic C → Email 3 → Token 3 → /review/token3
```

**Token Security**:
- Unique per review
- Expires: 7 days after due date
- Max accesses: 10 (configurable)
- Rate limited: 30 feedback submissions per hour per token

### What Reviewer Sees
**Endpoint**: `GET /api/review/<token>` (review_tokens.py, line 65)

**Returns**:
```json
{
  "review": {
    "id": 1,
    "topic_id": 123,
    "topic_title": "Database Design",
    "topic_content": "...",
    "author_message": "...",
    "due_date": "2025-03-15",
    "priority": "high",
    "status": "pending"
  },
  "feedback_items": [],  // Existing feedback from this review
  "token_info": {
    "access_count": 3,
    "max_access_count": 10,
    "expires_at": "..."
  }
}
```

**Can They Navigate Between Topics?** ❌ NO
- Each token is bound to ONE review (ONE topic)
- No "next" or "previous" navigation
- No dashboard or review list without authentication
- Each topic requires separate email/link

### Feedback Submission
**Endpoint**: `POST /api/review/<token>/feedback` (line 115)

**Structured feedback types**:
- `general_comment`
- `text_edit`, `text_addition`, `text_deletion`
- `structural_change`, `technical_correction`, `style_suggestion`

**Can include**:
- Section targeting (section_title, page_number, paragraph_number)
- Original text / Suggested text
- Comment and rationale
- Priority and impact ratings
- Edited content (full WYSIWYG editor output)

---

## 5. FRONTEND UI FOR CREATING/MANAGING REVIEWS

### UI Locations

#### A. **ReviewsDashboard.vue** (849 lines)
Main review management interface

**Quick Actions**:
```
[Send for Review] → routes to /topics list
[Review Guide]    → Shows help modal
[Incorporate Feedback] → routes to /reviews/incorporate
[Review History]  → routes to /reviews/history
```

**Dashboard Sections**:
1. **Metrics** (line 6-51):
   - Total Reviews, Pending, Completed, Avg Time, Overdue
   
2. **Urgent Reviews** (line 94-100):
   - Shows high-priority pending reviews
   
3. **Recent Reviews** (line 124-131):
   - Grid of recent review cards
   - Each card clickable → view details

4. **Review Lists** (multiple sections):
   - Pending reviews
   - Completed reviews
   - Filter by status/priority

**Create Flow**:
```
Click "Send for Review" 
→ Navigate to Topics list
→ Select ONE topic
→ Opens RequestReviewModal in context
```

#### B. **RequestReviewModal.vue** (317 lines)
Standard single-topic review creation

**Form Fields**:
1. **Topic Display** (read-only):
   - Topic title and summary
   
2. **Select Reviewer** (required):
   - Dropdown of can_review=true stakeholders
   - Loaded from `/api/reviews/reviewers` endpoint
   
3. **Priority** (optional):
   - Dropdown: Low, Medium, High, Urgent
   - Default: Medium
   
4. **Due Date** (optional):
   - Date picker
   - Min date: Today
   - Default: 7 days from today
   
5. **Message to Reviewer** (optional):
   - Textarea 4 rows
   - Example: "Please focus on technical accuracy"

**Submit Button**:
- Disabled while loading
- Shows "Request Review" → "Requesting..." during submit
- Emits `review-requested` event on success

#### C. **SequentialReviewModal.vue** (SequentialReviewModal.vue)
For multiple reviewers reviewing same topic in sequence

**Setup Fields**:
1. **Sequence Name** (optional): e.g., "Technical Review Process"
2. **Priority**: Low, Medium, High, Urgent
3. **Description**: Purpose of review sequence
4. **Initial Message**: To first reviewer (required)

**Reviewer Sequence**:
- "Expert-First Strategy" guidance
- Add/remove reviewers dynamically
- Reorder reviewers
- Set instructions per reviewer
- Configure auto-advance behavior

**Settings**:
- `auto_advance_on_approve`: Auto-advance if approve
- `pause_on_changes`: Pause if changes needed
- Shows step-by-step flow

**Submit**: Creates ReviewSequence + Review records for each step

#### D. **ReviewFeedbackView.vue** (431 lines)
Viewing and responding to feedback from reviewers

**Components**:
1. **Header** with breadcrumbs
2. **Topic Info** card:
   - Status, Requester, Last Updated, Priority
   
3. **Feedback Items**:
   - Shows each feedback item as card
   - Feedback type badge (text_edit, comment, etc.)
   - Section targeting info
   - Original vs. Suggested text comparison
   - Priority and impact pills
   
4. **Author Response** section:
   - Status (Pending, Accepted, Rejected, Modified)
   - Response text
   - Respond button

**Navigation**:
- Back to Reviews or Topics

### Review Status Lifecycle (UI Reflects)
```
pending 
  ↓
in_progress (when reviewer starts)
  ↓
completed (when reviewer submits)
  ↓
[View feedback]
```

**Status Badges**:
- Pending → Yellow (⏳)
- In Progress → Blue (🔄)
- Completed → Green (✅)
- Overdue → Red (⚠️)

### File Structure
```
frontend/src/
├── views/
│   ├── ReviewsDashboard.vue          (Main dashboard)
│   ├── ReviewFeedbackView.vue        (Feedback viewing)
│   └── ReviewHistory.vue             (History view)
├── components/
│   ├── RequestReviewModal.vue        (Single-topic modal)
│   ├── SequentialReviewModal.vue     (Multi-reviewer modal)
│   ├── ReviewCard.vue                (Card component)
│   └── ...
└── api/
    └── reviews.js                     (API methods)
```

### API Methods (frontend/src/api/reviews.js)
```javascript
getReviews()                    - List all
getReviewers()                  - List available reviewers
requestReview(reviewData)       - Create ONE review
startReview(reviewId)           - Mark started
submitReview(reviewId, data)    - Submit completed
getPendingReviews()             - Filter pending
getMyReviews(requesterId)       - Filter by requester
getTopicReviews(topicId)        - Get all reviews for topic
getReviewStats()                - Aggregated stats
sendFollowUpReminder(reviewId)  - Send reminder
```

**No bulk methods exist**.

---

## 6. DATA MODEL SCHEMA

### Core Tables

#### **reviews** (Review model, line 1107)
```sql
id                          INT PK
topic_id                    INT FK → topics.id
requested_by               INT FK → stakeholders.id (author)
reviewer_id                INT FK → stakeholders.id
status                     ENUM (pending, in_progress, completed, declined)
priority                   ENUM (low, medium, high, urgent)
requested_at              DATETIME
due_date                  DATETIME NULL
started_at                DATETIME NULL
completed_at              DATETIME NULL
follow_up_sent_at         DATETIME NULL
email_delivery_unavailable BOOLEAN (for failed email tracking)
feedback                  TEXT NULL (overall feedback)
recommendation            ENUM (approve, approve_with_changes, reject, needs_more_info)
review_notes              TEXT NULL (private reviewer notes)
author_message            TEXT NULL (from requester)
edited_content            TEXT NULL (WYSIWYG editor output)
sequence_id               INT FK → review_sequences.id NULL (for sequential reviews)
sequence_position         INT NULL (position in sequence)

INDEXES:
- topic_id
- status
- reviewer_id
- requested_at
```

#### **review_tokens** (ReviewToken model, line 1245)
```sql
id                      INT PK
token                   VARCHAR(64) UNIQUE
review_id              INT FK → reviews.id
reviewer_email         VARCHAR(120)
created_at             DATETIME
expires_at             DATETIME
accessed_at            DATETIME NULL
used_at                DATETIME NULL
is_active              BOOLEAN
access_count           INT (current accesses)
max_access_count       INT (limit, default 10)

INDEX: token
```

#### **review_feedback** (ReviewFeedback model, line 1300)
```sql
id                INT PK
review_id         INT FK → reviews.id
feedback_type     ENUM (general_comment, text_edit, text_addition, 
                        text_deletion, structural_change, 
                        technical_correction, style_suggestion)
section_title     VARCHAR(200) NULL
page_number       INT NULL
paragraph_number  INT NULL
line_reference    VARCHAR(100) NULL
original_text     TEXT NULL
suggested_text    TEXT NULL
comment           TEXT NOT NULL
rationale         TEXT NULL
priority          ENUM (low, medium, high, critical)
impact            ENUM (minor, moderate, major)
author_response   TEXT NULL (author's reply)
status            ENUM (pending, accepted, rejected, modified)
created_at        DATETIME
responded_at      DATETIME NULL

Allows: Multiple feedback items per review
```

#### **review_sequences** (ReviewSequence model, line 1377)
```sql
id             INT PK
topic_id       INT FK → topics.id
name           VARCHAR(200)
description    TEXT NULL
status         ENUM (active, inactive, completed)
created_at     DATETIME

Relationships:
- steps: ReviewSequenceStep[] (0-based order)
- reviews: Review[] (one per step)
```

#### **review_sequence_steps** (ReviewSequenceStep model, line 1412)
```sql
id               INT PK
sequence_id      INT FK → review_sequences.id
position         INT (0-based order)
reviewer_id      INT FK → stakeholders.id NULL
reviewer_role    VARCHAR(100) NULL (e.g., 'SME', 'Legal')
name             VARCHAR(200)
instructions     TEXT NULL

Relationships:
- reviewer: Stakeholder
- sequence: ReviewSequence
```

### Key Observations
- **No batch tables**: No "bulk_reviews", "review_batches", or "review_jobs"
- **Single-topic design**: Each Review is 1:1 with Topic
- **Sequential via join**: Multi-reviewer achieved via sequence_id foreign key + position
- **Feedback is atomic**: Each comment is separate ReviewFeedback row
- **Token is ephemeral**: For external access, not stored long-term in URL

---

## 7. WHAT'S MISSING FOR BULK REVIEW FEATURE

### Critical Gaps

#### A. Database Schema
- ❌ No `review_batches` table to group related reviews
- ❌ No `batch_id` foreign key on `reviews` table
- ❌ No batch status tracking (queued, in_progress, completed)
- ❌ No batch creation timestamp and completed_at

#### B. Backend Endpoints
- ❌ `POST /api/reviews/batch` - Create multiple reviews at once
- ❌ `POST /api/reviews/batch/send` - Send all notifications
- ❌ `GET /api/reviews/batches` - List all batches
- ❌ `GET /api/reviews/batches/<id>` - Batch details
- ❌ `GET /api/reviews/batches/<id>/progress` - Real-time progress
- ❌ `PUT /api/reviews/batches/<id>/cancel` - Cancel pending batch
- ❌ `POST /api/reviews/request-multiple` - Explicit bulk endpoint

#### C. Frontend UI
- ❌ Bulk review creation modal (multi-select topics)
- ❌ Topic selection table/checkboxes
- ❌ Reviewer assignment matrix (topics × reviewers)
- ❌ Batch preview before submission
- ❌ Batch progress tracking / real-time status
- ❌ Bulk email preview / customization
- ❌ Batch reports and analytics

#### D. Email System
- ❌ Batch email template (aggregating multiple topics)
- ❌ Digest emails (e.g., "5 reviews requested")
- ❌ Single email with multiple review links
- ❌ Batch email scheduling/queue management

#### E. Reviewer Experience
- ❌ Dashboard for assigned reviews (currently need separate links)
- ❌ Unified review interface for multiple topics
- ❌ Batch feedback submission
- ❌ Review prioritization and filtering

#### F. Feedback Handling
- ❌ Bulk feedback incorporation
- ❌ Batch status updates (e.g., "all approve")
- ❌ Bulk "accept all changes" functionality

### Implementation Complexity

| Feature | Complexity | Time Est. | Dependencies |
|---------|-----------|----------|--------------|
| Batch table schema | Low | 2h | Alembic migration |
| Bulk endpoint | Medium | 4h | Error handling, transaction management |
| UI modal | Medium | 6h | Vue component design, validation |
| Email batching | High | 8h | Email template restructuring, SMTP templates |
| Progress tracking | High | 10h | WebSockets/polling, async jobs (Celery) |
| Reviewer dashboard | High | 12h | Frontend routing, authentication |
| **Total** | **High** | **~42h** | **Full backend + frontend overhaul** |

---

## 8. CURRENT LIMITATIONS & EDGE CASES

### Workflow Limitations
1. **UI Friction**: Must select topic → open modal (vs. table multi-select)
2. **One at a time**: No parallel reviewer assignment
3. **Same configuration required**: Each review requires separate topic selection
4. **No templates**: No reusable review configurations
5. **No scheduling**: All reviews sent immediately

### Reviewer Limitations
1. **Multiple emails**: One email per topic (inbox spam)
2. **No dashboard**: Can't see all assigned reviews in one place
3. **Token per topic**: Can't browse between topics with same token
4. **Context switching**: Each topic requires separate browser tab/window
5. **No search/filter**: Can't search feedback across all reviews

### Feedback Limitations
1. **Per-review**: Feedback is isolated by review_id
2. **No cross-topic analysis**: Can't correlate feedback across topics
3. **No bulk actions**: Can't accept all changes at once
4. **Manual incorporation**: Author must manually integrate each feedback item

### Email Limitations
1. **No digest**: No "5 reviews requested" email
2. **Individual send**: Each email sent in separate SMTP transaction
3. **No customization**: Same template for all topics
4. **No scheduling**: No scheduled batch delivery
5. **No tracking**: Basic delivery status only

---

## 9. RECOMMENDATIONS FOR BULK REVIEW IMPLEMENTATION

### Phase 1: Minimal Viable Bulk Feature (1-2 weeks)
**Goal**: Multi-topic in single request, still single-reviewer

1. **Backend**:
   - Add `POST /api/reviews/request-multiple` endpoint
   - Accept array of topic_ids + single reviewer_id
   - Loop and create Reviews in transaction
   - Send emails in background job (Celery)

2. **Frontend**:
   - Modify modal to accept topic multi-select
   - Add checkbox table for topic selection
   - Show count: "Request review for 5 topics"

3. **Database**: No schema changes needed

### Phase 2: Review Batches (2-3 weeks)
**Goal**: Track related reviews, show progress

1. **Database**:
   - Add `review_batches` table
   - Add `batch_id` to `reviews` FK

2. **Backend**:
   - Track batch status and progress
   - Batch summary endpoint
   - Cancel batch endpoint

3. **Frontend**:
   - Batch tracking page
   - Progress bar (X of Y sent, Y pending, Z complete)

### Phase 3: Reviewer Dashboard (2 weeks)
**Goal**: Reviewers see all assigned reviews in one place

1. **Backend**:
   - `GET /api/reviewers/{id}/assigned-reviews`
   - Paginated list with filters

2. **Frontend**:
   - New view: "/reviews/assigned"
   - Table with all reviews (topic, priority, due_date)
   - Click to open specific review

3. **Database**: No changes (use existing relationships)

### Phase 4: Advanced Features (3-4 weeks)
- Parallel reviewers (same topic, multiple reviewers simultaneously)
- Review templates
- Bulk feedback incorporation
- Email digest/aggregation
- WebSocket-based real-time progress
- Reviewer dashboard with search/filter

---

## SUMMARY TABLE

| Feature | Current Status | Bottleneck | Gap Severity |
|---------|----------------|-----------|--------------|
| Single topic review | ✅ Full | - | N/A |
| Sequential reviews | ✅ Full | - | N/A |
| Token-based access | ✅ Full | - | N/A |
| Email notifications | ✅ Full (single) | Email per topic | N/A |
| **Bulk topics** | ❌ None | API + UI | **CRITICAL** |
| **Batch tracking** | ❌ None | DB + API | **HIGH** |
| **Reviewer dashboard** | ❌ None | API + UI | **HIGH** |
| **Email aggregation** | ❌ None | Email service | **MEDIUM** |
| **Parallel reviewers** | ⚠️ Partial (sequential only) | Logic + API | **MEDIUM** |
| **Bulk feedback** | ❌ None | UI + API | **LOW** |

---

## FILE REFERENCE

### Backend
- `/workspaces/StructuredDocs/backend/routes/reviews.py` (626 lines) - All endpoints
- `/workspaces/StructuredDocs/backend/routes/review_tokens.py` (293 lines) - Token handling
- `/workspaces/StructuredDocs/backend/models.py` (lines 1107-1450) - All models
- `/workspaces/StructuredDocs/backend/utils/email_service.py` (lines 105-715) - Email templates

### Frontend
- `/workspaces/StructuredDocs/frontend/src/views/ReviewsDashboard.vue` (849 lines)
- `/workspaces/StructuredDocs/frontend/src/views/ReviewFeedbackView.vue` (431 lines)
- `/workspaces/StructuredDocs/frontend/src/components/RequestReviewModal.vue` (317 lines)
- `/workspaces/StructuredDocs/frontend/src/components/SequentialReviewModal.vue` (long)
- `/workspaces/StructuredDocs/frontend/src/api/reviews.js` (86 lines)

### Database Migrations
- `backend/migrations/versions/a1b2c3d4e5f6_create_reviews_table.py`
- `backend/migrations/versions/e43f15c67e8b_add_review_sequences_tables.py`
- `backend/migrations/versions/f4b8d9a1c2e3_add_email_delivery_unavailable_to_reviews.py`

