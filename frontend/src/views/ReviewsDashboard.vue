<template>
  <div class="reviews-dashboard">
    
    <!-- Compact Toolbar -->
    <CompactToolbar :show-metrics="true">
      <template #metrics>
        <div class="metric-card">
          <div class="metric-icon">📝</div>
          <div class="metric-content">
            <h3>Total Reviews</h3>
            <div class="metric-number">{{ stats.total || 0 }}</div>
            <div class="metric-detail">All time</div>
          </div>
        </div>

        <div class="metric-card">
          <div class="metric-icon">⏳</div>
          <div class="metric-content">
            <h3>Pending</h3>
            <div class="metric-number">{{ stats.pending || 0 }}</div>
            <div class="metric-detail">Need attention</div>
          </div>
        </div>

        <div class="metric-card">
          <div class="metric-icon">✅</div>
          <div class="metric-content">
            <h3>Completed</h3>
            <div class="metric-number">{{ stats.completed || 0 }}</div>
            <div class="metric-detail">This month</div>
          </div>
        </div>

        <div class="metric-card">
          <div class="metric-icon">⚡</div>
          <div class="metric-content">
            <h3>Avg Time</h3>
            <div class="metric-number">{{ stats.avg_completion_days || 0 }}</div>
            <div class="metric-detail">Days to complete</div>
          </div>
        </div>

        <div class="metric-card">
          <div class="metric-icon">⚠️</div>
          <div class="metric-content">
            <h3>Overdue</h3>
            <div class="metric-number">{{ stats.overdue || 0 }}</div>
            <div class="metric-detail">Past due date</div>
          </div>
        </div>
      </template>
    </CompactToolbar>
    
    <div class="dashboard-header">
      <h1>Reviews Dashboard <HelpIcon feature="reviews.dashboard" /></h1>
      <p class="subtitle">Manage topic reviews and stakeholder feedback</p>
    </div>

    <!-- Quick Actions Section (Start Page style) -->
    <div class="quick-actions-section">
      <h2>Quick Actions</h2>
      <p class="section-description">Manage and track reviews</p>
      <div class="quick-actions-grid">
          <button class="quick-action-card" @click="sendNewReview">
            <div class="action-icon">📤</div>
            <div class="action-content" title="Submit topics to stakeholders">
              <h3>Send for Review</h3>
            </div>
          </button>
          <button class="quick-action-card" @click="showGuide = true">
            <div class="action-icon">📘</div>
            <div class="action-content" title="How the review workflow works">
              <h3>Review Guide</h3>
            </div>
          </button>
          <button class="quick-action-card" @click="navigateTo('/reviews/incorporate')">
            <div class="action-icon">🔄</div>
            <div class="action-content" title="Process stakeholder comments">
              <h3>Incorporate Feedback</h3>
            </div>
          </button>
          <button class="quick-action-card" @click="navigateTo('/reviews/history')">
            <div class="action-icon">📋</div>
            <div class="action-content" title="View completed reviews">
              <h3>Review History</h3>
            </div>
          </button>
      </div>
    </div>

    <!-- Combined Reviews Table -->
    <div class="dashboard-section reviews-table-section">
      <div class="table-toolbar">
        <h2>All Reviews</h2>
        <div class="toolbar-controls">
          <div class="search-wrap">
            <span class="search-icon">🔍</span>
            <input
              v-model="searchQuery"
              type="search"
              class="search-input"
              placeholder="Search by topic or reviewer…"
            />
          </div>
          <select v-model="filterStatus" class="filter-select">
            <option value="all">All Statuses</option>
            <option value="pending">Pending</option>
            <option value="in_progress">In Progress</option>
            <option value="completed">Completed</option>
            <option value="declined">Declined</option>
          </select>
          <button
            type="button"
            :class="['filter-pill', { active: filterUrgent }]"
            @click="filterUrgent = !filterUrgent"
          >⚠️ Urgent / Overdue</button>
        </div>
        <span class="result-count">{{ filteredReviews.length }} review{{ filteredReviews.length !== 1 ? 's' : '' }}</span>
      </div>

      <div v-if="filteredReviews.length === 0" class="empty-state">
        <p v-if="allReviews.length === 0">
          No reviews yet. <button @click="sendNewReview" class="link-btn">Send your first review</button>
        </p>
        <p v-else>No reviews match your filters.</p>
      </div>

      <div v-else class="reviews-table-wrap">
        <table class="reviews-table">
          <thead>
            <tr>
              <th>Topic</th>
              <th>Reviewer</th>
              <th>Status</th>
              <th>Due</th>
              <th>Sent</th>
              <th>Feedback</th>
              <th class="col-actions-head">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="review in filteredReviews"
              :key="review.id"
              class="review-row"
              :class="{ 'row-urgent': isUrgentReview(review), 'row-overdue': isOverdueReview(review) }"
              @click="viewReview(review)"
            >
              <td class="col-topic">
                <span class="row-topic-title">{{ review.topic_title || 'Unknown Topic' }}</span>
                <span class="row-topic-id">Topic #{{ review.topic_id }}</span>
                <span v-if="review.email_delivery_unavailable" class="email-badge">No email</span>
              </td>
              <td class="col-reviewer">{{ review.reviewer_name || '—' }}</td>
              <td class="col-status">
                <span :class="['status-badge', review.status]">{{ formatStatus(review.status) }}</span>
              </td>
              <td class="col-due" :class="{ 'overdue-text': isOverdueReview(review) }">
                {{ formatDueDate(review.due_date) }}
              </td>
              <td class="col-sent">{{ formatRelativeTime(review.requested_at) }}</td>
              <td class="col-feedback">{{ review.feedback_count || '—' }}</td>
              <td class="col-actions" @click.stop>
                <button
                  v-if="review.status === 'completed' && ['approve_with_changes', 'needs_more_info'].includes(review.recommendation) && review.topic_status === 'revisions_requested'"
                  @click="incorporateFeedback(review)"
                  class="btn btn-primary btn-sm"
                >Incorporate</button>
                <button
                  v-else-if="review.status === 'pending'"
                  @click="followUp(review)"
                  class="btn btn-secondary btn-sm"
                >Follow Up</button>
                <button @click="viewReview(review)" class="btn btn-secondary btn-sm">View</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="showGuide" class="guide-modal-backdrop" @click.self="showGuide = false">
      <div class="guide-modal" role="dialog" aria-modal="true" aria-label="Review workflow guide">
        <div class="guide-modal-header">
          <h3>How Reviews Work</h3>
          <button type="button" class="guide-close-btn" @click="showGuide = false" aria-label="Close">&times;</button>
        </div>
        <div class="guide-modal-body">
          <ol>
            <li><strong>Author submits topic for review:</strong> open a topic from Author Dashboard and click Submit for Review.</li>
            <li><strong>Select reviewer + details:</strong> choose reviewer, priority, due date, and optional message.</li>
            <li><strong>Topic status changes:</strong> topic moves to Pending Review and appears in the Reviews area.</li>
            <li><strong>Reviewer completes review:</strong> reviewer submits recommendation and feedback.</li>
            <li><strong>Author incorporates changes:</strong> use Incorporate Feedback to apply requested edits, then re-submit if needed.</li>
          </ol>
          <p><strong>Sequential review:</strong> when enabled, reviewers run in order (expert-first), and each next reviewer gets the updated content flow.</p>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-overlay">
      <div class="loading-spinner"></div>
    </div>
  </div>
