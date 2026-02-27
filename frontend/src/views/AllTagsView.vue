<template>
  <div class="all-tags">
  <h1>All Tags</h1>
    
  <p class="subtitle">
      Manage all tags used throughout the system. Tags help categorize and organize tasks and other content.
    </p>

    <div class="info-panel">
      <h2>How Tags Work</h2>
      <p>
        Tags are reusable labels you can assign to <strong>projects, collections, topics, stakeholders,
        images, and links</strong> to categorize and filter content across the system.
      </p>
      <div class="info-columns">
        <div class="info-col">
          <h3>Creating Tags</h3>
          <p>Click <strong>Create New Tag</strong> below. Tag names must be unique. Once created, a tag
          is available on any entity in the system.</p>
        </div>
        <div class="info-col">
          <h3>Assigning Tags</h3>
          <p>Open any project, collection, topic, stakeholder, image, or link and use the
          <strong>Tags</strong> field — type to search existing tags or create a new one inline.</p>
        </div>
        <div class="info-col">
          <h3>Filtering by Tag</h3>
          <p>Each list view (Topics, Links, Images, etc.) supports tag filtering so you can quickly
          surface all items sharing a label regardless of where they live.</p>
        </div>
        <div class="info-col">
          <h3>Renaming &amp; Deleting</h3>
          <p>Renaming a tag updates it everywhere it is used. Deleting a tag removes it from all
          entities. The <strong>Usage</strong> column shows total assignments per tag.</p>
        </div>
      </div>
    </div>

    <div class="page-actions">
      <button @click="openCreateModal" class="btn btn-primary">
  <span class="icon-plus">➕︎</span> Create New Tag
      </button>
    </div>

    <!-- Filters Section -->
    <div class="filters-section">
      <div class="filter-row">
        <div class="filter-group">
          <label>Search:</label>
          <input
            v-model="searchQuery"
            type="text"
            class="filter-input"
            placeholder="Search tags..."
            @keyup.enter="applyFilters"
          />
        </div>
        <div class="filter-group">
          <label>Sort by:</label>
          <select v-model="sortBy" @change="applyFilters" class="filter-input">
            <option value="name_asc">Name A→Z</option>
            <option value="name_desc">Name Z→A</option>
            <option value="usage_desc">Most used</option>
            <option value="usage_asc">Least used</option>
            <option value="newest">Newest</option>
            <option value="oldest">Oldest</option>
          </select>
        </div>
        <div class="filter-group actions-group">
          <div class="button-group">
            <button @click="applyFilters" class="btn btn-primary btn-sm">
              <i class="bi bi-search"></i> Search
            </button>
            <button @click="clearFilters" class="btn btn-secondary btn-sm"><i class="bi bi-x"></i> Clear Search</button>
          </div>
        </div>
      </div>
    </div>

  <div v-if="loading" class="loading">Loading tags...</div>
  <div v-else-if="error" class="error">{{ error }}</div>

    <div v-else class="tags-content">
      <p class="table-instruction">Select a tag to edit.</p>

      <div v-if="filteredTags.length === 0 && !searchQuery" class="no-data">
        <p>No tags found. Create your first tag to get started.</p>
      </div>
      <div v-else-if="filteredTags.length === 0 && searchQuery" class="no-data">
        <p>No tags match your search criteria.</p>
      </div>
      
      <div v-else class="tags-table-container">
        <table class="tags-table">
          <thead>
            <tr>
              <th class="id-column">ID</th>
              <th>Tag Name</th>
              <th>Created Date</th>
              <th>Usage Count</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="tag in filteredTags" :key="tag.id || ('name-'+tag.name)">
              <td class="id-cell">{{ tag.id }}</td>
              <td class="tag-name-cell">
                <div class="tag-name-display">{{ formatTagName(tag.name) }}</div>
              </td>
              <td class="created-date">{{ formatDate(tag.created_at) }}</td>
              <td class="usage-count">{{ tag.total_count || tag.usage_count || 0 }}</td>
              <td class="actions-cell">
                <div class="tag-actions">
                  <button @click="editTag(tag)" class="btn btn-sm btn-secondary">
                    <i class="bi bi-pencil-square"></i> Edit
                  </button>
                  <button @click="deleteTag(tag)" class="btn btn-sm btn-danger">
                    <i class="bi bi-trash"></i> Delete
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Create/Edit Modal -->
  <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="custom-modal" @click.stop>
        <div class="modal-header-row modal-header">
          <h3>{{ isEditing ? 'Edit Tag' : 'Create New Tag' }}</h3>
          <button @click="closeModal" class="plain-close close-btn">&times;</button>
        </div>
        
        <div class="modal-body">
          <form @submit.prevent="saveTag">
            <div class="form-group">
              <label for="tagName">Tag Name *</label>
              <input
                id="tagName"
                v-model="tagForm.name"
                type="text"
                class="form-input"
                placeholder="Enter tag name"
                required
                maxlength="100"
              />
            </div>
          </form>
        </div>
        
        <div class="modal-footer">
          <button @click="closeModal" class="btn btn-secondary">Cancel</button>
          <button @click="saveTag" class="btn btn-primary" :disabled="!tagForm.name.trim()">
            {{ isEditing ? 'Update Tag' : 'Create Tag' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
  <div v-if="showDeleteModal" class="modal-overlay" @click.self="closeDeleteModal">
      <div class="custom-modal" @click.stop>
        <div class="modal-header-row modal-header">
          <h3>Confirm Delete</h3>
          <button @click="closeDeleteModal" class="plain-close close-btn">&times;</button>
        </div>
        
        <div class="modal-body">
          <p>Are you sure you want to delete the tag "{{ tagToDelete?.name }}"?</p>
          <p class="warning">This action cannot be undone.</p>
        </div>
        
        <div class="modal-footer">
          <button @click="closeDeleteModal" class="btn btn-secondary">Cancel</button>
          <button @click="confirmDelete" class="btn btn-danger">Delete Tag</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { toast } from '@/composables/useToast'
import unsavedChangesGuard from '@/mixins/unsavedChangesGuard.js'
export default {
  name: 'AllTagsView',
  mixins: [unsavedChangesGuard],
  data() {
    return {
      tags: [],
      filteredTags: [],
      searchQuery: '',
      sortBy: 'name_asc',
      loading: false,
      error: null,
      showModal: false,
      showDeleteModal: false,
      isEditing: false,
      tagToDelete: null,
  tagForm: {
        id: null,
        name: ''
  },
  lastSavedSnapshot: ''
    }
  },
  
  mounted() {
    this.fetchTags()
  },
  
  methods: {
    normalizeTags(data) {
      // Ensure we always work with an array of objects: [{id, name, created_at, usage_count}]
      const arr = Array.isArray(data) ? data : (data == null ? [] : [data])
      return arr
        .filter(item => item != null)
        .map(item => {
          if (typeof item === 'string') {
            return { id: null, name: item, created_at: null, usage_count: 0 }
          }
          // If backend returns a dict-like object but with different keys, map name if possible
          if (typeof item === 'object') {
            return {
              id: item.id ?? null,
              name: item.name ?? String(item.tag || item.title || ''),
              created_at: item.created_at ?? null,
              usage_count: item.total_count ?? item.usage_count ?? item.task_count ?? 0
            }
          }
          return { id: null, name: String(item), created_at: null, usage_count: 0 }
        })
    },
    async fetchTags() {
      this.loading = true
      this.error = null
      try {
  const response = await fetch('/api/tags/');
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
  const data = await response.json()
  this.tags = this.normalizeTags(data)
        this.applyFilters() // Initialize filtered data
      } catch (error) {
        console.error('Failed to fetch tags:', error)
        this.error = 'Failed to load tags. Please try again.'
      } finally {
        this.loading = false
      }
    },

    applyFilters() {
      let filtered = Array.isArray(this.tags) ? [...this.tags] : this.normalizeTags(this.tags)
      
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase()
        filtered = filtered.filter(tag => {
          const name = (tag && tag.name) ? String(tag.name) : ''
          return name.toLowerCase().includes(query)
        })
      }

      const sorts = {
        name_asc:   (a, b) => a.name.localeCompare(b.name),
        name_desc:  (a, b) => b.name.localeCompare(a.name),
        usage_desc: (a, b) => (b.usage_count || 0) - (a.usage_count || 0),
        usage_asc:  (a, b) => (a.usage_count || 0) - (b.usage_count || 0),
        newest:     (a, b) => new Date(b.created_at || 0) - new Date(a.created_at || 0),
        oldest:     (a, b) => new Date(a.created_at || 0) - new Date(b.created_at || 0),
      }
      filtered.sort(sorts[this.sortBy] || sorts.name_asc)

      this.filteredTags = filtered
    },
    
    clearFilters() {
      this.searchQuery = ''
      this.sortBy = 'name_asc'
      this.applyFilters()
    },
    
    openCreateModal() {
      this.isEditing = false
      this.tagForm = {
        id: null,
        name: ''
      }
      this.showModal = true
      this.$nextTick(() => { this.lastSavedSnapshot = JSON.stringify(this.tagForm) })
    },
    
    editTag(tag) {
      this.isEditing = true
      this.tagForm = {
        id: tag.id,
        name: tag.name
      }
      this.showModal = true
      this.$nextTick(() => { this.lastSavedSnapshot = JSON.stringify(this.tagForm) })
    },
    
    closeModal() {
      this.showModal = false
      this.tagForm = {
        id: null,
        name: ''
      }
      this.lastSavedSnapshot = ''
    },
    
  async saveTag() {
      try {
        const url = this.isEditing ? `/api/tags/${this.tagForm.id}` : '/api/tags/'
        const method = this.isEditing ? 'PUT' : 'POST'
        
        const response = await fetch(url, {
          method: method,
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            name: this.tagForm.name.trim()
          })
        })
        
        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}))
          throw new Error(errorData.error || `HTTP error! status: ${response.status}`)
        }
        
  await this.fetchTags()
  this.lastSavedSnapshot = JSON.stringify(this.tagForm)
  this.closeModal()
  toast.success(this.isEditing ? 'Tag updated' : 'Tag created')
        
      } catch (error) {
        console.error('Failed to save tag:', error)
  this.error = error.message || 'Failed to save tag. Please try again.'
  toast.error(this.error)
      }
  },
    
    deleteTag(tag) {
      this.tagToDelete = tag
      this.showDeleteModal = true
    },
    
    closeDeleteModal() {
      this.showDeleteModal = false
      this.tagToDelete = null
    },
    
    async confirmDelete() {
      try {
        const response = await fetch(`/api/tags/${this.tagToDelete.id}`, { method: 'DELETE' })
        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}))
          const msg = errorData.error || `HTTP error! status: ${response.status}`
          // If backend indicates active usage, offer force delete
          if (/Cannot delete tag; referenced by/.test(msg)) {
            const proceed = window.confirm(msg + '\n\nForce delete? This will remove the tag from all referencing tasks.')
            if (proceed) {
              const forceResp = await fetch(`/api/tags/${this.tagToDelete.id}?force=1`, { method: 'DELETE' })
              if (!forceResp.ok) {
                const fd = await forceResp.json().catch(()=>({}))
                throw new Error(fd.error || 'Force delete failed')
              }
              const body = await forceResp.json()
              toast.success(`Tag force deleted (removed from ${body.removed_task_refs || 0} task(s))`)
              await this.fetchTags()
              this.closeDeleteModal()
              return
            }
          }
          throw new Error(msg)
        }
        const body = await response.json().catch(()=>({}))
        toast.success(body.message || 'Tag deleted')
        await this.fetchTags()
        this.closeDeleteModal()
        
      } catch (error) {
        console.error('Failed to delete tag:', error)
  this.error = error.message || 'Failed to delete tag. Please try again.'
  toast.error(this.error)
      }
    },
    
    formatDate(dateString) {
      if (!dateString) return 'N/A'
      return new Date(dateString).toLocaleDateString()
    },
    isDirty() {
      if (!this.showModal) return false
      try { return JSON.stringify(this.tagForm) !== this.lastSavedSnapshot } catch(e){ return false }
    },
    formatTagName(name){
      if(typeof name !== 'string') return ''
      return name
    },
  }
}
</script>

