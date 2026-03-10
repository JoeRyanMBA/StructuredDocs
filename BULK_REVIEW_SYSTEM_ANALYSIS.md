# StructuredDocs Review System - Complete Analysis for Bulk Review Feature

## 1. BACKEND MODELS

### 1.1 Review Model
**File**: `/workspaces/StructuredDocs/backend/models.py` (Lines 1107-1208)

**Columns & Relationships**:
```python
id (Integer, PK)
topic_id (Integer, FK → topics.id) - What's being reviewed
requested_by (Integer, FK → stakeholders.id) - Author/requester
reviewer_id (Integer, FK → stakeholders.id) - Assigned reviewer
status (Enum: 'pending', 'in_progress', 'completed', 'declined')
priority (Enum: 'low', 'medium', 'high', 'urgent')
requested_at (DateTime, default=now)
due_date (DateTime, nullable)
started_at (DateTime, nullable)
completed_at (DateTime, nullable)
follow_up_sent_at (DateTime, nullable)
email_delivery_unavailable (Boolean, default=False)
feedback (Text, nullable)
recommendation (Enum: 'approve', 'approve_with_changes', 'reject', 'needs_more_info')
review_notes (Text, nullable) - Private notes from reviewer
author_message (Text, nullable) - Context from requester
edited_content (Text, nullable) - WYSIWYG editor edits
sequence_id (Integer, FK → review_sequences.id, nullable) - For multi-step reviews
sequence_position (Integer, nullable) - Position in sequence (0-based)

Relationships:
- topic: relationship('Topic', backref='reviews')
- requester: relationship('Stakeholder', foreign_keys=[requested_by], backref='requested_reviews')
- reviewer: relationship('Stakeholder', foreign_keys=[reviewer_id], backref='assigned_reviews')
- sequence: relationship('ReviewSequence', back_populates='reviews')

Indexes:
- ix_reviews_topic_id
- ix_reviews_status
- ix_reviews_reviewer_id
- ix_reviews_requested_at
```

**to_dict() Output**:
```json
{
  "id": int,
  "topic_id": int,
  "topic_title": string,
  "topic_status": string,
  "requested_by": int,
  "requester_name": string,
  "reviewer_id": int,
  "reviewer_name": string,
  "status": string,
  "priority": string,
  "requested_at": ISO datetime,
  "due_date": ISO datetime,
  "started_at": ISO datetime,
  "completed_at": ISO datetime,
  "follow_up_sent_at": ISO datetime,
  "email_delivery_unavailable": boolean,
  "feedback": string,
  "recommendation": string,
  "review_notes": string,
  "author_message": string,
  "edited_content": string,
  "sequence_id": int,
  "sequence_position": int
}
```

---

### 1.2 ReviewToken Model
**File**: `/workspaces/StructuredDocs/backend/models.py` (Lines 1245-1297)

**Purpose**: Secure tokens for external reviewer access without authentication

**Columns**:
```python
id (Integer, PK)
token (String(64), UNIQUE, indexed) - URL-safe secure token
review_id (Integer, FK → reviews.id)
reviewer_email (String(120))
created_at (DateTime, default=now)
expires_at (DateTime) - Token expiration time
accessed_at (DateTime, nullable)
used_at (DateTime, nullable) - When review was submitted
is_active (Boolean, default=True)
access_count (Integer, default=0) - Tracks access attempts
max_access_count (Integer, default=10) - Access limit

Relationships:
- review: relationship("Review", backref="tokens")
```

**to_dict() Output**:
```json
{
  "id": int,
  "token": string,
  "review_id": int,
  "reviewer_email": string,
  "created_at": ISO datetime,
  "expires_at": ISO datetime,
  "accessed_at": ISO datetime,
  "used_at": ISO datetime,
  "is_active": boolean,
  "access_count": int,
  "max_access_count": int
}
```

**Validation Method**: `is_valid()` returns (bool, message)
- Checks if token is active
- Checks if token has expired
- Checks if access limit exceeded

---

### 1.3 ReviewFeedback Model
**File**: `/workspaces/StructuredDocs/backend/models.py` (Lines 1300-1375)

**Purpose**: Structured feedback items with suggested changes

