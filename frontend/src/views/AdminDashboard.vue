<template>
  <div class="admin-dashboard">
    <!-- NotificationTicker: Always visible at top -->
    <div class="full-width" style="margin-bottom:1.5rem;">
      <NotificationTicker
        :notifications="mergedNotifications"
        contextType="admin"
        @mark-read="markNotificationRead"
      />
    </div>
    <div class="dashboard-header">
      <h1>Admin Dashboard</h1>
      <p class="welcome-text">System administration and user management</p>
    </div>

    <!-- Key Metrics Cards -->
    <div class="metrics-grid">
      <div class="metric-card">
        <div class="metric-icon">👥</div>
        <div class="metric-content">
          <h3>Total Users</h3>
          <div class="metric-number">{{ stats.totalUsers || 0 }}</div>
          <div class="metric-detail">{{ stats.activeUsers || 0 }} Active</div>
        </div>
      </div>

      <div class="metric-card">
        <div class="metric-icon">✏️</div>
        <div class="metric-content">
          <h3>Authors</h3>
          <div class="metric-number">{{ stats.authors || 0 }}</div>
          <div class="metric-detail">Content creators</div>
        </div>
      </div>

      <div class="metric-card">
        <div class="metric-icon">📝</div>
        <div class="metric-content">
          <h3>Reviewers</h3>
          <div class="metric-number">{{ stats.reviewers || 0 }}</div>
          <div class="metric-detail">SME reviewers</div>
        </div>
      </div>

      <div class="metric-card">
        <div class="metric-icon">🔧</div>
        <div class="metric-content">
          <h3>System Health</h3>
          <div class="metric-number">{{ stats.systemHealth || 'Good' }}</div>
          <div class="metric-detail">{{ stats.uptime || '99.9%' }} Uptime</div>
        </div>
      </div>
    </div>

    <!-- Database Metrics Panel (below metrics, above notifications) -->
    <div style="margin-top:2rem;">
      <DatabaseMetricsPanel :metrics="dbMetrics" />
    </div>

    <!-- Main Content Grid -->
    <div class="content-grid">
      
      <!-- Quick Actions -->
 <!--     <div class="dashboard-section full-width">

        async loadDbMetrics() {
          try {
            const response = await fetch('/api/metrics/')
            if (!response.ok) throw new Error('Failed to fetch database metrics')
            const data = await response.json()
            const db = data.database || {}
            this.dbMetrics = {
              tables: db.tables || 0,
              rows: db.totalRecords || 0,
              size: db.size || '0 MB',
              lastBackup: db.lastBackup ? new Date(db.lastBackup).toLocaleString() : 'Unknown'
            }
          } catch (error) {
            console.error('Failed to load database metrics:', error)
          }
        },
        <h2>Quick Actions</h2>
        <div class="quick-actions-grid">
          <button class="action-card" @click="navigateTo('/admin/users')">
            <div class="action-icon">👥</div>Manage Users</button>-->
      <div class="dashboard-grid">
        <!--      <div class="dashboard-section full-width notification-management">
        <h2>Notification Management</h2>
        <div v-if="notifications.length === 0" class="empty-state">
          <p>No notifications found.</p>
        </div>
        <div v-else class="notification-list">
          <div v-for="notification in notifications" :key="notification.id" class="notification-item">
            <div class="notification-content">
              <div class="notification-title">{{ notification.title }}</div>
              <div class="notification-description">{{ notification.description }}</div>
              <div class="notification-meta">{{ formatRelativeTime(notification.created_at) }}</div>
            </div>
            <div class="notification-actions">
              <button @click="markNotificationRead(notification.id)">Mark Read</button>
              <button @click="deleteNotification(notification.id)">Delete</button>
            </div>
          </div>
        </div>
        <div class="create-notification">
          <input v-model="newNotification.title" placeholder="Title" />
          <input v-model="newNotification.description" placeholder="Description" />
          <button @click="createNotification">Create Notification</button>
        </div>
      </div>
      <div class="dashboard-section">
        <h2>Recent System Events</h2>
        <div v-if="systemEvents.length === 0" class="empty-state">
          <p>No recent system events.</p>
        </div>
        <div v-else class="event-list">
          <div v-for="event in systemEvents" :key="event.id" class="event-item">
            <div class="event-title">{{ event.title }}</div>
            <div class="event-description">{{ event.description }}</div>
            <div class="event-meta">{{ formatRelativeTime(event.created_at) }}</div>
          </div>
        </div>
      </div> -->
    </div>
    <!-- ...existing code... -->
  

      <!-- System Status -->
      <div class="dashboard-section full-width">
        <h2>System Overview</h2>
        <div class="system-overview">
          
          <!-- User Management -->
          <div class="system-section">
            <h3>User Management</h3>
            <div class="user-stats">
              <div class="stat-item">
                <span class="stat-label">Total Users:</span>
                <span class="stat-value">{{ userStats.totalUsers || 0 }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">New This Week:</span>
                <span class="stat-value">{{ userStats.newUsersThisWeek || 0 }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">Active Users:</span>
                <span class="stat-value">{{ userStats.activeUsers || 0 }}</span>
              </div>
            </div>
            <div class="user-actions">
              <button @click="navigateTo('/admin/users')" class="section-btn">Manage Users</button>
              <button @click="inviteUser" class="section-btn secondary">Invite User</button>
            </div>
          </div>

          <!-- System Performance -->
          <div class="system-section">
            <h3>System Performance</h3>
            <div class="performance-metrics">
              <div class="metric-row">
                <span class="metric-name">CPU Usage</span>
                <div class="metric-bar">
                  <div class="metric-fill" :style="{width: systemMetrics.cpu + '%'}"></div>
                </div>
                <span class="metric-value">{{ systemMetrics.cpu }}%</span>
              </div>
              <div class="metric-row">
                <span class="metric-name">Memory</span>
                <div class="metric-bar">
                  <div class="metric-fill" :style="{width: systemMetrics.memory + '%'}"></div>
                </div>
                <span class="metric-value">{{ systemMetrics.memory }}%</span>
              </div>
              <div class="metric-row">
                <span class="metric-name">Storage</span>
                <div class="metric-bar">
                  <div class="metric-fill" :style="{width: systemMetrics.storage + '%'}"></div>
                </div>
                <span class="metric-value">{{ systemMetrics.storage }}%</span>
              </div>
            </div>
          </div>


      <!-- Recent System Logs -->
      <div class="system-section">
        <h3>Recent System Events</h3>
        <div class="log-entries">
          <div v-if="systemLogs.length === 0" class="empty-state">
            <p>No recent system events</p>
          </div>
          <div v-else>
            <div 
              v-for="log in systemLogs" 
              :key="log.id"
              class="log-entry"
              :class="log.level"
            >
              <div class="log-time">{{ formatTime(log.timestamp) }}</div>
              <div class="log-message">{{ log.message }}</div>
              <div class="log-level">{{ log.level.toUpperCase() }}</div>
            </div>
          </div>
        </div>
        <div class="log-actions">
          <button @click="navigateTo('/admin/logs')" class="section-btn">View All Logs</button>
        </div>
      </div>
      <!-- Notification Management: Full width, consistent font -->
      <div class="dashboard-section full-width notification-management">
        <h2>Notification Management</h2>
        <div class="notification-list">
          <div v-if="adminNotifications.length === 0" class="empty-state">
            <p>No notifications found.</p>
          </div>
          <div v-else>
            <div v-for="notification in adminNotifications" :key="notification.id" class="notification-item">
              <div class="notification-title">{{ notification.title }}</div>
              <div class="notification-message">{{ notification.message }}</div>
              <div class="notification-meta">{{ formatRelativeTime(notification.date) }} • <span :class="{'read': notification.read}">{{ notification.read ? 'Read' : 'Unread' }}</span></div>
              <div class="notification-actions">
                <button @click="navigateTo('/notifications/new')" class="section-btn">Create Notification</button>
                <button @click="deleteNotification(notification.id)" class="section-btn secondary" style="margin-top:.75rem; margin-bottom:.75rem;">Delete</button>
              </div>
            </div>
          </div>
        </div>
        <br />
        <div class="notification-actions" align="center">
          <button @click="navigateTo('/notifications/new')" class="section-btn">Create Notification</button>
        </div>
      </div>
        </div>
      </div>

    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-overlay">
      <div class="loading-spinner">Loading admin data...</div>
    </div>
  </div>

</template>


<script>
import NotificationTicker from '../components/NotificationTicker.vue'
import DatabaseMetricsPanel from '../components/DatabaseMetricsPanel.vue'

export default {
  name: 'AdminDashboard',
  components: { NotificationTicker, DatabaseMetricsPanel },
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
      stats: {},
      dbMetrics: {},
      userStats: {},
      systemMetrics: {
        cpu: 15,
        memory: 32,
        storage: 45
      },
      recentActivity: [],
      systemLogs: [],
      systemEvents: [],
      adminNotifications: [],
      newNotification: {
        title: '',
        description: ''
      }
    }
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
    // ...existing computed properties...
  },
  async created() {
    await this.loadDashboardData()
  },
  methods: {
    deleteNotification(id) {
      // Persist notification deletion to backend
      fetch(`/api/notifications/${id}`, { method: 'DELETE' })
        .then(response => {
          if (!response.ok) throw new Error('Failed to delete notification')
          this.adminNotifications = this.adminNotifications.filter(n => n.id !== id)
        })
        .catch(error => {
          alert('Failed to delete notification: ' + error.message)
        })
    },

    async loadDashboardData() {
      this.loading = true
      try {
        await Promise.all([
          this.loadStats(),
          this.loadActivity(),
          this.loadSystemLogs(),
          this.loadAdminNotifications(),
          this.loadDbMetrics()
        ])
      } catch (error) {
        console.error('Failed to load admin dashboard:', error)
      } finally {
        this.loading = false
      }
    },

    async loadStats() {
      try {
        // Fetch real stats from backend API
        const response = await fetch('/api/admin/stats');
        if (response.ok) {
          const data = await response.json();
          this.stats = data.stats || {};
          this.userStats = data.userStats || {};
          this.systemMetrics = data.systemMetrics || {};
        } else {
          this.stats = {};
          this.userStats = {};
          this.systemMetrics = {};
        }
      } catch (error) {
        console.error('Failed to load stats:', error)
        this.stats = {};
        this.userStats = {};
        this.systemMetrics = {};
      }
    },

    async loadActivity() {
      try {
        // Fetch real activity from backend API
        const response = await fetch('/api/admin/activity');
        if (response.ok) {
          this.recentActivity = await response.json();
        } else {
          this.recentActivity = [];
        }
      } catch (error) {
        console.error('Failed to load activity:', error)
        this.recentActivity = [];
      }
    },

    async loadSystemLogs() {
      try {
        // Fetch real system logs from backend API
        const response = await fetch('/api/admin/system-logs');
        if (response.ok) {
          this.systemLogs = await response.json();
        } else {
          this.systemLogs = [];
        }
      } catch (error) {
        console.error('Failed to load system logs:', error)
        this.systemLogs = [];
      }
    },

    async loadAdminNotifications() {
      try {
        // Fetch admin notifications from backend API
        const response = await fetch('/api/admin/notifications');
        if (response.ok) {
          this.adminNotifications = await response.json();
        } else {
          this.adminNotifications = [];
        }
      } catch (error) {
        console.error('Failed to load admin notifications:', error)
        this.adminNotifications = [];
      }
    },

    async loadDbMetrics() {
      try {
        const response = await fetch('/api/metrics/')
        if (!response.ok) throw new Error('Failed to fetch database metrics')
        const data = await response.json()
        const db = data.database || {}
        this.dbMetrics = {
          tables: db.tables || 0,
          rows: db.totalRecords || 0,
          size: db.size || '0 MB',
          lastBackup: db.lastBackup ? new Date(db.lastBackup).toLocaleString() : 'Never'
        }
      } catch (error) {
        console.error('Failed to load database metrics:', error)
        this.dbMetrics = {
          tables: 0,
          rows: 0,
          size: '0 MB',
          lastBackup: 'Never'
        }
      }
    },

    performBackup() {
      alert('Database backup initiated. This may take a few minutes.')
      // Implement backup functionality
    },

    clearCache() {
      alert('Cache cleared successfully.')
      // Implement cache clearing
    },

    viewMetrics() {
      this.navigateTo('/admin/metrics')
    },

    inviteUser() {
      this.navigateTo('/admin/users?action=invite')
    },

    navigateTo(path) {
      this.$router.push(path)
    },

    formatActivityType(type) {
      const typeMap = {
        'user': 'User',
        'system': 'System',
        'security': 'Security',
        'backup': 'Backup'
      }
      return typeMap[type] || type
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

    formatTime(timestamp) {
      if (!timestamp) return 'Unknown'
      
      const time = new Date(timestamp)
      return time.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    },

    async createNotification() {
      // Persist new notification to backend
      if (!this.newNotification.title || !this.newNotification.description) {
        alert('Title and description are required.')
        return
      }
      try {
        const response = await fetch('/api/notifications', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            title: this.newNotification.title,
            description: this.newNotification.description
          })
        })
        if (!response.ok) throw new Error('Failed to create notification')
        await this.loadDashboardData()
        this.newNotification.title = ''
        this.newNotification.description = ''
        alert('Notification created successfully!')
      } catch (error) {
        alert('Failed to create notification: ' + error.message)
      }
    },
  }
}
</script>

