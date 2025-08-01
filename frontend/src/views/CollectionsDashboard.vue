<template>
  <div class="collections-dashboard">
    <div class="full-width" style="margin-bottom:1.5rem;">
      <NotificationTicker
        :notifications="mergedNotifications"
        contextType="collections"
        @mark-read="markNotificationRead"
      />
    </div>
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
              <div class="collection-project-info">
                <span class="project-label">Project:</span>
                <span class="project-name">{{ collection.projectName || 'Unknown Project' }}</span>
              </div>
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
              <div class="card-project">
                <span class="project-label">Project:</span>
                <span class="project-name">{{ collection.projectName || 'Unknown Project' }}</span>
              </div>
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

    <!-- Create Collection Modal -->
    <div v-if="showCreateModal" class="modal-overlay" @click="showCreateModal = false">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h2>Create New Collection</h2>
          <button @click="showCreateModal = false" class="close-btn">×</button>
        </div>
        <form @submit.prevent="submitNewCollection" class="modal-body">
          <div class="form-group">
            <label for="collectionProject">Project *</label>
            <select
              id="collectionProject"
              v-model="newCollection.projectId"
              required
            >
              <option value="">Select a project...</option>
              <option 
                v-for="project in projects" 
                :key="project.id" 
                :value="project.id"
              >
                {{ project.name }}
              </option>
            </select>
          </div>
          
          <div class="form-group">
            <label for="collectionName">Collection Name *</label>
            <input
              id="collectionName"
              v-model="newCollection.name"
              type="text"
              required
              placeholder="Enter collection name"
            />
          </div>
          
          <div class="form-group">
            <label for="collectionDescription">Description</label>
            <textarea
              id="collectionDescription"
              v-model="newCollection.description"
              rows="3"
              placeholder="Describe what this collection will contain"
            ></textarea>
          </div>
          
          <div class="form-group">
            <label for="collectionStatus">Status</label>
            <select id="collectionStatus" v-model="newCollection.status">
              <option value="active">Active</option>
              <option value="draft">Draft</option>
              <option value="archived">Archived</option>
            </select>
          </div>
          
          <div class="modal-actions">
            <button type="button" @click="showCreateModal = false" class="cancel-btn">
              Cancel
            </button>
            <button type="submit" class="create-btn">Create Collection</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-overlay">
      <div class="loading-spinner">Loading collections...</div>
    </div>
  </div>
</template>

<script>
import NotificationTicker from '../components/NotificationTicker.vue'

