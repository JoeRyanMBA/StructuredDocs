<template>
  <div class="import-dashboard">
    <div class="dashboard-header">
      <h1>Import Dashboard</h1>
      <p class="subtitle">Import and manage your document imports</p>
    </div>

    <!-- Key Metrics Cards -->
    <div class="dashboard-section">
      <h2>Key Metrics</h2>
      <div class="metrics-grid">
      <div class="metric-card">
        <div class="metric-icon">📥</div>
        <div class="metric-content">
          <h3>Total Imports</h3>
            <div class="metric-number">{{ stats.total || 0 }}</div> <!-- metric-number now centralized in global style.css -->
            <div class="metric-detail">All time</div> <!-- metric-detail now centralized in global style.css -->
        </div>
      </div>

      <div class="metric-card">
        <div class="metric-icon">⏳</div>
        <div class="metric-content">
          <h3>Pending Review</h3>
            <div class="metric-number">{{ stats.pending || 0 }}</div> <!-- metric-number now centralized in global style.css -->
            <div class="metric-detail">Need approval</div> <!-- metric-detail now centralized in global style.css -->
        </div>
      </div>

      <div class="metric-card">
        <div class="metric-icon">✅</div>
        <div class="metric-content">
          <h3>Approved</h3>
            <div class="metric-number">{{ stats.approved || 0 }}</div> <!-- metric-number now centralized in global style.css -->
            <div class="metric-detail">This month</div> <!-- metric-detail now centralized in global style.css -->
        </div>
      </div>

      <div class="metric-card">
        <div class="metric-icon">🆕</div>
        <div class="metric-content">
          <h3>This Week</h3>
            <div class="metric-number">{{ stats.thisWeek || 0 }}</div> <!-- metric-number now centralized in global style.css -->
            <div class="metric-detail">New imports</div> <!-- metric-detail now centralized in global style.css -->
        </div>
      </div>
      </div>
    </div>

    <!-- Quick Actions Section (Start Page style) -->
    <div class="quick-actions-section">
      <h2>Quick Actions</h2>
      <div class="quick-actions-grid">
          <button class="quick-action-card" @click="startNewImport">
            <div class="action-icon">📥</div>
            <div class="action-content" title="Upload and process new content">
              <h3>Import New Document</h3>
            </div>
          </button>
          <button class="quick-action-card" @click="navigateTo('/import/history')">
            <div class="action-icon">📋</div>
            <div class="action-content" title="Review past import activities">
              <h3>View Import History</h3>
            </div>
          </button>
          <button class="quick-action-card" @click="navigateTo('/topics')">
            <div class="action-icon">📝</div>
            <div class="action-content" title="Explore imported content">
              <h3>Browse Topics</h3>
            </div>
          </button>
      </div>
    </div>

    <!-- Main Content Grid -->
    <div class="content-grid">

      <!-- Pending Reviews -->
      <div class="dashboard-section full-width">
        <h2>Pending Reviews</h2>
        <div class="pending-list">
          <div v-if="pendingImports.length === 0" class="empty-state">
            <p>No imports pending review 🎉</p>
          </div>
          <div v-else>
            <div 
              v-for="importDoc in pendingImports" 
              :key="importDoc.id"
              class="import-item urgent"
              @click="reviewImport(importDoc)"
            >
              <div class="import-icon">📥</div>
              <div class="import-content">
                <div class="import-title">{{ importDoc.filename }}</div>
                <div class="import-description">{{ importDoc.topics_count || 0 }} topics imported</div>
                <div class="import-meta">{{ formatRelativeTime(importDoc.created_at) }}</div>
              </div>
              <div class="import-status pending">Pending</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Recent Imports -->
  <div class="dashboard-section full-width">
        <h2>Recent Import Activity</h2>
        <div class="imports-overview">
          <div v-if="recentImports.length === 0" class="empty-state">
            <p>No recent imports. <button @click="startNewImport" class="link-btn">Start your first import</button></p>
          </div>
          <div v-else class="imports-list">
            <div 
              v-for="importDoc in recentImports" 
              :key="importDoc.id"
              class="import-card"
              @click="viewImport(importDoc)"
            >
              <div class="card-header">
                <div class="card-title">
                  <h3>{{ importDoc.filename }}</h3>
                  <span class="card-badge">{{ importDoc.topics_count || 0 }} topics</span>
                </div>
                <span class="card-status" :class="importDoc.status">{{ formatStatus(importDoc.status) }}</span>
              </div>
              <div class="card-content">
                <p class="card-description">
                  Imported {{ formatRelativeTime(importDoc.created_at) }}
                  <span v-if="importDoc.collection_name"> into {{ importDoc.collection_name }}</span>
                </p>
                <div class="card-metrics">
                  <span class="card-metric">
                    <span class="metric-label">Size:</span>
                    {{ formatFileSize(importDoc.file_size) }}
                  </span>
                  <span class="card-metric">
                    <span class="metric-label">Type:</span>
                    {{ importDoc.file_type || 'Unknown' }}
                  </span>
                  <span class="card-metric">
                    <span class="metric-label">Status:</span>
                    {{ formatStatus(importDoc.status) }}
                  </span>
                </div>
              </div>
              <div class="card-footer">
                <span class="card-date">{{ formatRelativeTime(importDoc.updated_at || importDoc.created_at) }}</span>
                <div class="card-actions">
                  <button 
                    v-if="importDoc.status === 'staging'" 
                    @click.stop="reviewImport(importDoc)" 
                    class="card-action-btn primary"
                  >
                    Review
                  </button>
                  <button @click.stop="viewImport(importDoc)" class="card-action-btn">View</button>
                  <button @click.stop="deleteImport(importDoc)" class="card-action-btn btn-danger">Delete</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-overlay">
      <div class="loading-spinner">Loading import data...</div>
    </div>
  </div>
