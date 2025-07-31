<template>
  <div class="system-logs">
    <div class="header">
      <h2>System Logs</h2>
      <div class="controls">
        <div class="filter-group">
          <label for="logLevel">Level:</label>
          <select id="logLevel" v-model="selectedLevel" @change="filterLogs">
            <option value="">All Levels</option>
            <option value="info">Info</option>
            <option value="warning">Warning</option>
            <option value="error">Error</option>
            <option value="debug">Debug</option>
          </select>
        </div>
        <div class="filter-group">
          <label for="logCategory">Category:</label>
          <select id="logCategory" v-model="selectedCategory" @change="filterLogs">
            <option value="">All Categories</option>
            <option value="auth">Authentication</option>
            <option value="user">User Management</option>
            <option value="api">API Requests</option>
            <option value="system">System Events</option>
            <option value="database">Database</option>
          </select>
        </div>
        <button @click="refreshLogs" class="btn btn-primary">
          <span v-if="loading">Refreshing...</span>
          <span v-else>Refresh</span>
        </button>
      </div>
    </div>

    <!-- Logs Table -->
    <div class="logs-table">
      <table>
        <thead>
          <tr>
            <th>Timestamp</th>
            <th>Level</th>
            <th>Category</th>
            <th>Event</th>
            <th>User</th>
            <th>Details</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="log in filteredLogs" :key="log.id" :class="['log-row', `level-${log.level}`]">
            <td class="timestamp">{{ formatTimestamp(log.timestamp) }}</td>
            <td>
              <span :class="['level-badge', `level-${log.level}`]">
                {{ log.level.toUpperCase() }}
              </span>
            </td>
            <td>
              <span :class="['category-badge', `category-${log.category}`]">
                {{ log.category }}
              </span>
            </td>
            <td class="event">{{ log.event }}</td>
            <td class="user">{{ log.user || 'System' }}</td>
            <td class="details">
              <button 
                v-if="log.details" 
                @click="showDetails(log)" 
                class="btn btn-sm btn-secondary"
              >
                View
              </button>
              <span v-else class="no-details">-</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div class="pagination">
      <button 
        @click="previousPage" 
        :disabled="currentPage === 1" 
        class="btn btn-secondary"
      >
        Previous
      </button>
      <span class="page-info">
        Page {{ currentPage }} of {{ totalPages }} ({{ totalLogs }} total logs)
      </span>
      <button 
        @click="nextPage" 
        :disabled="currentPage === totalPages" 
        class="btn btn-secondary"
      >
        Next
      </button>
    </div>

    <!-- Log Details Modal -->
    <div v-if="selectedLog" class="modal-overlay" @click="closeModal">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h3>Log Details</h3>
          <button @click="closeModal" class="close-btn">&times;</button>
        </div>
        <div class="modal-body">
          <div class="log-detail">
            <strong>Timestamp:</strong> {{ formatTimestamp(selectedLog.timestamp) }}
          </div>
          <div class="log-detail">
            <strong>Level:</strong> 
            <span :class="['level-badge', `level-${selectedLog.level}`]">
              {{ selectedLog.level.toUpperCase() }}
            </span>
          </div>
          <div class="log-detail">
            <strong>Category:</strong> {{ selectedLog.category }}
          </div>
          <div class="log-detail">
            <strong>Event:</strong> {{ selectedLog.event }}
          </div>
          <div class="log-detail">
            <strong>User:</strong> {{ selectedLog.user || 'System' }}
          </div>
          <div class="log-detail">
            <strong>IP Address:</strong> {{ selectedLog.ip || 'N/A' }}
          </div>
          <div class="log-detail">
            <strong>Details:</strong>
            <pre class="details-content">{{ JSON.stringify(selectedLog.details, null, 2) }}</pre>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading overlay -->
    <div v-if="loading" class="loading-overlay">
      <div class="loading">Loading logs...</div>
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
  name: 'SystemLogs',
  data() {
    return {
      logs: [],
      filteredLogs: [],
      selectedLevel: '',
      selectedCategory: '',
      selectedLog: null,
      loading: false,
      error: '',
      currentPage: 1,
      logsPerPage: 50,
      totalLogs: 0
    }
  },
  computed: {
    totalPages() {
      return Math.ceil(this.totalLogs / this.logsPerPage)
    }
  },
  mounted() {
    this.loadLogs()
    // Auto-refresh logs every 30 seconds
    this.refreshInterval = setInterval(() => {
      this.loadLogs(false) // Silent refresh
    }, 30000)
  },
  beforeDestroy() {
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval)
    }
  },
  methods: {
    async loadLogs(showLoading = true) {
      if (showLoading) this.loading = true
      this.error = ''
      
      try {
        // For now, we'll create mock data since we don't have a real logging backend yet
        // In a real implementation, this would call: const response = await axios.get('/api/logs')
        this.logs = this.generateMockLogs()
        this.totalLogs = this.logs.length
        this.filterLogs()
      } catch (error) {
        console.error('❌ Error loading logs:', error)
        this.error = 'Failed to load system logs'
      } finally {
        if (showLoading) this.loading = false
      }
    },
    
    generateMockLogs() {
      const levels = ['info', 'warning', 'error', 'debug']
      const categories = ['auth', 'user', 'api', 'system', 'database']
      const events = [
        'User login successful',
        'User logout',
        'Failed login attempt',
        'User created',
        'User updated',
        'User deleted',
        'Password reset request',
        'API request processed',
        'Database query executed',
        'System startup',
        'Configuration updated',
        'Backup completed',
        'Cache cleared',
        'Session expired',
        'Permission denied'
      ]
      const users = ['admin@example.com', 'john@example.com', 'jane@example.com', 'Jim Test', null]
      
      const logs = []
      const now = new Date()
      
      for (let i = 0; i < 200; i++) {
        const timestamp = new Date(now.getTime() - (i * 1000 * 60 * Math.random() * 120)) // Random times in last 2 hours
        const level = levels[Math.floor(Math.random() * levels.length)]
        const category = categories[Math.floor(Math.random() * categories.length)]
        const event = events[Math.floor(Math.random() * events.length)]
        const user = users[Math.floor(Math.random() * users.length)]
        
        logs.push({
          id: i + 1,
          timestamp: timestamp.toISOString(),
          level,
          category,
          event,
          user,
          ip: `192.168.1.${Math.floor(Math.random() * 255)}`,
          details: this.generateMockDetails(category, event)
        })
      }
      
      return logs.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
    },
    
    generateMockDetails(category, event) {
      const details = {
        category,
        event,
        timestamp: new Date().toISOString()
      }
      
      switch (category) {
        case 'auth':
          details.sessionId = `sess_${Math.random().toString(36).substr(2, 9)}`
          details.userAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
          break
        case 'user':
          details.userId = Math.floor(Math.random() * 20) + 1
          details.changes = ['name', 'email', 'role'][Math.floor(Math.random() * 3)]
          break
        case 'api':
          details.endpoint = ['/api/users', '/api/topics', '/api/collections'][Math.floor(Math.random() * 3)]
          details.method = ['GET', 'POST', 'PUT', 'DELETE'][Math.floor(Math.random() * 4)]
          details.responseTime = Math.floor(Math.random() * 500) + 'ms'
          details.statusCode = [200, 201, 400, 401, 500][Math.floor(Math.random() * 5)]
          break
        case 'database':
          details.query = 'SELECT * FROM users WHERE active = true'
          details.executionTime = Math.floor(Math.random() * 100) + 'ms'
          details.rowsAffected = Math.floor(Math.random() * 10)
          break
        case 'system':
          details.component = ['server', 'database', 'cache', 'auth'][Math.floor(Math.random() * 4)]
          details.memory = Math.floor(Math.random() * 1000) + 'MB'
          details.cpu = Math.floor(Math.random() * 100) + '%'
          break
      }
      
      return details
    },
    
    filterLogs() {
      let filtered = [...this.logs]
      
      if (this.selectedLevel) {
        filtered = filtered.filter(log => log.level === this.selectedLevel)
      }
      
      if (this.selectedCategory) {
        filtered = filtered.filter(log => log.category === this.selectedCategory)
      }
      
      this.filteredLogs = filtered
      this.totalLogs = filtered.length
      this.currentPage = 1
    },
    
    refreshLogs() {
      this.loadLogs()
    },
    
    previousPage() {
      if (this.currentPage > 1) {
        this.currentPage--
      }
    },
    
    nextPage() {
      if (this.currentPage < this.totalPages) {
        this.currentPage++
      }
    },
    
    showDetails(log) {
      this.selectedLog = log
    },
    
    closeModal() {
      this.selectedLog = null
    },
    
    formatTimestamp(timestamp) {
      const date = new Date(timestamp)
      return date.toLocaleString()
    }
  }
}
</script>

