<template>
  <div class="review-portal">
    <!-- Loading State -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>Loading review content...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-container">
      <div class="error-icon">⚠️</div>
      <h2>Unable to Load Review</h2>
      <p>{{ error }}</p>
      <div class="error-actions">
        <button @click="retryLoad" class="btn btn-primary">Try Again</button>
        <a href="mailto:support@yourorganization.com" class="btn btn-secondary">Contact Support</a>
      </div>
    </div>

    <!-- Review Content -->
    <div v-else class="review-content">
      <!-- Header -->
      <div class="review-header">
        <div class="review-title">
          <h1>{{ review.topic_title }}</h1>
          <div class="topic-id-header">Topic #{{ review.topic_id }}</div>
          <div class="review-meta">
            <span class="due-date" :class="{ overdue: isOverdue }">
              Due: {{ formatDate(review.due_date) }}
            </span>
            <span class="priority" :class="'priority-' + review.priority">
              {{ review.priority.toUpperCase() }} Priority
            </span>
          </div>
        </div>
        <div class="review-status">
          <span class="access-info">
            Access {{ tokenInfo.access_count }}/{{ tokenInfo.max_access_count }}
          </span>
        </div>
      </div>

      <!-- Author Message -->
      <div v-if="review.author_message" class="author-message">
        <h3>Message from Author</h3>
        <p>{{ review.author_message }}</p>
      </div>

      <!-- Content to Review -->
      <div class="content-section">
        <div class="content-header">
          <h3>Content for Review</h3>
          <div class="view-toggle">
            <button 
              @click="activeView = 'read'" 
              :class="{ active: activeView === 'read' }"
              class="toggle-btn"
            >
              📖 Read Only
            </button>
            <button 
              @click="activeView = 'edit'" 
              :class="{ active: activeView === 'edit' }"
              class="toggle-btn"
            >
              ✏️ Edit Content
            </button>
          </div>
        </div>

        <!-- Read-only view -->
        <div v-if="activeView === 'read'" class="content-viewer">
          <div class="content-text" v-html="formattedContent"></div>
        </div>

        <!-- WYSIWYG Editor view -->
        <div v-if="activeView === 'edit'" class="editor-container">
          <div class="editor-notice">
            <span class="notice-icon">💡</span>
            <span>You can directly edit the content below. Your changes will be tracked and sent to the author for review.</span>
          </div>
          <div class="quill-wrapper">
            <div ref="quillEditor" class="quill-editor"></div>
          </div>
          <div class="editor-actions">
            <button @click="resetContent" class="btn btn-secondary">Reset to Original</button>
            <button @click="previewChanges" class="btn btn-outline">Preview Changes</button>
          </div>
        </div>

        <!-- Changes Summary -->
        <div v-if="hasChanges" class="changes-summary">
          <h4>📝 Your Changes</h4>
          <div class="changes-info">
            <span class="changes-count">{{ changeCount }} modification{{ changeCount !== 1 ? 's' : '' }} detected</span>
            <button @click="showChangesDetail = !showChangesDetail" class="btn btn-sm">
              {{ showChangesDetail ? 'Hide' : 'Show' }} Details
            </button>
          </div>
          <div v-if="showChangesDetail" class="changes-detail">
            <div class="change-preview">
              <div class="change-before">
                <strong>Original:</strong>
                <div v-html="formattedContent"></div>
              </div>
              <div class="change-after">
                <strong>Your Edit:</strong>
                <div v-html="editableContent"></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Existing Feedback (if any) -->
      <div v-if="existingFeedback.length > 0" class="existing-feedback">
        <h3>Previous Feedback</h3>
        <div class="feedback-list">
          <div v-for="item in existingFeedback" :key="item.id" class="feedback-item">
            <div class="feedback-header">
              <span class="feedback-type">{{ formatFeedbackType(item.feedback_type) }}</span>
              <span class="feedback-priority" :class="'priority-' + item.priority">
                {{ item.priority.toUpperCase() }}
              </span>
            </div>
            <div class="feedback-content">
              <p><strong>Comment:</strong> {{ item.comment }}</p>
              <div v-if="item.original_text" class="text-reference">
                <strong>Referring to:</strong> "{{ item.original_text }}"
              </div>
              <div v-if="item.suggested_text" class="suggested-text">
                <strong>Suggested change:</strong> "{{ item.suggested_text }}"
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Feedback Form -->
      <div class="feedback-form">
        <h3>Submit Your Review</h3>
        
        <!-- Changes Detection Alert -->
        <div v-if="hasChanges" class="changes-alert">
          <i class="icon">✏️</i>
          <strong>Content Changes Detected:</strong> You've made edits to the content above. 
          Choose "Approve with your edits" to include your changes, or "Approve original content" to ignore them.
        </div>
        
        <!-- Overall Recommendation -->
        <div class="form-group">
          <label>Overall Recommendation</label>
          <select v-model="overallRecommendation" class="form-select">
            <option value="">Select recommendation...</option>
            <option value="approve">{{ hasChanges ? 'Approve original content (ignore my edits)' : 'Approve as submitted' }}</option>
            <option value="approve_with_changes">{{ hasChanges ? 'Approve with my edits' : 'Approve with minor changes' }}</option>
            <option value="needs_more_info">Request more information</option>
            <option value="reject">Reject - significant issues</option>
          </select>
        </div>

        <!-- Overall Feedback -->
        <div class="form-group">
          <label>Overall Comments</label>
          <textarea 
            v-model="overallFeedback" 
            class="form-textarea"
            placeholder="Provide your general thoughts on this content..."
            rows="4"
          ></textarea>
        </div>

        <!-- Specific Feedback Items -->
        <div class="specific-feedback">
          <h4>Specific Feedback Items</h4>
          <p class="help-text">Add specific comments, suggestions, or corrections below.</p>
          
          <div v-for="(item, index) in feedbackItems" :key="index" class="feedback-item-form">
            <div class="item-header">
              <span>Feedback Item {{ index + 1 }}</span>
              <button @click="removeFeedbackItem(index)" type="button" class="remove-btn">×</button>
            </div>
            
            <div class="form-row">
              <div class="form-group">
                <label>Type</label>
                <select v-model="item.feedback_type" class="form-select">
                  <option value="general_comment">General Comment</option>
                  <option value="text_edit">Text Edit</option>
                  <option value="text_addition">Text Addition</option>
                  <option value="text_deletion">Text Deletion</option>
                  <option value="technical_correction">Technical Correction</option>
                  <option value="style_suggestion">Style Suggestion</option>
                </select>
              </div>
              <div class="form-group">
                <label>Priority</label>
                <select v-model="item.priority" class="form-select">
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                  <option value="critical">Critical</option>
                </select>
              </div>
            </div>

            <div class="form-group">
              <label>Section/Location</label>
              <input 
                v-model="item.section_title" 
                type="text" 
                class="form-input"
                placeholder="e.g., Introduction, paragraph 2"
              />
            </div>

            <div v-if="item.feedback_type !== 'general_comment'" class="form-group">
              <label>Original Text</label>
              <textarea 
                v-model="item.original_text" 
                class="form-textarea"
                placeholder="Copy the text you're referring to..."
                rows="2"
              ></textarea>
            </div>

            <div v-if="item.feedback_type.includes('edit') || item.feedback_type.includes('addition')" class="form-group">
              <label>Suggested Text</label>
              <textarea 
                v-model="item.suggested_text" 
                class="form-textarea"
                placeholder="Your suggested replacement or addition..."
                rows="2"
              ></textarea>
            </div>

            <div class="form-group">
              <label>Comment</label>
              <textarea 
                v-model="item.comment" 
                class="form-textarea"
                placeholder="Explain your feedback..."
                rows="3"
                required
              ></textarea>
            </div>

            <div class="form-group">
              <label>Rationale (Optional)</label>
              <textarea 
                v-model="item.rationale" 
                class="form-textarea"
                placeholder="Why is this change needed?"
                rows="2"
              ></textarea>
            </div>
          </div>

          <button @click="addFeedbackItem" type="button" class="btn btn-primary add-feedback-btn">
            + Add Another Feedback Item
          </button>
        </div>

        <!-- Submit Actions -->
        <div class="form-actions">
          <button @click="submitReview" :disabled="submitting || !canSubmit" class="btn btn-success">
            {{ submitting ? 'Submitting...' : 'Submit Review' }}
          </button>
          <button @click="saveDraft" :disabled="submitting" class="btn btn-primary">
            Save Draft
          </button>
        </div>
      </div>

      <!-- Success Message -->
      <div v-if="submitted" class="success-container">
        <div class="success-icon">✅</div>
        <h3>Review Submitted Successfully!</h3>
        <p>Thank you for your feedback. The author will be notified of your review.</p>
      </div>
    </div>
  </div>
