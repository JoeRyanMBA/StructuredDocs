<template>
  <NotificationTicker
    :notifications="allNotifications"
    contextType="global"
    @mark-read="markNotificationRead"
  />
  <div class="dashboard">
<!--    <div style="color: red; font-weight: bold; margin-bottom: 2rem;">
      DEBUG: StartPage.vue rendered. loading={{ loading }} projects={{ projects.length }}
    </div>-->
    <div class="dashboard-header">
      <h1>Documentation Project Hub Dashboard</h1>
      <p class="welcome-text">Welcome, {{ $route?.meta?.user?.name || 'User' }}!</p>
    </div>
    <div v-if="loading" class="loading-overlay">
      <span class="loading-spinner">Loading dashboard...</span>
    </div>
    <div v-else>
      <div class="metrics-grid">
        <div class="metric-card" @click="navigateTo('/projects')" style="cursor:pointer;">
          <div class="metric-icon">📁</div>
          <div class="metric-content">
            <h3>Projects</h3>
            <div class="metric-number">{{ stats.projects.total }}</div>
            <div class="metric-detail">Active: {{ stats.projects.active }}</div>
          </div>
        </div>
        <div class="metric-card" @click="navigateTo('/collections')" style="cursor:pointer;">
          <div class="metric-icon">📚</div>
          <div class="metric-content">
            <h3>Collections</h3>
            <div class="metric-number">{{ stats.collections.total }}</div>
            <div class="metric-detail">New Today: {{ stats.collections.new_today }}</div>
          </div>
        </div>
        <div class="metric-card" @click="navigateTo('/topics')" style="cursor:pointer;">
          <div class="metric-icon">📝</div>
          <div class="metric-content">
            <h3>Topics</h3>
            <div class="metric-number">{{ stats.topics.total }}</div>
            <div class="metric-detail">Drafts: {{ stats.topics.drafts }}</div>
          </div>
        </div>
        <div class="metric-card" @click="navigateTo('/reviews')" style="cursor:pointer;">
          <div class="metric-icon">🔎</div>
          <div class="metric-content">
            <h3>Reviews</h3>
            <div class="metric-number">{{ stats.reviews.total }}</div>
            <div class="metric-detail">Pending: {{ stats.reviews.pending }}</div>
          </div>
        </div>
      </div>
      <div class="content-grid">
        <div class="dashboard-section">
          <h2>Projects Overview</h2>
          <div v-if="projects.length === 0" class="empty-state">
            <p>No projects found.</p>
          </div>
          <div v-else class="project-list">
            <div v-for="project in projects" :key="project.id" class="project-item">
              <div class="project-header">
                <h4>{{ project.name }}</h4>
                <span :class="['project-status', formatStatus(project.status)]">{{ formatStatus(project.status) }}</span>
              </div>
              <div class="project-description">{{ project.description }}</div>
              <div class="project-metrics">
                <span class="project-metric"><span class="metric-label">Created:</span> {{ formatRelativeTime(project.created_at) }}</span>
                <span v-if="project.milestones && project.milestones.length" class="project-metric"><span class="metric-label">Milestones:</span> {{ project.milestones.length }}</span>
              </div>
            </div>
          </div>
        </div>
        <div class="dashboard-section">
          <h2>Pending Actions</h2>
          <div v-if="pendingActions.length === 0" class="empty-state">
            <p>No pending actions.</p>
          </div>
          <div v-else class="action-list">
            <div v-for="action in pendingActions" :key="action.id" class="action-item" @click="handleActionClick(action)">
              <div class="action-icon">⚡</div>
              <div class="action-content">
                <div class="action-title">{{ action.title || action.name }}</div>
                <div class="action-description">{{ action.description }}</div>
                <div class="action-meta">{{ formatRelativeTime(action.created_at) }}</div>
              </div>
            </div>
          </div>
        </div>
        <div class="dashboard-section full-width">
          <h2>Recent Activity</h2>
          <div v-if="recentActivity.length === 0" class="empty-state">
            <p>No recent activity.</p>
          </div>
          <div v-else class="activity-list">
            <div v-for="activity in recentActivity" :key="activity.id" class="activity-item">
              <div class="activity-icon">🔔</div>
              <div class="activity-content">
                <div class="activity-title">{{ activity.title || activity.name }}</div>
                <div class="activity-description">{{ activity.description }}</div>
                <div class="activity-time">{{ formatRelativeTime(activity.created_at) }}</div>
              </div>
            </div>
          </div>
        </div>
        <div class="dashboard-section">
          <h2>Calendar</h2>
          <CalendarWidget :events="calendarEvents" />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import NotificationTicker from '../components/NotificationTicker.vue'