<style scoped>
.system-logs {
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
  flex-wrap: wrap;
  gap: 20px;
}

.header h2 {
  margin: 0;
  color: #333;
}

.controls {
  display: flex;
  gap: 15px;
  align-items: center;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.filter-group label {
  font-size: 12px;
  font-weight: 600;
  color: #666;
}

.filter-group select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  min-width: 120px;
}

.logs-table {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  margin-bottom: 20px;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th {
  background: #f8f9fa;
  padding: 15px 12px;
  text-align: left;
  font-weight: 600;
  color: #555;
  border-bottom: 2px solid #e9ecef;
  font-size: 14px;
}

td {
  padding: 12px;
  border-bottom: 1px solid #e9ecef;
  font-size: 14px;
}

.log-row.level-error {
  background-color: #fff5f5;
}

.log-row.level-warning {
  background-color: #fffbf0;
}

.log-row.level-info {
  background-color: #f0f9ff;
}

.log-row.level-debug {
  background-color: #f9fafb;
}

.timestamp {
  font-family: 'Courier New', monospace;
  font-size: 12px;
  color: #666;
  white-space: nowrap;
}

.level-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
}

.level-info {
  background: #e3f2fd;
  color: #1976d2;
}

.level-warning {
  background: #fff3e0;
  color: #f57c00;
}

