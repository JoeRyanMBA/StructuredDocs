<template>
  <NotificationTicker
    :notifications="allNotifications"
    contextType="global"
    @mark-read="markNotificationRead"
  />
  <div class="dashboard">
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

      <!-- Quick Actions Section -->
      <div class="quick-actions-section">
        <h2>Quick Actions</h2>
        <p class="section-description">Manage your system data and resources</p>
        <div class="quick-actions-grid">
          <router-link to="/all-tasks" class="quick-action-card">
            <div class="action-icon">📋</div>
            <div class="action-content">
              <h3>All Tasks</h3>
              <p>Manage and organize all tasks across projects</p>
            </div>
            <div class="action-arrow">→</div>
          </router-link>

          <router-link to="/all-tags" class="quick-action-card">
            <div class="action-icon">🏷️</div>
            <div class="action-content">
              <h3>All Tags</h3>
              <p>Create and manage tags for categorization</p>
            </div>
            <div class="action-arrow">→</div>
          </router-link>

          <router-link to="/all-stakeholders" class="quick-action-card">
            <div class="action-icon">👥</div>
            <div class="action-content">
              <h3>All Stakeholders</h3>
              <p>Manage stakeholder profiles and information</p>
            </div>
            <div class="action-arrow">→</div>
          </router-link>

          <router-link to="/all-milestones" class="quick-action-card">
            <div class="action-icon">🎯</div>
            <div class="action-content">
              <h3>All Milestones</h3>
              <p>Track project milestones and deadlines</p>
            </div>
            <div class="action-arrow">→</div>
          </router-link>

          <router-link to="/topics" class="quick-action-card">
            <div class="action-icon">📝</div>
            <div class="action-content">
              <h3>All Topics</h3>
              <p>View and manage documentation topics</p>
            </div>
            <div class="action-arrow">→</div>
          </router-link>

          <router-link to="/projects" class="quick-action-card">
            <div class="action-icon">📁</div>
            <div class="action-content">
              <h3>All Projects</h3>
              <p>Manage projects and project settings</p>
            </div>
            <div class="action-arrow">→</div>
          </router-link>
        </div>
      </div>

      <div class="content-grid">
        <div class="dashboard-section">
          <h2>Projects Overview</h2>
          <div v-if="projects.length === 0" class="empty-state">
            <p>No projects found.</p>
          </div>
          <div v-else class="project-list">
            <div 
              v-for="project in projects" 
              :key="project.id" 
              class="project-item"
              @click="navigateTo('/projects')"
              style="cursor: pointer;"
            >
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
              <div class="activity-icon">📄</div>
              <div class="activity-content">
                <div class="activity-title">{{ activity.filename }}</div>
                <div class="activity-description">
                  {{ activity.type === 'word' ? 'Word Document' : 'Markdown File' }} import - 
                  Status: {{ formatStatus(activity.status) }}
                  <span v-if="activity.topics_count"> - {{ activity.topics_count }} topics</span>
                </div>
                <div class="activity-time">{{ formatRelativeTime(activity.created_at) }}</div>
              </div>
            </div>
          </div>
        </div>
        <div class="dashboard-section full-width">
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
      recentActivity: [],
      calendarEvents: []
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
          this.loadRecentActivity(),
          this.loadCalendarEvents()
        ])
      } catch (error) {
        console.error('Failed to load dashboard data:', error)
      } finally {
        this.loading = false
      }
    },
    
    async loadStats() {
      try {
        // Fetch real stats from backend API
        const response = await fetch('/api/dashboard/stats');
        if (response.ok) {
          this.stats = await response.json();
        } else {
          this.stats = {
            projects: { total: 0, active: 0 },
            collections: { total: 0, new_today: 0 },
            topics: { total: 0, drafts: 0 },
            reviews: { total: 0, pending: 0 }
          };
        }
      } catch (error) {
        console.error('Failed to load stats:', error)
        this.stats = {
          projects: { total: 0, active: 0 },
          collections: { total: 0, new_today: 0 },
          topics: { total: 0, drafts: 0 },
          reviews: { total: 0, pending: 0 }
        };
      }
    },
    
    async loadProjects() {
      try {
        const response = await fetch('/api/projects/')
        if (response.ok) {
          this.projects = await response.json()
        } else {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
      } catch (error) {
        console.error('Failed to load projects:', error)
        // Fallback to empty array
        this.projects = []
      }
    },
    
    async loadPendingActions() {
      try {
        // Fetch real pending actions from backend API
        const response = await fetch('/api/dashboard/pending-actions');
        if (response.ok) {
          this.pendingActions = await response.json();
        } else {
          this.pendingActions = [];
        }
      } catch (error) {
        console.error('Failed to load pending actions:', error)
        this.pendingActions = [];
      }
    },
    
    async loadRecentActivity() {
      try {
        const res = await fetch('/api/import/history');
        if (res.ok) {
          this.recentActivity = await res.json();
        }
      } catch (error) {
        console.error('Failed to load recent activity:', error)
      }
    },
    
    async loadCalendarEvents() {
      try {
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
        });
        this.calendarEvents = events;
      } catch (error) {
        console.error('Failed to load calendar events:', error)
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
/* Dashboard Layout */
.dashboard {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.dashboard-header {
  text-align: center;
  margin-bottom: 2rem;
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
}

/* Metrics Grid */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
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
  transition: all 0.2s ease;
}

.metric-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
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
}

