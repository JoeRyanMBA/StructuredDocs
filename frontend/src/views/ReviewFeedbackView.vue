<template>
  <div class="review-feedback-container">
    <div v-if="loading" class="text-center">
      <p>Loading review feedback...</p>
    </div>

    <div v-else-if="error" class="alert alert-danger" role="alert">
      {{ error }}
    </div>

    <div v-else class="review-feedback-content">
      <!-- Header -->
      <div class="header-section mb-4">
        <h1 class="h2 mb-3">Review Feedback</h1>
        <nav aria-label="breadcrumb">
          <ol class="breadcrumb">
            <li class="breadcrumb-item">
              <router-link to="/reviews">Reviews</router-link>
            </li>
            <li class="breadcrumb-item">
              <router-link to="/topics">Topics</router-link>
            </li>
            <li class="breadcrumb-item active" aria-current="page">
              {{ topic?.title || 'Topic' }} - Review Feedback
            </li>
          </ol>
        </nav>
      </div>

      <!-- Topic Info -->
      <div class="card mb-4">
        <div class="card-header bg-primary-subtle text-primary-emphasis">
          <h3 class="card-title mb-0">
            <i class="bi bi-file-text me-2"></i>{{ topic?.title }}
          </h3>
        </div>
        <div class="card-body">
          <div class="row">
            <div class="col-md-6">
              <p><strong>Status:</strong> 
                <span :class="statusBadgeClass">{{ formatStatus(topic?.status) }}</span>
              </p>
              <p><strong>Requested By:</strong> {{ review?.requester_name || '—' }}</p>
            </div>
            <div class="col-md-6">
              <p><strong>Last Updated:</strong> {{ formatDate(topic?.updated_at) }}</p>
              <p><strong>Priority:</strong> {{ review?.priority || '—' }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Structured Feedback Items -->
      <div v-if="review?.feedback_items?.length" class="card mb-4">
        <div class="card-header bg-danger-subtle text-danger-emphasis">
          <h4 class="card-title mb-0">
            <i class="bi bi-list-check me-2"></i>
            Requested Changes ({{ review.feedback_items.length }})
          </h4>
        </div>
        <div class="card-body p-0">
          <div
            v-for="(item, index) in review.feedback_items"
            :key="item.id"
            class="feedback-item"
            :class="'priority-border-' + item.priority"
          >
            <div class="feedback-item-header">
              <span class="feedback-index">#{{ index + 1 }}</span>
              <span class="feedback-type-badge">{{ formatFeedbackType(item.feedback_type) }}</span>
              <span v-if="item.section_title" class="feedback-section">
                <i class="bi bi-bookmark me-1"></i>{{ item.section_title }}
              </span>
              <span class="ms-auto d-flex gap-2">
                <span class="priority-pill" :class="'priority-' + item.priority">{{ item.priority }}</span>
                <span class="impact-pill" :class="'impact-' + item.impact">{{ item.impact }}</span>
              </span>
            </div>

            <div v-if="item.original_text || item.suggested_text" class="text-comparison">
              <div v-if="item.original_text" class="text-block original">
                <div class="text-block-label">Original</div>
                <div class="text-block-content">{{ item.original_text }}</div>
              </div>
              <div v-if="item.suggested_text" class="text-block suggested">
                <div class="text-block-label">Suggested</div>
                <div class="text-block-content">{{ item.suggested_text }}</div>
              </div>
            </div>

            <div v-if="item.comment" class="feedback-comment">
              <strong>Comment:</strong> {{ item.comment }}
            </div>
            <div v-if="item.rationale" class="feedback-rationale">
              <strong>Rationale:</strong> {{ item.rationale }}
            </div>
          </div>
        </div>
      </div>

      <!-- Review Feedback -->
      <div class="card mb-4">
        <div class="card-header bg-warning-subtle text-warning-emphasis">
          <h4 class="card-title mb-0">
            <i class="bi bi-chat-square-text me-2"></i>Reviewer Feedback
          </h4>
        </div>
        <div class="card-body">
          <div class="row mb-3">
            <div class="col-md-6">
              <p><strong>Reviewer:</strong> {{ review?.reviewer_name }}</p>
              <p><strong>Review Date:</strong> {{ formatDate(review?.updated_at) }}</p>
            </div>
            <div class="col-md-6">
              <p><strong>Recommendation:</strong> 
                <span :class="recommendationBadgeClass">{{ formatRecommendation(review?.recommendation) }}</span>
              </p>
              <p><strong>Status:</strong> 
                <span class="badge bg-warning">Revisions Requested</span>
              </p>
            </div>
          </div>

          <div v-if="review?.feedback" class="feedback-content">
            <h5>Reviewer Comments:</h5>
            <div class="feedback-text p-3 bg-light border-start border-warning border-4">
              {{ review.feedback }}
            </div>
          </div>

          <div v-if="review?.notes" class="reviewer-notes mt-3">
            <h5>Internal Notes:</h5>
            <div class="notes-text p-3 bg-light border-start border-info border-4">
              {{ review.notes }}
            </div>
          </div>

          <div v-if="!review?.feedback && !review?.notes" class="no-feedback">
            <p class="text-muted fst-italic">No specific feedback provided by the reviewer.</p>
          </div>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="action-buttons d-flex gap-3">
        <button 
          @click="editTopic" 
          class="btn btn-primary btn-lg"
        >
          <i class="bi bi-pencil-square me-2"></i>
          Edit Topic & Incorporate Changes
        </button>
        
        <button 
          @click="goBack" 
          class="btn btn-outline-secondary btn-lg"
        >
          <i class="bi bi-arrow-left me-2"></i>
          Back to Reviews
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'ReviewFeedbackView',
  props: {
    topicId: {
      type: Number,
      required: true
    },
    reviewId: {
      type: Number,
      required: true
    }
  },
  data() {
    return {
      loading: true,
      error: null,
      topic: null,
      review: null
    }
  },
  computed: {
    statusBadgeClass() {
      if (!this.topic?.status) return 'badge bg-secondary'
      
      const statusClasses = {
        'draft': 'badge bg-secondary',
        'pending_review': 'badge bg-warning',
        'approved': 'badge bg-success',
        'revisions_requested': 'badge bg-warning',
        'published': 'badge bg-primary',
        'rejected': 'badge bg-danger'
      }
      
      return statusClasses[this.topic.status] || 'badge bg-secondary'
    },
    
    recommendationBadgeClass() {
      if (!this.review?.recommendation) return 'badge bg-secondary'
      
      const recommendationClasses = {
        'approve': 'badge bg-success',
        'approve_with_changes': 'badge bg-warning',
        'needs_more_info': 'badge bg-info',
        'reject': 'badge bg-danger'
      }
      
      return recommendationClasses[this.review.recommendation] || 'badge bg-secondary'
    }
  },
  async mounted() {
    await this.loadData()
  },
  methods: {
    async loadData() {
      try {
        this.loading = true
        this.error = null

        // Load topic details
        const topicResponse = await axios.get(`/api/topics/${this.topicId}`)
        this.topic = topicResponse.data

        // Load review details
        const reviewResponse = await axios.get(`/api/reviews/${this.reviewId}`)
        this.review = reviewResponse.data

        // Verify review belongs to this topic
        if (this.review.topic_id !== this.topicId) {
          throw new Error('Review does not belong to this topic')
        }

      } catch (error) {
        console.error('Error loading review feedback:', error)
        this.error = error.response?.data?.error || 'Failed to load review feedback'
      } finally {
        this.loading = false
      }
    },

    formatFeedbackType(type) {
      const labels = {
        'general_comment': 'General Comment',
        'text_edit': 'Text Edit',
        'text_addition': 'Addition',
        'text_deletion': 'Deletion',
        'structural_change': 'Structural Change',
        'technical_correction': 'Technical Correction',
        'style_suggestion': 'Style Suggestion'
      }
      return labels[type] || type
    },

    formatStatus(status) {
      if (!status) return 'Unknown'
      return status.split('_').map(word => 
        word.charAt(0).toUpperCase() + word.slice(1)
      ).join(' ')
    },

    formatRecommendation(recommendation) {
      if (!recommendation) return 'Unknown'
      
      const recommendationLabels = {
        'approve': 'Approve',
        'approve_with_changes': 'Approve with Changes',
        'needs_more_info': 'Needs More Info',
        'reject': 'Reject'
      }
      
      return recommendationLabels[recommendation] || recommendation
    },

    formatDate(dateString) {
      if (!dateString) return 'Unknown'
      const date = new Date(dateString)
      return date.toLocaleDateString() + ' ' + date.toLocaleTimeString()
    },

    editTopic() {
      this.$router.push(`/topics/${this.topicId}/edit?reviewId=${this.reviewId}`)
    },

    goBack() {
      // Navigate back to reviews dashboard
      this.$router.push('/reviews')
    }
  }
}
</script>

