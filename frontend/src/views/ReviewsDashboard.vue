<template>
  <div class="reviews-dashboard">
    <div class="full-width" style="margin-bottom:1.5rem;">
      <NotificationTicker
        :notifications="mergedNotifications"
        contextType="reviews"
        @mark-read="markNotificationRead"
      />
    </div>
    <div class="dashboard-header">
      <h1>Reviews Dashboard</h1>
      <p class="welcome-text">Manage topic reviews and stakeholder feedback</p>
    </div>

    <!-- Key Metrics Cards -->
    <div class="metrics-grid">
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
    </div>

    <!-- Main Content Grid -->
    <div class="content-grid">
      
      <!-- Quick Actions -->
      <div class="dashboard-section">
        <h2>Quick Actions</h2>
        <div class="quick-actions-grid">
          <button class="action-card" @click="sendNewReview">
            <div class="action-icon">📤</div>
            <div class="action-content">
              <h3>Send for Review</h3>
              <p>Submit topics to stakeholders</p>
            </div>
          </button>
          <button class="action-card" @click="navigateTo('/reviews/incorporate')">
            <div class="action-icon">🔄</div>
            <div class="action-content">
              <h3>Incorporate Feedback</h3>
              <p>Process stakeholder comments</p>
            </div>
          </button>
          <button class="action-card" @click="navigateTo('/reviews/history')">
            <div class="action-icon">📋</div>
            <div class="action-content">
              <h3>Review History</h3>
              <p>View completed reviews</p>
            </div>
          </button>
        </div>
      </div>

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
      <div class="dashboard-section full-width">
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

    <!-- Loading State -->
    <div v-if="loading" class="loading-overlay">
      <div class="loading-spinner">Loading reviews...</div>
    </div>
  </div>
</template>

<script>
import NotificationTicker from '../components/NotificationTicker.vue'

export default {
  name: 'ReviewsDashboard',
  components: { NotificationTicker },
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
      stats: {
        total: 0,
        pending: 0,
        completed: 0,
        overdue: 0,
        avg_completion_days: 0
      },
      urgentReviews: [],
      recentReviews: [],
      currentUser: JSON.parse(localStorage.getItem('user') || '{}')
    }
  },

  async created() {
    await this.loadDashboardData()
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
        const { getPendingReviews, getMyReviews } = await import('@/api/reviews.js')
        
        // Get pending reviews (urgent ones)
        const pendingReviews = await getPendingReviews()
        
        // Filter urgent and overdue reviews
        const now = new Date()
        this.urgentReviews = pendingReviews.filter(review => {
          const isUrgent = review.priority === 'urgent' || review.priority === 'high'
          const isOverdue = review.due_date && new Date(review.due_date) < now
          return isUrgent || isOverdue
        }).slice(0, 5) // Show top 5
        
        // Get recent reviews requested by current user
        if (this.currentUser.id) {
          this.recentReviews = await getMyReviews(this.currentUser.id)
          this.recentReviews = this.recentReviews.slice(0, 10) // Show recent 10
        }
        
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
      if (review.topic_id) {
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
        
        // Show success message
        alert(`✅ Follow-up reminder sent to ${review.reviewer_name}!`)
        
        // Refresh the reviews list to show updated data
        await this.loadReviews()
        
      } catch (error) {
        console.error('Error sending follow-up reminder:', error)
        alert(`❌ Failed to send follow-up reminder: ${error.message}`)
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
  margin: 0 auto;
}

.dashboard-header {
  margin-bottom: 2rem;
  text-align: center;
}

.dashboard-header h1 {
  color: #205493;
  margin-bottom: 0.5rem;
  font-size: 2.5rem;
  font-weight: 300;
}

.welcome-text {
  color: #6c757d;
  font-size: 1.1rem;
  margin: 0;
}

/* Metrics Grid */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 3rem;
}

.metric-card {
  background: white;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.metric-icon {
  font-size: 2.5rem;
  min-width: 60px;
  text-align: center;
}

.metric-content h3 {
  margin: 0 0 0.25rem 0;
  color: #495057;
  font-size: 0.875rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.metric-number {
  font-size: 2rem;
  font-weight: 700;
  color: #205493;
  line-height: 1;
  margin-bottom: 0.25rem;
}

.metric-detail {
  color: #6c757d;
  font-size: 0.875rem;
}

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

/* Dashboard Sections */
.dashboard-section {
  background: white;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.dashboard-section h2 {
  margin: 0 0 1.5rem 0;
  color: #495057;
  font-size: 1.25rem;
  font-weight: 600;
  border-bottom: 2px solid #f8f9fa;
  padding-bottom: 0.5rem;
}

/* Quick Actions */
.quick-actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1rem;
}

.action-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: #f8fafc;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: left;
}

.action-card:hover {
  background: #205493;
  border-color: #205493;
  color: white;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 90, 156, 0.2);
}

