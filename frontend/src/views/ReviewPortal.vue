<template>
  <div class="review-portal">
    
    <!-- Loading State -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p class="loading-text">Loading review content...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-container">
      <div class="error-icon">⚠️</div>
      <h2>Unable to Load Review</h2>
      <p>{{ error }}</p>
      <div class="error-explanation">
        <p v-if="error === 'Invalid review token'">
          This link is no longer valid. The most common reasons are:
        </p>
        <p v-else-if="error === 'Token has expired'">
          Your review link has expired. Review links are valid for a limited time after they are sent. Common reasons include:
        </p>
        <p v-else-if="error === 'Token access limit exceeded'">
          This review link has been opened the maximum number of times allowed. Common reasons include:
        </p>
        <p v-else-if="error === 'Token has been deactivated'">
          This review link has been deactivated by the document owner. This may happen when:
        </p>
        <ul v-if="error === 'Invalid review token'">
          <li>The review was deleted or the system database was reset.</li>
          <li>The link in the email was incomplete or altered.</li>
          <li>The review was reassigned or replaced with a new link.</li>
        </ul>
        <ul v-else-if="error === 'Token has expired'">
          <li>The review deadline has passed.</li>
          <li>Too much time elapsed between when the email was sent and when this link was opened.</li>
        </ul>
        <ul v-else-if="error === 'Token access limit exceeded'">
          <li>The link was forwarded and opened by multiple people.</li>
          <li>You refreshed or reopened the link more times than the limit allows.</li>
        </ul>
        <ul v-else-if="error === 'Token has been deactivated'">
          <li>The review was cancelled or reassigned.</li>
          <li>A new review link was issued to replace this one.</li>
        </ul>
        <p class="error-contact-note">Please contact the person who sent you this link for a new invitation.</p>
      </div>
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
            <button @click="showChangesDetail = !showChangesDetail" class="btn btn-outline btn-sm">
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
import { toast } from '@/composables/useToast'
import { sanitizeHtml } from '@/utils/sanitize'

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
        sanitize: false,    // Allow HTML (sanitized below via DOMPurify)
        smartypants: true   // Use smart quotes and dashes
      })
      
      // Convert markdown to HTML and sanitize before rendering
      return sanitizeHtml(marked(this.review.topic_content))
    },
    
    canSubmit() {
      const hasOverallFeedback = !!(this.overallFeedback || '').trim()
      const hasFeedbackItemComment = (this.feedbackItems || []).some(item => !!(item?.comment || '').trim())
      if (!this.overallRecommendation) return false
      if (this.overallRecommendation === 'approve') return true
      return hasOverallFeedback || hasFeedbackItemComment || this.hasChanges
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
  
  mounted() {
    window.addEventListener('beforeunload', this.beforeUnloadHandler)
    this.loadReview()
  },
  unmounted() {
    window.removeEventListener('beforeunload', this.beforeUnloadHandler)
  },
  beforeRouteLeave(to, from, next) {
    if (!this.isDirty()) return next()
    const leave = window.confirm('You have unsaved review feedback. Leave without saving?')
    if (leave) return next()
    next(false)
  },
  
  methods: {
    isDirty() {
      if (this.submitted) return false
      const hasFeedbackItems = (this.feedbackItems || []).some(item => Object.values(item).some(v => (v||'').toString().trim()))
      return !!(this.overallRecommendation || this.overallFeedback || hasFeedbackItems || this.hasChanges)
    },
    beforeUnloadHandler(e) { if (this.isDirty()) { e.preventDefault(); e.returnValue = '' } },
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
      if (this.$refs.quillEditor && !this.quillEditor) {
        const toolbarOptions = [
          [{ 'header': [1, 2, 3, false] }],
          ['bold', 'italic', 'underline'],
          [{ 'list': 'ordered'}, { 'list': 'bullet' }],
          [{ 'align': [] }],
          ['link'],
          ['clean']
        ]

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
  toast.success('Review submitted successfully!')
        
      } catch (error) {
  toast.error('Failed to submit review: ' + error.message)
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
  toast.success('Draft saved successfully!')
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
    },

    
  }
}
</script>

<style scoped>
.review-portal {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  font-family: var(--font-family-sans);
  background-color: var(--bg-light-gray);
}

/* Loading and Error States */
.loading-container, .error-container {
  text-align: center;
  padding: 4rem 2rem;
  background-color: var(--bg-white);
  border-radius: var(--border-radius-lg);
  box-shadow: var(--box-shadow-sm);
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid var(--primary-light-blue);
  border-top: 4px solid var(--primary-deep-teal);
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
  color: var(--error-coral-red);
}

.error-container h2 {
    color: var(--text-dark-gray);
    margin-bottom: 0.5rem;
}

.error-container p {
    color: var(--text-medium-gray);
    margin-bottom: 1.5rem;
}