</template>

<script>
import CompactToolbar from '../components/CompactToolbar.vue'
import HelpIcon from '@/components/HelpIcon.vue'

export default {
  name: 'ReviewsDashboard',
  components: { CompactToolbar, HelpIcon },
  props: {
    notifications: {
      type: Array,
      default: () => []
    },
    globalNotifications: {
      type: Array,
      default: () => []
    },
    markNotificationRead: {
      type: Function,
      required: true
    }
  },
  data() {
    return {
      loading: true,
      error: null,
      stats: {
        total: 0,
        pending: 0,
        in_progress: 0,
        completed: 0,
        declined: 0,
        overdue: 0,
        avg_completion_days: 0
      },
      allReviews: [],
      showGuide: false,
      refreshInterval: null,
      currentUser: JSON.parse(localStorage.getItem('user') || '{}'),
      // Filter / search state
      searchQuery: '',
      filterStatus: 'all',
      filterUrgent: false,
    }
  },

  async created() {
    await this.loadDashboardData()
    this.refreshInterval = setInterval(() => this.loadDashboardData(), 60000)
  },

  beforeUnmount() {
    clearInterval(this.refreshInterval)
  },

  computed: {
    mergedNotifications() {
      const all = [...(this.globalNotifications || []), ...(this.notifications || [])]
      const seen = new Set()
      return all.filter(n => {
        if (!n || !n.id) return true
        if (seen.has(n.id)) return false
        seen.add(n.id)
        return true
      })
    },

    filteredReviews() {
      const q = this.searchQuery.trim().toLowerCase()
      return this.allReviews.filter(r => {
        if (this.filterStatus !== 'all' && r.status !== this.filterStatus) return false
        if (this.filterUrgent && !this.isUrgentReview(r) && !this.isOverdueReview(r)) return false
        if (q) {
          const inTitle = (r.topic_title || '').toLowerCase().includes(q)
          const inReviewer = (r.reviewer_name || '').toLowerCase().includes(q)
          if (!inTitle && !inReviewer) return false
        }
        return true
      })
    },
  },

  methods: {
    async loadDashboardData() {
      this.loading = true
      try {
        await Promise.all([
          this.loadReviews(),
          this.loadStats()
        ])
      } catch (error) {
        console.error('Failed to load reviews dashboard:', error)
      } finally {
        this.loading = false
      }
    },

    async loadReviews() {
      try {
        const { getPendingReviews, getMyReviews, getReviews } = await import('@/api/reviews.js')

        const now = new Date()
        const isUrgentOrOverdue = (r) =>
          r.priority === 'urgent' || r.priority === 'high' ||
          (r.due_date && new Date(r.due_date) < now)

        // Fetch pending and user-scoped reviews in parallel
        const [pendingReviews, userReviews] = await Promise.all([
          getPendingReviews(),
          this.currentUser.id ? getMyReviews(this.currentUser.id) : Promise.resolve([])
        ])

        // Merge with dedup by id; tag urgent rows
        const byId = new Map()
        const add = (r) => {
          if (!byId.has(r.id)) byId.set(r.id, { ...r, isUrgent: isUrgentOrOverdue(r) })
        }
        ;(pendingReviews || []).forEach(add)
        ;(userReviews || []).forEach(add)

        // Fallback to global reviews if nothing loaded
        if (byId.size === 0) {
          const fallback = await getReviews()
          ;(fallback || []).forEach(add)
        }

        this.allReviews = Array.from(byId.values()).sort((a, b) => {
          const at = new Date(a.requested_at || 0).getTime()
          const bt = new Date(b.requested_at || 0).getTime()
          return bt - at
        })
      } catch (error) {
        console.error('Failed to load reviews:', error)
        this.allReviews = []
      }
    },

    async loadStats() {
      try {
        const { getReviewStats } = await import('@/api/reviews.js')
        this.stats = await getReviewStats()
      } catch (error) {
        console.error('Failed to load review stats:', error)
      }
    },

    isUrgentReview(review) {
      return review.isUrgent ||
        review.priority === 'urgent' || review.priority === 'high'
    },

    isOverdueReview(review) {
      return review.due_date && new Date(review.due_date) < new Date()
    },

    sendNewReview() {
      this.$router.push('/topics')
    },

    viewReview(review) {
      if (!review.topic_id) return
      if (review.status === 'completed') {
        this.$router.push(`/topics/${review.topic_id}/review-feedback/${review.id}`)
      } else {
        this.$router.push(`/topics/${review.topic_id}/edit`)
      }
    },

    incorporateFeedback(review) {
      if (review.topic_id) {
        // Navigate to review feedback page instead of direct edit
        this.$router.push(`/topics/${review.topic_id}/review-feedback/${review.id}`)
      }
    },

    async followUp(review) {
      try {
        // Import the follow-up API function
        const { sendFollowUpReminder } = await import('@/api/reviews.js')
        
        // Send the follow-up reminder
        const response = await sendFollowUpReminder(review.id)

        if (response?.email_sent === false) {
          import('@/composables/useToast').then(({ toast }) => toast.warn(response.warning || 'Follow-up was recorded, but email delivery failed.'))
        } else {
          import('@/composables/useToast').then(({ toast }) => toast.success(`Follow-up reminder sent to ${review.reviewer_name}!`))
        }
        
        // Refresh the reviews list to show updated data from the backend.
        await this.loadReviews()
        
      } catch (error) {
  console.error('Error sending follow-up reminder:', error)
  import('@/composables/useToast').then(({ toast }) => toast.error(`Failed to send follow-up reminder: ${error.message}`))
      }
    },

    navigateTo(path) {
      this.$router.push(path)
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

    formatDueDate(dueDate) {
      if (!dueDate) return 'No due date'
      
      const now = new Date()
      const due = new Date(dueDate)
      const diffMs = due - now
      const diffDays = Math.ceil(diffMs / (24 * 60 * 60 * 1000))

      if (diffDays < 0) return `${Math.abs(diffDays)} days overdue`
      if (diffDays === 0) return 'Due today'
      if (diffDays === 1) return 'Due tomorrow'
      if (diffDays <= 7) return `Due in ${diffDays} days`
      
      return due.toLocaleDateString()
    },

    formatRelativeTime(timestamp) {
      if (!timestamp) return 'Unknown'
      
      const now = new Date()
      const time = new Date(timestamp)
      const diffMs = now - time
      const diffMins = Math.floor(diffMs / 60000)
      const diffHours = Math.floor(diffMs / 3600000)
      const diffDays = Math.floor(diffMs / 86400000)

      if (diffMins < 1) return 'Just now'
      if (diffMins < 60) return `${diffMins}m ago`
      if (diffHours < 24) return `${diffHours}h ago`
      if (diffDays < 7) return `${diffDays}d ago`
      
      return time.toLocaleDateString()
    },

    getLastActivityText(review) {
      if (review.completed_at) {
        return `Completed ${this.formatRelativeTime(review.completed_at)}`
      } else if (review.started_at) {
        return `Started ${this.formatRelativeTime(review.started_at)}`
      } else if (review.requested_at) {
        return `Requested ${this.formatRelativeTime(review.requested_at)}`
      }
      return 'No activity'
    }
  }
}
</script>

<style scoped>
.reviews-dashboard {
  padding: 0 2rem 2rem; /* remove top space before header */
  background-color: var(--bg-white);
}

.dashboard-header {
  margin-bottom: 2rem;
  text-align: center;
}

.dashboard-header h1 {
  color: var(--primary-deep-teal);
  margin-bottom: 0.5rem;
  font-size: 2.5rem;
  font-weight: 300;
}

/* subtitle uses global styles */

/* Metrics Grid */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 3rem;
}

