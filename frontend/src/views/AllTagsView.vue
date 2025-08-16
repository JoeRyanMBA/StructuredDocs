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
      <div class="tags-grid">
        <div v-for="tag in tags" :key="tag.id" class="tag-card">
          <div class="tag-name">{{ tag.name }}</div>
          <div class="tag-meta">
            <small>Created: {{ formatDate(tag.created_at) }}</small>
          </div>
          <div class="tag-actions">
            <button @click="editTag(tag)" class="btn btn-sm btn-secondary">
              <i class="fas fa-edit"></i> Edit
            </button>
            <button @click="deleteTag(tag)" class="btn btn-sm btn-danger">
              <i class="fas fa-trash"></i> Delete
            </button>
          </div>
        </div>
      </div>

      <div v-if="tags.length === 0" class="no-data">
        <p>No tags found. Create your first tag to get started.</p>
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
      } catch (error) {
        console.error('Failed to fetch tags:', error)
        this.error = 'Failed to load tags. Please try again.'
      } finally {
        this.loading = false
      }
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

.tags-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1rem;
}

.tag-card {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 1rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  transition: box-shadow 0.2s;
}

.tag-card:hover {
  box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}

.tag-name {
  font-size: 1.2rem;
  font-weight: 600;
  color: #333;
  margin-bottom: 0.5rem;
}

.tag-meta {
  color: #666;
  font-size: 0.9rem;
  margin-bottom: 1rem;
}

.tag-actions {
  display: flex;
  gap: 0.5rem;
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
  background-color: #007bff;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #0056b3;
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
</style>
