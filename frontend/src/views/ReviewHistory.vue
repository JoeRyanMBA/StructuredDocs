<template>
  <div class="review-history">
    <h1>Review History</h1>
    <p class="subtitle">Track completed and in-progress reviews across topics.</p>

    <div class="filters-section">
      <div class="filter-row">
        <div class="filter-group">
          <label>Search</label>
          <input v-model="searchQuery" type="text" class="filter-input" placeholder="Topic, reviewer, requester..." />
        </div>
        <div class="filter-group">
          <label>Status</label>
          <select v-model="statusFilter" class="filter-input">
            <option value="">All</option>
            <option value="pending">Pending</option>
            <option value="in_progress">In Progress</option>
            <option value="completed">Completed</option>
            <option value="declined">Declined</option>
          </select>
        </div>
        <div class="filter-group">
          <button type="button" class="btn btn-secondary btn-sm" @click="clearFilters">Clear Filters</button>
        </div>
      </div>
    </div>

    <div v-if="loading" class="loading">Loading review history...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else-if="filteredReviews.length === 0" class="empty-state">No review history found.</div>

    <div v-else class="history-table-container">
      <table class="history-table">
        <thead>
          <tr>
            <th>Topic</th>
            <th>Reviewer</th>
            <th>Requester</th>
            <th>Status</th>
            <th>Requested</th>
            <th>Completed</th>
            <th>Recommendation</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="review in filteredReviews" :key="review.id">
            <td>
              <div class="topic-title">{{ review.topic_title || `Topic #${review.topic_id}` }}</div>
              <div class="topic-id">ID: {{ review.topic_id }}</div>
            </td>
            <td>{{ review.reviewer_name || 'Unknown' }}</td>
            <td>{{ review.requester_name || 'Unknown' }}</td>
            <td>
              <span class="status-badge" :class="review.status">{{ formatStatus(review.status) }}</span>
            </td>
            <td>{{ formatDate(review.requested_at) }}</td>
            <td>{{ formatDate(review.completed_at) }}</td>
            <td>{{ formatRecommendation(review.recommendation) }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import { getReviews } from '@/api/reviews'

export default {
  name: 'ReviewHistory',
  data() {
    return {
      loading: false,
      error: '',
      reviews: [],
      searchQuery: '',
      statusFilter: ''
    }
  },
  computed: {
    filteredReviews() {
      let rows = [...this.reviews]

      if (this.statusFilter) {
        rows = rows.filter(review => review.status === this.statusFilter)
      }

      if (this.searchQuery) {
        const q = this.searchQuery.toLowerCase()
        rows = rows.filter(review =>
          (review.topic_title || '').toLowerCase().includes(q) ||
          (review.reviewer_name || '').toLowerCase().includes(q) ||
          (review.requester_name || '').toLowerCase().includes(q)
        )
      }

      return rows.sort((a, b) => new Date(b.requested_at || 0) - new Date(a.requested_at || 0))
    }
  },
  async created() {
    await this.loadReviewHistory()
  },
  methods: {
    async loadReviewHistory() {
      this.loading = true
      this.error = ''
      try {
        this.reviews = await getReviews()
      } catch (error) {
        this.error = error.message || 'Failed to load review history'
        this.reviews = []
      } finally {
        this.loading = false
      }
    },
    clearFilters() {
      this.searchQuery = ''
      this.statusFilter = ''
    },
    formatStatus(status) {
      const map = {
        pending: 'Pending',
        in_progress: 'In Progress',
        completed: 'Completed',
        declined: 'Declined'
      }
      return map[status] || status || 'Unknown'
    },
    formatRecommendation(recommendation) {
      if (!recommendation) return '—'
      const map = {
        approve: 'Approve',
        approve_with_changes: 'Approve w/ Changes',
        reject: 'Reject',
        needs_more_info: 'Needs More Info'
      }
      return map[recommendation] || recommendation
    },
    formatDate(value) {
      if (!value) return '—'
      const date = new Date(value)
      if (Number.isNaN(date.getTime())) return '—'
      return date.toLocaleString()
    }
  }
}
</script>

<style scoped>
.review-history { padding: 2rem; }
.filters-section { margin: 1rem 0 1.5rem; background: var(--bg-white); border: 1px solid var(--border-light-gray); border-radius: var(--border-radius-lg); padding: 1rem; }
.filter-row { display: grid; grid-template-columns: 1fr 220px auto; gap: 1rem; align-items: end; }
.filter-group { display: flex; flex-direction: column; gap: .4rem; }
.filter-input { padding: .65rem; border: 1px solid var(--border-light-gray); border-radius: var(--border-radius-md); }
.loading, .error, .empty-state { background: var(--bg-white); border-radius: var(--border-radius-lg); padding: 1.5rem; }
.error { color: var(--error-coral-red); }
.history-table-container { background: var(--bg-white); border: 1px solid var(--border-light-gray); border-radius: var(--border-radius-lg); overflow: auto; }
.history-table { width: 100%; border-collapse: collapse; }
.history-table th, .history-table td { padding: .75rem 1rem; border-bottom: 1px solid var(--border-light-gray); text-align: left; }
.topic-title { font-weight: 600; }
.topic-id { font-size: .8rem; color: var(--text-medium-gray); }
.status-badge { padding: .2rem .5rem; border-radius: 12px; font-size: .78rem; font-weight: 600; text-transform: uppercase; }
.status-badge.pending { background: var(--warning-light-yellow); color: var(--warning-dark-yellow); }
.status-badge.in_progress { background: var(--primary-light-blue); color: var(--primary-dark-blue); }
.status-badge.completed { background: var(--success-light-green); color: var(--success-dark-green); }
.status-badge.declined { background: var(--error-light-red); color: var(--error-dark-red); }
@media (max-width: 900px) { .filter-row { grid-template-columns: 1fr; } }
</style>