<template>
  <div class="all-milestones">
  <h1>All Milestones</h1>
    
  <p class="subtitle">
      Manage project milestones and deadlines. Milestones help track important dates and deliverables across all projects.
    </p>

    <div class="page-actions">
      <button @click="showModal = true" class="btn btn-primary">
  <span class="icon-plus">➕︎</span> Create New Milestone
      </button>
    </div>

    <div v-if="loading" class="loading">Loading milestones...</div>
    <div v-else-if="error" class="error">{{ error }}</div>

    <div v-else class="milestones-content">
      <!-- Filters -->
      <div class="filters-section">
        <div class="filter-row">
          <div class="filter-group">
            <label>Search:</label>
            <input
              v-model="searchQuery"
              type="text"
              class="filter-input"
              placeholder="Search milestones..."
              @input="applyFilters"
            />
          </div>
          <div class="filter-group">
            <label>Project:</label>
            <select v-model="projectFilter" @change="applyFilters" class="filter-input">
              <option value="">All Projects</option>
              <option v-for="project in uniqueProjects" :key="project" :value="project">{{ project }}</option>
            </select>
          </div>
          <div class="filter-group">
            <label>Status:</label>
            <select v-model="statusFilter" @change="applyFilters" class="filter-input">
              <option value="">All Statuses</option>
              <option value="planned">Planned</option>
              <option value="in-progress">In Progress</option>
              <option value="completed">Completed</option>
              <option value="overdue">Overdue</option>
            </select>
          </div>
          <div class="filter-group">
            <div class="button-group">
              <button @click="applyFilters" class="btn btn-primary btn-sm">
                <i class="bi bi-search"></i> Search
              </button>
              <button @click="clearFilters" class="btn btn-secondary btn-sm">Clear Filters</button>
            </div>
          </div>
        </div>
      </div>

      <p class="table-instruction">Select a milestone to edit.</p>

      <div class="milestones-table-container">
        <table class="milestones-table">
          <thead>
            <tr>
              <th class="id-column">ID</th>
              <th>Milestone</th>
              <th>Project</th>
              <th>Date</th>
              <th>Status</th>
              <th>Completion Date</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="milestone in filteredMilestones" :key="milestone.id">
              <td class="id-cell">{{ milestone.id }}</td>
              <td class="milestone-cell">
                <div class="milestone-name">{{ milestone.name }}</div>
                <div class="milestone-desc" v-if="milestone.description">{{ milestone.description }}</div>
              </td>
              <td>{{ milestone.project_name || '-' }}</td>
              <td>{{ formatDate(milestone.date) || '-' }}</td>
              <td>
                <span :class="`status-badge status-${milestone.status}`">
                  {{ formatStatus(milestone.status) }}
                </span>
              </td>
              <td>{{ formatDate(milestone.completion_date) || '-' }}</td>
              <td class="actions-cell">
                <button @click="editMilestone(milestone)" class="btn btn-sm btn-secondary">
                  <i class="bi bi-pencil-square"></i> Edit
                </button>
                <button @click="deleteMilestone(milestone)" class="btn btn-sm btn-danger">
                  <i class="bi bi-trash"></i> Delete
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="milestones.length === 0" class="no-data">
        <p>No milestones found. Create your first milestone to get started.</p>
      </div>
    </div>

    <!-- Create/Edit Modal -->
  <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="custom-modal" @click.stop>
        <div class="modal-header">
          <h3>{{ isEditing ? 'Edit Milestone' : 'Create New Milestone' }}</h3>
          <button @click="closeModal" class="close-btn">&times;</button>
        </div>
        
        <div class="modal-body">
          <form @submit.prevent="saveMilestone">
            <div class="form-group">
              <label for="milestoneName">Milestone Name *</label>
              <input
                id="milestoneName"
                v-model="milestoneForm.name"
                type="text"
                class="form-input"
                placeholder="Enter milestone name"
                required
                maxlength="200"
              />
            </div>

            <div class="form-group">
              <label for="milestoneProject">Project *</label>
              <select
                id="milestoneProject"
                v-model="milestoneForm.project_id"
                class="form-input"
                required
              >
                <option value="">Select a project</option>
                <option v-for="project in projects" :key="project.id" :value="project.id">
                  {{ project.name }}
                </option>
              </select>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label for="milestoneDate">Target Date</label>
                <input
                  id="milestoneDate"
                  v-model="milestoneForm.date"
                  type="date"
                  class="form-input"
                />
              </div>
              <div class="form-group">
                <label for="milestoneStatus">Status</label>
                <select
                  id="milestoneStatus"
                  v-model="milestoneForm.status"
                  class="form-input"
                >
                  <option value="planned">Planned</option>
                  <option value="in-progress">In Progress</option>
                  <option value="completed">Completed</option>
                  <option value="overdue">Overdue</option>
                </select>
              </div>
            </div>

            <div class="form-group">
              <label for="milestoneDescription">Description</label>
              <textarea
                id="milestoneDescription"
                v-model="milestoneForm.description"
                class="form-input"
                placeholder="Describe the milestone and deliverables"
                rows="4"
              ></textarea>
            </div>
          </form>
        </div>
        
        <div class="modal-footer">
          <button @click="closeModal" class="btn btn-secondary">Cancel</button>
          <button @click="saveMilestone" class="btn btn-primary" :disabled="!milestoneForm.name.trim() || !milestoneForm.project_id">
            {{ isEditing ? 'Update Milestone' : 'Create Milestone' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
  <div v-if="showDeleteModal" class="modal-overlay" @click.self="closeDeleteModal">
      <div class="custom-modal" @click.stop>
        <div class="modal-header">
          <h3>Confirm Delete</h3>
          <button @click="closeDeleteModal" class="close-btn">&times;</button>
        </div>
        
        <div class="modal-body">
          <p>Are you sure you want to delete the milestone "{{ milestoneToDelete?.name }}"?</p>
          <p class="warning">This action cannot be undone.</p>
        </div>
        
        <div class="modal-footer">
          <button @click="closeDeleteModal" class="btn btn-secondary">Cancel</button>
          <button @click="confirmDelete" class="btn btn-danger">Delete Milestone</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { toast } from '@/composables/useToast'
import unsavedChangesGuard from '@/mixins/unsavedChangesGuard.js'
export default {
  name: 'AllMilestonesView',
  mixins: [unsavedChangesGuard],
  data() {
    return {
      milestones: [],
      filteredMilestones: [],
      searchQuery: '',
      projectFilter: '',
      statusFilter: '',
      projects: [],
      loading: false,
      error: null,
      showModal: false,
      showDeleteModal: false,
      isEditing: false,
      milestoneToDelete: null,
  milestoneForm: {
        id: null,
        name: '',
        project_id: '',
        date: '',
        status: 'planned',
        description: ''
  },
  lastSavedMilestoneSnapshot: ''
    }
  },

  computed: {
    uniqueProjects() {
      const projects = [...new Set(this.milestones.map(m => m.project_name).filter(proj => proj))]
      return projects.sort()
    }
  },
  
  mounted() {
    this.fetchMilestones()
    this.fetchProjects()
  },
  
  methods: {
    async fetchMilestones() {
      this.loading = true
      this.error = null
      try {
        const response = await fetch('/api/milestones/')
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        this.milestones = await response.json()
        this.applyFilters() // Initialize filtered data
      } catch (error) {
        console.error('Failed to fetch milestones:', error)
        this.error = 'Failed to load milestones. Please try again.'
        toast.error('Failed to load milestones')
      } finally {
        this.loading = false
      }
    },

    applyFilters() {
      let filtered = [...this.milestones]
      
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase()
        filtered = filtered.filter(milestone => 
          milestone.name.toLowerCase().includes(query) ||
          (milestone.description && milestone.description.toLowerCase().includes(query)) ||
          (milestone.project_name && milestone.project_name.toLowerCase().includes(query))
        )
      }
      
      if (this.projectFilter) {
        filtered = filtered.filter(milestone => milestone.project_name === this.projectFilter)
      }
      
      if (this.statusFilter) {
        filtered = filtered.filter(milestone => milestone.status === this.statusFilter)
      }
      
      this.filteredMilestones = filtered
    },
    
    clearFilters() {
      this.searchQuery = ''
      this.projectFilter = ''
      this.statusFilter = ''
      this.applyFilters()
    },

    async fetchProjects() {
      try {
        const response = await fetch('/api/milestones/projects')
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        this.projects = await response.json()
      } catch (error) {
        console.error('Failed to fetch projects:', error)
      }
    },
    
    openCreateModal() {
      this.isEditing = false
      this.milestoneForm = {
        id: null,
        name: '',
        project_id: '',
        date: '',
        status: 'planned',
        description: ''
      }
      this.showModal = true
      this.$nextTick(()=>{ this.lastSavedMilestoneSnapshot = JSON.stringify(this.milestoneForm) })
    },
    
    editMilestone(milestone) {
      this.isEditing = true
      this.milestoneForm = {
        id: milestone.id,
        name: milestone.name,
        project_id: milestone.project_id,
        date: milestone.date || '',
        status: milestone.status,
        description: milestone.description || ''
      }
      this.showModal = true
      this.$nextTick(()=>{ this.lastSavedMilestoneSnapshot = JSON.stringify(this.milestoneForm) })
    },
    
    closeModal() {
      this.showModal = false
      this.milestoneForm = {
        id: null,
        name: '',
        project_id: '',
        date: '',
        status: 'planned',
        description: ''
      }
      this.lastSavedMilestoneSnapshot = ''
    },
    
  async saveMilestone() {
      try {
        const url = this.isEditing ? `/api/milestones/${this.milestoneForm.id}` : '/api/milestones/'
        const method = this.isEditing ? 'PUT' : 'POST'
        
        const response = await fetch(url, {
          method: method,
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            name: this.milestoneForm.name.trim(),
            project_id: parseInt(this.milestoneForm.project_id),
            date: this.milestoneForm.date || null,
            status: this.milestoneForm.status,
            description: this.milestoneForm.description.trim() || null
          })
        })
        
        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}))
          throw new Error(errorData.error || `HTTP error! status: ${response.status}`)
        }
        
  await this.fetchMilestones()
  this.lastSavedMilestoneSnapshot = JSON.stringify(this.milestoneForm)
  this.closeModal()
  toast.success(this.isEditing ? 'Milestone updated' : 'Milestone created')
        
      } catch (error) {
        console.error('Failed to save milestone:', error)
  this.error = error.message || 'Failed to save milestone. Please try again.'
  toast.error(this.error)
      }
  },
    
    deleteMilestone(milestone) {
      this.milestoneToDelete = milestone
      this.showDeleteModal = true
    },
    
    closeDeleteModal() {
      this.showDeleteModal = false
      this.milestoneToDelete = null
    },
    
    async confirmDelete() {
      try {
        const response = await fetch(`/api/milestones/${this.milestoneToDelete.id}`, {
          method: 'DELETE'
        })
        
        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}))
          throw new Error(errorData.error || `HTTP error! status: ${response.status}`)
        }
        
  await this.fetchMilestones()
  this.closeDeleteModal()
  toast.success('Milestone deleted')
        
      } catch (error) {
        console.error('Failed to delete milestone:', error)
  this.error = error.message || 'Failed to delete milestone. Please try again.'
  toast.error(this.error)
      }
    },
    
    formatDate(dateString) {
      if (!dateString) return null
      return new Date(dateString).toLocaleDateString()
    },
    
    formatStatus(status) {
      const statusMap = {
        'planned': 'Planned',
        'in-progress': 'In Progress',
        'completed': 'Completed',
        'overdue': 'Overdue'
      }
      return statusMap[status] || status
    },
    isDirty() {
      if (!this.showModal) return false
      try { return JSON.stringify(this.milestoneForm) !== this.lastSavedMilestoneSnapshot } catch(e){ return false }
    }
  }
}
</script>

