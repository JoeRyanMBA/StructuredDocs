<template>
  <div class="review-card">
    <div class="review-header">
      <div class="review-info">
        <h4>{{ review.topic_title }}</h4>
        <div class="review-meta">
          <span class="requester">Requested by: {{ review.requester_name }}</span>
          <span class="due-date" :class="{ overdue: isOverdue }">
            Due: {{ formatDate(review.due_date) }}
          </span>
          <span class="priority" :class="'priority-' + review.priority">
            {{ review.priority.toUpperCase() }}
          </span>
        </div>
      </div>
      <div class="review-status">
        <span class="status-badge" :class="'status-' + review.status">
          {{ formatStatus(review.status) }}
        </span>
      </div>
    </div>
    
    <div class="review-message" v-if="review.author_message">
      <h5>Message from Author:</h5>
      <p>{{ review.author_message }}</p>
    </div>
    
    <div class="review-actions">
      <button 
        v-if="review.status === 'pending'" 
        @click="startReview"
        class="btn btn-secondary btn-sm"
        :disabled="loading"
      >
        Start Review
      </button>
      
      <button 
        @click="viewTopic" 
        class="btn btn-primary btn-sm"
      >
        View Topic
      </button>
      
      <button 
        v-if="review.status === 'in_progress'" 
        @click="showReviewForm = !showReviewForm"
        class="btn btn-success btn-sm"
      >
        {{ showReviewForm ? 'Cancel' : 'Submit Review' }}
      </button>
    </div>
    
    <!-- Review Form -->
    <div v-if="showReviewForm" class="review-form">
      <form @submit.prevent="submitReview">
        <div class="form-group">
          <label>Recommendation *</label>
          <select v-model="recommendation" required class="form-input">
            <option value="">Select recommendation...</option>
            <option value="approve">Approve</option>
            <option value="approve_with_changes">Approve with Changes</option>
            <option value="needs_more_info">Needs More Information</option>
            <option value="reject">Reject</option>
          </select>
        </div>
        
        <div class="form-group">
          <label>Feedback to Author *</label>
          <textarea 
            v-model="feedback" 
            required
            class="form-input"
            rows="4"
            placeholder="Provide detailed feedback for the author..."
          ></textarea>
        </div>
        
        <div class="form-group">
          <label>Private Notes (Optional)</label>
          <textarea 
            v-model="reviewNotes" 
            class="form-input"
            rows="2"
            placeholder="Private notes for your records..."
          ></textarea>
        </div>
        
        <div class="form-actions">
          <button type="button" @click="showReviewForm = false" class="btn btn-secondary btn-sm">
            Cancel
          </button>
          <button type="submit" :disabled="loading" class="btn btn-success btn-sm">
            {{ loading ? 'Submitting...' : 'Submit Review' }}
          </button>
        </div>
      </form>
    </div>
    
    <!-- Completed Review Display -->
    <div v-if="review.status === 'completed'" class="completed-review">
      <div class="recommendation">
        <strong>Recommendation:</strong> 
        <span :class="'rec-' + review.recommendation">
          {{ formatRecommendation(review.recommendation) }}
        </span>
      </div>
      <div class="feedback" v-if="review.feedback">
        <strong>Feedback:</strong>
        <p>{{ review.feedback }}</p>
      </div>
      <div class="completed-date">
        <small>Completed: {{ formatDate(review.completed_at) }}</small>
      </div>
    </div>
  </div>
</template>

<script>
import { startReview, submitReview } from '@/api/reviews.js'

