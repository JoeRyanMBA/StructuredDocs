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
      <h1>Reviews Dashboard</h1>
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

    <!-- Main Content Grid -->
    <div class="content-grid two-col">
      <!-- Pending Reviews -->
      <div class="dashboard-section">
        <h2>Urgent Reviews</h2>
        <div class="reviews-list">
          <div v-if="urgentReviews.length === 0" class="empty-state">
            <p>No urgent reviews! 🎉</p>
          </div>
          <div v-else>
            <div 
              v-for="review in urgentReviews" 
              :key="review.id"
              class="review-item urgent"
              @click="viewReview(review)"
            >
              <div class="review-icon">📝</div>
              <div class="review-content">
                <div class="review-title">{{ review.topic_title || 'Unknown Topic' }}</div>
                <div class="review-description">{{ review.reviewer_name || 'Unknown Reviewer' }}</div>
                <div class="review-meta">Due {{ formatDueDate(review.due_date) }}</div>
              </div>
              <div class="review-status" :class="review.status">{{ formatStatus(review.status) }}</div>
            </div>
          </div>
        </div>
      </div>

  <!-- Review Statistics -->
  <div class="dashboard-section">
        <h2>Review Activity</h2>
        <div class="reviews-overview">
          <div v-if="recentReviews.length === 0" class="empty-state">
            <p>No recent review activity. <button @click="sendNewReview" class="link-btn">Send your first review</button></p>
          </div>
          <div v-else class="reviews-grid">
            <div 
              v-for="review in recentReviews" 
              :key="review.id"
              class="review-card"
              @click="viewReview(review)"
            >
              <div class="card-header">
                <div class="card-title">
                  <h3>{{ review.topic_title || 'Unknown Topic' }}</h3>
                </div>
                <div class="card-status-group">
                  <span class="card-status" :class="review.status">{{ formatStatus(review.status) }}</span>
                  <span v-if="review.email_delivery_unavailable" class="email-delivery-badge">Email delivery unavailable</span>
                  <span class="topic-id-subtle">Topic #{{ review.topic_id }}</span>
                </div>
              </div>
              <div class="card-content">
                <p class="card-description">
                  <strong>Reviewer:</strong> {{ review.reviewer_name || 'Unknown' }}
                </p>
                <p class="card-description">
                  <strong>Sent:</strong> {{ formatRelativeTime(review.requested_at) }}
                  <span v-if="review.due_date"> • <strong>Due:</strong> {{ formatDueDate(review.due_date) }}</span>
                </p>
                <div class="card-metrics" v-if="review.feedback_count">
                  <span class="card-metric">
                    <span class="metric-label">Feedback:</span>
                    {{ review.feedback_count }} comments
                  </span>
                </div>
              </div>
              <div class="card-footer">
                <span class="card-date">{{ getLastActivityText(review) }}</span>
                <div class="card-actions">
                  <button 
                    v-if="review.status === 'completed' && review.topic_status === 'revisions_requested'" 
                    @click.stop="incorporateFeedback(review)" 
                    class="card-action-btn primary"
                  >
                    Incorporate
                  </button>
                  <button 
                    v-else-if="review.status === 'pending'" 
                    @click.stop="followUp(review)" 
                    class="card-action-btn"
                  >
                    Follow Up
                  </button>
                  <button @click.stop="viewReview(review)" class="card-action-btn">View</button>
                </div>
              </div>
            </div>
          </div>
        </div>
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

