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
      <h1>Collections Dashboard <HelpIcon feature="collections.dashboard" /></h1>
      <p class="subtitle">Manage and organize your document collections</p>
    </div>

    <!-- Quick Actions Section (aligned with Start Page) -->
    <div class="quick-actions-section">
      <h2>Quick Actions</h2>
      <p class="section-description">Manage your collections and topics</p>
      <div class="quick-actions-grid">
        <button class="quick-action-card" @click="showCreateModal = true">
          <div class="action-icon create-icon" aria-hidden="true">
            <IconPlus className="plus-svg" size="28" />
          </div>
          <div class="action-content" title="Start organizing topics into collections">
            <h3>Create Collection</h3>
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
                <span class="obj-id-badge">#{{ collection.id }}</span>
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
                <span class="obj-id-badge">#{{ collection.id }}</span>
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
                  <ArchiveToggleButton
                    v-if="isAdmin"
                    :archived="collection.archived"
                    entity-label="collection"
                    @toggle="state => toggleArchiveState(collection, state)"
                  />
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
        <div class="modal-header-row modal-header">
          <h2>Create New Collection</h2>
          <button @click="showCreateModal = false" class="plain-close close-btn">×</button>
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
            <label for="collectionDescription">Subtitle</label>
            <input
              id="collectionDescription"
              v-model="newCollection.description"
              type="text"
              placeholder="Subtitle (optional — appears on PDF cover page)"
            />
          </div>
          
          <div class="form-group">
            <label for="collectionStatus">Status</label>
            <select id="collectionStatus" v-model="newCollection.status">
              <option value="active">Active</option>
              <option value="draft">Draft</option>
              <option value="archived">Archived</option>
            </select>
          </div>
          
          <div class="modal-footer modal-actions">
            <button type="button" @click="showCreateModal = false" class="secondary-btn">
              Cancel
            </button>
            <button type="submit" class="primary-btn">Create Collection</button>
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
        <div class="modal-header-row modal-header">
          <h2>Delete Collection</h2>
          <button @click="cancelDelete" class="plain-close close-btn">×</button>
        </div>
        <div class="modal-body">
          <p><strong>Warning:</strong> This will permanently remove the collection <strong>{{ collectionToDelete?.name }}</strong> and all nested child collections. Topics inside remain in the system and are not deleted.</p>
          <p>Type the collection name to confirm:</p>
          <input v-model="deleteConfirmText" :placeholder="collectionToDelete?.name" />
          <p v-if="deleteError" class="delete-error-msg">{{ deleteError }}</p>
          <div class="modal-footer modal-actions" style="margin-top:1rem;">
            <button type="button" class="secondary-btn" @click="cancelDelete">Cancel</button>
            <button type="button" class="btn-danger" :disabled="deleteConfirmText !== collectionToDelete?.name" @click="confirmDelete">Delete</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import CompactToolbar from '../components/CompactToolbar.vue'
import ArchiveToggleButton from '@/components/ArchiveToggleButton.vue'
import IconPlus from '@/components/icons/IconPlus.vue'
import { getCollections, saveCollections } from '@/api/collections.js'
import { apiRequest } from '@/api/base.js'
import { toast } from '@/composables/useToast'

import HelpIcon from '@/components/HelpIcon.vue'

