<template>
  <div class="request-review-modal" v-if="isVisible" @click.self="closeModal">
    <div class="modal-content">
      <div class="modal-header-row modal-header">
        <h3>Request Review</h3>
        <button @click="closeModal" class="plain-close close-btn">&times;</button>
      </div>
      
      <div class="modal-body">
        <div class="topic-info">
          <h4>{{ topic.title }}</h4>
          <p class="topic-summary">{{ topic.summary || 'No summary available' }}</p>
        </div>
        
        <form @submit.prevent="submitRequest">
          <!-- Review Type Selection -->
          <div class="form-group">
            <label class="review-type-label">Review Type</label>
            <div class="review-type-options">
              <label class="review-type-option">
                <input 
                  type="radio" 
                  v-model="reviewType" 
                  value="normal"
                  @change="onReviewTypeChange"
                />
                <span class="option-title">Normal Review</span>
                <span class="option-description">All reviewers work in parallel</span>
              </label>
              <label class="review-type-option">
                <input 
                  type="radio" 
                  v-model="reviewType" 
                  value="sequential"
                  @change="onReviewTypeChange"
                />
                <span class="option-title">Sequential Review</span>
                <span class="option-description">Reviewers work one after another in order</span>
              </label>
            </div>
          </div>

          <!-- Reviewer Selection -->
          <div class="form-group">
            <label>
              Select Reviewer<span v-if="reviewType === 'sequential'" class="sequential-note">(order matters)</span> *
            </label>
            <div v-if="reviewers.length" class="reviewers-list">
              <label v-for="reviewer in reviewers" :key="reviewer.id" class="reviewer-option">
                <input 
                  type="checkbox" 
                  :value="reviewer.id" 
                  v-model="selectedReviewers"
                />
                <span>{{ reviewer.name }} <small v-if="reviewer.role">({{ reviewer.role }})</small></span>
              </label>
            </div>
            <div v-else class="empty-help">No reviewers available. Please contact an administrator.</div>
          </div>

          <!-- Order hint for sequential reviews -->
          <div v-if="reviewType === 'sequential' && selectedReviewers.length > 1" class="sequential-hint">
            <strong>Review order:</strong> Reviewers will be assigned in the order selected above (first selected = first reviewer)
          </div>
          
          <!-- Priority (Normal Review only) -->
          <div v-if="reviewType === 'normal'" class="form-group">
            <label>Priority</label>
            <select v-model="priority" class="form-input">
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
              <option value="urgent">Urgent</option>
            </select>
          </div>
          
          <!-- Due Date -->
          <div class="form-group">
            <label>Due Date</label>
            <input 
              v-model="dueDate" 
              type="date" 
              class="form-input"
              :min="today"
            />
            <small class="form-help">Leave blank for default (7 days)</small>
          </div>
          
          <!-- Message to Reviewer(s) -->
          <div class="form-group">
            <label>Message to Reviewer<span v-if="selectedReviewers.length > 1">s</span></label>
            <textarea 
              v-model="message" 
              class="form-input"
              rows="4"
              placeholder="Any specific areas you'd like the reviewer(s) to focus on, or additional context..."
            ></textarea>
          </div>

          <!-- Sequential Options -->
          <div v-if="reviewType === 'sequential'" class="form-group sequential-options">
            <h5>Sequential Review Settings</h5>
            <label class="form-check">
              <input type="checkbox" v-model="autoAdvance" />
              <span>Auto-advance to next reviewer when current reviewer approves</span>
            </label>
            <label class="form-check">
              <input type="checkbox" v-model="pauseOnChanges" />
              <span>Pause sequence if reviewer requests changes</span>
            </label>
          </div>
          
          <div class="form-actions">
            <button type="button" @click="closeModal" class="btn btn-secondary">
              Cancel
            </button>
            <button type="submit" :disabled="loading || selectedReviewers.length === 0" class="btn btn-primary">
              {{ loading ? 'Submitting...' : 'Request Review' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { getReviewers, requestReview } from '@/api/reviews.js'
import { apiPost } from '@/api/base.js'
import { toast } from '@/composables/useToast'

export default {
  name: 'RequestReviewModal',
  
  props: {
    topic: {
      type: Object,
      required: true
    },
    isVisible: {
      type: Boolean,
      default: false
    },
    currentUser: {
      type: Object,
      required: true
    }
  },
  
  data() {
    return {
      reviewers: [],
      selectedReviewers: [],
      reviewType: 'normal',
      priority: 'medium',
      dueDate: '',
      message: '',
      loading: false,
      autoAdvance: true,
      pauseOnChanges: true
    }
  },
  
  computed: {
    today() {
      return new Date().toISOString().split('T')[0]
    }
  },
  
  watch: {
    isVisible(newVal) {
      if (newVal) {
        // Reset form when modal opens
        this.resetForm()
      }
    }
  },
  
  async mounted() {
    await this.loadReviewers()
  },
  
  methods: {
    async loadReviewers() {
      try {
        this.reviewers = await getReviewers()
      } catch (error) {
        console.error('Failed to load reviewers:', error)
        toast.error('Failed to load available reviewers')
      }
    },

    onReviewTypeChange() {
      // Reset selected reviewers when changing review type
      // to ensure fresh selection for the new mode
    },
    
    async submitRequest() {
      this.loading = true
      
      try {
        if (this.reviewType === 'sequential' && this.selectedReviewers.length > 1) {
          await this.submitSequentialReview()
        } else if (this.reviewType === 'sequential' && this.selectedReviewers.length === 1) {
          // Single reviewer with sequential review is effectively normal review
          toast.warning('Sequential review requires at least 2 reviewers. Submitting as normal review.')
          await this.submitNormalReview()
        } else {
          await this.submitNormalReview()
        }
        
        this.$emit('review-requested')
        this.closeModal()
        toast.success('Review requested successfully!')
        
      } catch (error) {
        console.error('Failed to request review:', error)
        toast.error('Failed to request review: ' + error.message)
      } finally {
        this.loading = false
      }
    },

    async submitNormalReview() {
      // Create a review for each selected reviewer
      const reviewPromises = this.selectedReviewers.map(async (reviewerId) => {
        const reviewData = {
          topic_id: this.topic.id,
          reviewer_id: parseInt(reviewerId),
          requested_by: this.currentUser.id,
          priority: this.priority,
          message: this.message
        }
        
        if (this.dueDate) {
          reviewData.due_date = new Date(this.dueDate).toISOString()
        }
        
        return await requestReview(reviewData)
      })

      await Promise.all(reviewPromises)
    },

    async submitSequentialReview() {
      // Get current user info
      const currentUser = this.currentUser || JSON.parse(localStorage.getItem('user') || '{}')
      
      // Create sequential review
      const sequencePayload = {
        topic_id: this.topic.id,
        created_by: Number(currentUser.id) || 1,
        name: `Review Sequence for ${this.topic.title}`,
        description: 'Sequential review workflow',
        initial_message: this.message || `Please review "${this.topic.title}".`,
        reviewers: this.selectedReviewers.map((reviewerId, index) => ({
          reviewer_id: parseInt(reviewerId),
          step_name: index === 0 ? 'First Review' : `Review Step ${index + 1}`,
          instructions: index === 0 ? 'Please provide your initial review' : 'Please review based on previous reviewer comments'
        })),
        auto_advance_on_approve: this.autoAdvance,
        pause_on_changes: this.pauseOnChanges,
        auto_start: true
      }

      if (this.dueDate) {
        sequencePayload.due_date = new Date(this.dueDate).toISOString()
      }

      return await apiPost('/api/sequences/', sequencePayload)
    },
    
    resetForm() {
      this.selectedReviewers = []
      this.reviewType = 'normal'
      this.priority = 'medium'
      this.dueDate = this.getDefaultDueDate()
      this.message = ''
      this.autoAdvance = true
      this.pauseOnChanges = true
    },

    getDefaultDueDate() {
      const defaultDate = new Date()
      defaultDate.setDate(defaultDate.getDate() + 7)
      return defaultDate.toISOString().split('T')[0]
    },
    
    closeModal() {
      this.$emit('close')
    }
  }
}
</script>

<style>
.request-review-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 650px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h3 {
  margin: 0;
  color: #1f2937;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #6b7280;
  cursor: pointer;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  color: #374151;
}

.modal-body {
  padding: 1.5rem;
}

.topic-info {
  background: #f9fafb;
  padding: 1rem;
  border-radius: 6px;
  margin-bottom: 1.5rem;
}

.topic-info h4 {
  margin: 0 0 0.5rem 0;
  color: #1f2937;
}

.topic-summary {
  margin: 0;
  color: #6b7280;
  font-size: 0.9rem;
}

.form-group {
  margin-bottom: 1.25rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #374151;
}

.form-input {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-size: 1rem;
  box-sizing: border-box;
}

.form-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-help {
  display: block;
  margin-top: 0.25rem;
  font-size: 0.875rem;
  color: #6b7280;
}

/* Review Type Selection */
.review-type-label {
  font-weight: 600 !important;
}

.review-type-options {
  display: flex;
  gap: 1rem;
  margin-top: 0.5rem;
}

.review-type-option {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 0.75rem;
  border: 2px solid #d1d5db;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.review-type-option input[type="radio"] {
  cursor: pointer;
  margin-right: 0.5rem;
}

.review-type-option:hover {
  border-color: #9ca3af;
  background-color: #f9fafb;
}

.review-type-option input[type="radio"]:checked ~ .option-title {
  color: #3b82f6;
}

.review-type-option input[type="radio"]:checked ~ .option-description {
  color: #3b82f6;
}

.review-type-option input[type="radio"]:checked {
  accent-color: #3b82f6;
}

.option-title {
  font-weight: 500;
  color: #374151;
  margin-bottom: 0.25rem;
}

.option-description {
  font-size: 0.85rem;
  color: #6b7280;
}

.sequential-note {
  color: #f59e0b;
  font-size: 0.9rem;
  margin-left: 0.5rem;
}

/* Reviewer Selection */
.reviewers-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.reviewer-option {
  display: flex;
  align-items: center;
  padding: 0.5rem;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.reviewer-option:hover {
  background-color: #f3f4f6;
}

.reviewer-option input[type="checkbox"] {
  margin-right: 0.5rem;
  cursor: pointer;
}

.reviewer-option span {
  flex: 1;
}

.empty-help {
  padding: 1rem;
  background-color: #fef3c7;
  border-left: 4px solid #f59e0b;
  border-radius: 4px;
  color: #92400e;
  font-size: 0.9rem;
}

/* Sequential Hints & Options */
.sequential-hint {
  padding: 0.75rem;
  background-color: #dbeafe;
  border-left: 4px solid #3b82f6;
  border-radius: 4px;
  color: #1e40af;
  font-size: 0.9rem;
  margin-bottom: 1rem;
}

.sequential-options {
  background-color: #f0f9ff;
  border: 1px solid #bfdbfe;
  border-radius: 6px;
  padding: 1rem;
  margin-bottom: 1rem;
}

.sequential-options h5 {
  margin: 0 0 0.75rem 0;
  color: #1e40af;
  font-size: 1rem;
}

.form-check {
  display: flex;
  align-items: center;
  margin-bottom: 0.5rem;
  cursor: pointer;
}

.form-check input[type="checkbox"] {
  margin-right: 0.5rem;
  cursor: pointer;
}

.form-check span {
  font-size: 0.95rem;
  color: #374151;
}

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid #e5e7eb;
}

.btn {
  padding: 0.5rem 1rem;
  border-radius: 4px;
  font-size: 0.9rem;
  cursor: pointer;
  border: none;
  font-weight: 500;
}

.btn-secondary {
  background: #f3f4f6;
  color: #374151;
}

.btn-secondary:hover {
  background: #e5e7eb;
}

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #2563eb;
}

.btn-primary:disabled {
  background: #9ca3af;
  cursor: not-allowed;
}
</style>