<style scoped>
.review-feedback-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.badge {
  color: #000 !important;
}

.feedback-item {
  border-bottom: 1px solid #dee2e6;
  padding: 1rem 1.25rem;
}
.feedback-item:last-child { border-bottom: none; }
.priority-border-critical { border-left: 4px solid #dc3545; }
.priority-border-high     { border-left: 4px solid #fd7e14; }
.priority-border-medium   { border-left: 4px solid #ffc107; }
.priority-border-low      { border-left: 4px solid #198754; }

.feedback-item-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
  flex-wrap: wrap;
}
.feedback-index {
  font-weight: 700;
  color: #6c757d;
  font-size: 0.85rem;
}
.feedback-type-badge {
  background: #e9ecef;
  color: #495057;
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.2rem 0.55rem;
  border-radius: 4px;
}
.feedback-section {
  font-size: 0.82rem;
  color: #0d6efd;
}
.priority-pill, .impact-pill {
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  padding: 0.15rem 0.45rem;
  border-radius: 3px;
}
.priority-critical { background:#f8d7da; color:#842029; }
.priority-high     { background:#ffe5d0; color:#7c3a00; }
.priority-medium   { background:#fff3cd; color:#664d03; }
.priority-low      { background:#d1e7dd; color:#0a3622; }
.impact-major    { background:#f8d7da; color:#842029; }
.impact-moderate { background:#fff3cd; color:#664d03; }
.impact-minor    { background:#d1e7dd; color:#0a3622; }

.text-comparison {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
}
@media (max-width: 600px) { .text-comparison { grid-template-columns: 1fr; } }

.text-block { border-radius: 4px; overflow: hidden; }
.text-block-label {
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  padding: 0.2rem 0.6rem;
}
.text-block-content {
  padding: 0.5rem 0.75rem;
  font-size: 0.88rem;
  white-space: pre-wrap;
  word-break: break-word;
}
.text-block.original .text-block-label  { background:#f8d7da; color:#842029; }
.text-block.original .text-block-content { background:#fff5f5; border: 1px solid #f5c2c7; }
.text-block.suggested .text-block-label { background:#d1e7dd; color:#0a3622; }
.text-block.suggested .text-block-content { background:#f0fff4; border: 1px solid #badbcc; }

.feedback-comment, .feedback-rationale {
  font-size: 0.88rem;
  margin-top: 0.4rem;
  color: #343a40;
}

.feedback-content h5,
.reviewer-notes h5 {
  color: var(--text-primary-charcoal);
  font-weight: 600;
  margin-bottom: 0.75rem;
}

.feedback-text,
.notes-text {
  white-space: pre-wrap;
  word-wrap: break-word;
  line-height: 1.6;
}

.action-buttons {
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid var(--border-color-gray);
}

.no-feedback {
  padding: 2rem;
  text-align: center;
  background-color: var(--bg-white);
  border-radius: 0.375rem;
}

@media (max-width: 768px) {
  .review-feedback-container {
    padding: 1rem;
  }
  
  .action-buttons {
    flex-direction: column;
  }
  
  .action-buttons .btn {
    width: 100%;
  }
}
</style>
