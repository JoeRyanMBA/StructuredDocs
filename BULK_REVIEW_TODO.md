# Bulk Review Feature - Implementation Roadmap

## Quick Reference: What Exists vs. What's Needed

### ✅ WHAT EXISTS (Current System)

**Single-Topic Review Workflow**
```
User → Topics List → Select 1 Topic 
      → RequestReviewModal 
      → Select 1 Reviewer 
      → Create 1 Review 
      → Send 1 Email 
      → /api/reviews/request (single)
```

**Sequential Multi-Reviewer (Same Topic)**
```
User → SequentialReviewModal 
     → Add multiple reviewers (queue)
     → Create ReviewSequence + N Reviews
     → Reviewer 1 → Approve/Changes → Auto-advance
     → Reviewer 2 → ...
     → Topic updated after each step
```

**Token-Based Reviewer Access**
```
Reviewer gets email with unique token
/review/{token} (no login needed)
View 1 topic + feedback for that review
Submit feedback
Token expires after due_date + 7 days
Rate limited: 30 feedback/hour, 10 max accesses
```

**Database Schema (Single-Topic Design)**
```
reviews (1 topic : 1 reviewer per row)
  ├─ topic_id (FK)
  ├─ reviewer_id (FK)
  ├─ status (pending/in_progress/completed/declined)
  ├─ priority, due_date, feedback, etc.
  └─ sequence_id (FK, optional) - for sequential only

review_tokens (1 per review)
  └─ Secure access for external reviewers

review_feedback (N per review)
  ├─ Multiple feedback items per review
  └─ Structured with priority/impact/type

review_sequences (for multi-reviewer same topic)
  ├─ review_sequence_steps (ordered queue of reviewers)
  └─ reviews FK (backref to reviews in sequence)
```

**Email System**
```
Per-Topic Template
Subject: Review Request: {topic_title} (Topic #{topic_id})
Body: 
  - Topic info (title, priority, due_date)
  - Author message
  - Single link: /review/{token}
  - Called for EACH review via email_service.send_review_notification()
```

---

## ❌ WHAT'S MISSING (Bulk Feature Gaps)

### A. Database Schema
```
MISSING:
├─ review_batches table
│  ├─ id
│  ├─ name (optional, auto-generated)
│  ├─ created_by (FK stakeholders)
│  ├─ status (pending, queued, in_progress, completed, failed)
│  ├─ total_reviews (count of reviews in batch)
│  ├─ completed_reviews (count complete)
│  ├─ created_at, completed_at
│  └─ notes (optional)
│
└─ reviews.batch_id (FK) [NEW COLUMN]
   └─ Links review to batch for grouping/tracking
```

### B. Backend API Endpoints
```
MISSING:
├─ POST /api/reviews/batch
│  └─ {topics: [id], reviewer_id, priority, due_date, message}
│  └─ Creates N Reviews in 1 request + batch tracking
│
├─ GET /api/reviews/batches
│  └─ List all batches with status summary
│
├─ GET /api/reviews/batches/{id}
│  └─ Details + related reviews list
│
├─ GET /api/reviews/batches/{id}/progress
│  └─ {total, completed, pending, failed, % complete}
│
├─ PUT /api/reviews/batches/{id}/cancel
│  └─ Mark unsent reviews as cancelled
│
└─ POST /api/reviews/batch/send
   └─ Bulk email sending (async job)
```

### C. Frontend UI Components
```
MISSING:
├─ BulkReviewModal (NEW)
│  ├─ Topic multi-select (table with checkboxes)
│  ├─ Show selected count
│  ├─ Single reviewer dropdown
│  ├─ Shared settings (priority, due_date, message)
│  ├─ Preview: "Will create N reviews"
│  └─ Submit button
│
├─ BatchProgressTracker (NEW)
│  ├─ Real-time progress bar (X of Y)
│  ├─ Status breakdown (pending, sent, complete, failed)
│  ├─ Cancel button
│  └─ Toast notifications
│
└─ BatchDetailsView (NEW)
   ├─ Batch info card
   ├─ Reviews table (searchable, filterable)
   ├─ Individual review status
   └─ Re-send failed reviews
```

