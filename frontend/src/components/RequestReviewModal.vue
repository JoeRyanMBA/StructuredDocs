<template>
  <div class="request-review-modal" v-if="isVisible" @click.self="closeModal">
    <div class="modal-content">
      <div class="modal-header">
        <h3>Request Review</h3>
        <button @click="closeModal" class="close-btn">&times;</button>
      </div>
      
      <div class="modal-body">
        <div class="topic-info">
          <h4>{{ topic.title }}</h4>
          <p class="topic-summary">{{ topic.summary || 'No summary available' }}</p>
        </div>
        
        <form @submit.prevent="submitRequest">
          <div class="form-group">
            <label>Select Reviewer *</label>
            <select v-model="selectedReviewer" required class="form-input">
              <option value="">Choose a reviewer...</option>
              <option 
                v-for="reviewer in reviewers" 
                :key="reviewer.id" 
                :value="reviewer.id"
              >
                {{ reviewer.name }} ({{ reviewer.role }}) - {{ reviewer.division }}
              </option>
            </select>
          </div>
          
          <div class="form-group">
            <label>Priority</label>
            <select v-model="priority" class="form-input">
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
              <option value="urgent">Urgent</option>
            </select>
          </div>
          
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
          
          <div class="form-group">
            <label>Message to Reviewer</label>
            <textarea 
              v-model="message" 
              class="form-input"
              rows="4"
              placeholder="Any specific areas you'd like the reviewer to focus on, or additional context..."
            ></textarea>
          </div>
          
          <div class="form-actions">
            <button type="button" @click="closeModal" class="btn btn-secondary">
              Cancel
            </button>
            <button type="submit" :disabled="loading" class="btn btn-primary">
              {{ loading ? 'Requesting...' : 'Request Review' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { getReviewers, requestReview } from '@/api/reviews.js'
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
      selectedReviewer: '',
      priority: 'medium',
      dueDate: '',
      message: '',
      loading: false
    }
  },
  
  computed: {
    today() {
      return new Date().toISOString().split('T')[0]
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
    
    async submitRequest() {
      this.loading = true
      
      try {
        const reviewData = {
          topic_id: this.topic.id,
          reviewer_id: parseInt(this.selectedReviewer),
          requested_by: this.currentUser.id,
          priority: this.priority,
          message: this.message
        }
        
        if (this.dueDate) {
          reviewData.due_date = new Date(this.dueDate).toISOString()
        }
        
        await requestReview(reviewData)
        
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
    
    closeModal() {
      this.$emit('close')
      // Reset form
      this.selectedReviewer = ''
      this.priority = 'medium'
      this.dueDate = ''
      this.message = ''
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
  max-width: 600px;
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
  margin-bottom: 1rem;
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

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 1.5rem;
}

.btn {
  padding: 0.5rem 1rem;
  border-radius: 4px;
  font-size: 0.9rem;
  cursor: pointer;
  border: none;
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