<style scoped>
.all-tags {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.info-panel {
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 2rem;
}

.info-panel h2 {
  font-size: 1.1rem;
  font-weight: 600;
  margin: 0 0 0.75rem;
  color: #333;
}

.info-panel > p {
  color: #555;
  margin-bottom: 1.25rem;
  line-height: 1.6;
}

.info-columns {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.25rem;
}

.info-col h3 {
  font-size: 0.875rem;
  font-weight: 600;
  color: #444;
  margin: 0 0 0.4rem;
}

.info-col p {
  font-size: 0.875rem;
  color: #666;
  line-height: 1.5;
  margin: 0;
}

.guidance-text {
  color: #666;
  margin-bottom: 2rem;
  font-size: 1.1rem;
  line-height: 1.5;
}

.page-actions {
  margin-bottom: 2rem;
  display: flex;
  justify-content: flex-end;
}

.table-instruction {
  color: #6b7280;
  font-size: 0.9rem;
  margin: 1rem 0 0.5rem 0;
  font-style: italic;
}

.loading, .error {
  text-align: center;
  padding: 2rem;
  font-size: 1.1rem;
}

.error {
  color: #d32f2f;
  background-color: #ffebee;
  border: 1px solid #ffcdd2;
  border-radius: 4px;
}

/* Tags Table */
.tags-table {
  min-width: 600px;
}

.tags-table th,
.tags-table td {
  padding: 1rem;
}

.tags-table th {
  color: #333;
  font-size: 0.875rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.id-column,
.id-cell {
  width: 60px;
  text-align: center;
  font-size: 0.85rem;
  color: #666;
  white-space: nowrap;
}

.tags-table tbody tr {
  transition: background-color 0.2s ease;
}

.tags-table tbody tr:hover {
  background-color: #f8f9fa;
}

.tag-name-cell {
  max-width: 250px;
}

.tag-name-display {
  font-weight: 600;
  color: #333;
  font-size: 1rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  word-break: normal;
  display: block;
  width: 100%;
}

.created-date {
  color: #666;
  font-size: 0.9rem;
}

.usage-count {
  color: #666;
  font-size: 0.9rem;
}

.actions-cell {
  min-width: 150px;
}

.tag-actions {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.no-data {
  text-align: center;
  padding: 3rem;
  color: #666;
  font-size: 1.1rem;
}

/* Modal Styles - use global .modal-overlay; keep .custom-modal for sizing */
.custom-modal {
  background: white;
  border-radius: 8px;
  min-width: 400px;
  max-width: 90vw;
  max-height: 90vh;
  overflow: auto;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #e0e0e0;
}

.modal-header h3 {
  margin: 0;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #666;
  cursor: pointer;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  color: #333;
}

.modal-body {
  padding: 1.5rem;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  padding: 1rem 1.5rem;
  border-top: 1px solid #e0e0e0;
  background-color: #f9f9f9;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #333;
}

.form-input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  box-sizing: border-box;
}

.form-input:focus {
  outline: none;
  border-color: var(--primary-medium-teal);
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
}

.warning {
  color: #f57c00;
  font-style: italic;
}

/* Button Styles */
/* .btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  transition: background-color 0.2s;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background-color: #205493;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #005E7B;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background-color: #545b62;
}

.btn-danger {
  background-color: #dc3545;
  color: white;
}

.btn-danger:hover {
  background-color: #c82333;
}

.btn-sm {
  padding: 0.375rem 0.75rem;
  font-size: 0.8rem;
}*/

/* Responsive Design */
@media (max-width: 768px) {
  .all-tags {
    padding: 1rem;
  }
  
  .tags-table-container {
    margin: 0 -1rem;
    border-radius: 0;
  }
  
  .tags-table {
    min-width: 500px;
  }
  
  .tags-table th,
  .tags-table td {
    padding: 0.75rem 0.5rem;
    font-size: 0.875rem;
  }
  
  .tag-actions {
    flex-direction: column;
    gap: 0.25rem;
    align-items: stretch;
  }
  
  .tag-actions .btn {
    width: 100%;
    justify-content: center;
  }
}
</style>