.error-explanation {
  text-align: left;
  background-color: var(--bg-light-gray, #f8f9fa);
  border: 1px solid var(--border-light-gray, #dee2e6);
  border-radius: var(--border-radius-md, 0.375rem);
  padding: 1rem 1.25rem;
  margin: 0 auto 1.5rem;
  max-width: 480px;
}

.error-explanation ul {
  margin: 0.5rem 0 0.75rem 1.25rem;
  padding: 0;
  color: var(--text-medium-gray);
}

.error-explanation li {
  margin-bottom: 0.25rem;
}

.error-contact-note {
  font-style: italic;
  margin-bottom: 0 !important;
  color: var(--text-medium-gray);
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
  border-bottom: 2px solid var(--border-light-gray);
}

.review-title h1 {
  margin: 0 0 0.5rem 0;
  color: var(--text-dark-gray);
  font-size: 2rem;
  font-weight: 600;
}

.topic-id-header {
  background: var(--primary-deep-teal);
  color: var(--bg-white);
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
  background: var(--primary-light-blue);
  color: var(--primary-dark-blue);
  border-radius: 20px;
  font-weight: 500;
}

.due-date.overdue {
  background: var(--error-light-red);
  color: var(--error-dark-red);
}

.priority {
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-weight: 600;
  font-size: 0.75rem;
  text-transform: uppercase;
}

.priority-low { background: var(--info-light-blue); color: var(--info-dark-blue); }
.priority-medium { background: var(--warning-light-yellow); color: var(--warning-dark-yellow); }
.priority-high { background: var(--error-light-red); color: var(--error-dark-red); }
.priority-critical { background: var(--error-light-red); color: var(--error-dark-red); }


.access-info {
  font-size: 0.85rem;
  color: var(--text-medium-gray);
  background: var(--bg-white);
  padding: 0.5rem 1rem;
  border-radius: var(--border-radius-md);
}

/* Content Sections */
.author-message, .content-section, .existing-feedback, .feedback-form {
  background: var(--bg-white);
  border: 1px solid var(--border-light-gray);
  border-radius: var(--border-radius-lg);
  padding: 1.5rem;
  margin-bottom: 2rem;
  box-shadow: var(--box-shadow-sm);
}

.author-message {
  background: var(--info-light-blue);
  border-left: 4px solid var(--primary-deep-teal);
}

.content-viewer {
  background: var(--bg-white);
  border: 1px solid var(--border-light-gray);
  border-radius: var(--border-radius-md);
  padding: 1.5rem;
  max-height: 500px;
  overflow-y: auto;
}

.content-text {
  line-height: 1.6;
  color: var(--text-dark-gray);
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
  color: var(--text-dark-gray);
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
  border-left: 4px solid var(--border-light-gray);
  padding-left: 1rem;
  margin: 1rem 0;
  font-style: italic;
  color: var(--text-medium-gray);
}

.content-text code {
  background: var(--bg-white);
  padding: 0.125rem 0.25rem;
  border-radius: 0.25rem;
  font-family: var(--font-family-mono);
  font-size: 0.875rem;
}

.content-text pre {
  background: var(--bg-white);
  padding: 1rem;
  border-radius: var(--border-radius-lg);
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
  border: 1px solid var(--border-light-gray);
  padding: 0.5rem;
  text-align: left;
}

.content-text th {
  background: var(--bg-white);
  font-weight: 600;
}

.content-text a {
  color: var(--primary-dark-blue);
  text-decoration: underline;
}

.content-text a:hover {
  color: var(--primary-deep-teal);
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

.editor-container {
  background: var(--bg-white);
  border: 1px solid var(--border-light-gray);
  border-radius: var(--border-radius-md);
  padding: 1rem;
}

.editor-notice {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: var(--warning-light-yellow);
  border: 1px solid var(--warning-dark-yellow);
  border-radius: var(--border-radius-md);
  padding: 0.75rem;
  margin-bottom: 1rem;
  font-size: 0.875rem;
  color: var(--warning-dark-yellow);
}

.notice-icon {
  font-size: 1.2rem;
}

.quill-wrapper {
  background: var(--bg-white);
  border-radius: var(--border-radius-md);
  margin: 1rem 0;
}

.quill-editor {
  min-height: 400px;
}

/* Quill Snow theme customization */
.ql-toolbar {
  border-top: 1px solid var(--border-light-gray);
  border-left: 1px solid var(--border-light-gray);
  border-right: 1px solid var(--border-light-gray);
  border-bottom: none;
  border-radius: var(--border-radius-md) var(--border-radius-md) 0 0;
}

.ql-container {
  border-bottom: 1px solid var(--border-light-gray);
  border-left: 1px solid var(--border-light-gray);
  border-right: 1px solid var(--border-light-gray);
  border-top: none;
  border-radius: 0 0 var(--border-radius-md) var(--border-radius-md);
  font-family: var(--font-family-sans);
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
  color: var(--text-dark-gray);
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
  border-top: 1px solid var(--border-light-gray);
}

.changes-summary {
  background: var(--info-light-blue);
  border: 1px solid var(--info-dark-blue);
  border-radius: var(--border-radius-md);
  padding: 1rem;
  margin-top: 1rem;
}

.changes-summary h4 {
  margin: 0 0 0.5rem 0;
  color: var(--info-dark-blue);
}

.changes-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.changes-count {
  font-weight: 600;
  color: var(--info-dark-blue);
}

.changes-detail {
  border-top: 1px solid var(--info-dark-blue);
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
  border-radius: var(--border-radius-md);
}

.change-before {
  background: var(--error-light-red);
  border: 1px solid var(--error-dark-red);
}

.change-after {
  background: var(--success-light-green);
  border: 1px solid var(--success-dark-green);
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
  color: var(--error-dark-red);
}

.change-after strong {
  color: var(--success-dark-green);
}

/* Feedback Items */
.feedback-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.feedback-item {
  background: var(--bg-white);
  border: 1px solid var(--border-light-gray);
  border-radius: var(--border-radius-md);
  padding: 1rem;
}

.feedback-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.feedback-type {
  font-weight: 600;
  color: var(--text-dark-gray);
}

.feedback-priority {
  padding: 0.2rem 0.6rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.feedback-content p {
  margin: 0.5rem 0;
}

.text-reference, .suggested-text {
  background: var(--bg-white);
  border: 1px solid var(--border-light-gray);
  padding: 0.5rem;
  border-radius: var(--border-radius-sm);
  margin-top: 0.5rem;
  font-size: 0.9rem;
}

.text-reference strong, .suggested-text strong {
  color: var(--text-medium-gray);
}

/* Feedback Form */
.feedback-form h3, .specific-feedback h4 {
  color: var(--text-dark-gray);
  margin-bottom: 1rem;
  border-bottom: 1px solid var(--border-light-gray);
  padding-bottom: 0.5rem;
}

.changes-alert {
  background-color: var(--info-light-blue);
  border: 1px solid var(--info-dark-blue);
  color: var(--info-dark-blue);
  padding: 1rem;
  border-radius: var(--border-radius-md);
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.changes-alert .icon {
  font-size: 1.5rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: var(--text-dark-gray);
}

.form-select, .form-input, .form-textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid var(--border-light-gray);
  border-radius: var(--border-radius-md);
  background-color: var(--bg-white);
  color: var(--text-dark-gray);
  font-size: 1rem;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.form-select:focus, .form-input:focus, .form-textarea:focus {
  outline: none;
  border-color: var(--primary-deep-teal);
  box-shadow: 0 0 0 3px rgba(32, 84, 147, 0.1);
}

.help-text {
  font-size: 0.9rem;
  color: var(--text-medium-gray);
  margin-top: -0.5rem;
  margin-bottom: 1rem;
}

.feedback-item-form {
  border: 1px solid var(--border-light-gray);
  border-radius: var(--border-radius-lg);
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  background-color: var(--bg-white);
  position: relative;
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid var(--border-light-gray);
}

.item-header span {
  font-weight: 600;
  color: var(--text-dark-gray);
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.add-feedback-btn {
  width: 100%;
  margin-top: 1rem;
}

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  align-items: center;
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--border-light-gray);
}

/* Success Message */
.success-container {
  text-align: center;
  padding: 4rem 2rem;
  background-color: var(--success-light-green);
  border: 1px solid var(--success-dark-green);
  border-radius: var(--border-radius-lg);
  color: var(--success-dark-green);
}

.success-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.success-container h3 {
  color: var(--success-dark-green);
}

/* General Button Styles */
.btn {
  padding: 0.75rem 1.5rem;
  border-radius: var(--border-radius-md);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid transparent;
  text-align: center;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background-color: var(--primary-deep-teal);
  color: var(--bg-white);
}
.btn-primary:hover:not(:disabled) {
  background-color: var(--primary-dark-blue);
}

.btn-secondary {
  background-color: var(--border-light-gray);
  color: var(--text-primary-charcoal);
  border-color: var(--extended-lavender-gray) !important;
}
.btn-secondary:hover:not(:disabled) {
  background-color: var(--extended-lavender-gray);
}

.btn-success {
  background-color: var(--success-dark-green);
  color: var(--bg-white);
}
.btn-success:hover:not(:disabled) {
  background-color: #14532d; /* Darker green */
}

.btn-outline {
  background-color: transparent;
  border-color: var(--primary-deep-teal);
  color: var(--primary-deep-teal);
}
.btn-outline:hover:not(:disabled) {
  background-color: var(--primary-light-blue);
}

.btn-sm {
  padding: 0.25rem 0.75rem;
  font-size: 0.875rem;
}
</style>