<style scoped>
.all-milestones {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.guidance-text {
  color: #666;
  margin-bottom: 2rem;
  font-size: 1.1rem;
  line-height: 1.5;
}


/* Filters */
.filters-section {
  margin-bottom: 2rem;
  background: var(--bg-white);
  padding: 1.5rem;
  border-radius: var(--border-radius-lg);
  border: 1px solid var(--border-light-gray);
  box-shadow: var(--box-shadow-sm);
}

.filter-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
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
  color: var(--text-dark-gray);
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

.button-group {
  display: flex;
  gap: 0.5rem;
  align-items: center !important; /* Force center alignment, override parent flex-end */
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

.milestones-table-container {
  overflow-x: auto;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.milestones-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 900px;
}

.milestones-table th,
.milestones-table td {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid #e0e0e0;
}

.milestones-table th {
  background-color: #f5f5f5;
  font-weight: 600;
  color: #333;
}

.id-column,
.id-cell {
  width: 60px;
  text-align: center;
  font-size: 0.85rem;
  color: #666;
  white-space: nowrap;
}

.milestone-cell {
  max-width: 300px;
}

.milestone-name {
  font-weight: 400;
  color: #333;
  margin-bottom: 0.25rem;
}

.milestone-desc {
  font-size: 0.9rem;
  color: #666;
  line-height: 1.4;
}

.status-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
}

.status-planned {
  background-color: #e3f2fd;
  color: #1976d2;
}

.status-in-progress {
  background-color: #fff3e0;
  color: #f57c00;
}

.status-completed {
  background-color: #e8f5e8;
  color: #2e7d32;
}

.status-overdue {
  background-color: #ffebee;
  color: #d32f2f;
}

.actions-cell {
  white-space: nowrap;
}

.actions-cell .btn {
  margin-right: 0.5rem;
}

.no-data {
  text-align: center;
  padding: 3rem;
  color: #666;
  font-size: 1.1rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

/* Modal Styles - use global .modal-overlay; keep .custom-modal for sizing */
.custom-modal {
  background: white;
  border-radius: 8px;
  min-width: 600px;
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

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 1rem;
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

/* Button Styles are centralized in global CSS; keep only icon spacing */
/* FontAwesome icon spacing */
.btn i {
  flex-shrink: 0;
  width: 1em;
}

@media (max-width: 768px) {
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .custom-modal {
    min-width: 95vw;
  }
}
</style>
