<template>
  <div class="collections-dashboard">
    
    <!-- Compact Toolbar -->
    <CompactToolbar :show-metrics="true">
      <template #metrics>
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
      </template>
    </CompactToolbar>
    
    <div class="dashboard-header">
      <h1>Collections Dashboard</h1>
      <p class="subtitle">Manage and organize your document collections</p>
    </div>

    <!-- Quick Actions Section (aligned with Start Page) -->
    <div class="quick-actions-section">
      <h2>Quick Actions</h2>
      <p class="section-description">Manage your collections and topics</p>
      <div class="quick-actions-grid">
        <button class="quick-action-card" @click="showCreateModal = true">
          <!-- Switched to inline SVG so we can control color for contrast on different backgrounds -->
          <div class="action-icon create-icon" aria-hidden="true">
            <svg class="plus-svg" width="28" height="28" viewBox="0 0 24 24" role="img" focusable="false">
              <path d="M11 4c-.552 0-1 .448-1 1v6H4c-.552 0-1 .448-1 1s.448 1 1 1h6v6c0 .552.448 1 1 1s1-.448 1-1v-6h6c.552 0 1-.448 1-1s-.448-1-1-1h-6V5c0-.552-.448-1-1-1z" fill="currentColor"/>
            </svg>
          </div>
          <div class="action-content" title="Start organizing topics into collections">
            <h3>Create New Collection</h3>
          </div>
        </button>
        <button class="quick-action-card" @click="navigateTo('/import')">
          <div class="action-icon">📥</div>
          <div class="action-content" title="Add content from external sources">
            <h3>Import Topics</h3>
          </div>
        </button>
        <button class="quick-action-card" @click="navigateTo('/topics')">
          <div class="action-icon">📝</div>
          <div class="action-content" title="View and manage existing topics">
            <h3>Browse Topics</h3>
          </div>
        </button>
      </div>
    </div>

    <!-- Main Content Grid -->
    <div class="content-grid">
  <!-- Recent Collections -->
  <div class="dashboard-section">
        <h2>Recent Collections</h2>
        <p class="section-guidance">Select a collection to open the Organize page for that collection.</p>
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
  <div class="dashboard-section">
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
                <h4>{{ collection.name }}</h4>
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
                  <button @click.stop="editCollection(collection)" class="btn btn-secondary btn-sm">Edit</button>
                  <button @click.stop="viewCollection(collection)" class="btn btn-primary btn-sm">View</button>
                  <button v-if="isAdmin" @click.stop="toggleArchive(collection)" class="btn btn-sm" :class="collection.archived ? 'btn-warning' : 'btn-outline'">
                    {{ collection.archived ? 'Unarchive' : 'Archive' }}
                  </button>
                  <button v-if="isAdmin" @click.stop="promptDelete(collection)" class="btn btn-danger btn-sm">Delete</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

    </div>

    <!-- Create Collection Modal -->
  <div v-if="showCreateModal" class="modal-overlay" @click.self="showCreateModal = false">
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
            <label for="collectionFormNumber">Collection ID (Form Number) *</label>
            <input
              id="collectionFormNumber"
              v-model="newCollection.form_number"
              type="text"
              required
              placeholder="e.g., FORM-001, DOC-ABC-123"
              pattern="^[A-Za-z0-9\-_]+$"
              title="Only letters, numbers, hyphens, and underscores are allowed"
            />
            <small class="form-help">
              Unique alphanumeric identifier for this collection (e.g., FORM-001, DOC-ABC-123)
            </small>
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
      <div class="loading-spinner"></div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteModal" class="modal-overlay" @click.self="cancelDelete">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h2>Delete Collection</h2>
          <button @click="cancelDelete" class="close-btn">×</button>
        </div>
        <div class="modal-body">
          <p><strong>Warning:</strong> This will permanently remove the collection <strong>{{ collectionToDelete?.name }}</strong> and all nested child collections. Topics inside remain in the system and are not deleted.</p>
          <p>Type the collection name to confirm:</p>
          <input v-model="deleteConfirmText" :placeholder="collectionToDelete?.name" />
          <div class="modal-actions" style="margin-top:1rem;">
            <button type="button" class="cancel-btn" @click="cancelDelete">Cancel</button>
            <button type="button" class="btn btn-danger" :disabled="deleteConfirmText !== collectionToDelete?.name" @click="confirmDelete">Delete</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import CompactToolbar from '../components/CompactToolbar.vue'
import { getCollections, saveCollections } from '@/api/collections.js'
import { toast } from '@/composables/useToast'

