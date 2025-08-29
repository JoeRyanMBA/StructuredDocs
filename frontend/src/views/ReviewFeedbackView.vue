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
        <div class="card-header bg-primary text-white">
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
              <p><strong>Author:</strong> {{ topic?.author_name }}</p>
            </div>
            <div class="col-md-6">
              <p><strong>Last Updated:</strong> {{ formatDate(topic?.updated_at) }}</p>
              <p><strong>Content Type:</strong> {{ topic?.content_type }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Review Feedback -->
      <div class="card mb-4">
        <div class="card-header bg-warning text-dark">
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
      // Navigate to topic edit page
      this.$router.push(`/topics/${this.topicId}/edit`)
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
  background-color: var(--bg-light-mist-gray);
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