### D. Email System
```
MISSING:
├─ Batch Email Template (Alternative)
│  ├─ Subject: "You have been assigned 5 reviews to complete"
│  ├─ Body: List of topics with individual links
│  └─ Called via email_service.send_batch_review_notification()
│
└─ Async Email Sending
   ├─ Queue (Redis/Celery)
   ├─ Background job for bulk sends
   └─ Retry logic for failures
```

### E. Reviewer Dashboard (Long-term)
```
MISSING:
├─ GET /api/reviewers/{id}/reviews
│  ├─ All assigned reviews (pending + completed)
│  ├─ Filtering: status, priority, due_date
│  └─ Pagination
│
└─ ReviewerDashboard.vue (NEW)
   ├─ List of all assigned reviews
   ├─ Table with topic, priority, due_date, status
   ├─ Quick filters
   └─ Click to open specific review
```

---

## Implementation Phases

### 🟢 PHASE 1: MVP Bulk Creation (1-2 weeks)
**Goal**: Request review for multiple topics, single reviewer

#### Database
```sql
-- NEW TABLE
CREATE TABLE review_batches (
    id INTEGER PRIMARY KEY,
    name VARCHAR(255),
    created_by INTEGER FK stakeholders.id,
    status ENUM(pending, sent, completed),
    total_reviews INTEGER,
    completed_reviews INTEGER,
    created_at DATETIME DEFAULT now(),
    completed_at DATETIME
);

-- ALTER EXISTING
ALTER TABLE reviews ADD COLUMN batch_id INTEGER FK review_batches.id;
ALTER TABLE reviews ADD INDEX idx_batch_id;
```

#### Backend
```python
# backend/routes/reviews.py

@reviews_bp.route('/batch', methods=['POST'])
@jwt_required()
def request_batch_review():
    """Request reviews for multiple topics to same reviewer"""
    data = request.get_json()
    
    # Validate
    topic_ids = data.get('topic_ids', [])  # Array!
    reviewer_id = data['reviewer_id']
    
    if not topic_ids or len(topic_ids) == 0:
        return jsonify({'error': 'At least 1 topic required'}), 400
    
    # Create batch
    batch = ReviewBatch(
        created_by=current_user.id,
        total_reviews=len(topic_ids),
        status='pending'
    )
    db.session.add(batch)
    db.session.flush()  # Get batch.id
    
    # Create reviews
    reviews = []
    for topic_id in topic_ids:
        review = Review(
            topic_id=topic_id,
            reviewer_id=reviewer_id,
            batch_id=batch.id,
            priority=data.get('priority', 'medium'),
            due_date=data.get('due_date'),
            author_message=data.get('message')
        )
        reviews.append(review)
    
    db.session.add_all(reviews)
    db.session.commit()
    
    # Send emails (async with Celery)
    send_batch_review_emails.delay(batch.id)
    
    return jsonify({
        'batch_id': batch.id,
        'review_count': len(reviews),
        'status': 'pending'
    }), 201
```