**Columns**:
```python
id (Integer, PK)
review_id (Integer, FK → reviews.id)

feedback_type (Enum: 'general_comment', 'text_edit', 'text_addition', 
               'text_deletion', 'structural_change', 'technical_correction', 
               'style_suggestion')

section_title (String(200), nullable)
page_number (Integer, nullable)
paragraph_number (Integer, nullable)
line_reference (String(100), nullable)

original_text (Text, nullable)
suggested_text (Text, nullable)
comment (Text, required) - Main feedback
rationale (Text, nullable) - Why the change is needed

priority (Enum: 'low', 'medium', 'high', 'critical')
impact (Enum: 'minor', 'moderate', 'major')

author_response (Text, nullable) - Author's response to feedback
status (Enum: 'pending', 'accepted', 'rejected', 'modified')

created_at (DateTime, default=now)
responded_at (DateTime, nullable)

Relationships:
- review: relationship("Review", backref="feedback_items")
```

**to_dict() Output**:
```json
{
  "id": int,
  "review_id": int,
  "feedback_type": string,
  "section_title": string,
  "page_number": int,
  "paragraph_number": int,
  "line_reference": string,
  "original_text": string,
  "suggested_text": string,
  "comment": string,
  "rationale": string,
  "priority": string,
  "impact": string,
  "author_response": string,
  "status": string,
  "created_at": ISO datetime,
  "responded_at": ISO datetime
}
```

---

### 1.4 Stakeholder Model
**File**: `/workspaces/StructuredDocs/backend/models.py` (Lines 620-671)

**Purpose**: Reusable person who can be author, reviewer, or SME

**Columns**:
```python
id (Integer, PK)
name (String(100), required)
email (String(120), required, UNIQUE)
title (String(200), nullable)
organization (String(200), nullable)
division (String(200), nullable)
department (String(200), nullable)
phone (String(20), nullable)
expertise_areas (Text, nullable) - JSON string of expertise areas
bio (Text, nullable)
role (Enum: 'author', 'reviewer', 'subject_matter_expert', 'stakeholder', 'admin')
can_review (Boolean, default=True)
active (Boolean, default=True)
created_at (DateTime, default=now)
updated_at (DateTime, default=now, onupdate=now)
```

**to_dict() Output**:
```json
{
  "id": int,
  "name": string,
  "email": string,
  "title": string,
  "organization": string,
  "division": string,
  "department": string,
  "phone": string,
  "expertise_areas": string,
  "bio": string,
  "role": string,
  "can_review": boolean,
  "active": boolean,
  "created_at": ISO datetime,
  "updated_at": ISO datetime
}
```

---

### 1.5 ReviewSequence & ReviewSequenceStep Models
**File**: `/workspaces/StructuredDocs/backend/models.py` (Lines 1377-1442)

**ReviewSequence** - Multi-step review process
```python
id (Integer, PK)
topic_id (Integer, FK → topics.id)
name (String(200))
description (Text, nullable)
status (Enum: 'active', 'inactive', 'completed')
created_at (DateTime, default=now)

Relationships:
- topic: relationship('Topic', backref='review_sequences')
- steps: relationship('ReviewSequenceStep', ordered by position)
- reviews: relationship('Review', back_populates='sequence')
```

**ReviewSequenceStep** - Individual step in sequence
```python
id (Integer, PK)
sequence_id (Integer, FK → review_sequences.id)
position (Integer) - 0-based index
reviewer_id (Integer, FK → stakeholders.id, nullable)
reviewer_role (String(100), nullable) - e.g., 'SME', 'Legal'
name (String(200))
instructions (Text, nullable)

Relationships:
- sequence: relationship('ReviewSequence', back_populates='steps')
- reviewer: relationship('Stakeholder')
```

---

## 2. BACKEND ROUTES

### 2.1 Main Review Endpoints
**File**: `/workspaces/StructuredDocs/backend/routes/reviews.py`

#### POST `/api/reviews/request`
**Purpose**: Request a review for a single topic with one reviewer

**Request Body**:
```json
{
  "topic_id": integer (required),
  "reviewer_id": integer (required),
  "requested_by": integer (optional - auto-resolved),
  "requester_email": string (optional fallback),
  "requester_name": string (optional fallback),
  "priority": string ("low"|"medium"|"high"|"urgent", default="medium"),
  "message": string (optional - author message),
  "due_date": ISO datetime (optional - defaults to 7 days)
}
```

**Response**:
```json
{
  "message": "Review requested successfully",
  "review": { review.to_dict() }
}
```