.level-error {
  background: #ffebee;
  color: #d32f2f;
}

.level-debug {
  background: #f3e5f5;
  color: #7b1fa2;
}

.category-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
}

.category-auth {
  background: #e8f5e8;
  color: #2e7d32;
}

.category-user {
  background: #e3f2fd;
  color: #1976d2;
}

.category-api {
  background: #fff3e0;
  color: #f57c00;
}

.category-system {
  background: #f3e5f5;
  color: #7b1fa2;
}

.category-database {
  background: #ffebee;
  color: #d32f2f;
}

.event {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.user {
  font-weight: 500;
  color: #333;
}

.details {
  text-align: center;
}

.no-details {
  color: #999;
  font-style: italic;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
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

.btn-secondary:hover:not(:disabled) {
  background: #545b62;
}

.btn-sm {
  padding: 6px 12px;
  font-size: 12px;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
  margin-top: 20px;
}

.page-info {
  font-size: 14px;
  color: #666;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #e9ecef;
}

.modal-header h3 {
  margin: 0;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #999;
}

.close-btn:hover {
  color: #333;
}

.modal-body {
  padding: 20px;
}

.log-detail {
  margin-bottom: 15px;
  padding: 10px;
  background: #f8f9fa;
  border-radius: 4px;
}

.log-detail strong {
  display: inline-block;
  min-width: 100px;
  color: #333;
}

.details-content {
  background: #f8f9fa;
  padding: 10px;
  border-radius: 4px;
  border: 1px solid #e9ecef;
  white-space: pre-wrap;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  margin-top: 10px;
  max-height: 200px;
  overflow-y: auto;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.loading {
  background: #007bff;
  color: white;
  padding: 10px 20px;
  border-radius: 4px;
  font-weight: 500;
}

.error-message {
  position: fixed;
  top: 20px;
  right: 20px;
  padding: 15px 20px;
  border-radius: 4px;
  background: #dc3545;
  color: white;
  font-weight: 500;
  z-index: 1001;
  display: flex;
  align-items: center;
  gap: 10px;
  max-width: 400px;
}

.close-error {
  background: none;
  border: none;
  color: white;
  font-size: 18px;
  cursor: pointer;
  padding: 0;
  margin-left: auto;
}

@media (max-width: 768px) {
  .system-logs {
    padding: 15px;
  }
  
  .header {
    flex-direction: column;
    align-items: stretch;
  }
  
  .controls {
    justify-content: center;
  }
  
  .logs-table {
    overflow-x: auto;
  }
  
  table {
    min-width: 800px;
  }
  
  .modal {
    width: 95%;
    margin: 20px;
  }
  
  .pagination {
    flex-direction: column;
    gap: 10px;
  }
}
</style>