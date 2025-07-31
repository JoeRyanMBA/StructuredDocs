<template>
  <div class="import-dashboard">
    <div class="dashboard-header">
      <h1>Import Dashboard</h1>
      <p class="welcome-text">Import and manage your document imports</p>
    </div>

    <!-- Key Metrics Cards -->
    <div class="metrics-grid">
      <div class="metric-card">
        <div class="metric-icon">📥</div>
        <div class="metric-content">
          <h3>Total Imports</h3>
          <div class="metric-number">{{ stats.total || 0 }}</div>
          <div class="metric-detail">All time</div>
        </div>
      </div>

      <div class="metric-card">
        <div class="metric-icon">⏳</div>
        <div class="metric-content">
          <h3>Pending Review</h3>
          <div class="metric-number">{{ stats.pending || 0 }}</div>
          <div class="metric-detail">Need approval</div>
        </div>
      </div>

      <div class="metric-card">
        <div class="metric-icon">✅</div>
        <div class="metric-content">
          <h3>Approved</h3>
          <div class="metric-number">{{ stats.approved || 0 }}</div>
          <div class="metric-detail">This month</div>
        </div>
      </div>

      <div class="metric-card">
        <div class="metric-icon">🆕</div>
        <div class="metric-content">
          <h3>This Week</h3>
          <div class="metric-number">{{ stats.thisWeek || 0 }}</div>
          <div class="metric-detail">New imports</div>
        </div>
      </div>
    </div>

    <!-- Main Content Grid -->
    <div class="content-grid">
      
      <!-- Quick Actions -->
      <div class="dashboard-section">
        <h2>Quick Actions</h2>
        <div class="quick-actions-grid">
          <button class="action-card" @click="startNewImport">
            <div class="action-icon">📥</div>
            <div class="action-content">
              <h3>Import New Document</h3>
              <p>Upload and process new content</p>
            </div>
          </button>
          <button class="action-card" @click="navigateTo('/import/history')">
            <div class="action-icon">📋</div>
            <div class="action-content">
              <h3>View Import History</h3>
              <p>Review past import activities</p>
            </div>
          </button>
          <button class="action-card" @click="navigateTo('/topics')">
            <div class="action-icon">📝</div>
            <div class="action-content">
              <h3>Browse Topics</h3>
              <p>Explore imported content</p>
            </div>
          </button>
        </div>
      </div>

      <!-- Pending Reviews -->
      <div class="dashboard-section">
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

    reviewImport(importDoc) {
      this.$router.push(`/import/${importDoc.id}/review`)
    },

    viewImport(importDoc) {
      this.$router.push(`/import/${importDoc.id}`)
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
  padding-top: 0;
  padding-right: 2rem;
  padding-bottom: 2rem;
  padding-left: 2rem;
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

/* Action Buttons */
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
  background: #005a9c;
  border-color: #005a9c;
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

/* Import Items */
.pending-list {
  max-height: 400px;
  overflow-y: auto;
}

.import-item {
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

.import-item:hover {
  border-color: #005a9c;
  background: #f8f9fa;
}

.import-item.urgent {
  border-color: #ffc107;
  background: #fff9e6;
}

.import-item:last-child {
  margin-bottom: 0;
}

.import-icon {
  font-size: 1.5rem;
  min-width: 30px;
}

.import-content {
  flex: 1;
}

.import-title {
  font-weight: 600;
  color: #495057;
  margin-bottom: 0.25rem;
}

.import-description {
  color: #6c757d;
  font-size: 0.875rem;
  margin-bottom: 0.25rem;
}

.import-meta {
  color: #adb5bd;
  font-size: 0.75rem;
}

.import-status {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.7rem;
  font-weight: 500;
  text-transform: uppercase;
}

.import-status.pending {
  background: #fff3cd;
  color: #856404;
}

/* Import Cards */
.imports-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
}

.import-card {
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.2s ease;
  background: white;
}

.import-card:hover {
  border-color: #005a9c;
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

.card-status.staging {
  background: #fff3cd;
  color: #856404;
}

.card-status.approved {
  background: #d4edda;
  color: #155724;
}

.card-status.rejected {
  background: #f8d7da;
  color: #721c24;
}

.card-status.completed {
  background: #d1ecf1;
  color: #0c5460;
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
  border-color: #005a9c;
  background: #f8f9fa;
}

.card-action-btn.primary {
  background: #005a9c;
  color: white;
  border-color: #005a9c;
}

.card-action-btn.primary:hover {
  background: #004080;
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
  color: #005a9c;
  text-decoration: underline;
  cursor: pointer;
  padding: 0;
  font-size: inherit;
}

.link-btn:hover {
  color: #004080;
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
  .import-dashboard {
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
  
  .imports-list {
    grid-template-columns: 1fr;
  }
  
  .dashboard-header h1 {
    font-size: 2rem;
  }
}
</style>