export default {
  name: 'CollectionsDashboard',
  components: { CompactToolbar, ArchiveToggleButton, IconPlus, HelpIcon },
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
      deleteError: '',
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
        await apiRequest(`/api/collections/${collection.id}`, {
          method: 'PUT',
          body: JSON.stringify(payload)
        })
        await this.loadCollections()
  toast.success('Collection updated')
      } catch (error) {
  toast.error('Failed to update collection: ' + error.message)
      }
    },

    async deleteCollection(collectionId) {
      this.deleteError = ''
      try {
        await apiRequest(`/api/collections/${collectionId}`, {
          method: 'DELETE'
        })
        await this.loadCollections()
        toast.success('Collection deleted')
      } catch (error) {
        this.deleteError = error.message
      }
    },
    async toggleArchiveState(collection, newState) {
      try {
        const data = await apiRequest(`/api/collections/${collection.id}/archive`, {
          method: 'POST',
          body: JSON.stringify({ archived: newState })
        })
        toast.success(newState ? 'Collection archived' : 'Collection unarchived')
        // Update local state
        const idx = this.collections.findIndex(c => c.id === collection.id)
        if (idx !== -1) this.collections.splice(idx, 1, { ...collection, archived: data.collection.archived })
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
      this.deleteError = ''
      this.showDeleteModal = false
    },
    async confirmDelete() {
      if (!this.collectionToDelete) return
      await this.deleteCollection(this.collectionToDelete.id)
      if (!this.deleteError) this.cancelDelete()
    },
    async submitNewCollection() {
      try {
        const payload = {
          name: this.newCollection.name,
          form_number: this.newCollection.form_number,
          description: this.newCollection.description,
          status: this.newCollection.status,
          projectId: this.newCollection.projectId ? Number(this.newCollection.projectId) : null
        }
        await apiRequest('/api/collections', {
          method: 'POST',
          body: JSON.stringify(payload)
        })
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
  // Support both camelCase and snake_case project id keys
  const rawProjectId = col.projectId ?? col.project_id ?? null;
  const colProjId = rawProjectId !== null ? Number(rawProjectId) : null;
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


    // Recursively flatten a tree of collections
    flattenCollections(collections) {
      let flat = [];
      for (const col of collections) {
        flat.push(col);
        if (col.children && col.children.length > 0) {
          flat = flat.concat(this.flattenCollections(col.children));
        }
      }
      return flat;
    },

    async loadCollections() {
      try {
        const data = await apiRequest('/api/collections')
        // Flatten the tree so all collections (roots and children) are shown
        const flat = this.flattenCollections(data)
        this.collections = flat
        // Get recent collections (last 5, sorted by updated_at)
        this.recentCollections = [...flat]
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
        const stats = await apiRequest('/api/collections/stats')
        // Use total from backend (all collections)
        this.stats = {
          total: stats.total,
          active: stats.active,
          totalTopics: stats.totalTopics,
          newThisWeek: stats.newThisWeek,
          avgTopics: stats.avgTopics
        }
      } catch (error) {
        // Fallback: count all loaded collections (flat)
        const flat = this.collections || []
        const total = flat.length
        const active = flat.filter(c => c.status === 'active' || !c.status).length
        const totalTopics = flat.reduce((sum, c) => sum + (c.topics_count || 0), 0)
        const now = new Date()
        const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)
        const newThisWeek = flat.filter(c => c.created_at && new Date(c.created_at) >= weekAgo).length
        const avgTopics = total > 0 ? Math.round(totalTopics / total) : 0
        this.stats = { total, active, totalTopics, newThisWeek, avgTopics }
      }
    },

    async loadProjects() {
      try {
        // Fetch real projects from backend
        const data = await apiRequest('/api/projects/');
        console.log('📁 Projects data received:', data);
        this.projects = Array.isArray(data) ? data : (Array.isArray(data?.projects) ? data.projects : []);
      } catch (error) {
        console.error('Failed to load projects:', error);
        this.projects = [];
      }
    },

    createNewCollection() {
      this.showCreateModal = true
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
.card-actions { 
  display: flex; 
  gap: 0.5rem; 
  align-items: center;
  justify-content: flex-end;
}

.card-actions .btn.btn-sm { 
  flex: 0 0 auto; /* Don't grow/shrink, use natural width */
  min-width: 72px; /* Reduced for better proportions */
  height: 32px; /* Explicit height for perfect alignment */
  text-align: center; 
  padding: 0.35rem 0.65rem; /* Consistent with global btn-sm */
  font-size: 0.85rem;
  line-height: 1.2;
  border-radius: 4px;
  box-sizing: border-box;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}
.card-action-btn { border: 1px solid var(--border-light-gray); padding: 0.35rem 0.6rem; border-radius: 6px; background: #fff; cursor: pointer; }
.card-action-btn.primary { background: var(--extended-steel-blue); color: #fff; border-color: var(--extended-steel-blue); }

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
  /* Align with global quick-action-card icon styling */
  width: var(--quick-action-icon-size);
  height: var(--quick-action-icon-size);
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  background: var(--bg-light-mist-gray);
  color: var(--primary-deep-teal);
}
.create-icon .plus-svg { width: 2rem; height: 2rem; }

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

.delete-error-msg {
  margin-top: 0.75rem;
  color: var(--error-red, #dc3545);
  font-size: 0.9rem;
  font-weight: 500;
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

.obj-id-badge {
  font-size: 0.7rem;
  font-weight: 500;
  color: #5a6a8a;
  background: #e8eef7;
  border: 1px solid #c5d3f0;
  border-radius: 10px;
  padding: 0.1rem 0.45rem;
  margin-left: 0.4rem;
  white-space: nowrap;
}
</style>