/* metric-icon uses global shape; only override font-size if needed */
.metric-icon { font-size: 2rem; }

/* metric-content h3 uses global styling from style.css */

/* metric-number and metric-detail now centralized in global style.css */

/* Main Content Grid */
.content-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  margin-bottom: 2rem;
}

.content-grid .full-width {
  grid-column: 1 / -1;
}

/* Dashboard Sections: use global .dashboard-section from style.css */



/* Quick Actions */
.quick-actions-grid {
  --quick-action-min-width: 200px;
  --quick-action-gap: 1rem;
}

.guide-modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1200;
}

.guide-modal {
  width: min(760px, 94vw);
  max-height: 88vh;
  overflow: auto;
  background: #fff;
  border-radius: 10px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.2);
}

.guide-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.9rem 1rem;
  border-bottom: 1px solid var(--border-light-gray);
}

.guide-modal-header h3 {
  margin: 0;
  color: var(--primary-deep-teal);
}

.guide-close-btn {
  border: none;
  background: transparent;
  font-size: 1.4rem;
  line-height: 1;
  color: var(--text-medium-gray);
  cursor: pointer;
}

.guide-modal-body {
  padding: 1rem;
  color: var(--text-dark-gray);
}

.guide-modal-body ol {
  margin: 0 0 0.9rem 1.15rem;
}