.metric-detail {
  font-size: 0.8rem;
  color: #6c757d;
  margin-top: 0.25rem;
}

/* Content Grid */
.content-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
}

.dashboard-section {
  background: white;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.dashboard-section.full-width {
  grid-column: 1 / -1;
}

.dashboard-section h2 {
  margin: 0 0 1rem 0;
  color: #112e51;
  font-size: 1.25rem;
  font-weight: 600;
}

/* Project List */
.project-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.project-item {
  border: 1px solid #e9ecef;
  border-radius: 6px;
  padding: 1rem;
  transition: all 0.2s ease;
}

.project-item:hover {
  border-color: #205493;
  background: #f8f9fa;
}

.project-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.project-header h4 {
  margin: 0;
  color: #112e51;
  font-size: 1rem;
  font-weight: 600;
}

.project-status {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.project-status.active {
  background: #d1fae5;
  color: #065f46;
}

.project-status.planning {
  background: #fef3c7;
  color: #92400e;
}

.project-status.completed {
  background: #dbeafe;
  color: #205493;
}

.project-description {
  color: #6c757d;
  font-size: 0.9rem;
  margin-bottom: 0.75rem;
}

.project-metrics {
  display: flex;
  gap: 1rem;
  font-size: 0.8rem;
  color: #6c757d;
}

.metric-label {
  font-weight: 600;
}

/* Action and Activity Lists */
.action-list, .activity-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.action-item, .activity-item {
  display: flex;
  gap: 0.75rem;
  padding: 0.75rem;
  border: 1px solid #e9ecef;
  border-radius: 6px;
  transition: all 0.2s ease;
}

.action-item:hover {
  border-color: #205493;
  background: #f8f9fa;
  cursor: pointer;
}

.action-icon, .activity-icon {
  font-size: 1.25rem;
  min-width: 24px;
  text-align: center;
}

.action-content, .activity-content {
  flex: 1;
}

.action-title, .activity-title {
  font-weight: 600;
  color: #112e51;
  margin-bottom: 0.25rem;
}

.action-description, .activity-description {
  font-size: 0.9rem;
  color: #6c757d;
  margin-bottom: 0.25rem;
}

.action-meta, .activity-time {
  font-size: 0.8rem;
  color: #9ca3af;
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 2rem;
  color: #6c757d;
}

/* Loading State */
.loading-overlay {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 4rem;
}

.loading-spinner {
  font-size: 1.1rem;
  color: #6c757d;
}

/* Quick Actions Section */
.quick-actions-section {
  margin: 3rem 0;
  padding: 2rem;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-radius: 12px;
  border: 1px solid #dee2e6;
}

.quick-actions-section h2 {
  color: #112e51;
  margin-bottom: 0.5rem;
  font-size: 1.5rem;
  font-weight: 600;
}

.section-description {
  color: #6c757d;
  margin-bottom: 2rem;
  font-size: 1rem;
}

.quick-actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.quick-action-card {
  display: flex;
  align-items: center;
  padding: 1.5rem;
  background: white;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  text-decoration: none;
  color: inherit;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.quick-action-card:hover {
  border-color: #007bff;
  box-shadow: 0 4px 12px rgba(0, 123, 255, 0.15);
  transform: translateY(-2px);
  text-decoration: none;
  color: inherit;
}

.quick-action-card .action-icon {
  font-size: 2rem;
  margin-right: 1rem;
  min-width: 60px;
  text-align: center;
}

.quick-action-card .action-content {
  flex: 1;
}

.quick-action-card h3 {
  margin: 0 0 0.5rem 0;
  color: #112e51;
  font-size: 1.1rem;
  font-weight: 600;
}

.quick-action-card p {
  margin: 0;
  color: #6c757d;
  font-size: 0.9rem;
  line-height: 1.4;
}

.quick-action-card .action-arrow {
  font-size: 1.5rem;
  color: #007bff;
  margin-left: 1rem;
  transition: transform 0.3s ease;
}

.quick-action-card:hover .action-arrow {
  transform: translateX(4px);
}

/* Responsive Design */
@media (max-width: 768px) {
  .dashboard {
    padding: 1rem;
  }
  
  .content-grid {
    grid-template-columns: 1fr;
  }
  
  .metrics-grid {
    grid-template-columns: 1fr;
  }
  
  .quick-actions-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  
  .quick-action-card {
    padding: 1rem;
  }
  
  .quick-action-card .action-icon {
    font-size: 1.5rem;
    min-width: 50px;
  }
  
  .project-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  
  .project-metrics {
    flex-direction: column;
    gap: 0.25rem;
  }
}
</style>