**Side Effects**:
1. Creates Review record with status='pending'
2. Updates Topic.status to 'pending_review'
3. Creates ReviewToken (urlsafe token, 30-day default expiration)
4. **SENDS EMAIL** via email_service.send_review_notification() with review token URL
5. Sets review.email_delivery_unavailable flag based on email success

---

#### GET `/api/reviews/`
Returns all reviews, ordered by requested_at DESC

---

#### GET `/api/reviews/<int:review_id>`
Returns single review with feedback_items array

**Response**:
```json
{
  ...review.to_dict(),
  "feedback_items": [feedback.to_dict()]
}
```

---

#### GET `/api/reviews/reviewers`
Returns stakeholders with can_review=True and role in ['reviewer', 'subject_matter_expert', 'stakeholder']

**Response**:
```json
[
  {
    "id": int,
    "name": string,
    "email": string,
    "role": string,
    "division": string
  }
]
```

---

#### POST `/api/reviews/<int:review_id>/start`
Marks review as 'in_progress', sets started_at=now

---

#### POST `/api/reviews/<int:review_id>/submit`
Completes review with feedback

**Request Body**:
```json
{
  "recommendation": "approve|approve_with_changes|reject|needs_more_info" (required),
  "feedback": string (optional - overall feedback),
  "review_notes": string (optional - private notes)
}
```

**Side Effects**:
- Updates review.status='completed', completed_at=now
- Updates review.recommendation & feedback
- Updates topic.status based on recommendation
- If part of ReviewSequence: auto-advances to next reviewer (if configured)

---

#### POST `/api/reviews/<int:review_id>/follow-up`
Sends reminder email to reviewer for pending review

**Response**:
```json
{
  "message": "Follow-up reminder sent successfully",
  "review": review.to_dict(),
  "email_sent": boolean
}
```

---

#### GET `/api/reviews/pending`
Returns pending/in_progress reviews, optionally filtered by reviewer_id

**Query Params**:
- `reviewer_id` (optional) - filter by reviewer

---

#### GET `/api/reviews/my-reviews`
Returns reviews requested by a specific user

**Query Params**:
- `requester_id` (required) - stakeholder who requested the reviews

---

#### GET `/api/reviews/topic/<int:topic_id>/reviews`
Returns all reviews for a specific topic

---

#### GET `/api/reviews/stats`
Returns review statistics

**Response**:
```json
{
  "total": int,
  "pending": int,
  "in_progress": int,
  "completed": int,
  "overdue": int,
  "avg_completion_days": float,
  "topics": { "total": int, "pending_review": int, "draft": int, "published": int },
  "imports": { "total": int, "pending": int, "sme_approved": int, "final_approved": int }
}
```

---

### 2.2 Review Token Routes (External Access)
**File**: `/workspaces/StructuredDocs/backend/routes/review_tokens.py`

#### GET `/api/review/<token>`
**Purpose**: Get review content using secure token (no auth required)

**Validation**:
- Token must exist and be valid (active, not expired, within access limit)
- Increments access_count
- Sets accessed_at on first access

**Response**:
```json
{
  "success": true,
  "review": {
    "id": int,
    "topic_id": int,
    "topic_title": string,
    "topic_content": string (HTML),
    "author_message": string,
    "due_date": ISO datetime,
    "priority": string,
    "status": string
  },
  "feedback_items": [feedback.to_dict()],
  "token_info": {
    "access_count": int,
    "max_access_count": int,
    "expires_at": ISO datetime
  }
}
```

---

#### POST `/api/review/<token>/feedback`
**Purpose**: Submit structured feedback using token

**Request Body**:
```json
{
  "feedback_items": [
    {
      "feedback_type": string,
      "section_title": string,
      "page_number": int,
      "paragraph_number": int,
      "line_reference": string,
      "original_text": string,
      "suggested_text": string,
      "comment": string,
      "rationale": string,
      "priority": string,
      "impact": string
    }
  ],
  "recommendation": string,
  "feedback": string (overall feedback),
  "edited_content": string (optional - HTML from WYSIWYG editor)
}
```

**Side Effects**:
1. Creates ReviewFeedback records for each item
2. Updates review with recommendation, feedback
3. If edited_content + "approve_with_changes": **applies edits directly to topic.content**
4. Sets review.status='completed', completed_at=now
5. Marks token as used

**Response**:
```json
{
  "success": true,
  "message": "Feedback submitted successfully",
  "feedback_items_count": int,
  "content_updated": boolean
}
```

---

#### GET `/api/reviews/<int:review_id>/feedback`
Gets feedback items for a review (author view)

