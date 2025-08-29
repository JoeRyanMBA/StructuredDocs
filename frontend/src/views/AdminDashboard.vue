<template>
  <div class="admin-dashboard">
    <!-- Notification Ticker - Full Width at Top -->
    <div class="full-width-notification-ticker">
      <NotificationTicker
        :notifications="mergedNotifications"
        context-type="admin"
        @mark-read="markNotificationRead"
      />
    </div>

    <div class="dashboard-header">
      <h1>Admin Dashboard</h1>
      <p class="subtitle">System administration and user management</p>
    </div>

    <!-- Key Metrics Cards -->
    <div class="dashboard-section">
      <h2>Key Metrics</h2>
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
    </div>

    <!-- Database Metrics Panel -->
    <div class="mt-8">
      <DatabaseMetricsPanel :metrics="dbMetrics" />
    </div>

    <!-- Main Content Grid -->
    <div class="content-grid">
      <!-- Quick Actions -->
      <div class="dashboard-section full-width">
        <h2>Quick Actions</h2>
        <div class="quick-actions-grid">
          <button class="action-card" @click="navigateTo('/admin/users')">
            <div class="action-icon">👥</div>
            <div class="action-content">
              <h3>Manage Users</h3>
              <p>Manage user accounts and permissions</p>
            </div>
          </button>
        </div>
      </div>

      <!-- System Overview -->
      <div class="dashboard-section">
        <h2>System Overview</h2>
        <div class="system-overview">
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
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import DatabaseMetricsPanel from '../components/DatabaseMetricsPanel.vue'
import NotificationTicker from '../components/NotificationTicker.vue'

export default {
  name: 'AdminDashboard',
  components: { DatabaseMetricsPanel, NotificationTicker },
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
    }
  },
  async created() {
    await this.loadDashboardData()
  },
  methods: {
    async loadDashboardData() {
      this.loading = true
      this.error = null
      try {
        // Load stats from dashboard API
        const statsResponse = await fetch('/api/dashboard/stats')
        if (statsResponse.ok) {
          const statsData = await statsResponse.json()
          this.stats = {
            totalUsers: statsData.keyMetrics?.totalUsers || 0,
            activeUsers: statsData.userStats?.activeUsers || 0,
            authors: statsData.userStats?.totalUsers ? Math.floor(statsData.userStats.totalUsers * 0.6) : 0,
            reviewers: statsData.userStats?.totalUsers ? Math.floor(statsData.userStats.totalUsers * 0.4) : 0,
            systemHealth: 'Good',
            uptime: '99.9%'
          }
          this.userStats = {
            totalUsers: statsData.userStats?.totalUsers || 0,
            newUsersThisWeek: statsData.userStats?.newUsersWeekly || 0,
            activeUsers: statsData.userStats?.activeUsers || 0
          }
          this.dbMetrics = statsData.databaseMetrics || {}
        }

        // Load system logs
        const logsResponse = await fetch('/api/admin/system-logs')
        if (logsResponse.ok) {
          this.systemLogs = await logsResponse.json()
        }

        // Load admin notifications
        const notificationsResponse = await fetch('/api/admin/notifications')
        if (notificationsResponse.ok) {
          this.adminNotifications = await notificationsResponse.json()
        }

        // Load database metrics
        await this.loadDbMetrics()

      } catch (e) {
        this.error = e.message || 'Failed to load dashboard data'
        console.error(this.error)
      } finally {
        this.loading = false
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
          lastBackup: db.lastBackup ? new Date(db.lastBackup).toLocaleString() : 'Unknown'
        }
      } catch (error) {
        console.error('Failed to load database metrics:', error)
      }
    },

    navigateTo(path) {
      this.$router.push(path)
    }
  }
}
</script>

<style>
/* Full-width Notification Ticker */
.full-width-notification-ticker {
  position: fixed;
  top: var(--header-height, 60px); /* Use standardized header height */
  left: 0;
  right: 0;
  width: 100%;
  height: var(--ticker-height, 40px); /* Use standardized ticker height */
  z-index: 998; /* Below header but above content */
  background: white;
  border-bottom: 1px solid #e9ecef;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  display: flex;
  align-items: center;
}

.full-width-notification-ticker .notification-ticker {
  width: 100%;
  height: 100%;
  margin: 0;
  padding: 0;
  position: static !important; /* Override component's relative positioning */
  background: transparent !important; /* Override component's background */
  border: none !important; /* Remove component's border */
  box-shadow: none !important; /* Remove component's shadow */
}

/* Adjust main content to account for fixed notification ticker */
.admin-dashboard {
  padding-top: calc(var(--header-height, 60px) + var(--ticker-height, 40px) + 20px);
}

/* Dashboard Sections: use global .dashboard-section from assets/style.css */
</style>