#### Frontend
```vue
<!-- RequestBulkReviewModal.vue (NEW) -->
<template>
  <div class="modal-overlay" v-if="isVisible" @click.self="closeModal">
    <div class="modal-content">
      <h3>Request Bulk Review</h3>
      
      <!-- Topic Multi-Select -->
      <div class="form-group">
        <label>Select Topics <span class="count">({{ selected.length }} selected)</span></label>
        <table class="topics-table">
          <thead>
            <tr>
              <th><input type="checkbox" v-model="selectAll" @change="toggleAll"></th>
              <th>Title</th>
              <th>Status</th>
              <th>Updated</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="topic in availableTopics" :key="topic.id">
              <td><input type="checkbox" v-model="selected" :value="topic.id"></td>
              <td>{{ topic.title }}</td>
              <td>{{ topic.status }}</td>
              <td>{{ formatDate(topic.updated_at) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <!-- Shared Settings -->
      <div class="form-group">
        <label>Reviewer *</label>
        <select v-model="reviewer_id" required>
          <option v-for="r in reviewers" :key="r.id" :value="r.id">
            {{ r.name }}
          </option>
        </select>
      </div>
      
      <div class="form-row">
        <div class="form-group">
          <label>Priority</label>
          <select v-model="priority">
            <option>Low</option>
            <option>Medium</option>
            <option>High</option>
            <option>Urgent</option>
          </select>
        </div>
        <div class="form-group">
          <label>Due Date</label>
          <input type="date" v-model="due_date" :min="today">
        </div>
      </div>
      
      <div class="form-group">
        <label>Message to All Reviewers</label>
        <textarea v-model="message" rows="3"></textarea>
      </div>
      
      <!-- Preview -->
      <div class="preview">
        <p>Will create <strong>{{ selected.length }}</strong> reviews to <strong>{{ selectedReviewerName }}</strong></p>
      </div>
      
      <div class="form-actions">
        <button @click="closeModal" class="btn-secondary">Cancel</button>
        <button @click="submitBatch" :disabled="selected.length === 0" class="btn-primary">
          Request {{ selected.length }} Reviews
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { getReviewers, requestBulkReview } from '@/api/reviews.js'

export default {
  name: 'RequestBulkReviewModal',
  props: ['isVisible', 'topics'],
  data() {
    return {
      availableTopics: [],
      selected: [],
      selectAll: false,
      reviewer_id: '',
      priority: 'medium',
      due_date: '',
      message: '',
      reviewers: []
    }
  },
  computed: {
    today() {
      return new Date().toISOString().split('T')[0]
    },
    selectedReviewerName() {
      const r = this.reviewers.find(x => x.id == this.reviewer_id)
      return r?.name || '—'
    }
  },
  methods: {
    async submitBatch() {
      const batch = {
        topic_ids: this.selected,
        reviewer_id: parseInt(this.reviewer_id),
        priority: this.priority,
        due_date: this.due_date ? new Date(this.due_date).toISOString() : null,
        message: this.message
      }
      
      const result = await requestBulkReview(batch)
      // Show BatchProgressTracker
      this.$emit('batch-created', result)
      this.closeModal()
    },
    toggleAll() {
      this.selected = this.selectAll 
        ? this.availableTopics.map(t => t.id)
        : []
    },
    closeModal() {
      this.$emit('close')
    }
  }
}
</script>
```

#### API Method
```javascript
// frontend/src/api/reviews.js
export async function requestBulkReview(batchData) {
  const res = await fetch('/api/reviews/batch', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(batchData)
  })
  if (!res.ok) await throwApiError(res, 'Failed to request bulk review')
  return res.json()
}
```

#### Integration Point
```vue
<!-- ReviewsDashboard.vue or TopicsList.vue -->
<button @click="showBulkReviewModal = true" class="btn btn-primary">
  📤 Request Bulk Review
</button>

<RequestBulkReviewModal 
  :isVisible="showBulkReviewModal"
  :topics="topics"
  @close="showBulkReviewModal = false"
  @batch-created="onBatchCreated"
/>

<BatchProgressTracker 
  v-if="activeBatch"
  :batch="activeBatch"
  @completed="onBatchCompleted"
/>
```

---

### 🟡 PHASE 2: Batch Tracking & Progress (1-2 weeks)

#### Frontend
```vue
<!-- BatchProgressTracker.vue (NEW) -->
<template>
  <div class="batch-tracker">
    <div class="progress-card">
      <h4>Batch {{ batch.id }}</h4>
      
      <!-- Progress Bar -->
      <div class="progress-bar">
        <div class="progress-fill" :style="{ width: progressPercent + '%' }"></div>
      </div>
      <p class="progress-text">{{ batch.completed_reviews }} of {{ batch.total_reviews }} sent</p>
      
      <!-- Status Breakdown -->
      <div class="status-breakdown">
        <span class="badge pending">⏳ {{ pendingCount }}</span>
        <span class="badge sent">📤 {{ sentCount }}</span>
        <span class="badge failed">❌ {{ failedCount }}</span>
      </div>
      
      <!-- Cancel Button -->
      <button v-if="batch.status !== 'completed'" @click="cancelBatch">
        Cancel Batch
      </button>
    </div>
  </div>
</template>
```