.guide-modal-body li {
  margin-bottom: 0.45rem;
}

/* Review Items */
.reviews-list {
  max-height: 400px;
  overflow-y: auto;
  padding-right: 0.5rem; /* For scrollbar */
}

/* Reviews Table Section */
.reviews-table-section {
  grid-column: 1 / -1;
}

.table-toolbar {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.table-toolbar h2 {
  margin: 0;
  flex-shrink: 0;
}

.toolbar-controls {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
  flex: 1;
}

.search-wrap {
  position: relative;
  flex: 1;
  min-width: 180px;
}

.search-icon {
  position: absolute;
  left: 0.6rem;
  top: 50%;
  transform: translateY(-50%);
  pointer-events: none;
  font-size: 0.85rem;
}

.search-input {
  width: 100%;
  padding: 0.4rem 0.75rem 0.4rem 2rem;
  border: 1px solid var(--border-light-gray);
  border-radius: var(--border-radius-sm);
  font-size: 0.875rem;
  background: var(--bg-white);
  color: var(--text-dark-gray);
  transition: border-color 0.15s;
}

.search-input:focus {
  outline: none;
  border-color: var(--primary-deep-teal);
}

.filter-select {
  padding: 0.4rem 0.75rem;
  border: 1px solid var(--border-light-gray);
  border-radius: var(--border-radius-sm);
  font-size: 0.875rem;
  background: var(--bg-white);
  color: var(--text-dark-gray);
  cursor: pointer;
}

.filter-pill {
  padding: 0.35rem 0.75rem;
  border: 1px solid var(--border-light-gray);
  border-radius: 999px;
  font-size: 0.8rem;
  background: var(--bg-white);
  color: var(--text-medium-gray);
  cursor: pointer;
  transition: all 0.15s;
  white-space: nowrap;
}

.filter-pill.active {
  background: var(--error-light-red);
  border-color: var(--error-coral-red);
  color: var(--error-dark-red);
  font-weight: 600;
}

.result-count {
  margin-left: auto;
  font-size: 0.8rem;
  color: var(--text-medium-gray);
  white-space: nowrap;
}

.reviews-table-wrap {
  overflow-x: auto;
  border: 1px solid var(--border-light-gray);
  border-radius: var(--border-radius-md);
}

.reviews-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
}