<style scoped>
/* Notification Management Font Consistency */
.notification-management {
  font-family: inherit;
}
.notification-management h2 {
  color: #495057;
  font-size: 1.25rem;
  font-weight: 600;
  border-bottom: 2px solid #f8f9fa;
  padding-bottom: 0.5rem;
  margin: 0 0 1.5rem 0;
}
.notification-management .notification-title {
  font-weight: 600;
  color: #495057;
  font-size: 1rem;
  margin-bottom: 0.25rem;
}
.notification-management .notification-description {
  color: #6c757d;
  font-size: 0.875rem;
  margin-bottom: 0.25rem;
}
.notification-management .notification-meta {
  color: #adb5bd;
  font-size: 0.75rem;
}
.notification-meta {
  color: #91989e;
  font-size: 0.875rem;
}
.notification-message {
  color: #6c757d;
  font-size: 0.875rem;
  margin-bottom: 0.25rem;
}

.notification-title {
  font-weight: 300;
  color: #333;
  font-size: 1rem;
  margin-bottom: 0.25rem;
  margin-top:0.24rem;
}
.admin-dashboard {
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

/* Tool Section */
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

.tool-buttons {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.tool-btn {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  border: 1px solid #e9ecef;
  border-radius: 4px;
  background: white;
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: left;
  font-size: 0.85rem;
}

.tool-btn:hover {
  border-color: #205493;
  background: #f8f9fa;
}

.tool-icon {
  font-size: 1rem;
}

/* Activity List */
.activity-list {
  max-height: 400px;
  overflow-y: auto;
}

.activity-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  border: 1px solid #f8f9fa;
  border-radius: 6px;
  margin-bottom: 0.75rem;
}

.activity-item:last-child {
  margin-bottom: 0;
}

.activity-icon {
  font-size: 1.5rem;
  min-width: 30px;
}

.activity-content {
  flex: 1;
}

.activity-title {
  font-weight: 600;
  color: #495057;
  margin-bottom: 0.25rem;
}

.activity-description {
  color: #6c757d;
  font-size: 0.875rem;
  margin-bottom: 0.25rem;
}

.activity-meta {
  color: #adb5bd;
  font-size: 0.75rem;
}

.activity-status {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.7rem;
  font-weight: 500;
  text-transform: uppercase;
}

.activity-status.user {
  background: #d4edda;
  color: #155724;
}

.activity-status.system {
  background: #cce5ff;
  color: #004085;
}

.activity-status.security {
  background: #fff3cd;
  color: #856404;
}

/* System Overview */
.system-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.system-section {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 6px;
  padding: 1.5rem;
}

.system-section h3 {
  margin: 0 0 1rem 0;
  color: #495057;
  font-size: 1.1rem;
  font-weight: 600;
}

/* User Stats */
.user-stats {
  margin-bottom: 1.5rem;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
  padding: 0.5rem 0;
  border-bottom: 1px solid #e9ecef;
}

.stat-item:last-child {
  border-bottom: none;
}

.stat-label {
  color: #6c757d;
  font-size: 0.875rem;
}

.stat-value {
  color: #495057;
  font-weight: 600;
}

.user-actions {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.section-btn {
  padding: 0.5rem 1rem;
  border: 1px solid #205493;
  border-radius: 4px;
  background: #205493;
  color: white;
  cursor: pointer;
  font-size: 0.875rem;
  transition: all 0.2s ease;
}

.section-btn:hover {
  background: #005E7B;
}

.section-btn.secondary {
  background: white;
  color: #205493;
}

.section-btn.secondary:hover {
  background: #f8f9fa;
}

/* Performance Metrics */
.performance-metrics {
  margin-bottom: 1rem;
}

.metric-row {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.metric-row:last-child {
  margin-bottom: 0;
}

.metric-name {
  min-width: 80px;
  font-size: 0.875rem;
  color: #495057;
}

.metric-bar {
  flex: 1;
  height: 8px;
  background: #e9ecef;
  border-radius: 4px;
  overflow: hidden;
}

.metric-fill {
  height: 100%;
  background: linear-gradient(90deg, #28a745, #ffc107, #dc3545);
  transition: width 0.3s ease;
}

.metric-value {
  min-width: 40px;
  text-align: right;
  font-size: 0.875rem;
  font-weight: 600;
  color: #495057;
}

/* System Logs */
.log-entries {
  margin-bottom: 1rem;
}

.log-entry {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem;
  margin-bottom: 0.5rem;
  border-radius: 4px;
  font-size: 0.875rem;
}

.log-entry:last-child {
  margin-bottom: 0;
}

.log-entry.info {
  background: #d1ecf1;
  border-left: 3px solid #17a2b8;
}

.log-entry.warning {
  background: #fff3cd;
  border-left: 3px solid #ffc107;
}

.log-entry.error {
  background: #f8d7da;
  border-left: 3px solid #dc3545;
}

.log-time {
  min-width: 60px;
  color: #6c757d;
  font-size: 0.75rem;
}

.log-message {
  flex: 1;
  color: #495057;
}

.log-level {
  font-size: 0.7rem;
  font-weight: 600;
  padding: 0.25rem 0.5rem;
  border-radius: 3px;
  text-transform: uppercase;
}

.log-entry.info .log-level {
  background: #17a2b8;
  color: white;
}

.log-entry.warning .log-level {
  background: #ffc107;
  color: #212529;
}

.log-entry.error .log-level {
  background: #dc3545;
  color: white;
}

.log-actions {
  text-align: center;
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
  .admin-dashboard {
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
  
  .system-overview {
    grid-template-columns: 1fr;
  }
  
  .dashboard-header h1 {
    font-size: 2rem;
  }
  
  .metric-row {
    flex-direction: column;
    align-items: stretch;
    gap: 0.5rem;
  }
  
  .metric-name {
    min-width: auto;
  }
  
  .metric-value {
    text-align: left;
  }
}
</style>