#### Backend
```python
@reviews_bp.route('/batches/<int:batch_id>/progress', methods=['GET'])
@jwt_required()
def get_batch_progress(batch_id):
    batch = ReviewBatch.query.get_or_404(batch_id)
    
    total = batch.total_reviews
    completed = Review.query.filter_by(batch_id=batch_id, status='completed').count()
    pending = Review.query.filter_by(batch_id=batch_id, status='pending').count()
    failed = Review.query.filter_by(batch_id=batch_id, status='declined').count()
    
    return jsonify({
        'batch_id': batch.id,
        'status': batch.status,
        'total_reviews': total,
        'completed_reviews': completed,
        'pending': pending,
        'failed': failed,
        'percent_complete': int((completed / total) * 100) if total > 0 else 0
    })
```

---

### 🔴 PHASE 3: Reviewer Dashboard (2 weeks)

#### Backend
```python
@reviews_bp.route('/my-assigned', methods=['GET'])
@jwt_required()
def get_my_assigned_reviews():
    """Get reviews assigned to current user (reviewer perspective)"""
    current_user_id = get_jwt_identity()
    
    reviews = Review.query.filter(
        Review.reviewer_id == current_user_id
    ).order_by(Review.due_date.asc()).all()
    
    return jsonify([review.to_dict() for review in reviews])
```

#### Frontend
```vue
<!-- ReviewerDashboard.vue (NEW) -->
<template>
  <div class="reviewer-dashboard">
    <h1>My Assigned Reviews</h1>
    
    <!-- Filter Bar -->
    <div class="filters">
      <select v-model="filterStatus">
        <option value="">All Status</option>
        <option value="pending">Pending</option>
        <option value="in_progress">In Progress</option>
        <option value="completed">Completed</option>
      </select>
      <input type="search" v-model="searchText" placeholder="Search topics...">
    </div>
    
    <!-- Reviews Table -->
    <table class="reviews-table">
      <thead>
        <tr>
          <th>Topic</th>
          <th>Requester</th>
          <th>Priority</th>
          <th>Due Date</th>
          <th>Status</th>
          <th>Action</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="review in filteredReviews" :key="review.id">
          <td>{{ review.topic_title }}</td>
          <td>{{ review.requester_name }}</td>
          <td><span :class="'priority-' + review.priority">{{ review.priority }}</span></td>
          <td>{{ formatDate(review.due_date) }}</td>
          <td><span :class="'status-' + review.status">{{ review.status }}</span></td>
          <td>
            <button v-if="review.status !== 'completed'" @click="openReview(review)">
              Review
            </button>
            <button v-else @click="viewFeedback(review)">
              View
            </button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
```

---

### 💬 PHASE 4: Advanced Features (3-4 weeks)

- Parallel reviewers (same topic, multiple reviewers at once)
- Review templates (save/reuse configurations)
- Bulk feedback incorporation
- Email digest/aggregation
- WebSocket real-time updates
- Bulk export/reporting

---

## Code Checklist

### ✅ Phase 1 Checklist
- [ ] Create ReviewBatch model + migration
- [ ] Add batch_id FK to reviews table
- [ ] Implement `POST /api/reviews/batch` endpoint
- [ ] Implement async email sending (Celery task)
- [ ] Create RequestBulkReviewModal.vue component
- [ ] Create BatchProgressTracker.vue component
- [ ] Update ReviewsDashboard.vue to include bulk button
- [ ] Update reviews.js API with `requestBulkReview()` function
- [ ] Test: Create 10 reviews in single request
- [ ] Test: All reviewers receive emails
- [ ] Test: Batch progress updates in real-time