export default {
  name: 'ReviewsDashboard',
  components: { CompactToolbar },
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
      urgentReviews: [],
      recentReviews: [],
      showGuide: false,
      refreshInterval: null,
      currentUser: JSON.parse(localStorage.getItem('user') || '{}')
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
        // Load reviews from the new reviews API
        const { getPendingReviews, getMyReviews, getReviews } = await import('@/api/reviews.js')
        
        // Get pending reviews (urgent ones)
        const pendingReviews = await getPendingReviews()
        
        // Filter urgent and overdue reviews
        const now = new Date()
        this.urgentReviews = pendingReviews.filter(review => {
          const isUrgent = review.priority === 'urgent' || review.priority === 'high'
          const isOverdue = review.due_date && new Date(review.due_date) < now
          return isUrgent || isOverdue
        }).slice(0, 5) // Show top 5
        
        // Get recent reviews requested by current user when possible
        if (this.currentUser.id) {
          this.recentReviews = await getMyReviews(this.currentUser.id)
        }

        // Fallback: if requester-scoped query returns nothing (or no user id), show recent global reviews.
        if (!this.recentReviews || this.recentReviews.length === 0) {
          this.recentReviews = await getReviews()
        }

        // Ensure newest first and cap visible list
        this.recentReviews = (this.recentReviews || [])
          .sort((a, b) => {
            const aTime = new Date(a.requested_at || 0).getTime()
            const bTime = new Date(b.requested_at || 0).getTime()
            return bTime - aTime
          })
          .slice(0, 10)
        
      } catch (error) {
        console.error('Failed to load reviews:', error)
        // Fallback to empty arrays
        this.urgentReviews = []
        this.recentReviews = []
      }
    },

    async loadStats() {
    },

    async loadStats() {
      try {
        const { getReviewStats } = await import('@/api/reviews.js')
        this.stats = await getReviewStats()
      } catch (error) {
        console.error('Failed to load review stats:', error)
        // Keep default stats
      }
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
        
        // Refresh the reviews list to show updated data
        await this.loadReviews()

        if (response?.email_sent === false) {
          const failedReview = this.recentReviews.find(r => r.id === review.id)
          if (failedReview) {
            failedReview.email_delivery_unavailable = true
          }
        }
        
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

.review-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  border: 1px solid transparent;
  border-bottom: 1px solid var(--border-light-gray);
  border-radius: var(--border-radius-md);
  margin-bottom: 0.75rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.review-item:hover {
  border-color: var(--primary-deep-teal);
  background: var(--bg-white);
}

.review-item.urgent {
  border-left: 4px solid var(--error-coral-red);
  background: var(--error-light-red);
}

.review-item:last-child {
  margin-bottom: 0;
  border-bottom: 1px solid transparent;
}

.review-icon {
  font-size: 1.5rem;
  min-width: 30px;
}

.review-content {
  flex: 1;
}

.review-title {
  font-weight: 600;
  color: var(--text-dark-gray);
  margin-bottom: 0.25rem;
}

.review-description {
  color: var(--text-medium-gray);
  font-size: 0.875rem;
  margin-bottom: 0.25rem;
}

.review-meta {
  color: var(--text-light-gray);
  font-size: 0.75rem;
}

.review-status {
  padding: 0.25rem 0.5rem;
  border-radius: var(--border-radius-sm);
  font-size: 0.7rem;
  font-weight: 500;
  text-transform: uppercase;
}

.review-status.pending {
  background: var(--warning-light-yellow);
  color: var(--warning-dark-yellow);
}

.review-status.completed {
  background: var(--success-light-green);
  color: var(--success-dark-green);
}

.review-status.overdue {
  background: var(--error-light-red);
  color: var(--error-dark-red);
}

/* Review Cards */
.reviews-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
}

.review-card {
  border: 1px solid var(--border-light-gray);
  border-radius: var(--border-radius-lg);
  cursor: pointer;
  transition: all 0.2s ease;
  background: var(--bg-white);
  display: flex;
  flex-direction: column;
}

.review-card:hover {
  border-color: var(--primary-deep-teal);
  box-shadow: var(--box-shadow-md);
  transform: translateY(-3px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
  padding: 1.5rem 1.5rem 0 1.5rem;
}

.card-title h3 {
  margin: 0;
  color: var(--text-dark-gray);
  font-size: 1rem;
  font-weight: 600;
}

.card-status {
  padding: 0.25rem 0.5rem;
  border-radius: var(--border-radius-sm);
  font-size: 0.7rem;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.card-status.pending {
  background: var(--warning-light-yellow);
  color: var(--warning-dark-yellow);
}

.card-status.completed {
  background: var(--success-light-green);
  color: var(--success-dark-green);
}

.card-status.overdue {
  background: var(--error-light-red);
  color: var(--error-dark-red);
}

.card-content {
  margin-bottom: 1rem;
  flex-grow: 1;
  padding: 0 1.5rem;
}

.card-description {
  color: var(--text-medium-gray);
  font-size: 0.875rem;
  line-height: 1.4;
  margin: 0 0 0.5rem 0;
}

.card-metrics {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin-top: 1rem;
}

.card-metric {
  font-size: 0.75rem;
  color: var(--text-medium-gray);
}

.metric-label {
  font-weight: 500;
  color: var(--text-dark-gray);
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: auto;
  padding: 1rem 1.5rem;
  border-top: 1px solid var(--border-light-gray);
  background-color: var(--bg-white);
  border-radius: 0 0 var(--border-radius-lg) var(--border-radius-lg);
}

.card-date {
  color: var(--text-light-gray);
  font-size: 0.75rem;
}

.card-actions {
  display: flex;
  gap: 0.5rem;
}

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

.card-status-group {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
}

.topic-id-subtle {
  color: var(--text-light-gray);
  font-size: 0.7rem;
  font-weight: 400;
  text-align: right;
}

.email-delivery-badge {
  display: inline-block;
  margin-top: 0.1rem;
  padding: 0.15rem 0.45rem;
  border-radius: 999px;
  font-size: 0.65rem;
  font-weight: 600;
  background: var(--warning-light-yellow);
  color: var(--warning-dark-yellow);
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

/* Responsive Design */
.two-col { grid-template-columns: 1fr 1fr; }

@media (max-width: 768px) {
  .reviews-dashboard {
    padding: 1rem;
  }
  .two-col { grid-template-columns: 1fr; }
  
  .metrics-grid,
  .content-grid,
  .reviews-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  
  .dashboard-header h1 {
    font-size: 2rem;
  }
}
</style>
