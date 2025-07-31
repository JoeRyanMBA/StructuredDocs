<template>
  <div class="performance-metrics">
    <div class="header">
      <h2>Performance Metrics</h2>
      <div class="header-actions">
        <button @click="refreshMetrics" class="btn btn-primary" :disabled="loading">
          <span class="icon">🔄</span>
          {{ loading ? 'Refreshing...' : 'Refresh' }}
        </button>
        <button @click="exportMetrics" class="btn btn-secondary">
          <span class="icon">📊</span>
          Export Report
        </button>
      </div>
    </div>

    <!-- Overview Cards -->
    <div class="metrics-overview">
      <div class="metric-card">
        <div class="metric-icon">💾</div>
        <div class="metric-content">
          <h3>Database Size</h3>
          <div class="metric-value">{{ metrics.database.size }}</div>
          <div class="metric-change positive">
            +{{ metrics.database.growth }} since last week
          </div>
        </div>
      </div>

      <div class="metric-card">
        <div class="metric-icon">⚡</div>
        <div class="metric-content">
          <h3>Avg Response Time</h3>
          <div class="metric-value">{{ metrics.performance.avgResponseTime }}ms</div>
          <div class="metric-change" :class="metrics.performance.responseTimeChange > 0 ? 'negative' : 'positive'">
            {{ metrics.performance.responseTimeChange > 0 ? '+' : '' }}{{ metrics.performance.responseTimeChange }}ms
          </div>
        </div>
      </div>

      <div class="metric-card">
        <div class="metric-icon">👥</div>
        <div class="metric-content">
          <h3>Active Users</h3>
          <div class="metric-value">{{ metrics.users.active }}</div>
          <div class="metric-change positive">
            +{{ metrics.users.newThisWeek }} this week
          </div>
        </div>
      </div>

      <div class="metric-card">
        <div class="metric-icon">📄</div>
        <div class="metric-content">
          <h3>Total Documents</h3>
          <div class="metric-value">{{ metrics.content.totalDocs }}</div>
          <div class="metric-change positive">
            +{{ metrics.content.newDocs }} new docs
          </div>
        </div>
      </div>
    </div>

    <!-- System Health -->
    <div class="metrics-section">
      <h3>System Health</h3>
      <div class="health-grid">
        <div class="health-item">
          <div class="health-label">Server Status</div>
          <div class="health-value">
            <span :class="['status-indicator', metrics.system.serverStatus]"></span>
            {{ metrics.system.serverStatus.charAt(0).toUpperCase() + metrics.system.serverStatus.slice(1) }}
          </div>
        </div>

        <div class="health-item">
          <div class="health-label">Database Status</div>
          <div class="health-value">
            <span :class="['status-indicator', metrics.system.databaseStatus]"></span>
            {{ metrics.system.databaseStatus.charAt(0).toUpperCase() + metrics.system.databaseStatus.slice(1) }}
          </div>
        </div>

        <div class="health-item">
          <div class="health-label">Memory Usage</div>
          <div class="health-value">
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: metrics.system.memoryUsage + '%' }"></div>
            </div>
            {{ metrics.system.memoryUsage }}%
          </div>
        </div>

        <div class="health-item">
          <div class="health-label">CPU Usage</div>
          <div class="health-value">
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: metrics.system.cpuUsage + '%' }"></div>
            </div>
            {{ metrics.system.cpuUsage }}%
          </div>
        </div>
      </div>
    </div>

    <!-- Database Metrics -->
    <div class="metrics-section">
      <h3>Database Metrics</h3>
      <div class="db-metrics">
        <div class="db-metric">
          <div class="db-metric-label">Total Tables</div>
          <div class="db-metric-value">{{ metrics.database.tables }}</div>
        </div>
        <div class="db-metric">
          <div class="db-metric-label">Total Records</div>
          <div class="db-metric-value">{{ metrics.database.totalRecords.toLocaleString() }}</div>
        </div>
        <div class="db-metric">
          <div class="db-metric-label">Avg Query Time</div>
          <div class="db-metric-value">{{ metrics.database.avgQueryTime }}ms</div>
        </div>
        <div class="db-metric">
          <div class="db-metric-label">Last Backup</div>
          <div class="db-metric-value">{{ formatDate(metrics.database.lastBackup) }}</div>
        </div>
        <div class="db-metric">
          <div class="db-metric-label">Backup Status</div>
          <div class="db-metric-value">
            <span :class="['backup-status', metrics.database.backupStatus]">
              {{ metrics.database.backupStatus.charAt(0).toUpperCase() + metrics.database.backupStatus.slice(1) }}
            </span>
          </div>
        </div>
        <div class="db-metric">
          <div class="db-metric-label">Index Health</div>
          <div class="db-metric-value">
            <span :class="['index-health', metrics.database.indexHealth]">
              {{ metrics.database.indexHealth.charAt(0).toUpperCase() + metrics.database.indexHealth.slice(1) }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Performance Trends -->
    <div class="metrics-section">
      <h3>Performance Trends (Last 7 Days)</h3>
      <div class="trends-container">
        <div class="trend-chart">
          <h4>Response Times</h4>
          <div class="chart-placeholder">
            <div class="chart-bars">
              <div v-for="(time, index) in metrics.trends.responseTimes" :key="index" 
                   class="chart-bar" 
                   :style="{ height: (time / Math.max(...metrics.trends.responseTimes)) * 100 + '%' }">
              </div>
            </div>
            <div class="chart-labels">
              <span v-for="(day, index) in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']" :key="index">
                {{ day }}
              </span>
            </div>
          </div>
        </div>

        <div class="trend-chart">
          <h4>User Activity</h4>
          <div class="chart-placeholder">
            <div class="chart-bars">
              <div v-for="(activity, index) in metrics.trends.userActivity" :key="index" 
                   class="chart-bar activity-bar" 
                   :style="{ height: (activity / Math.max(...metrics.trends.userActivity)) * 100 + '%' }">
              </div>
            </div>
            <div class="chart-labels">
              <span v-for="(day, index) in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']" :key="index">
                {{ day }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Recent Operations -->
    <div class="metrics-section">
      <h3>Recent System Operations</h3>
      <div class="operations-list">
        <div v-for="operation in metrics.recentOperations" :key="operation.id" class="operation-item">
          <div class="operation-icon">
            <span :class="['op-icon', operation.type]">{{ getOperationIcon(operation.type) }}</span>
          </div>
          <div class="operation-details">
            <div class="operation-name">{{ operation.name }}</div>
            <div class="operation-time">{{ formatDateTime(operation.timestamp) }}</div>
          </div>
          <div class="operation-status">
            <span :class="['status-badge', operation.status]">{{ operation.status }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Storage Analysis -->
    <div class="metrics-section">
      <h3>Storage Analysis</h3>
      <div class="storage-breakdown">
        <div class="storage-item">
          <div class="storage-type">Documents</div>
          <div class="storage-bar">
            <div class="storage-fill documents" :style="{ width: (metrics.storage.documents / metrics.storage.total) * 100 + '%' }"></div>
          </div>
          <div class="storage-size">{{ formatBytes(metrics.storage.documents) }}</div>
        </div>
        <div class="storage-item">
          <div class="storage-type">Media Files</div>
          <div class="storage-bar">
            <div class="storage-fill media" :style="{ width: (metrics.storage.media / metrics.storage.total) * 100 + '%' }"></div>
          </div>
          <div class="storage-size">{{ formatBytes(metrics.storage.media) }}</div>
        </div>
        <div class="storage-item">
          <div class="storage-type">Database</div>
          <div class="storage-bar">
            <div class="storage-fill database" :style="{ width: (metrics.storage.database / metrics.storage.total) * 100 + '%' }"></div>
          </div>
          <div class="storage-size">{{ formatBytes(metrics.storage.database) }}</div>
        </div>
        <div class="storage-item">
          <div class="storage-type">Cache</div>
          <div class="storage-bar">
            <div class="storage-fill cache" :style="{ width: (metrics.storage.cache / metrics.storage.total) * 100 + '%' }"></div>
          </div>
          <div class="storage-size">{{ formatBytes(metrics.storage.cache) }}</div>
        </div>
      </div>
    </div>

    <!-- Loading overlay -->
    <div v-if="loading" class="loading-overlay">
      <div class="loading">Loading metrics...</div>
    </div>

    <!-- Error message -->
    <div v-if="error" class="error-message">
      {{ error }}
      <button @click="error = ''" class="close-error">&times;</button>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'PerformanceMetrics',
  data() {
    return {
      loading: false,
      error: '',
      metrics: {
        database: {
          size: '0 MB',
          growth: '0 MB',
          tables: 0,
          totalRecords: 0,
          avgQueryTime: 0,
          lastBackup: null,
          backupStatus: 'unknown',
          indexHealth: 'unknown'
        },
        performance: {
          avgResponseTime: 0,
          responseTimeChange: 0
        },
        users: {
          active: 0,
          newThisWeek: 0
        },
        content: {
          totalDocs: 0,
          newDocs: 0
        },
        system: {
          serverStatus: 'unknown',
          databaseStatus: 'unknown',
          memoryUsage: 0,
          cpuUsage: 0
        },
        trends: {
          responseTimes: [120, 145, 132, 189, 156, 123, 134],
          userActivity: [25, 32, 28, 45, 38, 29, 35]
        },
        storage: {
          total: 50 * 1024 * 1024, // 50MB
          documents: 20 * 1024 * 1024, // 20MB
          media: 15 * 1024 * 1024, // 15MB
          database: 10 * 1024 * 1024, // 10MB
          cache: 5 * 1024 * 1024 // 5MB
        },
        recentOperations: []
      }
    }
  },
  mounted() {
    this.loadMetrics()
  },
  methods: {
    async loadMetrics() {
      this.loading = true
      this.error = ''
      
      try {
        console.log('📊 PerformanceMetrics - Loading metrics from API...')
        const response = await axios.get('/api/metrics/')
        console.log('✅ PerformanceMetrics - API response:', response.data)
        
        // Merge the API data with our current structure
        if (response.data.database) {
          this.metrics.database = { ...this.metrics.database, ...response.data.database }
        }
        if (response.data.system) {
          this.metrics.system = { ...this.metrics.system, ...response.data.system }
        }
        if (response.data.application) {
          if (response.data.application.users) {
            this.metrics.users = { ...this.metrics.users, ...response.data.application.users }
          }
          if (response.data.application.content) {
            this.metrics.content = { ...this.metrics.content, ...response.data.application.content }
          }
          if (response.data.application.performance) {
            this.metrics.performance = { ...this.metrics.performance, ...response.data.application.performance }
          }
          if (response.data.application.trends) {
            this.metrics.trends = { ...this.metrics.trends, ...response.data.application.trends }
          }
          if (response.data.application.recentOperations) {
            this.metrics.recentOperations = response.data.application.recentOperations
          }
        }
        if (response.data.storage) {
          this.metrics.storage = { ...this.metrics.storage, ...response.data.storage }
        }
        
        console.log('✅ PerformanceMetrics - Metrics loaded successfully')
        
      } catch (error) {
        console.error('❌ PerformanceMetrics - Error loading metrics:', error)
        this.error = 'Failed to load performance metrics: ' + (error.response?.data?.error || error.message)
        
        // Keep the default/mock data if API fails
        console.log('🔄 Using default metrics data due to API error')
        this.setDefaultMetrics()
      } finally {
        this.loading = false
      }
    },
    
    setDefaultMetrics() {
      // Set some default values when API is unavailable
      this.metrics = {
        database: {
          size: '45.2 MB',
          growth: '2.1 MB',
          tables: 12,
          totalRecords: 15847,
          avgQueryTime: 12,
          lastBackup: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000), // 2 days ago
          backupStatus: 'healthy',
          indexHealth: 'good'
        },
        performance: {
          avgResponseTime: 156,
          responseTimeChange: -23
        },
        users: {
          active: 47,
          newThisWeek: 8
        },
        content: {
          totalDocs: 324,
          newDocs: 12
        },
        system: {
          serverStatus: 'healthy',
          databaseStatus: 'healthy',
          memoryUsage: 68,
          cpuUsage: 32
        },
        trends: {
          responseTimes: [120, 145, 132, 189, 156, 123, 134],
          userActivity: [25, 32, 28, 45, 38, 29, 35]
        },
        storage: {
          total: 50 * 1024 * 1024, // 50MB
          documents: 20 * 1024 * 1024, // 20MB
          media: 15 * 1024 * 1024, // 15MB
          database: 10 * 1024 * 1024, // 10MB
          cache: 5 * 1024 * 1024 // 5MB
        },
        recentOperations: [
          {
            id: 1,
            name: 'Database Backup',
            type: 'backup',
            timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000), // 2 hours ago
            status: 'success'
          },
          {
            id: 2,
            name: 'Index Optimization',
            type: 'optimization',
            timestamp: new Date(Date.now() - 6 * 60 * 60 * 1000), // 6 hours ago
            status: 'success'
          },
          {
            id: 3,
            name: 'Cache Clear',
            type: 'maintenance',
            timestamp: new Date(Date.now() - 12 * 60 * 60 * 1000), // 12 hours ago
            status: 'success'
          },
          {
            id: 4,
            name: 'Security Scan',
            type: 'security',
            timestamp: new Date(Date.now() - 24 * 60 * 60 * 1000), // 1 day ago
            status: 'warning'
          }
        ]
      }
    },
    
    async refreshMetrics() {
      await this.loadMetrics()
    },
    
    exportMetrics() {
      // Create a simple CSV export of key metrics
      const csvData = [
        ['Metric', 'Value'],
        ['Database Size', this.metrics.database.size],
        ['Total Records', this.metrics.database.totalRecords],
        ['Active Users', this.metrics.users.active],
        ['Total Documents', this.metrics.content.totalDocs],
        ['Avg Response Time', this.metrics.performance.avgResponseTime + 'ms'],
        ['Memory Usage', this.metrics.system.memoryUsage + '%'],
        ['CPU Usage', this.metrics.system.cpuUsage + '%'],
        ['Last Backup', this.formatDate(this.metrics.database.lastBackup)]
      ]
      
      const csvContent = csvData.map(row => row.join(',')).join('\n')
      const blob = new Blob([csvContent], { type: 'text/csv' })
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `performance-metrics-${new Date().toISOString().split('T')[0]}.csv`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
    },
    
    formatDate(date) {
      if (!date) return 'Never'
      return new Date(date).toLocaleDateString()
    },
    
    formatDateTime(date) {
      if (!date) return ''
      return new Date(date).toLocaleString()
    },
    
    formatBytes(bytes) {
      if (bytes === 0) return '0 Bytes'
      const k = 1024
      const sizes = ['Bytes', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
    },
    
    getOperationIcon(type) {
      const icons = {
        backup: '💾',
        optimization: '⚡',
        maintenance: '🔧',
        security: '🔒',
        update: '📦'
      }
      return icons[type] || '📋'
    }
  }
}
</script>

<style scoped>
.performance-metrics {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
  position: relative;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.header h2 {
  margin: 0;
  color: #333;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.btn {
  padding: 10px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: #007bff;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #0056b3;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background: #545b62;
}

.icon {
  font-size: 16px;
}

/* Overview Cards */
.metrics-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
}

.metric-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 16px;
  transition: transform 0.2s;
}