export default {
  name: 'CollectionsDashboard',
  components: { CompactToolbar },
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
      showDeleteModal: false,
      collectionToDelete: null,
      deleteConfirmText: '',
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
    isAdmin() {
      try {
        const stored = JSON.parse(localStorage.getItem('user') || 'null')
        return stored && stored.role === 'admin'
      } catch { return false }
    }
  },

  methods: {
    async updateCollection(collection) {
      try {
        const payload = {
          name: collection.name,
          form_number: collection.form_number,
          description: collection.description,
          status: collection.status,
          project_id: collection.projectId
        }
        const response = await fetch(`/api/collections/${collection.id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        })
        if (!response.ok) {
          const errorText = await response.text()
          throw new Error(`Failed to update collection: ${response.status} ${errorText}`)
        }
        await this.loadCollections()
  toast.success('Collection updated')
      } catch (error) {
  toast.error('Failed to update collection: ' + error.message)
      }
    },

    async deleteCollection(collectionId) {
      try {
        const response = await fetch(`/api/collections/${collectionId}`, {
          method: 'DELETE'
        })
        if (!response.ok) {
          const errorText = await response.text()
          throw new Error(`Failed to delete collection: ${response.status} ${errorText}`)
        }
        await this.loadCollections()
  toast.success('Collection deleted')
      } catch (error) {
  toast.error('Failed to delete collection: ' + error.message)
      }
    },
    async toggleArchive(collection) {
      try {
        const response = await fetch(`/api/collections/${collection.id}/archive`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ archived: !collection.archived })
        })
        if (!response.ok) {
          throw new Error(await response.text())
        }
        const data = await response.json()
        toast.success(collection.archived ? 'Collection unarchived' : 'Collection archived')
        // Update local state
        const idx = this.collections.findIndex(c => c.id === collection.id)
        if (idx !== -1) this.$set(this.collections, idx, { ...collection, archived: data.collection.archived })
      } catch (e) {
        toast.error('Failed to update archive state')
      }
    },
    promptDelete(collection) {
      this.collectionToDelete = collection
      this.deleteConfirmText = ''
      this.showDeleteModal = true
    },
    cancelDelete() {
      this.collectionToDelete = null
      this.deleteConfirmText = ''
      this.showDeleteModal = false
    },
    async confirmDelete() {
      if (!this.collectionToDelete) return
      await this.deleteCollection(this.collectionToDelete.id)
      this.cancelDelete()
    },
    async submitNewCollection() {
      try {
        const payload = {
          name: this.newCollection.name,
          form_number: this.newCollection.form_number,
          description: this.newCollection.description,
          status: this.newCollection.status,
          project_id: this.newCollection.projectId
        }
        const response = await fetch('/api/collections', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        })
        if (!response.ok) {
          const errorText = await response.text()
          throw new Error(`Failed to create collection: ${response.status} ${errorText}`)
        }
        await this.loadCollections()
        this.showCreateModal = false
        this.resetNewCollection()
  toast.success('Collection created')
      } catch (error) {
  toast.error('Failed to create collection: ' + error.message)
      }
    },
    // Helper to assign projectName to collections based on projectId
    assignProjectNames(collections) {
      if (!this.projects || this.projects.length === 0) return collections;
      return collections.map(col => {
  // Robustly match projectId (number or string)
  const colProjId = col.projectId !== undefined && col.projectId !== null ? Number(col.projectId) : null;
  const proj = this.projects.find(p => Number(p.id) === colProjId);
        return { ...col, projectName: proj ? proj.name : 'Unknown Project' };
      });
    },

    async loadDashboardData() {
      this.loading = true
      try {
        await this.loadProjects();
        await this.loadCollections();
        // Assign project names after both projects and collections are loaded
        this.collections = this.assignProjectNames(this.collections);
        this.recentCollections = this.assignProjectNames(this.recentCollections);
        await this.loadStats();
      } catch (error) {
        console.error('Failed to load collections dashboard:', error)
  toast.error('Failed to load collections dashboard')
      } finally {
        this.loading = false
      }
    },

    async loadCollections() {
      try {
        const response = await fetch('/api/collections')
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        
        const data = await response.json()
        this.collections = data
        
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


    async loadStats() {
      try {
        // Use the backend stats API for accurate calculation
        const response = await fetch('/api/collections/stats')
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        
        const stats = await response.json()
        console.log('📊 Stats from backend:', stats)
        this.stats = {
          total: stats.total,
          active: stats.active,
          totalTopics: stats.totalTopics,
          newThisWeek: stats.newThisWeek,
          avgTopics: stats.avgTopics
        }
        console.log('📊 Final stats applied:', this.stats)
      } catch (error) {
        console.error('Failed to load stats from backend, falling back to frontend calculation:', error)
        
        // Fallback to frontend calculation with hierarchical support
        
        // Helper function to recursively count all collections and topics
        const countCollectionsAndTopics = (collections) => {
          let totalCollections = 0
          let totalTopics = 0
          let activeCollections = 0
          
          collections.forEach(collection => {
            totalCollections++
            if (collection.status === 'active' || !collection.status) {
              activeCollections++
            }
            totalTopics += (collection.topics_count || 0)
            console.log(`Collection ${collection.name}: topics_count = ${collection.topics_count}`)
            
            // Recursively count children
            if (collection.children && collection.children.length > 0) {
              const childCounts = countCollectionsAndTopics(collection.children)
              totalCollections += childCounts.collections
              totalTopics += childCounts.topics
              activeCollections += childCounts.active
            }
          })
          
          return { collections: totalCollections, topics: totalTopics, active: activeCollections }
        }
        
        const counts = countCollectionsAndTopics(this.collections)
        const total = counts.collections
        const active = counts.active
        const totalTopics = counts.topics
        
        console.log(`📊 Fallback stats calculated: total=${total}, active=${active}, totalTopics=${totalTopics}`)
        
  // Calculate new this week from created_at
  const now = new Date()
  const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)
  const newThisWeek = (this.collections || []).filter(c => c.created_at && new Date(c.created_at) >= weekAgo).length

        // Calculate average topics per collection
        const avgTopics = total > 0 ? Math.round(totalTopics / total) : 0

        this.stats = {
          total,
          active,
          totalTopics,
          newThisWeek,
          avgTopics
        };
      }
    },

    async loadProjects() {
      try {
        // Fetch real projects from backend
  const response = await fetch('/api/projects/');
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        console.log('📁 Projects data received:', data);
        this.projects = data;
      } catch (error) {
        console.error('Failed to load projects:', error);
        this.projects = [];
      }
    },

    resetNewCollection() {
      this.newCollection = {
        name: '',
        form_number: '',
        description: '',
        status: 'active',
        projectId: null
      }
    },

    viewCollection(collection) {
      this.$router.push(`/organize/${collection.id}`)
    },

    editCollection(collection) {
      this.$router.push(`/organize/${collection.id}?edit=true`)
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
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem 2rem; /* remove top space before header */
  /* Use app background; remove mist-gray */
}

.full-width {
  grid-column: 1 / -1;
}

.dashboard-header {
  text-align: center;
  margin-bottom: 2rem;
}

.dashboard-header h1 {
  font-size: 2.5rem;
  margin: 0 0 0.5rem 0;
  font-weight: 300;
  color: var(--primary-deep-teal);
}

/* subtitle uses global styles */

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 3rem;
}

/* metric-icon uses global shape; only override font-size if needed */
.metric-icon { font-size: 2rem; }


/* metric-number and metric-detail now centralized in global style.css */

.content-grid {
  display: grid;
  grid-template-columns: 1fr 1fr; /* 50/50 split on desktop */
  gap: 1.5rem;
}

/* Use global .dashboard-section from style.css; spacing centralized */



.section-guidance {
  font-size: 0.875rem;
  color: var(--text-secondary-cool-gray);
  margin-bottom: 1rem;
}

.collections-list {
  max-height: 400px;
  overflow-y: auto;
}

.empty-state {
  text-align: center;
  padding: 2rem;
  color: var(--text-secondary-cool-gray);
}

.collection-item {
  background: var(--bg-white);
  border: 1px solid var(--border-light-gray);
  border-radius: var(--border-radius-lg);
  padding: 1.5rem;
  margin-bottom: 1rem;
  cursor: pointer;
  box-shadow: var(--box-shadow-sm);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.collection-item:hover {
  transform: translateY(-2px);
  box-shadow: var(--box-shadow-md);
}

.collection-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.collection-meta {
  font-size: 0.875rem;
  color: var(--text-secondary-cool-gray);
}

.collection-description {
  font-size: 0.875rem;
  color: var(--text-primary-charcoal);
  margin: 0.5rem 0;
}

.collection-project-info {
  font-size: 0.875rem;
  color: var(--text-secondary-cool-gray);
  margin-bottom: 0.5rem;
}

.collection-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.875rem;
  color: var(--text-secondary-cool-gray);
}

.collection-status {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-weight: 600;
}

.collection-status.active {
  background: var(--extended-cool-mint);
  color: var(--primary-deep-teal);
}

.collection-status.archived {
  background: var(--extended-dusty-rose);
  color: #991b1b; /* Consider adding a dark red variable */
}

.collection-status.draft {
  background: var(--extended-slate-purple);
  color: var(--bg-light-mist-gray);
}

.stats-overview {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 1.25rem;
}

.collections-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 1.25rem;
}

.collection-card {
  background: #fff;
  border: 1px solid var(--border-light-gray);
  border-radius: var(--border-radius-lg);
  box-shadow: var(--box-shadow-sm);
  padding: 1rem;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.collection-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--box-shadow-md);
}

.card-header { display: flex; justify-content: space-between; align-items: center; }
.card-badge { background: var(--primary-teal); color: #fff; padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.8rem; }
.card-description { color: var(--text-primary-charcoal); font-size: 0.9rem; margin: 0.5rem 0; }
.card-project { color: var(--text-secondary-cool-gray); font-size: 0.85rem; margin-bottom: 0.5rem; }
.card-footer { display: flex; justify-content: space-between; align-items: center; color: var(--text-secondary-cool-gray); font-size: 0.85rem; }
.card-actions { display: flex; gap: 0.5rem; }
.card-actions .btn.btn-sm { flex: 1 1 0; min-width: 96px; text-align: center; }
.card-action-btn { border: 1px solid var(--border-light-gray); padding: 0.35rem 0.6rem; border-radius: 6px; background: #fff; cursor: pointer; }
.card-action-btn.primary { background: var(--extended-steel-blue); color: #fff; border-color: var(--extended-steel-blue); }

.quick-actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}


/* Use global .quick-actions-section h2 styles from assets/style.css */

.section-description {
  color: var(--text-medium-gray);
  margin-bottom: 2rem;
  font-size: 1rem;
}

.action-card {
  background: var(--bg-light-mist-gray);
  border-radius: 8px;
  padding: 1.5rem;
  cursor: pointer;
  transition: transform 0.2s;
}

.action-card:hover {
  transform: translateY(-2px);
}

.action-icon {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

/* Enhanced theming for create button icon */
.create-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--extended-cool-mint, #d1f5ed) 0%, #ffffff 95%);
  color: var(--primary-deep-teal, #006d77);
  box-shadow: 0 2px 4px rgba(0,0,0,0.08);
  transition: transform .15s ease, box-shadow .2s ease, background .3s ease;
}
.create-icon .plus-svg { display: block; }
.quick-action-card:hover .create-icon {
  transform: translateY(-2px);
  box-shadow: 0 4px 10px rgba(0,0,0,0.15);
}

/* Dark container / dark mode support (if a parent adds .dark or body has .dark-theme) */
.dark .create-icon, .dark-theme .create-icon, .quick-action-card.dark-bg .create-icon {
  background: var(--primary-deep-teal, #006d77);
  color: #ffffff;
}

/* Fallback high-contrast mode detection */
@media (prefers-contrast: more) {
  .create-icon { box-shadow: 0 0 0 2px var(--primary-deep-teal, #006d77); }
  .dark .create-icon, .dark-theme .create-icon { box-shadow: 0 0 0 2px #ffffff; }
}

/* Optional: reduce motion */
@media (prefers-reduced-motion: reduce) {
  .create-icon { transition: none; }
  .quick-action-card:hover .create-icon { transform: none; }
}

.action-content h3 {
  font-size: 1.125rem;
  margin: 0 0 0.5rem 0;
  color: var(--primary-deep-teal);
}

.action-content p {
  font-size: 0.875rem;
  color: var(--text-secondary-cool-gray);
}

/* Using global .modal-overlay and .modal styles from assets/style.css */

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h2 {
  font-size: 1.5rem;
  margin: 0;
  font-weight: 600;
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
  color: var(--primary-deep-teal);
  font-size: 0.9rem;
}

.form-group input, .form-group textarea, .form-group select {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid var(--extended-lavender-gray);
  border-radius: 6px;
  font-size: 0.9rem;
  box-sizing: border-box;
}

.form-group input:focus, .form-group textarea:focus, .form-group select:focus {
  outline: none;
  border-color: var(--extended-steel-blue);
  box-shadow: 0 0 0 3px rgba(0, 90, 156, 0.1);
}

.form-help {
  display: block;
  font-size: 0.875rem;
  color: var(--text-secondary-cool-gray);
  margin-top: 0.25rem;
  line-height: 1.4;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid var(--extended-lavender-gray);
}

/* Responsive Design */
@media (max-width: 900px) {
  .collections-dashboard {
    padding: 1rem;
  }
  
  .metrics-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  
  .content-grid {
    grid-template-columns: 1fr; /* stack on smaller screens */
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
