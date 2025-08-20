# WYSIWYG Review with Change Tracking - Technical Design

## 🎯 Enhanced Review Workflow

### Current State
- Reviewer provides text feedback and comments
- Author manually implements suggested changes
- No direct editing capability

### Proposed Enhancement
- Reviewer can directly edit content with WYSIWYG editor
- All changes are tracked with metadata (who, when, what type)
- Author can accept/reject individual changes
- Full audit trail of review process

## 🛠️ Technical Implementation

### 1. Frontend: WYSIWYG Editor with Change Tracking

#### Option A: TinyMCE (Recommended)
```javascript
// Enhanced ReviewPortal.vue with TinyMCE
import { Editor } from '@tinymce/tinymce-vue'

// TinyMCE configuration
editorConfig: {
  plugins: 'trackchanges collaborate comments paste lists',
  toolbar: 'trackchanges | formatselect | bold italic underline | 
           bullist numlist | accept-all reject-all | comment',
  trackchanges_author: this.reviewer.name,
  trackchanges_author_color: '#ff6b35',
  trackchanges_enabled: true,
  content_style: 'body { font-family: Arial; font-size: 14pt; }'
}
```

#### Option B: Quill.js with Custom Track Changes
```javascript
// Custom change tracking with Quill
const quill = new Quill('#editor', {
  modules: {
    history: { userOnly: true },
    trackChanges: {
      authorId: 'reviewer_id',
      authorName: 'reviewer_name'
    }
  }
})
```

### 2. Database Schema Extensions

#### New Table: ReviewChanges
```sql
CREATE TABLE review_changes (
    id INTEGER PRIMARY KEY,
    review_id INTEGER REFERENCES reviews(id),
    change_type ENUM('insert', 'delete', 'modify', 'format'),
    
    -- Position tracking
    start_position INTEGER,
    end_position INTEGER,
    target_element VARCHAR(100), -- h1, p, li, etc.
    
    -- Content changes
    original_content TEXT,
    new_content TEXT,
    
    -- Change metadata
    author_id INTEGER REFERENCES users(id),
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    status ENUM('pending', 'accepted', 'rejected') DEFAULT 'pending',
    
    -- Review workflow
    reviewed_by INTEGER REFERENCES users(id),
    reviewed_at DATETIME,
    review_comment TEXT
);
```

#### Enhanced Review Model
```python
class Review(db.Model):
    # ... existing fields ...
    
    # New fields for change tracking
    has_tracked_changes = db.Column(db.Boolean, default=False)
    original_content = db.Column(db.Text)  # Snapshot of original
    edited_content = db.Column(db.Text)    # Content with changes
    change_summary = db.Column(db.Text)    # Auto-generated summary
    
    # Workflow status
    changes_status = db.Column(
        Enum('draft', 'submitted', 'under_review', 'completed'),
        default='draft'
    )
```

### 3. Backend API Enhancements

#### New Endpoints
```python
# routes/reviews.py

@reviews_bp.route('/<int:review_id>/changes', methods=['POST'])
def save_tracked_changes(review_id):
    """Save tracked changes from WYSIWYG editor"""
    changes_data = request.json
    # Process and save individual changes
    # Return change IDs for frontend tracking

@reviews_bp.route('/<int:review_id>/changes/<int:change_id>/approve', methods=['POST'])
def approve_change(review_id, change_id):
    """Author approves a specific change"""

@reviews_bp.route('/<int:review_id>/changes/<int:change_id>/reject', methods=['POST'])
def reject_change(review_id, change_id):
    """Author rejects a specific change"""

@reviews_bp.route('/<int:review_id>/apply-changes', methods=['POST'])
def apply_approved_changes(review_id):
    """Apply all approved changes to the topic content"""
```

### 4. Enhanced Review Portal UI

#### Split-View Interface
```vue
<template>
  <div class="review-workspace">
    <!-- Original content (read-only) -->
    <div class="original-content">
      <h3>Original Content</h3>
      <div v-html="originalContent"></div>
    </div>
    
    <!-- Editable content with change tracking -->
    <div class="editor-pane">
      <h3>Edit Content</h3>
      <Editor
        v-model="editableContent"
        :init="editorConfig"
        @change="trackChanges"
      />
    </div>
    
    <!-- Changes summary -->
    <div class="changes-summary">
      <h3>Your Changes ({{ trackedChanges.length }})</h3>
      <div v-for="change in trackedChanges" :key="change.id">
        <ChangePreview :change="change" />
      </div>
    </div>
  </div>
</template>
```

### 5. Author Review Interface

#### Change Management Dashboard
```vue
<template>
  <div class="change-review-dashboard">
    <div class="content-comparison">
      <!-- Side-by-side comparison -->
      <div class="before-after">
        <div class="before">
          <h4>Before</h4>
          <div v-html="originalContent"></div>
        </div>
        <div class="after">
          <h4>With Proposed Changes</h4>
          <div v-html="contentWithChanges"></div>
        </div>
      </div>
    </div>
    
    <!-- Individual change review -->
    <div class="changes-list">
      <div v-for="change in pendingChanges" :key="change.id" 
           class="change-item">
        <ChangeReviewCard 
          :change="change"
          @approve="approveChange"
          @reject="rejectChange"
        />
      </div>
    </div>
  </div>
</template>
```

## 🎨 User Experience Flow

### 1. Reviewer Experience
1. Opens review portal from email
2. Sees original content + WYSIWYG editor
3. Makes direct edits with change tracking enabled
4. Adds comments to specific changes
5. Submits review with tracked changes

### 2. Author Experience
1. Receives notification of completed review
2. Opens change review dashboard
3. Sees side-by-side comparison
4. Reviews each change individually
5. Accepts/rejects with optional comments
6. Applies approved changes to original topic

### 3. Workflow Integration
1. Auto-update topic content with approved changes
2. Maintain version history
3. Send notifications to stakeholders
4. Generate change summary reports

## 📊 Benefits

### For Reviewers
- ✅ Direct editing capability
- ✅ Visual feedback of changes
- ✅ Familiar word-processor experience
- ✅ Context-aware editing

### For Authors
- ✅ Granular change control
- ✅ Visual diff comparison
- ✅ Efficient change application
- ✅ Complete audit trail

### For Organization
- ✅ Faster review cycles
- ✅ Better change quality
- ✅ Reduced back-and-forth
- ✅ Improved collaboration

## 🚀 Implementation Phases

### Phase 1: Basic WYSIWYG (2-3 days)
- Integrate TinyMCE in ReviewPortal
- Basic change tracking
- Save/load edited content

### Phase 2: Change Management (3-4 days)
- Database schema updates
- Change tracking backend
- Basic approve/reject workflow

### Phase 3: Enhanced UI (2-3 days)
- Split-view interface
- Change comparison views
- Author review dashboard

### Phase 4: Advanced Features (2-3 days)
- Version history
- Bulk change operations
- Advanced reporting

## 💡 Technical Considerations

### Performance
- Large documents may need chunked loading
- Change tracking could be resource-intensive
- Consider real-time collaboration limits

### Security
- Validate all content changes
- Sanitize HTML input
- Audit trail for compliance

### Compatibility
- Ensure mobile responsiveness
- Browser compatibility testing
- Fallback for non-JS environments

Would you like me to start implementing this enhanced review system? I'd recommend beginning with Phase 1 to get the basic WYSIWYG functionality working, then we can iterate from there.