export default {
  name: 'CollectionsDashboard',
  components: { NotificationTicker },
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
      showCreateModal: false,
      newCollection: {
        name: '',
        description: '',
        status: 'active',
        projectId: null
      },
      stats: {
        total: 0,
        active: 0,
        totalTopics: 0,
        newThisWeek: 0,
        avgTopics: 0
      },
      collections: [],
      recentCollections: [],
      projects: []
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
          this.loadCollections(),
          this.loadProjects(),
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
        // Mock collections data including some from projects
        const mockCollections = [
          {
            id: 1,
            name: 'Census Portal User Documentation',
            description: 'User guides and tutorials for the new Census data portal interface',
            status: 'active',
            topics_count: 12,
            projectId: 1,
            projectName: 'Census Data Portal Redesign',
            created_at: '2025-07-01T10:00:00Z',
            updated_at: '2025-07-25T14:30:00Z'
          },
          {
            id: 2,
            name: 'API Documentation Collection',
            description: 'Complete API reference and integration guides for developers',
            status: 'active',
            topics_count: 8,
            projectId: 3,
            projectName: 'Mobile App API Documentation',
            created_at: '2025-06-15T09:00:00Z',
            updated_at: '2025-07-20T11:45:00Z'
          },
          {
            id: 3,
            name: 'Economic Survey Methodology',
            description: 'Detailed documentation of survey processes and statistical methods',
            status: 'draft',
            topics_count: 6,
            projectId: 2,
            projectName: 'Economic Survey Documentation',
            created_at: '2025-07-10T16:00:00Z',
            updated_at: '2025-07-22T10:15:00Z'
          },
          {
            id: 4,
            name: 'Mobile App User Guide',
            description: 'Step-by-step guide for using the Census mobile application',
            status: 'active',
            topics_count: 15,
            projectId: 3,
            projectName: 'Mobile App API Documentation',
            created_at: '2025-06-01T08:00:00Z',
            updated_at: '2025-07-18T13:20:00Z'
          },
          {
            id: 5,
            name: 'Data Visualization Toolkit',
            description: 'Templates and guidelines for creating Census data visualizations',
            status: 'archived',
            topics_count: 9,
            projectId: 1,
            projectName: 'Census Data Portal Redesign',
            created_at: '2025-05-20T12:00:00Z',
            updated_at: '2025-06-30T15:45:00Z'
          }
        ]

        this.collections = mockCollections
        
        // Get recent collections (last 5, sorted by updated_at)
        this.recentCollections = [...this.collections]
          .sort((a, b) => new Date(b.updated_at || b.created_at) - new Date(a.updated_at || a.created_at))
          .slice(0, 5)
          
      } catch (error) {
        console.error('Failed to load collections:', error)
        this.collections = []
        this.recentCollections = []
      }
    },

    async loadProjects() {
      try {
        // Mock projects data - should match the projects from ProjectsView
        const mockProjects = [
          {
            id: 1,
            name: 'Census Data Portal Redesign',
            description: 'Modernizing the main census data access portal with improved user experience and performance.',
            status: 'active'
          },
          {
            id: 2,
            name: 'Economic Survey Documentation',
            description: 'Creating comprehensive documentation for the new economic indicators survey methodology.',
            status: 'planning'
          },
          {
            id: 3,
            name: 'Mobile App API Documentation',
            description: 'Complete API documentation for the new Census mobile application developers.',
            status: 'completed'
          }
        ]

        this.projects = mockProjects
        
      } catch (error) {
        console.error('Failed to load projects:', error)
        this.projects = []
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
      this.showCreateModal = true
    },

    async submitNewCollection() {
      try {
        // Find the selected project
        const selectedProject = this.projects.find(p => p.id === parseInt(this.newCollection.projectId))
        
        // Create new collection object
        const collection = {
          id: Date.now(),
          name: this.newCollection.name,
          description: this.newCollection.description,
          status: this.newCollection.status,
          projectId: this.newCollection.projectId,
          projectName: selectedProject ? selectedProject.name : 'Unknown Project',
          topics_count: 0,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        }
        
        // Add to collections array
        this.collections.push(collection)
        
        // Update recent collections
        this.recentCollections = [...this.collections]
          .sort((a, b) => new Date(b.updated_at || b.created_at) - new Date(a.updated_at || a.created_at))
          .slice(0, 5)
        
        // Recalculate stats
        await this.loadStats()
        
        // Reset form and close modal
        this.resetNewCollection()
        this.showCreateModal = false
        
      } catch (error) {
        console.error('Failed to create collection:', error)
      }
    },

    resetNewCollection() {
      this.newCollection = {
        name: '',
        description: '',
        status: 'active',
        projectId: null
      }
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

.collection-project-info {
  margin-bottom: 0.75rem;
  padding: 0.25rem 0.5rem;
  background: #f8f9fa;
  border-radius: 3px;
  font-size: 0.8rem;
}

.collection-project-info .project-label {
  color: #6c757d;
  font-weight: 600;
}

.collection-project-info .project-name {
  color: #005a9c;
  font-weight: 500;
  margin-left: 0.25rem;
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

.card-project {
  margin-bottom: 1rem;
  padding: 0.5rem;
  background: #f8f9fa;
  border-radius: 4px;
  border-left: 3px solid #005a9c;
}

.project-label {
  font-size: 0.75rem;
  color: #6c757d;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.project-name {
  font-size: 0.875rem;
  color: #005a9c;
  font-weight: 500;
  margin-left: 0.5rem;
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

/* Modal Styles */
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
  border-radius: 12px;
  min-width: 500px;
  max-width: 90vw;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h2 {
  margin: 0;
  color: #112e51;
  font-size: 1.5rem;
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #9ca3af;
  padding: 0.25rem;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.close-btn:hover {
  color: #112e51;
  background: #f3f4f6;
}

.modal-body {
  padding: 1.5rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #112e51;
  font-size: 0.9rem;
}

.form-group input, .form-group textarea, .form-group select {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.9rem;
  box-sizing: border-box;
}

.form-group input:focus, .form-group textarea:focus, .form-group select:focus {
  outline: none;
  border-color: #005a9c;
  box-shadow: 0 0 0 3px rgba(0, 90, 156, 0.1);
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid #e5e7eb;
}

.cancel-btn, .create-btn {
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  border: none;
  transition: all 0.2s ease;
}

.cancel-btn {
  background: #f3f4f6;
  color: #374151;
}

.cancel-btn:hover {
  background: #e5e7eb;
}

.create-btn {
  background: #005a9c;
  color: white;
}

.create-btn:hover {
  background: #004080;
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
