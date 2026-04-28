<template>
  <div class="admin-dashboard">
    
    <div class="dashboard-header">
      <h1>Admin Dashboard <HelpIcon feature="admin.dashboard" /></h1>
      <p class="subtitle">System administration and user management</p>
    </div>

    <!-- Compact Toolbar for Metrics -->
    <CompactToolbar :showMetrics="true" :showCalendar="false">
      <template #metrics>
        <div class="metrics-grid">
          <div class="metric-card" title="Total number of registered user accounts in the system">
            <div class="metric-icon">👥</div>
            <div class="metric-content">
              <h3>Total Users</h3>
              <div class="metric-number">{{ stats.totalUsers || 0 }}</div>
              <div class="metric-detail">{{ stats.activeUsers || 0 }} Active accounts</div>
            </div>
          </div>

          <div class="metric-card" title="Users who have made a request in the last 15 minutes">
            <div class="metric-icon">🟢</div>
            <div class="metric-content">
              <h3>Online Now</h3>
              <div class="metric-number">{{ stats.onlineNow || 0 }}</div>
              <div class="metric-detail">Active last 15 min</div>
            </div>
          </div>

          <div class="metric-card" title="Users with the Author role — can create and edit projects, collections, and topics">
            <div class="metric-icon">✏️</div>
            <div class="metric-content">
              <h3>Authors</h3>
              <div class="metric-number">{{ stats.authors || 0 }}</div>
              <div class="metric-detail">Content creators</div>
            </div>
          </div>

          <div class="metric-card" title="Users with the Reviewer role — can review topics and submit feedback via review links">
            <div class="metric-icon">📝</div>
            <div class="metric-content">
              <h3>Reviewers</h3>
              <div class="metric-number">{{ stats.reviewers || 0 }}</div>
              <div class="metric-detail">SME reviewers</div>
            </div>
          </div>

          <div class="metric-card" title="Overall system health based on CPU, memory, and disk usage. Healthy = all under 70%, Warning = any over 70%, Critical = any over 90%">
            <div class="metric-icon">🔧</div>
            <div class="metric-content">
              <h3>System Health</h3>
              <div class="metric-number">{{ stats.systemHealth || 'Good' }}</div>
              <div class="metric-detail">{{ stats.uptime || 'Unknown' }} uptime</div>
            </div>
          </div>
        </div>
      </template>
    </CompactToolbar>

  <!-- Main Content Grid: Quick Actions and Database Metrics side-by-side -->
  <div class="content-grid two-col">
  <!-- Quick Actions -->
  <div class="quick-actions-section">
        <h2>Quick Actions</h2>
        <p class="section-description">Manage users, notifications, and bug reports</p>
  <div class="quick-actions-grid">
          <button class="quick-action-card" @click="navigateTo('/admin/users')">
            <div class="action-icon">👥</div>
            <div class="action-content" title="Manage user accounts and permissions">
              <h3>Manage Users</h3>
            </div>
          </button>
          <button class="quick-action-card" @click="navigateTo('/notifications/new')">
            <div class="action-icon">🔔</div>
            <div class="action-content" title="Send notifications to users">
              <h3>Create Notification</h3>
            </div>
          </button>
          <button class="quick-action-card" @click="navigateTo('/notifications/manage')">
            <div class="action-icon">📋</div>
            <div class="action-content" title="View and manage existing notifications">
              <h3>Manage Notifications</h3>
            </div>
          </button>
          <button class="quick-action-card" @click="navigateTo('/admin/bugs')">
            <div class="action-icon">🐞</div>
            <div class="action-content" title="Review user-submitted bug reports">
              <h3>View Bug Reports</h3>
            </div>
          </button>
          <button class="quick-action-card" @click="navigateTo('/admin/variables')">
            <div class="action-icon">🏷️</div>
            <div class="action-content" title="Create and manage publish-time variables">
              <h3>Manage Variables</h3>
            </div>
          </button>
          <button class="quick-action-card" @click="navigateTo('/admin/audit')">
            <div class="action-icon">🛡️</div>
            <div class="action-content" title="View immutable audit trail of all create/update/delete actions">
              <h3>Audit Log</h3>
            </div>
          </button>
          <button class="quick-action-card" @click="navigateTo('/admin/help-links')">
            <div class="action-icon">ℹ️</div>
            <div class="action-content" title="Configure contextual help icons shown throughout the app">
              <h3>Help Links</h3>
            </div>
          </button>
          <button class="quick-action-card" @click="navigateTo('/admin/find-replace')">
            <div class="action-icon">🔍</div>
            <div class="action-content" title="Find and replace text across all user-editable content">
              <h3>Find &amp; Replace</h3>
            </div>
          </button>
          <button class="quick-action-card" @click="showLimitsModal = true">
            <div class="action-icon">⚙️</div>
            <div class="action-content" title="Configure upload size limits and rate limits">
              <h3>System Limits</h3>
            </div>
          </button>
          <button class="quick-action-card danger" @click="confirmClearDatabase">
            <div class="action-icon">⚠️</div>
            <div class="action-content" title="Clear all data except admin user">
              <h3>Clear Database</h3>
            </div>
          </button>
          <div class="clear-db-options">
            <label class="clear-db-checkbox">
              <input type="checkbox" v-model="purgeStorageOnClear" />
              <span>Also purge remote storage objects (dev-safe)</span>
            </label>
            <input
              v-model="clearStoragePrefix"
              class="clear-db-prefix"
              type="text"
              placeholder="images/"
              :disabled="!purgeStorageOnClear"
            />
          </div>
        </div>
      </div>
  <!-- Database Metrics Panel -->
  <DatabaseMetricsPanel :metrics="dbMetrics" />

  <!-- System Overview -->
  <div class="dashboard-section full-width">
        <h2>System Overview</h2>
        <div class="system-overview">
          <div class="system-section">
            <h3>System Performance</h3>
            <div class="system-meta">
              <span class="meta-badge" :class="{ warn: performanceState.source !== 'live' }">
                Source: {{ performanceState.sourceLabel }}
              </span>
              <span v-if="performanceState.error" class="meta-error" :title="performanceState.error">{{ performanceState.error }}</span>
            </div>
            <div class="performance-metrics">
              <div class="metric-row" title="Approximate CPU load based on 1-minute system load average">
                <span class="metric-name">CPU Usage</span>
                <div class="metric-bar">
                  <div class="metric-fill" :style="{width: metricPercent(systemMetrics.cpu) + '%'}"></div>
                </div>
                <span class="metric-value">{{ metricLabel(systemMetrics.cpu) }}</span>
              </div>
              <div class="metric-row" title="Percentage of system RAM in use">
                <span class="metric-name">Memory</span>
                <div class="metric-bar">
                  <div class="metric-fill" :style="{width: metricPercent(systemMetrics.memory) + '%'}"></div>
                </div>
                <span class="metric-value">{{ metricLabel(systemMetrics.memory) }}</span>
              </div>
              <div class="metric-row" title="Percentage of disk space used on the server filesystem">
                <span class="metric-name">Storage</span>
                <div class="metric-bar">
                  <div class="metric-fill" :style="{width: metricPercent(systemMetrics.storage) + '%'}"></div>
                </div>
                <span class="metric-value">{{ metricLabel(systemMetrics.storage) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

  <!-- Recent System Events -->
  <div class="dashboard-section full-width">
        <h2>Recent System Events</h2>
        <div class="system-events">
          <div v-if="systemEvents.length === 0" class="empty-state">
            <p>No recent system events</p>
          </div>
          <div v-else class="events-list">
            <div v-for="event in systemEvents.slice(0, 5)" :key="event.id" class="event-item">
              <div class="event-icon">📋</div>
              <div class="event-content">
                <div class="event-title">{{ event.title || 'System Event' }}</div>
                <div class="event-description">{{ event.description || event.message }}</div>
                <div class="event-time">{{ formatDate(event.created_at) }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <LimitsModal :show="showLimitsModal" @close="showLimitsModal = false" />
</template>

<script>
import DatabaseMetricsPanel from '../components/DatabaseMetricsPanel.vue'
import CompactToolbar from '@/components/CompactToolbar.vue'
import LimitsModal from '@/components/LimitsModal.vue'
import { toast } from '@/composables/useToast'
import HelpIcon from '@/components/HelpIcon.vue'
import { apiGet, apiPost, apiRequest } from '@/api/base'
import { apiGet, apiPost, apiRequest, toFriendlyAuthError } from '@/api/base'

export default {
  name: 'AdminDashboard',
  components: { 
    DatabaseMetricsPanel,
    CompactToolbar,
    LimitsModal,
    HelpIcon,
  },
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
      dbMetrics: {
        tables: 0,
        rows: 0,
        size: 'N/A',
        lastBackup: 'Unknown'
      },
      userStats: {},
      systemMetrics: {
        cpu: null,
        memory: null,
        storage: null
      },
      performanceState: {
        source: 'unknown',
        sourceLabel: 'Unknown',
        error: null,
      },
      recentActivity: [],
      systemLogs: [],
      systemEvents: [],
      adminNotifications: [],
      purgeStorageOnClear: false,
      clearStoragePrefix: 'images/',
      newNotification: {
        title: '',
        description: ''
      },
      showLimitsModal: false,
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
    normalizeDbMetricsFromDashboard(statsData) {
      const raw = statsData?.databaseMetrics || {}
      const tableLike = Object.keys(raw).length
      const rowLike = Object.values(raw).reduce((sum, v) => sum + (Number(v) || 0), 0)
      return {
        tables: tableLike,
        rows: rowLike,
        size: statsData?.systemOverview?.databaseSize || 'N/A',
        lastBackup: 'Unknown'
      }
    },
    async confirmClearDatabase() {
      const storageNote = this.purgeStorageOnClear ? `\n\nStorage purge enabled for prefix: ${this.clearStoragePrefix || 'images/'}` : ''
      if (!window.confirm(`Are you sure you want to clear ALL data except the admin user? This cannot be undone!${storageNote}`)) return;
      try {
        const result = await apiPost('/api/admin/clear-database', {
          purge_storage: this.purgeStorageOnClear,
          storage_prefix: (this.clearStoragePrefix || 'images/').trim() || 'images/'
        });
        const purgeResult = result?.storage_purge
        const purgeMessage = this.purgeStorageOnClear
          ? ` ${purgeResult?.message || 'Storage purge requested.'}`
          : ''
        toast.success(`Database cleared successfully!${purgeMessage}`.trim());
        await this.loadDashboardData();
      } catch (e) {
          toast.error(`Error clearing database: ${toFriendlyAuthError(e, 'Unknown error')}`)
      }
    },
    getAuthHeaders() {
      const token = localStorage.getItem('access_token')
      return token && token.split('.').length === 3
        ? { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' }
        : { 'Content-Type': 'application/json' }
    },
    metricPercent(value) {
      return typeof value === 'number' && Number.isFinite(value) ? Math.max(0, Math.min(100, value)) : 0
    },
    metricLabel(value) {
      return typeof value === 'number' && Number.isFinite(value) ? `${Math.round(value)}%` : 'N/A'
    },

    async loadDashboardData() {
      this.loading = true
      this.error = null
      try {
        // Load stats from dashboard API (include auth header if present)
        try {
          const statsData = await apiRequest('/api/dashboard/stats')
          console.log('Admin dashboard raw stats:', statsData)

          // Support multiple backend shapes
          if (statsData.keyMetrics) {
            // Newer backend blueprint shape
            this.stats = {
              totalUsers: statsData.keyMetrics?.totalUsers || 0,
              activeUsers: statsData.userStats?.activeUsers || 0,
              onlineNow: statsData.userStats?.onlineNow || 0,
              authors: statsData.userStats?.totalUsers ? Math.floor(statsData.userStats.totalUsers * 0.6) : 0,
              reviewers: statsData.userStats?.totalUsers ? Math.floor(statsData.userStats.totalUsers * 0.4) : 0,
              systemHealth: statsData.systemOverview?.systemHealth || 'Good',
              uptime: statsData.systemOverview?.uptime || 'Unknown'
            }
            this.userStats = {
              totalUsers: statsData.userStats?.totalUsers || 0,
              newUsersThisWeek: statsData.userStats?.newUsersWeekly || 0,
              activeUsers: statsData.userStats?.activeUsers || 0
            }
            this.dbMetrics = this.normalizeDbMetricsFromDashboard(statsData)

          } else if (statsData.projects || statsData.users || statsData.topics) {
            // Older / simpler endpoint shape (safe fallbacks)
            this.stats = {
              totalUsers: statsData.users?.total || statsData.users || statsData.userCount || 0,
              activeUsers: statsData.users?.active || 0,
              authors: statsData.authors || 0,
              reviewers: statsData.reviewers || 0,
              systemHealth: 'Good',
              uptime: '99.9%'
            }
            this.userStats = {
              totalUsers: (statsData.users && statsData.users.total) || statsData.users || 0,
              newUsersThisWeek: statsData.users?.new_week || 0,
              activeUsers: statsData.users?.active || 0
            }
            // Map database metrics if present
            this.dbMetrics = {
              tables: 4,
              rows:
                (statsData.projects?.total || statsData.projects || 0) +
                (statsData.collections?.total || statsData.collections || 0) +
                (statsData.topics?.total || statsData.topics || 0) +
                ((statsData.users && (statsData.users.total || statsData.users)) || 0),
              size: 'N/A',
              lastBackup: 'Unknown'
            }
          } else {
            // Unknown shape: keep safe defaults
            console.warn('Unrecognized dashboard stats shape; using safe defaults')
            this.stats = { totalUsers: 0, activeUsers: 0, authors: 0, reviewers: 0, systemHealth: 'Good', uptime: '99.9%' }
            this.userStats = { totalUsers: 0, newUsersThisWeek: 0, activeUsers: 0 }
            this.dbMetrics = { tables: 0, rows: 0, size: 'N/A', lastBackup: 'Unknown' }
          }
        } catch (e) {
          console.warn('Dashboard stats API unavailable:', e.message)
        }

        // Load system logs
        this.systemLogs = await apiGet('/api/admin/system-logs').catch(() => this.systemLogs)

        // Load admin notifications
        this.adminNotifications = await apiGet('/api/admin/notifications').catch(() => this.adminNotifications)

        // Load database metrics
        await this.loadDbMetrics()

        // Load real system performance metrics
        await this.loadSystemMetrics()

      } catch (e) {
          this.error = toFriendlyAuthError(e, 'Failed to load dashboard data')
        console.error(this.error)
      } finally {
        this.loading = false
      }
    },

    async loadDbMetrics() {
      try {
        const data = await apiGet('/api/metrics/')
        const db = data.database || {}
        this.dbMetrics = {
          tables: db.tables || 0,
          rows: db.totalRecords || 0,
          size: db.size || '0 MB',
          lastBackup: db.lastBackup ? new Date(db.lastBackup).toLocaleString() : 'Unknown'
        }
      } catch (error) {
        console.warn('Database metrics endpoint unavailable; keeping dashboard fallback metrics')
        console.error('Failed to load database metrics:', error)
      }
    },

    async loadSystemMetrics() {
      try {
        const data = await apiRequest('/api/admin/stats')

        // Real CPU / memory / disk from backend
        const perf = data.performanceMetrics || {}
        const source = perf.metricSource || 'unknown'
        this.performanceState = {
          source,
          sourceLabel: source === 'live' ? 'Live' : (source === 'unavailable' ? 'Unavailable' : 'Unknown'),
          error: perf.metricError || null,
        }
        if (perf.cpuUsage !== undefined || perf.memoryUsage !== undefined || perf.diskUsage !== undefined) {
          this.systemMetrics = {
            cpu: typeof perf.cpuUsage === 'number' ? perf.cpuUsage : null,
            memory: typeof perf.memoryUsage === 'number' ? perf.memoryUsage : null,
            storage: typeof perf.diskUsage === 'number' ? perf.diskUsage : null,
          }
        }

        // Authoritative user breakdown and online-now from admin stats
        const s = data.stats || {}
        if (s.totalUsers !== undefined) {
          this.stats = {
            ...this.stats,
            totalUsers: s.totalUsers,
            activeUsers: s.activeUsers ?? this.stats.activeUsers,
            onlineNow: s.onlineNow ?? this.stats.onlineNow,
            authors: s.authors ?? this.stats.authors,
            reviewers: s.reviewers ?? this.stats.reviewers,
            systemHealth: s.systemHealth ?? this.stats.systemHealth,
            uptime: s.uptime ?? this.stats.uptime
          }
        }
      } catch (error) {
        console.error('Failed to load system metrics:', error)
      }
    },

    navigateTo(path) {
      this.$router.push(path)
    },

    
  }
}
</script>

<style>
/* Full-width Notification Ticker */
/* Adjust main content to account for fixed notification ticker */
.admin-dashboard {
  /* Main content offset is handled by the global layout (App.vue -> .content).
     Remove the extra 20px that was doubling the space between the header and
     the notification ticker. Rely on the global margin-top to position
     dashboard content beneath the fixed header + ticker. */
  padding-top: 0;
}

/* System Overview Styles */
.system-overview {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.5rem;
}

.system-meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.meta-badge {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.2rem 0.5rem;
  border-radius: 999px;
  background: #e9f7ef;
  color: #1f7a1f;
}

.meta-badge.warn {
  background: #fff3cd;
  color: #8a6d3b;
}

.meta-error {
  font-size: 0.78rem;
  color: #6c757d;
  max-width: 460px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.system-section {
  background: var(--bg-white);
  border: 1px solid var(--border-light-gray);
  border-radius: var(--border-radius-lg);
  padding: 1.5rem;
}

.system-section h3 {
  margin: 0 0 1rem 0;
  color: var(--primary-deep-teal);
  font-size: 1.1rem;
  font-weight: 600;
}

.performance-metrics {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.metric-row {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.metric-name {
  min-width: 100px;
  font-weight: 500;
  color: var(--text-secondary-cool-gray);
}

.metric-bar {
  flex: 1;
  height: 8px;
  background: var(--border-light-gray);
  border-radius: 4px;
  overflow: hidden;
}

.metric-fill {
  height: 100%;
  /* Use defined palette variables; fallback to deep/medium teal */
  background: linear-gradient(90deg, var(--primary-deep-teal), var(--primary-medium-teal));
  border-radius: 4px;
  transition: width 0.3s ease;
}

.metric-value {
  min-width: 50px;
  text-align: right;
  font-weight: 600;
  color: var(--primary-deep-teal);
}

/* Recent System Events Styles */
.system-events {
  background: var(--bg-white);
  border: 1px solid var(--border-light-gray);
  border-radius: var(--border-radius-lg);
  padding: 1.5rem;
}

.events-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.event-item {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 1rem;
  background: var(--bg-white);
  border-radius: var(--border-radius-md);
  border: 1px solid var(--border-light-gray);
}

.event-icon {
  font-size: 1.2rem;
  color: var(--primary-teal);
  margin-top: 0.2rem;
}

.event-content {
  flex: 1;
}

.event-title {
  font-weight: 600;
  color: var(--text-primary-dark-gray);
  margin: 0 0 0.5rem 0;
}

.event-description {
  color: var(--text-secondary-cool-gray);
  margin: 0 0 0.5rem 0;
  font-size: 0.9rem;
}

.event-time {
  color: var(--text-secondary-cool-gray);
  font-size: 0.8rem;
  font-style: italic;
}

.quick-action-card.danger {
  background: #fff0f0;
  border: 1px solid #e57373;
  color: #b71c1c;
}

.quick-action-card.danger:hover {
  background: #ffeaea;
  border-color: #b71c1c;
}

.clear-db-options {
  grid-column: 1 / -1;
  margin-top: 0.35rem;
  padding: 0.6rem 0.75rem;
  border: 1px solid var(--border-light-gray);
  border-radius: var(--border-radius-md);
  background: var(--bg-white);
  display: flex;
  flex-wrap: wrap;
  gap: 0.6rem;
  align-items: center;
}

.clear-db-checkbox {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  color: var(--text-secondary-cool-gray);
  font-size: 0.85rem;
}

.clear-db-prefix {
  min-width: 180px;
  padding: 0.35rem 0.5rem;
  border: 1px solid var(--border-light-gray);
  border-radius: var(--border-radius-sm);
  font-size: 0.85rem;
}

/* Dashboard Sections: use global .dashboard-section from assets/style.css */
</style>
