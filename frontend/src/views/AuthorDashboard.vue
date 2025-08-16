<template>
  <div class="author-dashboard">
    <div class="full-width" style="margin-bottom:1.5rem;">
      <NotificationTicker
        :notifications="mergedNotifications"
        contextType="author"
        @mark-read="markNotificationRead"
      />
    </div>
    <div class="dashboard-header">
      <h1>Author Dashboard</h1>
      <p class="welcome-text">Create and manage your content</p>
    </div>

    <!-- Key Metrics Cards -->
    <div class="metrics-grid">
      <div class="metric-card" @click="navigateTo('/topics')">
        <div class="metric-icon">📝</div>
        <div class="metric-content">
          <h3>My Topics</h3>
          <div class="metric-number">{{ stats.myTopics || 0 }}</div>
          <div class="metric-detail">{{ stats.drafts || 0 }} Drafts</div>
        </div>
      </div>

      <div class="metric-card">
        <div class="metric-icon">✅</div>
        <div class="metric-content">
          <h3>Published</h3>
          <div class="metric-number">{{ stats.published || 0 }}</div>
          <div class="metric-detail">Live topics</div>
        </div>
      </div>

      <div class="metric-card">
        <div class="metric-icon">🔄</div>
        <div class="metric-content">
          <h3>In Review</h3>
          <div class="metric-number">{{ stats.inReview || 0 }}</div>
          <div class="metric-detail">Pending feedback</div>
        </div>
      </div>

      <div class="metric-card">
        <div class="metric-icon">📊</div>
        <div class="metric-content">
          <h3>This Week</h3>
          <div class="metric-number">{{ stats.createdThisWeek || 0 }}</div>
          <div class="metric-detail">Topics created</div>
        </div>
      </div>
    </div>

    <!-- Main Content Grid -->
    <div class="content-grid">
      
      <!-- Quick Actions -->
      <div class="dashboard-section">
        <h2>Quick Actions</h2>
        <div class="quick-actions-grid">
          <button class="action-card" @click="navigateTo('/topics/new')">
            <div class="action-icon">➕</div>
            <div class="action-content">
              <h3>Create New Topic</h3>
              <p>Start writing new content</p>
            </div>
          </button>
          <button class="action-card" @click="navigateTo('/topics')">
            <div class="action-icon">📚</div>
            <div class="action-content">
              <h3>Browse My Topics</h3>
              <p>Review and edit your work</p>
            </div>
          </button>
          <button class="action-card" @click="navigateTo('/import')">
            <div class="action-icon">📥</div>
            <div class="action-content">
              <h3>Import Content</h3>
              <p>Add from external sources</p>
            </div>
          </button>
        </div>

        <div class="action-section">
          <h3>Content Templates</h3>
          <div class="template-buttons">
            <button class="template-btn" @click="createFromTemplate('procedure')">
              <span class="template-icon">📋</span>
              <span>Procedure Guide</span>
            </button>
            <button class="template-btn" @click="createFromTemplate('reference')">
              <span class="template-icon">📖</span>
              <span>Reference Document</span>
            </button>
            <button class="template-btn" @click="createFromTemplate('faq')">
              <span class="template-icon">❓</span>
              <span>FAQ Section</span>
            </button>
            <button class="template-btn" @click="createFromTemplate('blank')">
              <span class="template-icon">📄</span>
              <span>Blank Topic</span>
            </button>
          </div>
        </div>
      </div>

      <!-- Recent Topics -->
      <div class="dashboard-section">
        <h2>Recent Work</h2>
        <div class="topics-list">
          <div v-if="recentTopics.length === 0" class="empty-state">
            <p>No topics yet. Create your first topic to get started!</p>
          </div>
          <div v-else>
            <div 
              v-for="topic in recentTopics" 
              :key="topic.id"
              class="topic-item"
              @click="editTopic(topic)"
            >
              <div class="topic-icon">📝</div>
              <div class="topic-content">
                <div class="topic-title">{{ topic.title }}</div>
                <div class="topic-description">{{ topic.collection_name || 'No collection' }}</div>
                <div class="topic-meta">{{ formatRelativeTime(topic.updated_at) }}</div>
              </div>
              <div class="topic-status" :class="topic.status">{{ formatStatus(topic.status) }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Writing Progress -->
      <div class="dashboard-section full-width">
        <h2>Writing Progress</h2>
        <div class="progress-overview">
          <div v-if="myTopics.length === 0" class="empty-state">
            <p>No topics found. <button @click="navigateTo('/topics/new')" class="link-btn">Create your first topic</button></p>
          </div>
          <div v-else class="topics-grid">
            <div 
              v-for="topic in myTopics" 
              :key="topic.id"
              class="topic-card"
              @click="editTopic(topic)"
            >
              <div class="card-header">
                <div class="card-title">
                  <h3>{{ topic.title }}</h3>
                  <span class="card-badge">{{ topic.word_count || 0 }} words</span>
                </div>
                <span class="card-status" :class="topic.status">{{ formatStatus(topic.status) }}</span>
              </div>
              <div class="card-content">
                <p class="card-description">{{ topic.summary || 'No summary available' }}</p>
                <div class="card-metrics">
                  <span class="card-metric">
                    <span class="metric-label">Collection:</span>
                    {{ topic.collection_name || 'None' }}
                  </span>
                  <span class="card-metric">
                    <span class="metric-label">Updated:</span>
                    {{ formatRelativeTime(topic.updated_at) }}
                  </span>
                  <span class="card-metric" v-if="topic.review_status">
                    <span class="metric-label">Review:</span>
                    {{ formatReviewStatus(topic.review_status) }}
                  </span>
                </div>
              </div>
              <div class="card-footer">
                <span class="card-date">Created {{ formatRelativeTime(topic.created_at) }}</span>
                <div class="card-actions">
                  <button 
                    v-if="topic.status === 'draft'" 
                    @click.stop="sendForReview(topic)" 
                    class="card-action-btn primary"
                  >
                    Send for Review
                  </button>
                  <button 
                    v-else-if="topic.status === 'published'" 
                    @click.stop="viewPublished(topic)" 
                    class="card-action-btn primary"
                  >
                    View Published
                  </button>
                  <button @click.stop="editTopic(topic)" class="card-action-btn">Edit</button>
                  <button @click.stop="duplicateTopic(topic)" class="card-action-btn">Duplicate</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-overlay">
      <div class="loading-spinner">Loading your content...</div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AuthorDashboard',
  
  data() {
    return {
      loading: true,
      stats: {
        myTopics: 0,
        drafts: 0,
        published: 0,
        inReview: 0,
        createdThisWeek: 0
      },
      myTopics: [],
      recentTopics: []
    }
  },

  async created() {
    await this.loadDashboardData()
  },

  methods: {
    async loadDashboardData() {
      this.loading = true
      try {
        await Promise.all([
          this.loadMyTopics(),
          this.loadStats()
        ])
      } catch (error) {
        console.error('Failed to load author dashboard:', error)
      } finally {
        this.loading = false
      }
    },

    async loadMyTopics() {
      try {
        const res = await fetch('/api/topics/')
        if (res.ok) {
          const allTopics = await res.json()
          // Filter to current user's topics (in real app, this would be done server-side)
          this.myTopics = allTopics
          // Get recent topics (last 5, sorted by updated_at)
          this.recentTopics = [...this.myTopics]
            .sort((a, b) => new Date(b.updated_at || b.created_at) - new Date(a.updated_at || a.created_at))
            .slice(0, 5)
        }
      } catch (error) {
        console.error('Failed to load topics:', error)
        this.myTopics = []
        this.recentTopics = []
      }
    },



    async loadStats() {
      try {
        // Calculate stats from topics data
        const total = this.myTopics.length
        const drafts = this.myTopics.filter(t => t.status === 'draft').length
        const published = this.myTopics.filter(t => t.status === 'published').length
        const inReview = this.myTopics.filter(t => t.status === 'in_review').length
        
        // Calculate topics created this week
        const oneWeekAgo = new Date()
        oneWeekAgo.setDate(oneWeekAgo.getDate() - 7)
        const createdThisWeek = this.myTopics.filter(t => 
          t.created_at && new Date(t.created_at) > oneWeekAgo
        ).length

        this.stats = {
          myTopics: total,
          drafts,
          published,
          inReview,
          createdThisWeek
        }
      } catch (error) {
        console.error('Failed to calculate stats:', error)
      }
    },

    createFromTemplate(type) {
      const templates = {
        'procedure': '/topics/new?template=procedure',
        'reference': '/topics/new?template=reference',
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
        'faq': '/topics/new?template=faq',
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
        'blank': '/topics/new'
      }
      this.navigateTo(templates[type])
    },

    editTopic(topic) {
      this.$router.push(`/topics/${topic.id}/edit`)
    },

    viewPublished(topic) {
      this.$router.push(`/topics/${topic.id}`)
    },

    async sendForReview(topic) {
      // Persist review request to backend
      try {
        const res = await fetch(`/api/topics/${topic.id}/review`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ status: 'in_review' })
        })
        if (!res.ok) throw new Error('Failed to send for review')
        await this.loadMyTopics()
      } catch (err) {
        console.error('Error sending for review:', err)
      }
      this.$router.push(`/topics/${topic.id}/review`)
    },

    async duplicateTopic(topic) {
      // Persist duplication to backend
      try {
        const res = await fetch(`/api/topics/${topic.id}/duplicate`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' }
        })
        if (!res.ok) throw new Error('Failed to duplicate topic')
        await this.loadMyTopics()
      } catch (err) {
        console.error('Error duplicating topic:', err)
      }
    },

    navigateTo(path) {
      this.$router.push(path)
    },

    formatStatus(status) {
      const statusMap = {
        'draft': 'Draft',
        'in_review': 'In Review',
        'published': 'Published',
        'archived': 'Archived'
      }
      return statusMap[status] || status
    },

    formatReviewStatus(status) {
      const statusMap = {
        'pending': 'Pending',
        'approved': 'Approved',
        'needs_changes': 'Needs Changes',
        'rejected': 'Rejected'
      }
      return statusMap[status] || status
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
    }
  }
}
</script>

