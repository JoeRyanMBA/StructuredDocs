<template>
  <div class="collections-dashboard">
    <div class="dashboard-header">
      <h1>Collections Dashboard</h1>
      <p class="welcome-text">Manage and organize your document collections</p>
    </div>

    <!-- Key Metrics Cards -->
    <div class="metrics-grid">
      <div class="metric-card">
        <div class="metric-icon">📚</div>
        <div class="metric-content">
          <h3>Total Collections</h3>
          <div class="metric-number">{{ stats.total || 0 }}</div>
          <div class="metric-detail">{{ stats.active || 0 }} Active</div>
        </div>
      </div>

      <div class="metric-card">
        <div class="metric-icon">📄</div>
        <div class="metric-content">
          <h3>Total Topics</h3>
          <div class="metric-number">{{ stats.totalTopics || 0 }}</div>
          <div class="metric-detail">Across all collections</div>
        </div>
      </div>

      <div class="metric-card">
        <div class="metric-icon">🆕</div>
        <div class="metric-content">
          <h3>New This Week</h3>
          <div class="metric-number">{{ stats.newThisWeek || 0 }}</div>
          <div class="metric-detail">Collections created</div>
        </div>
      </div>

      <div class="metric-card">
        <div class="metric-icon">📊</div>
        <div class="metric-content">
          <h3>Avg Topics</h3>
          <div class="metric-number">{{ stats.avgTopics || 0 }}</div>
          <div class="metric-detail">Per collection</div>
        </div>
      </div>
    </div>

    <!-- Main Content Grid -->
    <div class="content-grid">
      
      <!-- Quick Actions -->
      <div class="dashboard-section">
        <h2>Quick Actions</h2>
        <div class="quick-actions-grid">
          <button class="action-card" @click="createNewCollection">
            <div class="action-icon">➕</div>
            <div class="action-content">
              <h3>Create New Collection</h3>
              <p>Start organizing topics into collections</p>
            </div>
          </button>
          <button class="action-card" @click="navigateTo('/import')">
            <div class="action-icon">📥</div>
            <div class="action-content">
              <h3>Import Topics</h3>
              <p>Add content from external sources</p>
            </div>
          </button>
          <button class="action-card" @click="navigateTo('/topics')">
            <div class="action-icon">📝</div>
            <div class="action-content">
              <h3>Browse All Topics</h3>
              <p>View and manage existing topics</p>
            </div>
          </button>
        </div>
      </div>

      <!-- Recent Collections -->
      <div class="dashboard-section">
        <h2>Recent Collections</h2>
        <div class="collections-list">
          <div v-if="recentCollections.length === 0" class="empty-state">
            <p>No collections yet. Create your first collection to get started!</p>
          </div>
          <div v-else>
            <div 
              v-for="collection in recentCollections" 
              :key="collection.id"
              class="collection-item"
              @click="viewCollection(collection)"
            >
              <div class="collection-header">
                <h4>{{ collection.name }}</h4>
                <span class="collection-meta">{{ collection.topics_count || 0 }} topics</span>
              </div>
              <p class="collection-description">{{ collection.description || 'No description available' }}</p>
              <div class="collection-footer">
                <span class="collection-date">{{ formatRelativeTime(collection.updated_at || collection.created_at) }}</span>
                <span class="collection-status" :class="collection.status">{{ formatStatus(collection.status) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Collection Statistics -->
      <div class="dashboard-section full-width">
        <h2>Collection Overview</h2>
        <div class="stats-overview">
          <div v-if="collections.length === 0" class="empty-state">
            <p>No collections found. <button @click="createNewCollection" class="link-btn">Create your first collection</button></p>
          </div>
          <div v-else class="collections-grid">
            <div 
              v-for="collection in collections" 
              :key="collection.id"
              class="collection-card"
              @click="viewCollection(collection)"
            >
              <div class="card-header">
                <h3>{{ collection.name }}</h3>
                <span class="card-badge">{{ collection.topics_count || 0 }} topics</span>
              </div>
              <p class="card-description">{{ collection.description || 'No description available' }}</p>
              <div class="card-footer">
                <span class="card-date">Updated {{ formatRelativeTime(collection.updated_at || collection.created_at) }}</span>
                <div class="card-actions">
                  <button @click.stop="editCollection(collection)" class="card-action-btn">Edit</button>
                  <button @click.stop="viewCollection(collection)" class="card-action-btn primary">View</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-overlay">
      <div class="loading-spinner">Loading collections...</div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CollectionsDashboard',
  
  data() {
    return {
      loading: true,
      stats: {
        total: 0,
        active: 0,
        totalTopics: 0,
        newThisWeek: 0,
        avgTopics: 0
      },
      collections: [],
      recentCollections: []
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
          this.loadCollections(),
          this.loadStats()
        ])
      } catch (error) {
        console.error('Failed to load collections dashboard:', error)
      } finally {
        this.loading = false
      }
    },

    async loadCollections() {
      try {
        const res = await fetch('/api/collections/')
        if (res.ok) {
          this.collections = await res.json()
          // Get recent collections (last 5, sorted by updated_at)
          this.recentCollections = [...this.collections]
            .sort((a, b) => new Date(b.updated_at || b.created_at) - new Date(a.updated_at || a.created_at))
            .slice(0, 5)
        }
      } catch (error) {
        console.error('Failed to load collections:', error)
      }
    },

    async loadStats() {
      try {
        // Calculate stats from collections data
        const total = this.collections.length
        const active = this.collections.filter(c => c.status === 'active' || !c.status).length
        const totalTopics = this.collections.reduce((sum, c) => sum + (c.topics_count || 0), 0)
        
        // Calculate new this week
        const oneWeekAgo = new Date()
        oneWeekAgo.setDate(oneWeekAgo.getDate() - 7)
        const newThisWeek = this.collections.filter(c => 
          c.created_at && new Date(c.created_at) > oneWeekAgo
        ).length

        // Calculate average topics per collection
        const avgTopics = total > 0 ? Math.round(totalTopics / total) : 0

        this.stats = {
          total,
          active,
          totalTopics,
          newThisWeek,
          avgTopics
        }
      } catch (error) {
        console.error('Failed to calculate stats:', error)
      }
    },

    createNewCollection() {
      // For now, navigate to collections page - you might want a dedicated create page
      this.$router.push('/collections?action=create')
    },

    viewCollection(collection) {
      this.$router.push(`/collections/${collection.id}`)
    },

    editCollection(collection) {
      this.$router.push(`/collections/${collection.id}/edit`)
    },

    navigateTo(path) {
      this.$router.push(path)
    },

    formatStatus(status) {
      const statusMap = {
        'active': 'Active',
        'archived': 'Archived',
        'draft': 'Draft'
      }
      return statusMap[status] || 'Active'
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
.collections-dashboard {
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

/* Collections List */
.collections-list {
  max-height: 400px;
  overflow-y: auto;
}

.collection-item {
  padding: 1rem;
  border: 1px solid #f8f9fa;
  border-radius: 6px;
  margin-bottom: 0.75rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.collection-item:hover {
  border-color: #005a9c;
  background: #f8f9fa;
}

.collection-item:last-child {
  margin-bottom: 0;
}

.collection-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.collection-header h4 {
  margin: 0;
  color: #495057;
  font-size: 1rem;
  font-weight: 600;
}

.collection-meta {
  color: #6c757d;
  font-size: 0.8rem;
}

.collection-description {
  color: #6c757d;
  font-size: 0.875rem;
  margin: 0 0 0.75rem 0;
  line-height: 1.4;
}

.collection-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.collection-date {
  color: #adb5bd;
  font-size: 0.75rem;
}

.collection-status {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.7rem;
  font-weight: 500;
  text-transform: uppercase;
  background: #d4edda;
  color: #155724;
}

/* Collections Grid */
.collections-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.collection-card {
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.2s ease;
  background: white;
}

.collection-card:hover {
  border-color: #005a9c;
  box-shadow: 0 4px 12px rgba(0,90,156,0.15);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.card-header h3 {
  margin: 0;
  color: #495057;
  font-size: 1.1rem;
  font-weight: 600;
  flex: 1;
}

.card-badge {
  background: #e9ecef;
  color: #495057;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  margin-left: 1rem;
}

.card-description {
  color: #6c757d;
  font-size: 0.875rem;
  line-height: 1.4;
  margin: 0 0 1rem 0;
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
  .collections-dashboard {
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
  
  .collections-grid {
    grid-template-columns: 1fr;
  }
  
  .dashboard-header h1 {
    font-size: 2rem;
  }
}
</style>
