<template>
  <div class="all-stakeholders">
    <h2>All Stakeholders</h2>
    
    <p class="guidance-text">
      Manage stakeholders who can be associated with projects and involved in reviews. Stakeholders represent key individuals and subject matter experts.
    </p>

    <div class="page-actions">
      <button @click="openCreateModal" class="btn btn-primary">
        <i class="fas fa-plus"></i> Create New Stakeholder
      </button>
    </div>

    <div v-if="loading" class="loading">Loading stakeholders...</div>
    <div v-else-if="error" class="error">{{ error }}</div>

    <div v-else class="stakeholders-content">
      <!-- Filters -->
      <div class="filters-section">
        <div class="filter-row">
          <div class="filter-group">
            <label>Search:</label>
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Type your search term and press Enter..."
              class="filter-input"
              @input="applyFilters"
            />
          </div>
          <div class="filter-group">
            <label>Status:</label>
            <select v-model="statusFilter" @change="applyFilters" class="filter-input">
              <option value="">All Statuses</option>
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
            </select>
          </div>
          <div class="filter-group">
            <label>Organization:</label>
            <select v-model="organizationFilter" @change="applyFilters" class="filter-input">
              <option value="">All Organizations</option>
              <option v-for="org in uniqueOrganizations" :key="org" :value="org">{{ org }}</option>
            </select>
          </div>
          <div class="filter-group">
            <label>Division:</label>
            <select v-model="divisionFilter" @change="applyFilters" class="filter-input">
              <option value="">All Divisions</option>
              <option v-for="div in uniqueDivisions" :key="div" :value="div">{{ div }}</option>
            </select>
          </div>
          <div class="filter-group">
            <div class="button-group">
              <button @click="applyFilters" class="btn btn-primary btn-sm">
                <i class="fas fa-search"></i> Search
              </button>
              <button @click="clearFilters" class="btn btn-secondary btn-sm">Clear Filters</button>
            </div>
          </div>
        </div>
      </div>

      <p class="table-instruction">Select a stakeholder to edit.</p>

      <div class="stakeholders-table-container">
        <table class="stakeholders-table">
          <thead>
            <tr>
              <th class="id-column">ID</th>
              <th>Name</th>
              <th>Title</th>
              <th>Organization</th>
              <th>Division</th>
              <th>Department</th>
              <th>Status</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="stakeholder in filteredStakeholders" :key="stakeholder.id" 
                @click="editStakeholder(stakeholder)" class="clickable-row">
              <td class="id-cell">{{ stakeholder.id }}</td>
              <td class="name-cell">{{ stakeholder.name }}</td>
              <td>{{ stakeholder.title || '-' }}</td>
              <td>{{ stakeholder.organization || '-' }}</td>
              <td>{{ stakeholder.division || '-' }}</td>
              <td>{{ stakeholder.department || '-' }}</td>
              <td>
                <span :class="`status-badge ${stakeholder.active ? 'active' : 'inactive'}`">
                  {{ stakeholder.active ? 'Active' : 'Inactive' }}
                </span>
              </td>
              <td class="actions-cell" @click.stop>
                <button @click="deleteStakeholder(stakeholder)" class="btn-icon btn-danger" title="Delete Stakeholder">
                  <i class="fas fa-times"></i>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="stakeholders.length === 0" class="no-data">
        <p>No stakeholders found. Create your first stakeholder to get started.</p>
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <div v-if="showModal" class="modal-overlay" @click="closeModal">
      <div class="custom-modal" @click.stop>
        <div class="modal-header">
          <h3>{{ isEditing ? 'Edit Stakeholder' : 'Create New Stakeholder' }}</h3>
          <button @click="closeModal" class="close-btn">&times;</button>
        </div>
        
        <div class="modal-body">
          <form @submit.prevent="saveStakeholder">
            <div class="form-row">
              <div class="form-group">
                <label for="stakeholderName">Name *</label>
                <input
                  id="stakeholderName"
                  v-model="stakeholderForm.name"
                  type="text"
                  class="form-input"
                  placeholder="Enter full name"
                  required
                  maxlength="100"
                />
              </div>
              <div class="form-group">
                <label for="stakeholderEmail">Email *</label>
                <input
                  id="stakeholderEmail"
                  v-model="stakeholderForm.email"
                  type="email"
                  class="form-input"
                  placeholder="Enter email address"
                  required
                  maxlength="120"
                />
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label for="stakeholderTitle">Title</label>
                <input
                  id="stakeholderTitle"
                  v-model="stakeholderForm.title"
                  type="text"
                  class="form-input"
                  placeholder="Job title or role"
                  maxlength="200"
                />
              </div>
              <div class="form-group">
                <label for="stakeholderPhone">Phone</label>
                <input
                  id="stakeholderPhone"
                  v-model="stakeholderForm.phone"
                  type="tel"
                  class="form-input"
                  placeholder="Phone number"
                  maxlength="20"
                />
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label for="stakeholderOrganization">Organization</label>
                <input
                  id="stakeholderOrganization"
                  v-model="stakeholderForm.organization"
                  type="text"
                  class="form-input"
                  placeholder="Company or organization"
                  maxlength="200"
                />
              </div>
              <div class="form-group">
                <label for="stakeholderDivision">Division</label>
                <input
                  id="stakeholderDivision"
                  v-model="stakeholderForm.division"
                  type="text"
                  class="form-input"
                  placeholder="Division or branch"
                  maxlength="200"
                />
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label for="stakeholderDepartment">Department</label>
                <input
                  id="stakeholderDepartment"
                  v-model="stakeholderForm.department"
                  type="text"
                  class="form-input"
                  placeholder="Department or unit"
                  maxlength="200"
                />
              </div>
              <div class="form-group">
                <!-- Empty space to maintain layout -->
              </div>
            </div>

            <div class="form-group">
              <label for="stakeholderExpertise">Expertise Areas</label>
              <textarea
                id="stakeholderExpertise"
                v-model="stakeholderForm.expertise_areas"
                class="form-input"
                placeholder="Areas of expertise (one per line)"
                rows="3"
              ></textarea>
            </div>

            <div class="form-group">
              <label for="stakeholderBio">Bio</label>
              <textarea
                id="stakeholderBio"
                v-model="stakeholderForm.bio"
                class="form-input"
                placeholder="Brief biography or description"
                rows="4"
              ></textarea>
            </div>

            <div class="form-group">
              <label class="checkbox-label">
                <input
                  v-model="stakeholderForm.active"
                  type="checkbox"
                  class="form-checkbox"
                />
                Active stakeholder
              </label>
            </div>
          </form>
        </div>
        
        <div class="modal-footer">
          <button @click="closeModal" class="btn btn-secondary">Cancel</button>
          <button @click="saveStakeholder" class="btn btn-primary" :disabled="!stakeholderForm.name.trim() || !stakeholderForm.email.trim()">
            {{ isEditing ? 'Update Stakeholder' : 'Create Stakeholder' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteModal" class="modal-overlay" @click="closeDeleteModal">
      <div class="custom-modal" @click.stop>
        <div class="modal-header">
          <h3>Confirm Delete</h3>
          <button @click="closeDeleteModal" class="close-btn">&times;</button>
        </div>
        
        <div class="modal-body">
          <p>Are you sure you want to delete stakeholder "{{ stakeholderToDelete?.name }}"?</p>
          <p class="warning">This action cannot be undone and will remove the stakeholder from all associated projects.</p>
        </div>
        
        <div class="modal-footer">
          <button @click="closeDeleteModal" class="btn btn-secondary">Cancel</button>
          <button @click="confirmDelete" class="btn btn-danger">Delete Stakeholder</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AllStakeholdersView',
  data() {
    return {
      stakeholders: [],
      filteredStakeholders: [],
      searchQuery: '',
      statusFilter: '',
      organizationFilter: '',
      divisionFilter: '',
      loading: false,
      error: null,
      showModal: false,
      showDeleteModal: false,
      isEditing: false,
      stakeholderToDelete: null,
      stakeholderForm: {
        id: null,
        name: '',
        email: '',
        title: '',
        organization: '',
        division: '',
        department: '',
        phone: '',
        expertise_areas: '',
        bio: '',
        active: true
      }
    }
  },
  
  computed: {
    uniqueOrganizations() {
      const orgs = [...new Set(this.stakeholders.map(s => s.organization).filter(org => org))]
      return orgs.sort()
    },
    uniqueDivisions() {
      const divs = [...new Set(this.stakeholders.map(s => s.division).filter(div => div))]
      return divs.sort()
    }
  },
  
  mounted() {
    this.fetchStakeholders()
  },
  
  methods: {
    async fetchStakeholders() {
      this.loading = true
      this.error = null
      try {
        const response = await fetch('/api/stakeholders/')
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        this.stakeholders = await response.json()
        this.applyFilters() // Initialize filtered data
      } catch (error) {
        console.error('Failed to fetch stakeholders:', error)
        this.error = 'Failed to load stakeholders. Please try again.'
      } finally {
        this.loading = false
      }
    },

    applyFilters() {
      let filtered = [...this.stakeholders]
      
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase()
        filtered = filtered.filter(stakeholder => 
          stakeholder.name.toLowerCase().includes(query) ||
          stakeholder.email.toLowerCase().includes(query) ||
          (stakeholder.title && stakeholder.title.toLowerCase().includes(query)) ||
          (stakeholder.organization && stakeholder.organization.toLowerCase().includes(query)) ||
          (stakeholder.division && stakeholder.division.toLowerCase().includes(query)) ||
          (stakeholder.department && stakeholder.department.toLowerCase().includes(query))
        )
      }
      
      if (this.statusFilter) {
        const isActive = this.statusFilter === 'active'
        filtered = filtered.filter(stakeholder => stakeholder.active === isActive)
      }
      
      if (this.organizationFilter) {
        filtered = filtered.filter(stakeholder => stakeholder.organization === this.organizationFilter)
      }
      
      if (this.divisionFilter) {
        filtered = filtered.filter(stakeholder => stakeholder.division === this.divisionFilter)
      }
      
      this.filteredStakeholders = filtered
    },
    
    clearFilters() {
      this.searchQuery = ''
      this.statusFilter = ''
      this.organizationFilter = ''
      this.divisionFilter = ''
      this.applyFilters()
    },
    
    openCreateModal() {
      this.isEditing = false
      this.stakeholderForm = {
        id: null,
        name: '',
        email: '',
        title: '',
        organization: '',
        division: '',
        department: '',
        phone: '',
        expertise_areas: '',
        bio: '',
        active: true
      }
      this.showModal = true
    },
    
    editStakeholder(stakeholder) {
      this.isEditing = true
      this.stakeholderForm = {
        id: stakeholder.id,
        name: stakeholder.name,
        email: stakeholder.email,
        title: stakeholder.title || '',
        organization: stakeholder.organization || '',
        division: stakeholder.division || '',
        department: stakeholder.department || '',
        phone: stakeholder.phone || '',
        expertise_areas: stakeholder.expertise_areas || '',
        bio: stakeholder.bio || '',
        active: stakeholder.active
      }
      this.showModal = true
    },
    
    closeModal() {
      this.showModal = false
      this.stakeholderForm = {
        id: null,
        name: '',
        email: '',
        title: '',
        organization: '',
        division: '',
        department: '',
        phone: '',
        expertise_areas: '',
        bio: '',
        active: true
      }
    },
    
    async saveStakeholder() {
      try {
        const url = this.isEditing ? `/api/stakeholders/${this.stakeholderForm.id}` : '/api/stakeholders/'
        const method = this.isEditing ? 'PUT' : 'POST'
        
        const response = await fetch(url, {
          method: method,
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            name: this.stakeholderForm.name.trim(),
            email: this.stakeholderForm.email.trim(),
            title: this.stakeholderForm.title.trim() || null,
            organization: this.stakeholderForm.organization.trim() || null,
            division: this.stakeholderForm.division.trim() || null,
            department: this.stakeholderForm.department.trim() || null,
            phone: this.stakeholderForm.phone.trim() || null,
            expertise_areas: this.stakeholderForm.expertise_areas.trim() || null,
            bio: this.stakeholderForm.bio.trim() || null,
            active: this.stakeholderForm.active
          })
        })
        
        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}))
          throw new Error(errorData.error || `HTTP error! status: ${response.status}`)
        }
        
        await this.fetchStakeholders()
        this.closeModal()
        
      } catch (error) {
        console.error('Failed to save stakeholder:', error)
        this.error = error.message || 'Failed to save stakeholder. Please try again.'
      }
    },
    
    deleteStakeholder(stakeholder) {
      this.stakeholderToDelete = stakeholder
      this.showDeleteModal = true
    },
    
    closeDeleteModal() {
      this.showDeleteModal = false
      this.stakeholderToDelete = null
    },
    
    async confirmDelete() {
      try {
        const response = await fetch(`/api/stakeholders/${this.stakeholderToDelete.id}`, {
          method: 'DELETE'
        })
        
        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}))
          throw new Error(errorData.error || `HTTP error! status: ${response.status}`)
        }
        
        await this.fetchStakeholders()
        this.closeDeleteModal()
        
      } catch (error) {
        console.error('Failed to delete stakeholder:', error)
        this.error = error.message || 'Failed to delete stakeholder. Please try again.'
      }
    }
  }
}
</script>

