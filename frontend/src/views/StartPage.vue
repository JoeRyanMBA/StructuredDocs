<template>
  <div class="dashboard">
    <div class="dashboard-header">
      <h1>Dashboard</h1>
      <p class="welcome-text">Welcome to the SCCMB Documentation Project Hub.</p>
    </div>

    <!-- Key Metrics Cards -->
    <div class="metrics-grid">
      <div class="metric-card" @click="navigateTo('/projects')">
        <div class="metric-icon">📊</div>
        <div class="metric-content">
          <h3>Projects</h3>
          <div class="metric-number">{{ stats.projects?.total || 0 }}</div>
          <div class="metric-detail">{{ stats.projects?.active || 0 }} Active</div>
        </div>
      </div>

      <div class="metric-card" @click="navigateTo('/collections')">
        <div class="metric-icon">📚</div>
        <div class="metric-content">
          <h3>Collections</h3>
          <div class="metric-number">{{ stats.collections?.total || 0 }}</div>
          <div class="metric-detail">{{ stats.collections?.new_today || 0 }} New Today</div>
        </div>
      </div>

      <div class="metric-card" @click="navigateTo('/topics')">
        <div class="metric-icon">📝</div>
        <div class="metric-content">
          <h3>Topics</h3>
          <div class="metric-number">{{ stats.topics?.total || 0 }}</div>
          <div class="metric-detail">{{ stats.topics?.drafts || 0 }} Drafts</div>
        </div>
      </div>

      <div class="metric-card" @click="navigateTo('/reviews')">
        <div class="metric-icon">✅</div>
        <div class="metric-content">
          <h3>Reviews</h3>
          <div class="metric-number">{{ stats.reviews?.total || 0 }}</div>
          <div class="metric-detail">{{ stats.reviews?.pending || 0 }} Pending</div>
        </div>
      </div>
    </div>

    <!-- Main Content Grid -->
    <div class="content-grid">
      
      <!-- Pending Actions -->
      <div class="dashboard-section">
        <h2>Pending Actions</h2>
        <div class="action-list">
          <div v-if="pendingActions.length === 0" class="empty-state">
            <p>No pending actions - great work! 🎉</p>
          </div>
          <div v-else>
            <div 
              v-for="action in pendingActions" 
              :key="`${action.type}-${action.id}`"
              class="action-item"
              @click="handleActionClick(action)"
            >
              <div class="action-icon">{{ action.icon }}</div>
              <div class="action-content">
                <div class="action-title">{{ action.title }}</div>
                <div class="action-description">{{ action.description }}</div>
                <div class="action-meta">{{ action.meta }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Recent Activity -->
      <div class="dashboard-section">
        <h2>Recent Activity</h2>
        <div class="activity-list">
          <div v-if="recentActivity.length === 0" class="empty-state">
            <p>No recent activity</p>
          </div>
          <div v-else>
            <div 
              v-for="activity in recentActivity" 
              :key="`${activity.type}-${activity.id}-${activity.timestamp}`"
              class="activity-item"
            >
              <div class="activity-icon">{{ activity.icon }}</div>
              <div class="activity-content">
                <div class="activity-title">{{ activity.title }}</div>
                <div class="activity-description">{{ activity.description }}</div>
                <div class="activity-time">{{ formatRelativeTime(activity.timestamp) }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Calendar Overview -->
      <div class="dashboard-section">
        <h2>Calendar Overview</h2>
        <CalendarWidget :events="calendarEvents" :showLegend="false" />
      </div>

      <!-- Project Status Overview -->
      <div class="dashboard-section full-width">
        <h2>Project Status Overview</h2>
        <div class="project-overview">
          <div v-if="projects.length === 0" class="empty-state">
            <p>No projects found. <router-link to="/projects">Create your first project</router-link></p>
          </div>
          <div v-else class="project-list">
            <div 
              v-for="project in projects" 
              :key="project.id"
              class="project-item"
              @click="navigateTo(`/projects/${project.id}`)"
            >
              <div class="project-header">
                <h4>{{ project.name }}</h4>
                <span class="project-status" :class="project.status">{{ formatStatus(project.status) }}</span>
              </div>
              <p class="project-description">{{ project.description }}</p>
              <div class="project-metrics">
                <span class="project-metric">
                  <span class="metric-label">Collections:</span>
                  {{ project.collections_count || 0 }}
                </span>
                <span class="project-metric">
                  <span class="metric-label">Reviews:</span>
                  {{ project.active_reviews_count || 0 }}
                </span>
                <span class="project-metric">
                  <span class="metric-label">Stakeholders:</span>
                  {{ project.stakeholders_count || 0 }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-overlay">
      <div class="loading-spinner">Loading dashboard...</div>
    </div>
  </div>
</template>

<script>
import CalendarWidget from '../components/CalendarWidget.vue'

export default {
  name: 'Dashboard',
  components: {
    CalendarWidget
  },
  
  data() {
    return {
      loading: true,
      stats: {
        projects: { total: 0, active: 0 },
        collections: { total: 0, new_today: 0 },
        topics: { total: 0, drafts: 0 },
        reviews: { total: 0, pending: 0 }
      },
      projects: [],
      pendingActions: [],
      recentActivity: []
    }
  },

  computed: {
    calendarEvents() {
      const events = []
      
      // Generate events from projects with milestones
      this.projects.forEach(project => {
        // Add project milestones if they exist
        if (project.milestones && Array.isArray(project.milestones)) {
          project.milestones.forEach(milestone => {
            if (milestone.date) {
              events.push({
                id: `${project.id}-${milestone.name}`,
                title: `${project.name}: ${milestone.name}`,
                date: milestone.date,
                type: 'milestone',
                project: project.name
              })
            }
          })
        }
        
        // Add project creation date
        if (project.created_at) {
          const createdDate = project.created_at.split('T')[0]
          events.push({
            id: `${project.id}-created`,
            title: `Project Created: ${project.name}`,
            date: createdDate,
            type: 'meeting',
            project: project.name
          })
        }
      })
      
      // Add mock upcoming deadlines for demonstration
      const today = new Date()
      const nextWeek = new Date(today.getTime() + 7 * 24 * 60 * 60 * 1000)
      const nextMonth = new Date(today.getTime() + 30 * 24 * 60 * 60 * 1000)
      
      events.push(
        {
          id: 'deadline-1',
          title: 'Quarterly Review Deadline',
          date: nextWeek.toISOString().split('T')[0],
          type: 'deadline'
        },
        {
          id: 'meeting-1',
          title: 'Stakeholder Meeting',
          date: nextMonth.toISOString().split('T')[0],
          type: 'meeting'
        }
      )
      
      return events
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
          this.loadStats(),
          this.loadProjects(),
          this.loadPendingActions(),
          this.loadRecentActivity()
        ])
      } catch (error) {
        console.error('Failed to load dashboard data:', error)
      } finally {
        this.loading = false
      }
    },

    async loadStats() {
      try {
        // Load projects stats
        const projectsRes = await fetch('/api/projects/')
        if (projectsRes.ok) {
          const projects = await projectsRes.json()
          this.stats.projects = {
            total: projects.length,
            active: projects.filter(p => p.status === 'active').length
          }
        }

        // Load collections stats
        const collectionsRes = await fetch('/api/collections/')
        if (collectionsRes.ok) {
          const collections = await collectionsRes.json()
          const today = new Date().toDateString()
          this.stats.collections = {
            total: collections.length,
            new_today: collections.filter(c => 
              c.created_at && new Date(c.created_at).toDateString() === today
            ).length
          }
        }

        // Load topics stats
        const topicsRes = await fetch('/api/topics/')
        if (topicsRes.ok) {
          const topics = await topicsRes.json()
          this.stats.topics = {
            total: topics.length,
            drafts: topics.filter(t => t.status === 'draft').length
          }
        }

        // Load reviews stats
        const reviewsRes = await fetch('/api/reviews/stats')
        if (reviewsRes.ok) {
          const reviewStats = await reviewsRes.json()
          this.stats.reviews = {
            total: reviewStats.total_reviews || 0,
            pending: reviewStats.pending_reviews || 0
          }
        }
      } catch (error) {
        console.error('Failed to load stats:', error)
      }
    },

    async loadProjects() {
      try {
        const res = await fetch('/api/projects/')
        if (res.ok) {
          this.projects = await res.json()
        }
      } catch (error) {
        console.error('Failed to load projects:', error)
      }
    },

    async loadPendingActions() {
      try {
        const actions = []

        // Check for topics needing review
        const topicsRes = await fetch('/api/reviews/topics/pending')
        if (topicsRes.ok) {
          const pendingTopics = await topicsRes.json()
          pendingTopics.slice(0, 3).forEach(topic => {
            actions.push({
              type: 'topic_review',
              id: topic.id,
              icon: '📝',
              title: `Review "${topic.title}"`,
              description: 'Topic needs review',
              meta: `Created ${this.formatRelativeTime(topic.created_at)}`,
              link: `/topics/${topic.id}/review`
            })
          })
        }

        // Check for import documents needing approval
        const importsRes = await fetch('/api/import/history')
        if (importsRes.ok) {
          const imports = await importsRes.json()
          const pending = imports.filter(imp => imp.status === 'staging').slice(0, 3)
          pending.forEach(imp => {
            actions.push({
              type: 'import_review',
              id: imp.id,
              icon: '📥',
              title: `Review Import: ${imp.filename}`,
              description: 'Import document needs approval',
              meta: `Imported ${this.formatRelativeTime(imp.created_at)}`,
              link: `/import/${imp.id}/review`
            })
          })
        }

        this.pendingActions = actions.slice(0, 5) // Limit to 5 items
      } catch (error) {
        console.error('Failed to load pending actions:', error)
      }
    },

    async loadRecentActivity() {
      try {
        const activities = []

        // Get recent topics
        const topicsRes = await fetch('/api/topics/')
        if (topicsRes.ok) {
          const topics = await topicsRes.json()
          topics.slice(0, 3).forEach(topic => {
            activities.push({
              type: 'topic',
              id: topic.id,
              icon: '📝',
              title: topic.title,
              description: `Status: ${this.formatStatus(topic.status)}`,
              timestamp: topic.updated_at || topic.created_at
            })
          })
        }

        // Get recent imports
        const importsRes = await fetch('/api/import/history')
        if (importsRes.ok) {
          const imports = await importsRes.json()
          imports.slice(0, 3).forEach(imp => {
            activities.push({
              type: 'import',
              id: imp.id,
              icon: '📥',
              title: `Import: ${imp.filename}`,
              description: `Status: ${this.formatStatus(imp.status)}`,
              timestamp: imp.created_at
            })
          })
        }

        // Sort by timestamp and limit
        this.recentActivity = activities
          .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
          .slice(0, 6)
      } catch (error) {
        console.error('Failed to load recent activity:', error)
      }
    },

    navigateTo(path) {
      this.$router.push(path)
    },

    handleActionClick(action) {
      if (action.link) {
        this.navigateTo(action.link)
      }
    },

    formatStatus(status) {
      const statusMap = {
        'draft': 'Draft',
        'published': 'Published',
        'archived': 'Archived',
        'pending': 'Pending',
        'approved': 'Approved',
        'rejected': 'Rejected',
        'staging': 'Staging',
        'active': 'Active',
        'planning': 'Planning',
        'review': 'In Review',
        'completed': 'Completed',
        'on_hold': 'On Hold'
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
.dashboard {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.dashboard-header {
  margin-bottom: 2rem;
  text-align: center;
}

.dashboard-header h1 {
  color: #005a9c;
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
  border-color: #005a9c;
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
  color: #005a9c;
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

/* Action List */
.action-list {
  max-height: 400px;
  overflow-y: auto;
}

.action-item {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 1rem;
  border: 1px solid #f8f9fa;
  border-radius: 6px;
  margin-bottom: 0.75rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.action-item:hover {
  border-color: #005a9c;
  background: #f8f9fa;
}

.action-item:last-child {
  margin-bottom: 0;
}

.action-icon {
  font-size: 1.5rem;
  min-width: 30px;
}

.action-content {
  flex: 1;
}

.action-title {
  font-weight: 600;
  color: #495057;
  margin-bottom: 0.25rem;
}

.action-description {
  color: #6c757d;
  font-size: 0.875rem;
  margin-bottom: 0.25rem;
}

.action-meta {
  color: #adb5bd;
  font-size: 0.75rem;
}

/* Activity List */
.activity-list {
  max-height: 400px;
  overflow-y: auto;
}

.activity-item {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 0.75rem 0;
  border-bottom: 1px solid #f8f9fa;
}

.activity-item:last-child {
  border-bottom: none;
}

.activity-icon {
  font-size: 1.25rem;
  min-width: 25px;
}

.activity-content {
  flex: 1;
}

.activity-title {
  font-weight: 500;
  color: #495057;
  margin-bottom: 0.25rem;
  font-size: 0.875rem;
}

.activity-description {
  color: #6c757d;
  font-size: 0.75rem;
  margin-bottom: 0.25rem;
}

.activity-time {
  color: #adb5bd;
  font-size: 0.75rem;
}

/* Project Overview */
.project-overview {
  margin-top: 1rem;
}

.project-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 1.5rem;
}

.project-item {
  border: 1px solid #e9ecef;
  border-radius: 6px;
  padding: 1.25rem;
  cursor: pointer;
  transition: all 0.2s ease;
  background: #f8f9fa;
}

.project-item:hover {
  border-color: #005a9c;
  box-shadow: 0 2px 8px rgba(0,90,156,0.1);
}

.project-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.project-header h4 {
  margin: 0;
  color: #495057;
  font-size: 1rem;
  font-weight: 600;
}

.project-status {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.project-status.active {
  background: #d4edda;
  color: #155724;
}

.project-status.planning {
  background: #fff3cd;
  color: #856404;
}

.project-status.review {
  background: #cce5ff;
  color: #004085;
}

.project-status.completed {
  background: #d1ecf1;
  color: #0c5460;
}

.project-status.on_hold {
  background: #f8d7da;
  color: #721c24;
}

.project-description {
  color: #6c757d;
  font-size: 0.875rem;
  margin: 0 0 1rem 0;
  line-height: 1.4;
}

.project-metrics {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.project-metric {
  font-size: 0.75rem;
  color: #6c757d;
}

.metric-label {
  font-weight: 500;
  color: #495057;
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

.empty-state a {
  color: #005a9c;
  text-decoration: none;
}

.empty-state a:hover {
  text-decoration: underline;
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
  color: #005a9c;
  font-size: 1.1rem;
}

/* Responsive Design */
@media (max-width: 768px) {
  .dashboard {
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
  
  .project-list {
    grid-template-columns: 1fr;
  }
  
  .dashboard-header h1 {
    font-size: 2rem;
  }
  
  .metric-card {
    padding: 1rem;
  }
  
  .dashboard-section {
    padding: 1rem;
  }
}

@media (max-width: 480px) {
  .project-metrics {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .project-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
}
</style>