.reviews-table thead th {
  background: var(--bg-light-gray);
  color: var(--text-medium-gray);
  font-weight: 600;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.4px;
  padding: 0.65rem 0.9rem;
  text-align: left;
  white-space: nowrap;
  border-bottom: 1px solid var(--border-light-gray);
}

.reviews-table tbody tr {
  border-bottom: 1px solid var(--border-light-gray);
  cursor: pointer;
  transition: background 0.12s;
}

.reviews-table tbody tr:last-child {
  border-bottom: none;
}

.reviews-table tbody tr:hover {
  background: var(--bg-light-gray);
}

.reviews-table tbody tr.row-urgent {
  border-left: 3px solid var(--error-coral-red);
  background: var(--error-light-red, #fff5f5);
}

.reviews-table tbody tr.row-overdue td.col-due {
  color: var(--error-coral-red);
  font-weight: 600;
}

.reviews-table td {
  padding: 0.7rem 0.9rem;
  vertical-align: middle;
  color: var(--text-dark-gray);
}

.col-topic {
  min-width: 160px;
}

.row-topic-title {
  display: block;
  font-weight: 500;
  color: var(--text-dark-gray);
}

.row-topic-id {
  display: block;
  font-size: 0.72rem;
  color: var(--text-light-gray);
}

.email-badge {
  display: inline-block;
  margin-top: 0.15rem;
  padding: 0.1rem 0.4rem;
  border-radius: 999px;
  font-size: 0.65rem;
  font-weight: 600;
  background: var(--warning-light-yellow);
  color: var(--warning-dark-yellow);
}

.col-reviewer { white-space: nowrap; }
.col-sent,
.col-due     { white-space: nowrap; font-size: 0.8rem; }
.col-feedback { text-align: center; }
.col-actions-head,
.col-actions  { white-space: nowrap; text-align: right; }

.col-actions .btn + .btn {
  margin-left: 0.3rem;
}

.status-badge {
  display: inline-block;
  padding: 0.2rem 0.55rem;
  border-radius: 999px;
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.status-badge.pending     { background: var(--warning-light-yellow); color: var(--warning-dark-yellow); }
.status-badge.in_progress { background: #dbeafe; color: #1e40af; }
.status-badge.completed   { background: var(--success-light-green); color: var(--success-dark-green); }
.status-badge.declined    { background: #f3f4f6; color: #6b7280; }
.status-badge.overdue     { background: var(--error-light-red); color: var(--error-dark-red); }

/* Empty States */
.empty-state {
  text-align: center;
  padding: 2rem;
  color: var(--text-medium-gray);
}

.empty-state p {
  margin: 0;
}

.link-btn {
  background: none;
  border: none;
  color: var(--primary-deep-teal);
  text-decoration: underline;
  cursor: pointer;
  padding: 0;
  font-size: inherit;
}

.link-btn:hover {
  color: var(--primary-dark-blue);
}

/* Loading */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.loading-spinner {
  color: var(--primary-deep-teal);
  font-size: 1.1rem;
}

@media (max-width: 768px) {
  .reviews-dashboard {
    padding: 1rem;
  }

  .metrics-grid,
  .content-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  .table-toolbar {
    flex-direction: column;
    align-items: stretch;
  }

  .toolbar-controls {
    flex-direction: column;
  }

  .result-count {
    margin-left: 0;
  }

  .dashboard-header h1 {
    font-size: 2rem;
  }
}
</style>