import CalendarWidget from '../components/CalendarWidget.vue'

export default {
  name: 'StartPage',
  components: { NotificationTicker, CalendarWidget },
  props: {
    notifications: {
      type: Array,
      default: () => []
    },
    globalNotifications: {
      type: Array,
      default: () => []
    },
    dashboardNotifications: {
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
    allNotifications() {
      const all = [
        ...(this.globalNotifications || []),
        ...(this.dashboardNotifications || []),
        ...(this.notifications || [])
      ]
      const seen = new Set()
      return all.filter(n => {
        if (!n || !n.id) return true
        if (seen.has(n.id)) return false
        seen.add(n.id)
        return true
      })
    },
    calendarEvents() {
      const events = [];
      this.projects.forEach(project => {
        if (project.milestones && Array.isArray(project.milestones)) {
          project.milestones.forEach(milestone => {
            if (milestone.date) {
              events.push({
                id: `${project.id}-${milestone.name}`,
                title: `${project.name}: ${milestone.name}`,
                date: milestone.date,
                type: 'milestone',
                project: project.name
              });
            }
          });
        }
        if (project.created_at) {
          const createdDate = project.created_at.split('T')[0];
          events.push({
            id: `${project.id}-created`,
            title: `Project Created: ${project.name}`,
            date: createdDate,
            type: 'meeting',
            project: project.name
          });
        }
      });
      const today = new Date();
      const nextWeek = new Date(today.getTime() + 7 * 24 * 60 * 60 * 1000);
      const nextMonth = new Date(today.getTime() + 30 * 24 * 60 * 60 * 1000);
      events.push({
        id: 'deadline-1',
        title: 'Quarterly Review Deadline',
        date: nextWeek.toISOString().split('T')[0],
        type: 'deadline'
      });
      events.push({
        id: 'meeting-1',
        title: 'Stakeholder Meeting',
        date: nextMonth.toISOString().split('T')[0],
        type: 'meeting'
      });
      return events;
    }
  },
  created() {
    this.loadDashboardData()
  },
  methods: {
    loadDashboardData() {
      this.loading = true;
      Promise.all([
        this.loadStats(),
        this.loadProjects(),
        this.loadPendingActions(),
        this.loadRecentActivity()
      ]).catch(error => {
        console.error('Failed to load dashboard data:', error);
      }).finally(() => {
        this.loading = false;
      });
    },
    async loadStats() {
      try {
        const projectsRes = await fetch('/api/projects/');
        if (projectsRes.ok) {
          const projects = await projectsRes.json();
          this.stats.projects = {
            total: projects.length,
            active: projects.filter(p => p.status === 'active').length
          };
        }
        const collectionsRes = await fetch('/api/collections/');
        if (collectionsRes.ok) {
          const collections = await collectionsRes.json();
          this.stats.collections = {
            total: collections.length,
            new_today: collections.filter(c => {
              const created = new Date(c.created_at);
              const today = new Date();
              return created.toDateString() === today.toDateString();
            }).length
          };
        }
        const topicsRes = await fetch('/api/topics/');
        if (topicsRes.ok) {
          const topics = await topicsRes.json();
          this.stats.topics = {
            total: topics.length,
            drafts: topics.filter(t => t.status === 'draft').length
          };
        }
        const reviewsRes = await fetch('/api/reviews/stats');
        if (reviewsRes.ok) {
          const reviews = await reviewsRes.json();
          this.stats.reviews = {
            total: reviews.topics.pending_review + reviews.topics.draft + reviews.topics.published,
            pending: reviews.topics.pending_review
          };
        }
      } catch (error) {
        console.error('Failed to load stats:', error);
      }
    },
    async loadProjects() {
      try {
        const res = await fetch('/api/projects/');
        if (res.ok) {
          this.projects = await res.json();
        }
      } catch (error) {
        console.error('Failed to load projects:', error);
      }
    },
    async loadPendingActions() {
      try {
        const res = await fetch('/api/reviews/topics/pending');
        if (res.ok) {
          this.pendingActions = await res.json();
        }
      } catch (error) {
        console.error('Failed to load pending actions:', error);
      }
    },
    async loadRecentActivity() {
      try {
        const res = await fetch('/api/import/history');
        if (res.ok) {
          this.recentActivity = await res.json();
        }
      } catch (error) {
        console.error('Failed to load recent activity:', error);
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
  },
  watch: {
    '$route' (to, from) {
      this.loadDashboardData()
    }
  }
}
</script>

<style scoped>
.dashboard {
  margin: 0 auto;
}

.dashboard-header {
  margin-bottom: 2rem;
  text-align: center;
}

.dashboard-header h1 {
  color: #005a9c;
  margin-top:0;
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