**Response**:
```json
{
  "success": true,
  "review_id": int,
  "feedback_items": [feedback.to_dict()],
  "summary": {
    "total_items": int,
    "pending": int,
    "accepted": int,
    "rejected": int
  }
}
```

---

#### PUT `/api/feedback/<int:feedback_id>/respond`
Author responds to specific feedback

**Request Body**:
```json
{
  "author_response": string,
  "status": "accepted|rejected|modified"
}
```

---

## 3. EMAIL SERVICE

**File**: `/workspaces/StructuredDocs/backend/utils/email_service.py`

### EmailService Class

**Configuration**:
```python
SMTP_SERVER (default: 'localhost')
SMTP_PORT (default: 587)
SMTP_USERNAME (optional)
SMTP_PASSWORD (optional)

FROM_EMAIL (default: 'noreply@structureddocs.local')
FROM_NAME (default: 'StructuredDocs Review System')

EMAIL_PROVIDER ('postmark'|'resend'|'sendgrid') - Optional HTTP API provider
POSTMARK_API_TOKEN
POSTMARK_MESSAGE_STREAM (default: 'outbound')
RESEND_API_KEY
SENDGRID_API_KEY
SENDGRID_VERIFIED_SENDER

EMAIL_DEBUG (boolean, default: false) - Writes emails to files instead of sending
```

### Key Methods

#### send_review_notification()
```python
def send_review_notification(self, 
    reviewer_email: str,
    reviewer_name: str,
    topic_title: str,
    topic_id: int,
    author_message: str,
    due_date: datetime,
    priority: str,
    review_token: str,
    base_url: str = None  # defaults to FRONTEND_URL env var
) -> bool
```

**Email Format**:
- Subject: "Review Request: {topic_title} (Topic #{topic_id})"
- HTML + Plain text versions
- Includes: topic ID, priority, due date, author message, secure review link
- CTA button: "Start Review"
- URL pattern: `{base_url}/review/{review_token}`

---

#### send_review_reminder()
```python
def send_review_reminder(self,
    reviewer_email: str,
    reviewer_name: str,
    topic_title: str,
    due_date: datetime,
    review_token: str,
    base_url: str = None,
    is_follow_up: bool = False
) -> bool
```

**Email Format**:
- Subject: "Review Reminder: {topic_title}" or "Second Request: Review Reminder: {topic_title}"
- Different greeting based on is_follow_up flag
- Includes urgent tone if follow-up

---

#### send_review_request()
```python
def send_review_request(self,
    reviewer_email: str,
    reviewer_name: str,
    topic_title: str,
    author_name: str,
    due_date: datetime,
    review_url: str,
    author_message: str = "",
    is_sequential: bool = False,
    sequence_position: int = None,
    total_reviewers: int = None
) -> bool
```

**Email Format**:
- Subject: "Review Request: {topic_title}" or "Sequential Review Request (Step X of Y): {topic_title}"
- Handles sequential review context

---

#### Internal Template Methods
- `_create_review_email_html()` - HTML template for review notifications
- `_create_review_email_text()` - Plain text version
- `_create_reminder_email_html()` - Reminder email HTML
- `_create_reminder_email_text()` - Reminder email text
- `_create_review_request_email_html()` - Request email HTML
- `_create_review_request_email_text()` - Request email text
- `_create_password_setup_email_html()` / `_text()` - Password setup
- `_create_password_reset_email_html()` / `_text()` - Password reset

**Delivery Methods**:
1. **Provider HTTP API**: If EMAIL_PROVIDER set (Postmark, Resend, SendGrid)
2. **SMTP Fallback**: STARTTLS on port 587 or SSL
3. **Debug Mode**: Writes to `backend/debug_emails/` directory (if EMAIL_DEBUG=true)

---

## 4. FRONTEND REVIEW COMPONENTS

### 4.1 RequestReviewModal.vue
**Path**: `/workspaces/StructuredDocs/frontend/src/components/RequestReviewModal.vue`

**Purpose**: Modal for requesting a single review on a topic

**Props**:
```javascript
{
  topic: Object (required) - Topic to review
  isVisible: Boolean (default: false)
  currentUser: Object (required)
}
```

**Data**:
```javascript
{
  reviewers: [],
  selectedReviewer: '',
  priority: 'medium',
  dueDate: '',
  message: '',
  loading: false
}
```