### ✅ Phase 2 Checklist
- [ ] Implement `GET /api/reviews/batches/{id}/progress` endpoint
- [ ] Implement `GET /api/reviews/batches` endpoint
- [ ] Implement `PUT /api/reviews/batches/{id}/cancel` endpoint
- [ ] Add polling/WebSocket for real-time progress
- [ ] Create BatchDetailsView.vue component
- [ ] Update ReviewsDashboard.vue batch history section
- [ ] Test: Cancel batch stops pending emails

### ✅ Phase 3 Checklist
- [ ] Implement `GET /api/reviews/my-assigned` endpoint
- [ ] Create ReviewerDashboard.vue
- [ ] Add routing: `/reviews/assigned`
- [ ] Implement search/filter
- [ ] Test: Reviewer sees all assigned reviews
- [ ] Test: Can click to open any review token

---

## Database Migration Template

```python
# backend/migrations/versions/xxxx_add_review_batches.py
from alembic import op
import sqlalchemy as sa

def upgrade():
    # Create review_batches table
    op.create_table(
        'review_batches',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(255), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('status', sa.Enum('pending', 'sent', 'completed'), nullable=False, server_default='pending'),
        sa.Column('total_reviews', sa.Integer(), nullable=False),
        sa.Column('completed_reviews', sa.Integer(), default=0),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['created_by'], ['stakeholders.id'])
    )
    
    # Add batch_id to reviews
    op.add_column('reviews', sa.Column('batch_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_reviews_batch_id', 'reviews', 'review_batches', ['batch_id'], ['id'])
    op.create_index('ix_reviews_batch_id', 'reviews', ['batch_id'])

def downgrade():
    op.drop_table('review_batches')
    op.drop_column('reviews', 'batch_id')
```

---

## Testing Scenarios

### Phase 1 Tests
```
1. Create batch with 5 topics, 1 reviewer
   ✓ 5 Review records created
   ✓ Batch status = 'pending'
   ✓ All reviews linked to batch_id
   
2. Check emails sent
   ✓ 5 emails sent (1 per topic)
   ✓ Each email different token
   ✓ Each reviewer can access only their review
   
3. Complete reviews
   ✓ Reviews can be submitted independently
   ✓ Batch status updates based on completion
   ✓ Progress tracker shows correct count
```

### Phase 2 Tests
```
1. Monitor batch progress
   ✓ Progress endpoint returns correct counts
   ✓ Progress updates as reviews complete
   
2. Cancel batch
   ✓ Pending reviews marked as cancelled
   ✓ In-progress reviews continue
   ✓ No more emails sent for cancelled batch
```

---

## File Additions/Modifications

### New Files
```
backend/
  routes/
    review_batches.py (or add to reviews.py)
  models/
    (add ReviewBatch model to models.py)
  migrations/versions/
    xxxx_add_review_batches.py

frontend/src/
  components/
    RequestBulkReviewModal.vue (NEW)
    BatchProgressTracker.vue (NEW)
    BatchDetailsCard.vue (NEW)
  views/
    ReviewerDashboard.vue (NEW, Phase 3)
    BatchManagementView.vue (NEW, Phase 2)
```

### Modified Files
```
backend/
  models.py (add ReviewBatch class + batch_id to Review)
  routes/reviews.py (add bulk endpoints)
  utils/email_service.py (optional: batch email template)

frontend/src/
  views/ReviewsDashboard.vue (add bulk button)
  components/RequestReviewModal.vue (update to use BulkReviewModal)
  api/reviews.js (add requestBulkReview, etc.)
  router/index.js (add new routes)
```

---

## Questions for Product/Design

1. **Email Strategy**: 
   - Send individual emails per topic (current approach)?
   - OR digest email with all topics listed?
   
2. **Parallel Reviewers**: 
   - Support same topic to multiple reviewers simultaneously?
   - Or only sequential?
   
3. **Reviewer Dashboard**:
   - Priority: High (many reviews) or Low (rare bulk)?
   - Should be internal user or external reviewer feature?
   
4. **Email Aggregation**:
   - Support template variables per topic (e.g., "Topic A: ..., Topic B: ...")?
   - One email per topic or one digest email?

---

End of Roadmap
