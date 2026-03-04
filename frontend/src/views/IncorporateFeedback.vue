<template>
  <div class="incorporate-feedback">
    <div class="page-header">
      <div class="header-left">
        <button class="btn btn-outline-secondary btn-sm me-3" @click="$router.push('/reviews')">
          ← Back to Dashboard
        </button>
        <div>
          <h1>Incorporate Feedback</h1>
          <p class="page-subtitle">Completed reviews with requested revisions</p>
        </div>
      </div>
    </div>

    <div v-if="loading" class="empty-state">
      <p>Loading reviews…</p>
    </div>

    <div v-else-if="reviews.length === 0" class="empty-state">
      <div class="empty-icon">✅</div>
      <h3>All caught up!</h3>
      <p>There are no completed reviews awaiting incorporation right now.</p>
    </div>

    <div v-else>
      <p class="results-count">{{ reviews.length }} review{{ reviews.length !== 1 ? 's' : '' }} awaiting incorporation</p>
      <div class="reviews-list">
        <div
          v-for="review in reviews"
          :key="review.id"
          class="review-row"
          @click="openReview(review)"
        >
          <div class="review-row-main">
            <div class="review-topic-title">{{ review.topic_title || 'Unknown Topic' }}</div>
            <div class="review-meta">
              <span class="meta-item">Reviewer: {{ review.reviewer_name || 'Unknown' }}</span>
              <span class="meta-item">Completed: {{ formatDate(review.completed_at) }}</span>
              <span v-if="review.feedback_count" class="meta-item">{{ review.feedback_count }} comment{{ review.feedback_count !== 1 ? 's' : '' }}</span>
            </div>
          </div>
          <div class="review-row-actions">
            <span class="priority-badge" :class="'priority-' + review.priority">{{ review.priority }}</span>
            <button class="btn btn-primary btn-sm" @click.stop="openReview(review)">
              Incorporate →
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'IncorporateFeedback',
  data() {
    return {
      loading: true,
      reviews: []
    }
  },
  async created() {
    await this.loadReviews()
  },
  methods: {
    async loadReviews() {
      try {
        const { getReviews } = await import('@/api/reviews.js')
        const all = await getReviews()
        this.reviews = (all || []).filter(
          r => r.status === 'completed' && r.topic_status === 'revisions_requested'
        ).sort((a, b) => new Date(b.completed_at || 0) - new Date(a.completed_at || 0))
      } catch (e) {
        console.error('Failed to load reviews:', e)
      } finally {
        this.loading = false
      }
    },
    openReview(review) {
      this.$router.push(`/topics/${review.topic_id}/review-feedback/${review.id}`)
    },
    formatDate(val) {
      if (!val) return '—'
      return new Date(val).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })
    }
  }
}
</script>

<style scoped>
.incorporate-feedback {
  max-width: 900px;
  margin: 0 auto;
  padding: 2rem 1.5rem;
}

.page-header {
  display: flex;
  align-items: center;
  margin-bottom: 2rem;
}

.header-left {
  display: flex;
  align-items: center;
}

.page-header h1 {
  margin: 0 0 0.25rem;
  font-size: 1.6rem;
}

.page-subtitle {
  margin: 0;
  color: #6c757d;
  font-size: 0.9rem;
}

.results-count {
  color: #6c757d;
  font-size: 0.9rem;
  margin-bottom: 1rem;
}

.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  color: #6c757d;
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.empty-state h3 {
  margin-bottom: 0.5rem;
}

.reviews-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.review-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  padding: 1rem 1.25rem;
  cursor: pointer;
  transition: box-shadow 0.15s, border-color 0.15s;
}

.review-row:hover {
  border-color: #0d6efd;
  box-shadow: 0 2px 8px rgba(13, 110, 253, 0.1);
}

.review-topic-title {
  font-weight: 600;
  font-size: 1rem;
  margin-bottom: 0.3rem;
}

.review-meta {
  display: flex;
  gap: 1rem;
  font-size: 0.82rem;
  color: #6c757d;
}

.review-row-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-shrink: 0;
}

.priority-badge {
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  padding: 0.2rem 0.55rem;
  border-radius: 4px;
  background: #f8f9fa;
  color: #495057;
}

.priority-urgent { background: #f8d7da; color: #842029; }
.priority-high    { background: #fff3cd; color: #664d03; }
.priority-medium  { background: #d1ecf1; color: #0c5460; }
.priority-low     { background: #d4edda; color: #155724; }
</style>