**Features**:
- Fetches available reviewers on mount
- Dropdown selector for single reviewer
- Priority dropdown (Low, Medium, High, Urgent)
- Date picker for due date (min = today)
- Message textarea for author context
- Submit/Cancel actions
- Toast notifications for success/error

**Emits**: `review-requested` on successful submission

---

### 4.2 ReviewPortal.vue
**Path**: `/workspaces/StructuredDocs/frontend/src/views/ReviewPortal.vue`

**Purpose**: External reviewer portal - accessed via secure token (no auth required)

**Key Features**:

1. **Token Validation**
   - Loads review content using token from URL
   - Shows errors: invalid token, expired, access limit exceeded, deactivated
   - Retry mechanism with helpful error messages

2. **Content Display**
   - Topic title, ID, due date, priority
   - Author message
   - Original content (read-only view)
   - WYSIWYG editor view for direct editing

3. **Content Editing**
   - Quill editor for WYSIWYG editing
   - Change detection with change count
   - Reset to original button
   - Preview changes (shows before/after)
   - Smart recommendation: "Approve with your edits" appears when content modified

4. **Previous Feedback Display**
   - Shows existing feedback items from prior reviews
   - Displays feedback type, priority, comment, original/suggested text

5. **Feedback Submission Form**
   - Overall Recommendation dropdown:
     - Approve (as submitted or original content)
     - Approve with changes/edits
     - Request more information
     - Reject
   - Overall Comments textarea
   - Specific Feedback Items section:
     - Type (General, Text Edit, Text Addition, Deletion, Technical, Style)
     - Priority (Low, Medium, High, Critical)
     - Section/Location reference
     - Original text (conditional)
     - Suggested text (conditional on type)
     - Comment (required)
     - Rationale (optional)
   - Add/Remove feedback items dynamically
   - Submit Review button
   - Save Draft button

6. **Success State**
   - Confirmation message after submission
   - Thank you text

**Data**:
```javascript
{
  loading: true,
  error: null,
  review: {},
  tokenInfo: {},
  existingFeedback: [],
  
  overallRecommendation: '',
  overallFeedback: '',
  feedbackItems: [],
  
  activeView: 'read', // or 'edit'
  editableContent: '',
  originalContent: '',
  hasChanges: false,
  changeCount: 0,
  quillEditor: null,
  
  submitting: false,
  submitted: false
}
```

---

### 4.3 ReviewsDashboard.vue
**Path**: `/workspaces/StructuredDocs/frontend/src/views/ReviewsDashboard.vue`

**Purpose**: Main dashboard for authors to manage reviews they've requested

**Sections**:
1. **Metrics Panel**
   - Total Reviews
   - Pending count
   - Completed count
   - Average completion days
   - Overdue count

2. **Quick Actions**
   - Send for Review
   - Review Guide
   - Incorporate Feedback
   - Review History

3. **Urgent Reviews Section**
   - Shows high/urgent priority pending reviews
   - Click to view details

4. **Review Activity Section**
   - Recent reviews grid
   - Shows topic title, reviewer, status, sent date, due date
   - Email delivery unavailable badge (if applicable)

---

### 4.4 Other Review Components
- **ReviewCard.vue** - Card component for displaying review summary
- **SequentialReviewModal.vue** - Modal for configuring multi-step reviews
- **ReviewFeedbackView.vue** - View for authors to see feedback on their topics

---

## 5. FRONTEND API LAYER

**File**: `/workspaces/StructuredDocs/frontend/src/api/reviews.js`

### Available Functions

```javascript
// Get all reviews
export async function getReviews()
// GET /api/reviews/

// Get available reviewers
export async function getReviewers()
// GET /api/reviews/reviewers

// Request a review
export async function requestReview(reviewData)
// POST /api/reviews/request
// reviewData = { topic_id, reviewer_id, priority, message, due_date, requested_by }

// Start a review (mark as in_progress)
export async function startReview(reviewId)
// POST /api/reviews/{reviewId}/start

// Submit completed review
export async function submitReview(reviewId, reviewData)
// POST /api/reviews/{reviewId}/submit
// reviewData = { recommendation, feedback, review_notes }

// Get pending reviews (optionally filtered by reviewer)
export async function getPendingReviews(reviewerId = null)
// GET /api/reviews/pending?reviewer_id={id}

// Get reviews requested by a user
export async function getMyReviews(requesterId)
// GET /api/reviews/my-reviews?requester_id={id}

// Get all reviews for a topic
export async function getTopicReviews(topicId)
// GET /api/reviews/topic/{topicId}/reviews

// Get review statistics
export async function getReviewStats()
// GET /api/reviews/stats

// Send follow-up reminder
export async function sendFollowUpReminder(reviewId)
// POST /api/reviews/{reviewId}/follow-up
```