</template>

<script>
import { marked } from 'marked'
import Quill from 'quill'
import 'quill/dist/quill.snow.css'

export default {
  name: 'ReviewPortal',
  
  data() {
    return {
      loading: true,
      error: null,
      review: {},
      tokenInfo: {},
      existingFeedback: [],
      
      // Form data
      overallRecommendation: '',
      overallFeedback: '',
      feedbackItems: [],
      
      // WYSIWYG Editor data
      activeView: 'read', // 'read' or 'edit'
      editableContent: '',
      originalContent: '',
      hasChanges: false,
      changeCount: 0,
      showChangesDetail: false,
      quillEditor: null,
      
      // State
      submitting: false,
      submitted: false
    }
  },
  
  computed: {
    token() {
      return this.$route.params.token
    },
    
    isOverdue() {
      if (!this.review.due_date) return false
      return new Date() > new Date(this.review.due_date)
    },
    
    formattedContent() {
      if (!this.review.topic_content) return ''
      
      // Configure marked options for better rendering
      marked.setOptions({
        breaks: true,        // Convert line breaks to <br>
        gfm: true,          // GitHub Flavored Markdown
        sanitize: false,    // Allow HTML (since we trust the content)
        smartypants: true   // Use smart quotes and dashes
      })
      
      // Convert markdown to HTML using marked
      return marked(this.review.topic_content)
    },
    
    canSubmit() {
      return this.overallRecommendation && (this.overallFeedback || this.feedbackItems.length > 0)
    }
  },

  watch: {
    activeView(newView) {
      if (newView === 'edit') {
        this.$nextTick(() => {
          this.initializeQuillEditor()
        })
      }
    }
  },
  
  async mounted() {
    await this.loadReview()
  },
  
  methods: {
    async loadReview() {
      try {
        this.loading = true
        this.error = null
        
        const response = await fetch(`/api/review/${this.token}`)
        const data = await response.json()
        
        if (!response.ok) {
          throw new Error(data.error || 'Failed to load review')
        }
        
        this.review = data.review
        this.tokenInfo = data.token_info
        this.existingFeedback = data.feedback_items || []
        
        // Initialize editable content for WYSIWYG
        this.initializeEditableContent()
        
        // Initialize with one feedback item
        this.addFeedbackItem()
        
      } catch (error) {
        this.error = error.message
      } finally {
        this.loading = false
      }
    },

    // WYSIWYG Editor Methods
    initializeEditableContent() {
      if (this.review.topic_content) {
        // Convert markdown to HTML for editing
        marked.setOptions({
          breaks: true,
          gfm: true,
          sanitize: false,
          smartypants: true
        })
        this.originalContent = marked(this.review.topic_content)
        this.editableContent = this.originalContent
        
        // Initialize Quill editor if not already done
        this.$nextTick(() => {
          this.initializeQuillEditor()
        })
      }
    },

    initializeQuillEditor() {
  // Only initialize Quill when the ref exists, is a DOM Node, and is connected to document.
  // This prevents third-party code (Parchment/Quill) from calling MutationObserver.observe
  // with a non-Node target during race conditions.
  if (this.$refs.quillEditor && !this.quillEditor && this.$refs.quillEditor instanceof Node && (this.$refs.quillEditor.isConnected || document.contains(this.$refs.quillEditor))) {
        const toolbarOptions = [
          [{ 'header': [1, 2, 3, false] }],
          ['bold', 'italic', 'underline'],
          [{ 'list': 'ordered'}, { 'list': 'bullet' }],
          [{ 'align': [] }],
          ['link'],
          ['clean']
        ]

  // Durably guarded in the quill package source; temporary init-time monkeypatch removed.
  this.quillEditor = new Quill(this.$refs.quillEditor, {
          modules: {
            toolbar: toolbarOptions
          },
          theme: 'snow',
          placeholder: 'Edit the content here...'
        })

        // Set initial content
        this.quillEditor.root.innerHTML = this.originalContent

        // Track changes
        this.quillEditor.on('text-change', () => {
          this.editableContent = this.quillEditor.root.innerHTML
          this.detectChanges()
        })
      }
    },

    handleContentChange() {
      // This method is called by Quill's text-change event
      this.detectChanges()
    },

    detectChanges() {
      if (this.originalContent && this.editableContent) {
        this.hasChanges = this.originalContent !== this.editableContent
        
        // Simple change detection - count different words/elements
        if (this.hasChanges) {
          const originalWords = this.originalContent.replace(/<[^>]*>/g, '').split(/\s+/).length
          const editedWords = this.editableContent.replace(/<[^>]*>/g, '').split(/\s+/).length
          this.changeCount = Math.abs(editedWords - originalWords) + 1
        } else {
          this.changeCount = 0
        }
      }
    },

    resetContent() {
      this.editableContent = this.originalContent
      if (this.quillEditor) {
        this.quillEditor.root.innerHTML = this.originalContent
      }
      this.hasChanges = false
      this.changeCount = 0
      this.showChangesDetail = false
    },

    previewChanges() {
      this.showChangesDetail = true
    },
    
    async retryLoad() {
      await this.loadReview()
    },
    
    addFeedbackItem() {
      this.feedbackItems.push({
        feedback_type: 'general_comment',
        priority: 'medium',
        section_title: '',
        original_text: '',
        suggested_text: '',
        comment: '',
        rationale: ''
      })
    },
    
    removeFeedbackItem(index) {
      this.feedbackItems.splice(index, 1)
    },
    
    async submitReview() {
      try {
        this.submitting = true
        
        // Filter out empty feedback items
        const validFeedbackItems = this.feedbackItems.filter(item => item.comment.trim())
        
        const payload = {
          recommendation: this.overallRecommendation,
          feedback: this.overallFeedback,
          feedback_items: validFeedbackItems,
          // Include edited content if changes were made
          has_content_changes: this.hasChanges,
          edited_content: this.hasChanges ? this.editableContent : null,
          original_content: this.originalContent,
          change_summary: this.hasChanges ? `${this.changeCount} modifications made to content` : null
        }
        
        const response = await fetch(`/api/review/${this.token}/feedback`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        })
        
        const data = await response.json()
        
        if (!response.ok) {
          throw new Error(data.error || 'Failed to submit review')
        }
        
        this.submitted = true
        
      } catch (error) {
        alert('Error submitting review: ' + error.message)
      } finally {
        this.submitting = false
      }
    },
    
    async saveDraft() {
      // Save to localStorage for now
      const draft = {
        overallRecommendation: this.overallRecommendation,
        overallFeedback: this.overallFeedback,
        feedbackItems: this.feedbackItems,
        savedAt: new Date().toISOString()
      }
      
      localStorage.setItem(`review_draft_${this.token}`, JSON.stringify(draft))
      alert('Draft saved successfully!')
    },
    
    formatDate(dateString) {
      if (!dateString) return 'No deadline'
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      })
    },
    
    formatFeedbackType(type) {
      return type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
    }
  }
}
</script>