.metric-card:hover {
  transform: translateY(-2px);
}

.metric-icon {
  font-size: 32px;
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  color: white;
}

.metric-content h3 {
  margin: 0 0 8px 0;
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.metric-value {
  font-size: 28px;
  font-weight: 700;
  color: #333;
  margin-bottom: 4px;
}

.metric-change {
  font-size: 12px;
  font-weight: 500;
}

.metric-change.positive {
  color: #28a745;
}

.metric-change.negative {
  color: #dc3545;
}

/* Sections */
.metrics-section {
  background: white;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.metrics-section h3 {
  margin: 0 0 20px 0;
  color: #333;
  font-size: 18px;
  font-weight: 600;
}

/* System Health */
.health-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.health-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.health-label {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.health-value {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.status-indicator {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.status-indicator.healthy {
  background: #28a745;
}

.status-indicator.warning {
  background: #ffc107;
}

.status-indicator.error {
  background: #dc3545;
}

.progress-bar {
  flex: 1;
  height: 8px;
  background: #e9ecef;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #28a745, #20c997);
  transition: width 0.3s ease;
}

/* Database Metrics */
.db-metrics {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.db-metric {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.db-metric-label {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.db-metric-value {
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.backup-status,
.index-health {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
}

.backup-status.healthy,
.index-health.good {
  background: #d4edda;
  color: #155724;
}

.backup-status.warning,
.index-health.warning {
  background: #fff3cd;
  color: #856404;
}

.backup-status.error,
.index-health.poor {
  background: #f8d7da;
  color: #721c24;
}

/* Trends */
.trends-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 30px;
}

.trend-chart h4 {
  margin: 0 0 16px 0;
  color: #333;
  font-size: 16px;
}

.chart-placeholder {
  height: 200px;
  position: relative;
}

.chart-bars {
  display: flex;
  align-items: end;
  justify-content: space-between;
  height: 160px;
  padding: 0 8px;
  gap: 4px;
}

.chart-bar {
  flex: 1;
  background: linear-gradient(to top, #007bff, #0056b3);
  border-radius: 2px 2px 0 0;
  min-height: 20px;
  transition: all 0.3s ease;
}

.chart-bar.activity-bar {
  background: linear-gradient(to top, #28a745, #20c997);
}

.chart-bar:hover {
  opacity: 0.8;
}

.chart-labels {
  display: flex;
  justify-content: space-between;
  padding: 8px;
  font-size: 12px;
  color: #666;
}

/* Operations */
.operations-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.operation-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
  transition: background 0.2s;
}

.operation-item:hover {
  background: #e9ecef;
}

.operation-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  background: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.op-icon {
  font-size: 18px;
}

.operation-details {
  flex: 1;
}

.operation-name {
  font-weight: 600;
  color: #333;
  margin-bottom: 4px;
}

.operation-time {
  font-size: 14px;
  color: #666;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
}

.status-badge.success {
  background: #d4edda;
  color: #155724;
}

.status-badge.warning {
  background: #fff3cd;
  color: #856404;
}

.status-badge.error {
  background: #f8d7da;
  color: #721c24;
}

/* Storage */
.storage-breakdown {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.storage-item {
  display: flex;
  align-items: center;
  gap: 16px;
}

.storage-type {
  width: 120px;
  font-weight: 500;
  color: #333;
}

.storage-bar {
  flex: 1;
  height: 12px;
  background: #e9ecef;
  border-radius: 6px;
  overflow: hidden;
}

.storage-fill {
  height: 100%;
  transition: width 0.3s ease;
}

.storage-fill.documents {
  background: #007bff;
}

.storage-fill.media {
  background: #28a745;
}

.storage-fill.database {
  background: #ffc107;
}

.storage-fill.cache {
  background: #6c757d;
}

.storage-size {
  width: 80px;
  text-align: right;
  font-weight: 600;
  color: #333;
}

/* Loading and Error */
.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.loading {
  background: #007bff;
  color: white;
  padding: 16px 24px;
  border-radius: 8px;
  font-weight: 500;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.error-message {
  position: fixed;
  top: 20px;
  right: 20px;
  padding: 16px 20px;
  background: #dc3545;
  color: white;
  border-radius: 8px;
  font-weight: 500;
  z-index: 1001;
  display: flex;
  align-items: center;
  gap: 12px;
  max-width: 400px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.close-error {
  background: none;
  border: none;
  color: white;
  font-size: 18px;
  cursor: pointer;
  padding: 0;
}

/* Responsive Design */
@media (max-width: 768px) {
  .performance-metrics {
    padding: 15px;
  }
  
  .header {
    flex-direction: column;
    align-items: stretch;
    gap: 16px;
  }
  
  .header-actions {
    justify-content: center;
  }
  
  .metrics-overview {
    grid-template-columns: 1fr;
  }
  
  .metric-card {
    padding: 20px;
  }
  
  .health-grid,
  .db-metrics {
    grid-template-columns: 1fr;
  }
  
  .trends-container {
    grid-template-columns: 1fr;
  }
  
  .storage-item {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }
  
  .storage-type {
    width: auto;
  }
  
  .storage-size {
    width: auto;
    text-align: left;
  }
}
</style>