<style scoped>
.all-stakeholders {
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

.page-actions {
  margin-bottom: 2rem;
  display: flex;
  justify-content: flex-end;
}

/* Filters */
.filters-section {
  background: white;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 2rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
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

.button-group {
  display: flex;
  gap: 0.5rem;
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

.stakeholders-table-container {
  overflow-x: auto;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.stakeholders-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 800px;
}

.stakeholders-table th,
.stakeholders-table td {
  padding: 0.25rem;
  text-align: left;
  border-bottom: 1px solid #e0e0e0;
  font-size: 0.85rem;
}

.clickable-row {
  cursor: pointer;
  transition: background-color 0.2s;
}

.clickable-row:hover {
  background-color: #f8f9fa;
}

.stakeholders-table th {
  background-color: #f5f5f5;
  font-weight: 600;
  color: #333;
}

.id-column,
.id-cell {
  text-align: center;
  font-size: 0.85rem;
  color: #666;
  white-space: nowrap;
}

.name-cell {
  color: #333;
}

.status-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
}

.status-badge.active {
  background-color: #e8f5e8;
  color: #2e7d32;
}

.status-badge.inactive {
  background-color: #fff3e0;
  color: #f57c00;
}

.actions-cell {
  white-space: nowrap;

  text-align: center;
}

.btn-icon {
  border: none;
  background: none;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 3px;
  width: 24px;
  height: 24px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  transition: background-color 0.2s;
}

.btn-icon.btn-danger {
  color: white;
  background-color: #dc3545;
}

.btn-icon.btn-danger:hover {
  background-color: #c82333;
  color: white;
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
  z-index: 2500;
}

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
  border-color: #007bff;
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
}

.checkbox-label {
  display: flex !important;
  align-items: center;
  gap: 0.5rem;
  font-weight: normal !important;
}

.form-checkbox {
  width: auto !important;
  margin: 0 !important;
  padding: 0 !important;
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

/* FontAwesome icon spacing */
.btn i {
  flex-shrink: 0;
  width: 1em;
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

@media (max-width: 768px) {
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .modal {
    min-width: 95vw;
  }
}
</style>