---

## 6. CURRENT REVIEW WORKFLOW

### Single Review Flow
1. Author clicks "Request Review" on a topic
2. Selects one reviewer from dropdown
3. Optionally sets priority, due date, message
4. System creates Review + ReviewToken
5. Email sent to reviewer with secure token link
6. Reviewer accesses portal via token (no login needed)
7. Reviewer reviews content, optionally edits
8. Reviewer submits feedback with recommendation
9. Author sees feedback, responds to individual items
10. Topic status updated (approved, revisions_requested, rejected, etc.)

### Sequential Review Flow
1. Author creates ReviewSequence with multiple ReviewSequenceSteps
2. System creates Review for first reviewer
3. After first review complete, auto-advances to next reviewer
4. Each reviewer sees previous reviewer's feedback
5. Final reviewer's approval completes sequence

---

## 7. KEY DESIGN PATTERNS & LIMITATIONS

### Current Design
- **1 Review = 1 Topic + 1 Reviewer**
- Each review is independent
- Bulk review = multiple separate POST requests to /api/reviews/request
- No native "batch review" concept

### Email System
- Relies on tokens for external reviewer access
- No authentication required for review portal (token-based)
- Email failures don't block review creation (flagged with email_delivery_unavailable)

### Token Security
- 32-byte URL-safe tokens (generated via secrets.token_urlsafe(32))
- 30-day default expiration (configurable per request)
- 10 access limit (configurable)
- Tracked access count and usage timestamp

---

## 8. RECOMMENDATIONS FOR BULK REVIEW FEATURE

### Database Model Changes Needed
1. **New Model: BulkReviewRequest**
   - Tracks a group of topics + 1 reviewer
   - Portal link shared across all topics
   - Allows prev/next navigation
   - Single email for entire batch

2. **New Model: BulkReviewSequence**
   - Links multiple Topic IDs to single Reviewer
   - Position tracking for navigation
   - Shared feedback context across topics

3. **Extend ReviewToken**
   - Add `bulk_review_sequence_id` (nullable FK)
   - Add `current_topic_index` for navigation state

### API Endpoints to Add
1. `POST /api/reviews/bulk-request`
   - Body: { topic_ids: [int], reviewer_id: int, priority, message, due_date }
   - Creates ReviewToken with bulk_review_sequence_id
   - Single email sent

2. `GET /api/bulk-review/<token>`
   - Returns all topics in sequence with current position
   - Navigation info (prev/next indices)

3. `GET /api/bulk-review/<token>/topic/<position>`
   - Get specific topic content at position

4. `POST /api/bulk-review/<token>/feedback`
   - Submit feedback for current topic
   - Auto-advance position on next submission

5. `GET /api/bulk-review/<token>/summary`
   - Progress through bulk review (X of Y topics)

### Frontend Portal Changes
1. **BulkReviewPortal.vue** - New component
   - Shows "Topic X of Y"
   - Prev/Next topic navigation
   - Topic breadcrumb
   - Same feedback form as single review
   - Progress indicator

2. **RequestBulkReviewModal.vue** - New component
   - Multi-select topics (with search/filter)
   - Single reviewer selector
   - Priority, due date, message
   - Submit creates bulk review request

### Email Template Changes
- Subject: "Review Request: {N} Topics" 
- Includes topic list summary
- Bulk review portal link (not individual topic links)

---

## 9. IMPORTANT CAVEATS

### Active Code Patterns
- Review model includes `sequence_id` and `sequence_position` - sequential reviews partially implemented
- ReviewSequence/ReviewSequenceStep models exist but may not be fully integrated in UI
- Auto-advance logic exists in `/reviews` endpoint but needs verification

### Rate Limiting
- Review token generation: configurable (default "10 per hour")
- Feedback submission: configurable (default "30 per hour")
- Configured via `get_setting()` utility

### Email Delivery
- Can fail silently (flagged in DB but review created successfully)
- Multiple fallback mechanisms (provider > SMTP > debug file)
- No retry mechanism for failed emails currently

### Token Expiration
- Default: 30 days after request
- Due date + 7 days for sequential reviews
- Access limit: default 10 (per token)