<style scoped>
.review-portal {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

/* Loading and Error States */
.loading-container, .error-container {
  text-align: center;
  padding: 4rem 2rem;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #205493;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.error-actions {
  margin-top: 2rem;
  display: flex;
  gap: 1rem;
  justify-content: center;
}

/* Review Header */
.review-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid #e9ecef;
}

.review-title h1 {
  margin: 0 0 0.5rem 0;
  color: #1f2937;
  font-size: 2rem;
}

.topic-id-header {
  background: #205493;
  color: white;
  padding: 0.4rem 0.8rem;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 600;
  display: inline-block;
  margin-bottom: 1rem;
}

.review-meta {
  display: flex;
  gap: 1rem;
  font-size: 0.9rem;
}

.due-date {
  padding: 0.25rem 0.75rem;
  background: #dbeafe;
  color: #1e40af;
  border-radius: 20px;
  font-weight: 500;
}

.due-date.overdue {
  background: #fecaca;
  color: #991b1b;
}

.priority {
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-weight: 600;
  font-size: 0.75rem;
}

.priority-low { background: #dbeafe; color: #1e40af; }
.priority-medium { background: #fef3c7; color: #92400e; }
.priority-high { background: #fecaca; color: #991b1b; }
.priority-urgent { background: #fca5a5; color: #7f1d1d; }

.access-info {
  font-size: 0.85rem;
  color: #6b7280;
  background: #f9fafb;
  padding: 0.5rem 1rem;
  border-radius: 6px;
}

/* Content Sections */
.author-message, .content-section, .existing-feedback, .feedback-form {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 2rem;
}

.author-message {
  background: #f0f9ff;
  border-left: 4px solid #205493;
}

.content-viewer {
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  padding: 1.5rem;
  max-height: 500px;
  overflow-y: auto;
}

.content-text {
  line-height: 1.6;
  color: #374151;
}

/* Markdown Content Styling */
.content-text h1,
.content-text h2,
.content-text h3,
.content-text h4,
.content-text h5,
.content-text h6 {
  margin-top: 1.5rem;
  margin-bottom: 0.75rem;
  font-weight: 600;
  color: #1f2937;
}

.content-text h1 { font-size: 1.875rem; }
.content-text h2 { font-size: 1.5rem; }
.content-text h3 { font-size: 1.25rem; }
.content-text h4 { font-size: 1.125rem; }

.content-text p {
  margin-bottom: 1rem;
}

.content-text ul,
.content-text ol {
  margin-bottom: 1rem;
  padding-left: 1.5rem;
}

.content-text li {
  margin-bottom: 0.25rem;
}

.content-text blockquote {
  border-left: 4px solid #e5e7eb;
  padding-left: 1rem;
  margin: 1rem 0;
  font-style: italic;
  color: #6b7280;
}

.content-text code {
  background: #f3f4f6;
  padding: 0.125rem 0.25rem;
  border-radius: 0.25rem;
  font-family: ui-monospace, SFMono-Regular, 'SF Mono', Consolas, 'Liberation Mono', Menlo, monospace;
  font-size: 0.875rem;
}

.content-text pre {
  background: #f3f4f6;
  padding: 1rem;
  border-radius: 0.5rem;
  overflow-x: auto;
  margin: 1rem 0;
}

.content-text pre code {
  background: none;
  padding: 0;
}

.content-text strong {
  font-weight: 600;
}

.content-text em {
  font-style: italic;
}

.content-text table {
  width: 100%;
  border-collapse: collapse;
  margin: 1rem 0;
}

.content-text th,
.content-text td {
  border: 1px solid #e5e7eb;
  padding: 0.5rem;
  text-align: left;
}

.content-text th {
  background: #f9fafb;
  font-weight: 600;
}

.content-text a {
  color: #2563eb;
  text-decoration: underline;
}

.content-text a:hover {
  color: #1d4ed8;
}

/* WYSIWYG Editor Styles */
.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.view-toggle {
  display: flex;
  gap: 0.5rem;
}

.toggle-btn {
  padding: 0.5rem 1rem;
  border: 1px solid #d1d5db;
  background: white;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.875rem;
  transition: all 0.2s;
}

.toggle-btn:hover {
  background: #f3f4f6;
}

.toggle-btn.active {
  background: #205493;
  color: white;
  border-color: #205493;
}

.editor-container {
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  padding: 1rem;
}

.editor-notice {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: #fef3c7;
  border: 1px solid #f59e0b;
  border-radius: 6px;
  padding: 0.75rem;
  margin-bottom: 1rem;
  font-size: 0.875rem;
  color: #92400e;
}

.notice-icon {
  font-size: 1.2rem;
}

.wysiwyg-editor {
  margin: 1rem 0;
}

.quill-wrapper {
  background: white;
  border-radius: 6px;
  margin: 1rem 0;
}

.quill-editor {
  min-height: 400px;
}

/* Quill Snow theme customization */
.ql-toolbar {
  border-top: 1px solid #ccc;
  border-left: 1px solid #ccc;
  border-right: 1px solid #ccc;
  border-bottom: none;
  border-radius: 6px 6px 0 0;
}

.ql-container {
  border-bottom: 1px solid #ccc;
  border-left: 1px solid #ccc;
  border-right: 1px solid #ccc;
  border-top: none;
  border-radius: 0 0 6px 6px;
  font-family: Helvetica, Arial, sans-serif;
  font-size: 14px;
  line-height: 1.6;
}

.ql-editor {
  padding: 1.5rem;
  min-height: 350px;
}

.ql-editor h1, .ql-editor h2, .ql-editor h3 {
  margin-top: 1.5rem;
  margin-bottom: 0.75rem;
  font-weight: 600;
  color: #1f2937;
}

.ql-editor p {
  margin-bottom: 1rem;
}

.ql-editor ul, .ql-editor ol {
  margin-bottom: 1rem;
}

.ql-editor li {
  margin-bottom: 0.25rem;
}

.editor-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #e5e7eb;
}

.changes-summary {
  background: #f0f9ff;
  border: 1px solid #0ea5e9;
  border-radius: 6px;
  padding: 1rem;
  margin-top: 1rem;
}

.changes-summary h4 {
  margin: 0 0 0.5rem 0;
  color: #0c4a6e;
}

.changes-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.changes-count {
  font-weight: 600;
  color: #0369a1;
}

.changes-detail {
  border-top: 1px solid #0ea5e9;
  padding-top: 1rem;
}

.change-preview {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.change-before,
.change-after {
  padding: 1rem;
  border-radius: 6px;
}

.change-before {
  background: #fef2f2;
  border: 1px solid #fca5a5;
}

.change-after {
  background: #f0fdf4;
  border: 1px solid #86efac;
}

.change-before strong,
.change-after strong {
  display: block;
  margin-bottom: 0.5rem;
  font-size: 0.875rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.change-before strong {
  color: #dc2626;
}

.change-after strong {
  color: #16a34a;
}

/* Feedback Items */
.feedback-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.feedback-item {
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  padding: 1rem;
}

.feedback-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.feedback-type {
  font-weight: 600;
  color: #374151;
}

.feedback-priority {
  padding: 0.2rem 0.5rem;
  border-radius: 12px;
  font-size: 0.7rem;
  font-weight: 600;
}

.text-reference, .suggested-text {
  margin-top: 0.5rem;
  padding: 0.5rem;
  background: white;
  border-radius: 4px;
  font-style: italic;
}

.suggested-text {
  background: #f0fdf4;
  border-left: 3px solid #10b981;
}

/* Form Styles */
.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #374151;
}

.form-input, .form-select, .form-textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.95rem;
  transition: border-color 0.2s ease;
}

.form-input:focus, .form-select:focus, .form-textarea:focus {
  outline: none;
  border-color: #205493;
  box-shadow: 0 0 0 2px rgba(32, 84, 147, 0.1);
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

/* Feedback Item Forms */
.feedback-item-form {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 1rem;
  position: relative;
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  font-weight: 600;
  color: #475569;
}

.remove-btn {
  background: #ef4444;
  color: white;
  border: none;
  border-radius: 4px;
  width: 28px;
  height: 28px;
  cursor: pointer;
  font-size: 1rem;
  line-height: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.remove-btn:hover {
  background: #dc2626;
  transform: scale(1.05);
}

.add-feedback-btn {
  width: 100%;
  margin-top: 1rem;
  padding: 0.75rem;
  border: 2px dashed #205493;
  background: transparent;
  color: #205493;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-weight: 500;
}

.add-feedback-btn:hover {
  background: #205493;
  color: white;
  border-style: solid;
}

/* Button Styles */

/* Buttons */
.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  text-decoration: none;
  display: inline-block;
  text-align: center;
}

.btn-primary {
  background: #205493;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #1c4a86;
}

.btn-primary:disabled {
  background: #9ca3af;
  cursor: not-allowed;
}

.btn-secondary {
  background: #6b7280;
  color: white;
}

.btn-secondary:hover {
  background: #4b5563;
}

/* Success/Submit Button - Organizational Green */
.btn-success {
  background: #28a745;
  color: white;
}

.btn-success:hover:not(:disabled) {
  background: #218838;
}

.btn-success:disabled {
  background: #9ca3af;
  cursor: not-allowed;
}

/* Outline Button */
.btn-outline {
  background: transparent;
  color: #205493;
  border: 2px solid #205493;
}

.btn-outline:hover {
  background: #205493;
  color: white;
}

/* Small Button */
.btn-sm {
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
}

.form-actions {
  display: flex;
  gap: 1rem;
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid #e5e7eb;
}

/* Success State */
.success-container {
  text-align: center;
  padding: 3rem 2rem;
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  border-radius: 8px;
  margin-top: 2rem;
}

.changes-alert {
  background-color: #fef3c7;
  border: 1px solid #f59e0b;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 2rem;
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
}

.changes-alert .icon {
  font-size: 1.2rem;
  margin-top: 0.1rem;
}

.success-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.help-text {
  font-size: 0.9rem;
  color: #6b7280;
  margin-bottom: 1rem;
}

/* Responsive Design */
@media (max-width: 768px) {
  .review-portal {
    padding: 1rem;
  }
  
  .review-header {
    flex-direction: column;
    gap: 1rem;
  }
  
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .form-actions {
    flex-direction: column;
  }
}
</style>