<style scoped>
.author-dashboard {
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
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.metric-card:hover {
  border-color: #205493;
  box-shadow: 0 4px 12px rgba(0,90,156,0.15);
  transform: translateY(-2px);
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
  margin-bottom: 2rem;
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

/* Template Section */
.action-section {
  border-top: 1px solid #f8f9fa;
  padding-top: 1.5rem;
}

.action-section h3 {
  margin: 0 0 1rem 0;
  color: #495057;
  font-size: 1rem;
  font-weight: 600;
}

.template-buttons {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}

.template-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem;
  border: 1px solid #e9ecef;
  border-radius: 4px;
  background: white;
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: left;
  font-size: 0.8rem;
}

.template-btn:hover {
  border-color: #205493;
  background: #f8f9fa;
}

.template-icon {
  font-size: 1rem;
}

/* Topics List */
.topics-list {
  max-height: 400px;
  overflow-y: auto;
}

.topic-item {
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

.topic-item:hover {
  border-color: #205493;
  background: #f8f9fa;
}

.topic-item:last-child {
  margin-bottom: 0;
}

.topic-icon {
  font-size: 1.5rem;
  min-width: 30px;
}

.topic-content {
  flex: 1;
}

.topic-title {
  font-weight: 600;
  color: #495057;
  margin-bottom: 0.25rem;
}

.topic-description {
  color: #6c757d;
  font-size: 0.875rem;
  margin-bottom: 0.25rem;
}

.topic-meta {
  color: #adb5bd;
  font-size: 0.75rem;
}

.topic-status {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.7rem;
  font-weight: 500;
  text-transform: uppercase;
}

.topic-status.draft {
  background: #fff3cd;
  color: #856404;
}

.topic-status.published {
  background: #d4edda;
  color: #155724;
}

.topic-status.in_review {
  background: #cce5ff;
  color: #004085;
}

/* Topic Cards */
.topics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
}

.topic-card {
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.2s ease;
  background: white;
}

.topic-card:hover {
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

.card-status.draft {
  background: #fff3cd;
  color: #856404;
}

.card-status.published {
  background: #d4edda;
  color: #155724;
}

.card-status.in_review {
  background: #cce5ff;
  color: #004085;
}

.card-content {
  margin-bottom: 1rem;
}

.card-description {
  color: #6c757d;
  font-size: 0.875rem;
  line-height: 1.4;
  margin: 0 0 0.75rem 0;
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
  flex-wrap: wrap;
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
  .author-dashboard {
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
  
  .topics-grid {
    grid-template-columns: 1fr;
  }
  
  .template-buttons {
    grid-template-columns: 1fr;
  }
  
  .dashboard-header h1 {
    font-size: 2rem;
  }
  
  .card-actions {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>