</template>

<script>

export default {
  name: 'ImportDashboard',
  components: { },
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
        approved: 0,
        thisWeek: 0
      },
      pendingImports: [],
      recentImports: []
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
          this.loadImports(),
          this.loadStats()
        ])
      } catch (error) {
        console.error('Failed to load import dashboard:', error)
      } finally {
        this.loading = false
      }
    },

    async loadImports() {
      try {
        const res = await fetch('/api/import/history')
        if (res.ok) {
          const imports = await res.json()
          
          // Get pending imports
          this.pendingImports = imports.filter(imp => imp.status === 'staging').slice(0, 5)
          
          // Get recent imports (last 10, sorted by created_at)
          this.recentImports = imports
            .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
            .slice(0, 10)
            
          // Calculate stats
          this.calculateStats(imports)
        }
      } catch (error) {
        console.error('Failed to load imports:', error)
      }
    },

    async loadStats() {
      // Stats are calculated in loadImports for efficiency
    },

    calculateStats(imports) {
      const total = imports.length
      const pending = imports.filter(imp => imp.status === 'staging').length
      
      // Count approved this month
      const oneMonthAgo = new Date()
      oneMonthAgo.setMonth(oneMonthAgo.getMonth() - 1)
      const approved = imports.filter(imp => 
        imp.status === 'approved' && 
        imp.updated_at && 
        new Date(imp.updated_at) > oneMonthAgo
      ).length

      // Count imports this week
      const oneWeekAgo = new Date()
      oneWeekAgo.setDate(oneWeekAgo.getDate() - 7)
      const thisWeek = imports.filter(imp => 
        imp.created_at && new Date(imp.created_at) > oneWeekAgo
      ).length

      this.stats = {
        total,
        pending,
        approved,
        thisWeek
      }
    },

    startNewImport() {
      this.$router.push('/import')
    },

    async reviewImport(importDoc) {
      // Persist review action to backend before navigating
      try {
        const res = await fetch(`/api/import/${importDoc.id}/review`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ status: 'reviewed' })
        })
        if (!res.ok) throw new Error('Failed to persist review')
        // Optionally reload imports to update UI
        await this.loadImports()
      } catch (err) {
        console.error('Error persisting review:', err)
      }
      this.$router.push(`/import/${importDoc.id}/review`)
    },

    async viewImport(importDoc) {
      // Optionally, mark as viewed in backend (if needed)
      this.$router.push(`/import/${importDoc.id}/review`)
    },

    async deleteImport(importDoc) {
      // Persist delete action to backend
      if (!confirm('Are you sure you want to delete this import?')) return
      try {
        const res = await fetch(`/api/import/${importDoc.id}`, {
          method: 'DELETE'
        })
        if (!res.ok) throw new Error('Failed to delete import')
        await this.loadImports()
      } catch (err) {
        console.error('Error deleting import:', err)
      }
    },

    navigateTo(path) {
      this.$router.push(path)
    },

    formatStatus(status) {
      const statusMap = {
        'staging': 'Pending Review',
        'approved': 'Approved',
        'rejected': 'Rejected',
        'processing': 'Processing',
        'completed': 'Completed',
        'failed': 'Failed'
      }
      return statusMap[status] || status
    },

    formatFileSize(bytes) {
      if (!bytes) return 'Unknown'
      
      const sizes = ['Bytes', 'KB', 'MB', 'GB']
      if (bytes === 0) return '0 Bytes'
      
      const i = Math.floor(Math.log(bytes) / Math.log(1024))
      return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i]
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
.import-dashboard {
  margin: 0 auto;
  padding: 2rem;
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

.welcome-text {
  color: var(--text-secondary-cool-gray);
  font-size: 1.1rem;
  margin: 0;
}

/* Metrics Grid */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 3rem;
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

/* Dashboard Sections: use global .dashboard-section from style.css */



/* Action Buttons */
/* Quick Actions */
.quick-actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1rem;
}