.action-icon {
  font-size: 1.5rem;
  opacity: 0.8;
}

.action-content h3 {
  margin: 0 0 0.25rem 0;
  font-size: 1rem;
  font-weight: 600;
}

.action-content p {
  margin: 0;
  font-size: 0.85rem;
  opacity: 0.8;
}

/* Review Items */
.reviews-list {
  max-height: 400px;
  overflow-y: auto;
}

.review-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  border: 1px solid #f8f9fa;
  border-radius: 6px;
  margin-bottom: 0.75rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.review-item:hover {
  border-color: #205493;
  background: #f8f9fa;
}

.review-item.urgent {
  border-color: #dc3545;
  background: #fff5f5;
}

.review-item:last-child {
  margin-bottom: 0;
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
  color: #495057;
  margin-bottom: 0.25rem;
}

.review-description {
  color: #6c757d;
  font-size: 0.875rem;
  margin-bottom: 0.25rem;
}

.review-meta {
  color: #adb5bd;
  font-size: 0.75rem;
}

.review-status {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.7rem;
  font-weight: 500;
  text-transform: uppercase;
}

.review-status.pending {
  background: #fff3cd;
  color: #856404;
}

.review-status.completed {
  background: #d4edda;
  color: #155724;
}

.review-status.overdue {
  background: #f8d7da;
  color: #721c24;
}

/* Review Cards */
.reviews-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
}

.review-card {
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.2s ease;
  background: white;
}

.review-card:hover {
  border-color: #205493;
  box-shadow: 0 4px 12px rgba(0,90,156,0.15);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex: 1;
}

.card-title h3 {
  margin: 0;
  color: #495057;
  font-size: 1rem;
  font-weight: 600;
}

.card-badge {
  background: #e9ecef;
  color: #495057;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
}

.card-status {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.7rem;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.card-status.pending {
  background: #fff3cd;
  color: #856404;
}

.card-status.completed {
  background: #d4edda;
  color: #155724;
}

.card-status.overdue {
  background: #f8d7da;
  color: #721c24;
}

.card-content {
  margin-bottom: 1rem;
}

.card-description {
  color: #6c757d;
  font-size: 0.875rem;
  line-height: 1.4;
  margin: 0 0 0.5rem 0;
}

.card-metrics {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}

.card-metric {
  font-size: 0.75rem;
  color: #6c757d;
}

.metric-label {
  font-weight: 500;
  color: #495057;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-date {
  color: #adb5bd;
  font-size: 0.75rem;
}

.card-actions {
  display: flex;
  gap: 0.5rem;
}

.card-action-btn {
  padding: 0.25rem 0.75rem;
  border: 1px solid #e9ecef;
  border-radius: 4px;
  background: white;
  color: #495057;
  cursor: pointer;
  font-size: 0.75rem;
  transition: all 0.2s ease;
}

.card-action-btn:hover {
  border-color: #205493;
  background: #f8f9fa;
}

.card-action-btn.primary {
  background: #205493;
  color: white;
  border-color: #205493;
}

.card-action-btn.primary:hover {
  background: #005E7B;
}

/* Empty States */
.empty-state {
  text-align: center;
  padding: 2rem;
  color: #6c757d;
}

.empty-state p {
  margin: 0;
}

.link-btn {
  background: none;
  border: none;
  color: #205493;
  text-decoration: underline;
  cursor: pointer;
  padding: 0;
  font-size: inherit;
}

.link-btn:hover {
  color: #005E7B;
}

.topic-id-badge {
  background: #205493;
  color: white;
  padding: 0.2rem 0.5rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  margin-left: 0.5rem;
}

.card-status-group {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.25rem;
}

.topic-id-subtle {
  color: #6b7280;
  font-size: 0.7rem;
  font-weight: 400;
  text-align: right;
}

.topic-id-small {
  color: #6b7280;
  font-size: 0.8rem;
  font-weight: 500;
  margin-top: 0.2rem;
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
  color: #205493;
  font-size: 1.1rem;
}

/* Responsive Design */
@media (max-width: 768px) {
  .reviews-dashboard {
    padding: 1rem;
  }
  
  .metrics-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  
  .content-grid {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }
  
  .reviews-grid {
    grid-template-columns: 1fr;
  }
  
  .dashboard-header h1 {
    font-size: 2rem;
  }
}
</style>
