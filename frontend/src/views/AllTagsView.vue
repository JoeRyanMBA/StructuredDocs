<template>
  <div class="all-tags">
    <h2>All Tags</h2>
    
    <p class="guidance-text">
      Manage all tags used throughout the system. Tags help categorize and organize tasks and other content.
    </p>

    <div class="page-actions">
      <button @click="openCreateModal" class="btn btn-primary">
        <i class="fas fa-plus"></i> Create New Tag
      </button>
    </div>

    <div v-if="loading" class="loading">Loading tags...</div>
    <div v-else-if="error" class="error">{{ error }}</div>

    <div v-else class="tags-content">
      <!-- Filters -->
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
            <button @click="applyFilters" class="btn btn-primary btn-sm">
              <i class="fas fa-search"></i> Search
            </button>
            <button @click="clearFilters" class="btn btn-secondary btn-sm">Clear Search</button>
          </div>
        </div>
      </div>

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
            <tr v-for="tag in filteredTags" :key="tag.id">
              <td class="id-cell">{{ tag.id }}</td>
              <td class="tag-name-cell">
                <div class="tag-name-display">{{ tag.name }}</div>
              </td>
              <td class="created-date">{{ formatDate(tag.created_at) }}</td>
              <td class="usage-count">{{ tag.usage_count || 0 }} topics</td>
              <td class="actions-cell">
                <div class="tag-actions">
                  <button @click="editTag(tag)" class="btn btn-sm btn-secondary">
                    <i class="fas fa-edit"></i> Edit
                  </button>
                  <button @click="deleteTag(tag)" class="btn btn-sm btn-danger">
                    <i class="fas fa-trash"></i> Delete
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <div v-if="showModal" class="modal-overlay" @click="closeModal">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h3>{{ isEditing ? 'Edit Tag' : 'Create New Tag' }}</h3>
          <button @click="closeModal" class="close-btn">&times;</button>
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
    <div v-if="showDeleteModal" class="modal-overlay" @click="closeDeleteModal">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h3>Confirm Delete</h3>
          <button @click="closeDeleteModal" class="close-btn">&times;</button>
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
export default {
  name: 'AllTagsView',
  data() {
    return {
      tags: [],
      filteredTags: [],
      searchQuery: '',
      loading: false,
      error: null,
      showModal: false,
      showDeleteModal: false,
      isEditing: false,
      tagToDelete: null,
      tagForm: {
        id: null,
        name: ''
      }
    }
  },
  
  mounted() {
    this.fetchTags()
  },
  
  methods: {
    async fetchTags() {
      this.loading = true
      this.error = null
      try {
        const response = await fetch('/api/tags/')
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        this.tags = await response.json()
        this.applyFilters() // Initialize filtered data
      } catch (error) {
        console.error('Failed to fetch tags:', error)
        this.error = 'Failed to load tags. Please try again.'
      } finally {
        this.loading = false
      }
    },

    applyFilters() {
      let filtered = [...this.tags]
      
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase()
        filtered = filtered.filter(tag => 
          tag.name.toLowerCase().includes(query)
        )
      }
      
      this.filteredTags = filtered
    },
    
    clearFilters() {
      this.searchQuery = ''
      this.applyFilters()
    },
    
    openCreateModal() {
      this.isEditing = false
      this.tagForm = {
        id: null,
        name: ''
      }
      this.showModal = true
    },
    
    editTag(tag) {
      this.isEditing = true
      this.tagForm = {
        id: tag.id,
        name: tag.name
      }
      this.showModal = true
    },
    
    closeModal() {
      this.showModal = false
      this.tagForm = {
        id: null,
        name: ''
      }
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
        this.closeModal()
        
      } catch (error) {
        console.error('Failed to save tag:', error)
        this.error = error.message || 'Failed to save tag. Please try again.'
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
        const response = await fetch(`/api/tags/${this.tagToDelete.id}`, {
          method: 'DELETE'
        })
        
        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}))
          throw new Error(errorData.error || `HTTP error! status: ${response.status}`)
        }
        
        await this.fetchTags()
        this.closeDeleteModal()
        
      } catch (error) {
        console.error('Failed to delete tag:', error)
        this.error = error.message || 'Failed to delete tag. Please try again.'
      }
    },
    
    formatDate(dateString) {
      if (!dateString) return 'N/A'
      return new Date(dateString).toLocaleDateString()
    }
  }
}
</script>

<style scoped>
.all-tags {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
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

/* Filters */
.filters-section {
  margin-bottom: 2rem;
  background: #f8f9fa;
  padding: 1.5rem;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.filter-row {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 1rem;
  align-items: end;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.filter-group label {
  font-weight: 600;
  color: #495057;
  font-size: 0.9rem;
}

.filter-input {
  padding: 0.5rem;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 0.9rem;
  background: white;
}

.filter-input:focus {
  outline: none;
  border-color: #205493;
  box-shadow: 0 0 0 2px rgba(32, 84, 147, 0.2);
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
.tags-table-container {
  overflow-x: auto;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.tags-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 600px;
}

.tags-table th,
.tags-table td {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid #e0e0e0;
}

.tags-table th {
  background-color: #f5f5f5;
  font-weight: 600;
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

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
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
  border-color: #007bff;
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
}

.warning {
  color: #f57c00;
  font-style: italic;
}

/* Button Styles */
.btn {
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
}

/* Responsive Design */
@media (max-width: 768px) {
  .all-tags {
    padding: 1rem;
  }
  
  .filter-row {
    grid-template-columns: 1fr;
    gap: 1rem;
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