/* Pending Reviews */
.pending-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.import-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: white;
  border: 1px solid var(--extended-lavender-gray);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.import-item.urgent {
  background: var(--extended-warm-taupe);
  border-color: var(--warning-amber);
}

.import-item:hover {
  border-color: var(--primary-deep-teal);
  transform: translateY(-2px);
}

.import-icon {
  font-size: 1.5rem;
}

.import-content {
  flex: 1;
}

.import-title {
  font-weight: 600;
  color: var(--primary-deep-teal);
}

.import-description {
  color: var(--text-secondary-cool-gray);
  font-size: 0.875rem;
}

.import-meta {
  color: var(--extended-lavender-gray);
  font-size: 0.75rem;
}

.import-status {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.import-status.pending {
  background: var(--warning-amber);
  color: white;
}

/* Recent Imports */
.imports-list {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.5rem;
}

.import-card {
  background: white;
  border: 1px solid var(--extended-lavender-gray);
  border-radius: 8px;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.import-card:hover {
  border-color: var(--primary-deep-teal);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.card-title h3 {
  margin: 0;
  color: var(--primary-deep-teal);
  font-size: 1.125rem;
}

.card-badge {
  background: var(--extended-sky-blue);
  color: var(--primary-deep-teal);
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
}

.card-status {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.card-status.staging {
  background: var(--warning-amber);
  color: white;
}

.card-status.approved, .card-status.completed {
  background: var(--success-mint-green);
  color: white;
}

.card-status.failed, .card-status.rejected {
  background: var(--error-coral-red);
  color: white;
}

.card-content {
  margin-bottom: 1rem;
}

.card-description {
  color: var(--text-secondary-cool-gray);
  font-size: 0.875rem;
  margin-bottom: 1rem;
}

.card-metrics {
  display: flex;
  gap: 1.5rem;
  font-size: 0.875rem;
}

.card-metric .metric-label {
  font-weight: 600;
  color: var(--text-primary-charcoal);
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 1px solid var(--extended-lavender-gray);
  padding-top: 1rem;
}

.card-date {
  color: var(--extended-lavender-gray);
  font-size: 0.875rem;
}

.card-actions {
  display: flex;
  gap: 0.5rem;
}

.card-action-btn {
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  border: 1px solid transparent;
  transition: all 0.2s ease;
}

.card-action-btn.primary {
  background: var(--primary-deep-teal);
  color: white;
  border-color: var(--primary-deep-teal);
}

.card-action-btn.primary:hover {
  background: var(--primary-medium-teal);
}

.card-action-btn:not(.primary) {
  background: white;
  color: var(--text-primary-charcoal);
  border-color: var(--extended-lavender-gray);
}

.card-action-btn:not(.primary):hover {
  background: var(--bg-white);
  border-color: var(--text-secondary-cool-gray);
}

.empty-state {
  text-align: center;
  padding: 2rem;
  color: var(--text-secondary-cool-gray);
}

.link-btn {
  background: none;
  border: none;
  color: var(--primary-medium-teal);
  text-decoration: underline;
  cursor: pointer;
}

.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.loading-spinner {
  font-size: 1.25rem;
  color: var(--primary-deep-teal);
}

@media (max-width: 768px) {
  .content-grid {
    grid-template-columns: 1fr;
  }
}
</style>