export default {
  name: 'ReviewCard',
  
  props: {
    review: {
      type: Object,
      required: true
    }
  },
  
  data() {
    return {
      showReviewForm: false,
      recommendation: '',
      feedback: '',
      reviewNotes: '',
      loading: false
    }
  },
  
  computed: {
    isOverdue() {
      if (!this.review.due_date) return false
      return new Date(this.review.due_date) < new Date() && 
             ['pending', 'in_progress'].includes(this.review.status)
    }
  },
  
  methods: {
    async startReview() {
      this.loading = true
      try {
        await startReview(this.review.id)
        this.$emit('review-updated')
        alert('Review started!')
      } catch (error) {
        console.error('Failed to start review:', error)
        alert('Failed to start review: ' + error.message)
      } finally {
        this.loading = false
      }
    },
    
    async submitReview() {
      this.loading = true
      try {
        const reviewData = {
          recommendation: this.recommendation,
          feedback: this.feedback,
          review_notes: this.reviewNotes
        }
        
        await submitReview(this.review.id, reviewData)
        this.$emit('review-updated')
        this.showReviewForm = false
        alert('Review submitted successfully!')
        
        // Reset form
        this.recommendation = ''
        this.feedback = ''
        this.reviewNotes = ''
        
      } catch (error) {
        console.error('Failed to submit review:', error)
        alert('Failed to submit review: ' + error.message)
      } finally {
        this.loading = false
      }
    },
    
    viewTopic() {
      this.$router.push(`/topics/${this.review.topic_id}/edit`)
    },
    
    formatDate(dateString) {
      if (!dateString) return 'Not set'
      return new Date(dateString).toLocaleDateString()
    },
    
    formatStatus(status) {
      const statusMap = {
        'pending': 'Review Pending',
        'in_progress': 'Review In Progress',
        'completed': 'Review Completed',
        'declined': 'Review Declined'
      }
      return statusMap[status] || status
    },
    
    formatRecommendation(rec) {
      const recMap = {
        'approve': 'Approve',
        'approve_with_changes': 'Approve with Changes',
        'needs_more_info': 'Needs More Information',
        'reject': 'Reject'
      }
      return recMap[rec] || rec
    }
  }
}
</script>

<style>
.review-card {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1rem;
  background: white;
}

.review-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.review-status {
  display: flex;
  align-items: center;
  min-height: 2rem;
}

.review-info h4 {
  margin: 0 0 0.5rem 0;
  color: #1f2937;
}

.review-meta {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  font-size: 0.875rem;
  color: #6b7280;
}

.due-date.overdue {
  color: #dc2626;
  font-weight: 600;
}

.priority {
  padding: 0.125rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
}

.priority-low { background: #dbeafe; color: #1e40af; }
.priority-medium { background: #fef3c7; color: #92400e; }
.priority-high { background: #fecaca; color: #991b1b; }
.priority-urgent { background: #fca5a5; color: #7f1d1d; }

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 1.5rem;
  white-space: nowrap;
}

.status-pending { background: #fef3c7; color: #92400e; }
.status-in_progress { background: #dbeafe; color: #1e40af; }
.status-completed { background: #d1fae5; color: #065f46; }
.status-declined { background: #fecaca; color: #991b1b; }

.review-message {
  background: #f9fafb;
  padding: 1rem;
  border-radius: 6px;
  margin-bottom: 1rem;
}

.review-message h5 {
  margin: 0 0 0.5rem 0;
  color: #374151;
}

.review-message p {
  margin: 0;
  color: #6b7280;
}

.review-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.btn {
  padding: 0.375rem 0.75rem;
  border-radius: 4px;
  font-size: 0.875rem;
  cursor: pointer;
  border: none;
  text-decoration: none;
}

.btn-sm {
  padding: 0.25rem 0.5rem;
  font-size: 0.8rem;
}

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-secondary {
  background: #f3f4f6;
  color: #374151;
}

.btn-success {
  background: #10b981;
  color: white;
}

.review-form {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #e5e7eb;
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

.form-actions {
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
}

.completed-review {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #e5e7eb;
}

.recommendation {
  margin-bottom: 0.5rem;
}

.rec-approve { color: #065f46; }
.rec-approve_with_changes { color: #92400e; }
.rec-needs_more_info { color: #1e40af; }
.rec-reject { color: #991b1b; }

.feedback p {
  margin: 0.5rem 0;
  color: #374151;
}

.completed-date {
  color: #6b7280;
  font-size: 0.875rem;
}
</style>
