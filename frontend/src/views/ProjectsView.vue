<template>
  <div class="projects-dashboard">
    <!-- Dashboard Header -->
     <div class="dashboard-header">
        <h1>Projects Dashboard</h1>
        <p class="welcome-text">Manage projects, stakeholders, and review workflows</p>
  </div>

    <!-- Metrics Overview -->
    <div class="metrics-grid">
      <div class="metric-card">
        <div class="metric-icon">📊</div>
        <div class="metric-content">
          <h3>Total Projects</h3>
          <div class="metric-number">{{ projectMetrics.total }}</div>
          <div class="metric-detail">+{{ projectMetrics.newThisMonth }} this month</div>
        </div>
      </div>
      
      <div class="metric-card">
        <div class="metric-icon">🚀</div>
        <div class="metric-content">
          <h3>Active Projects</h3>
          <div class="metric-number">{{ projectMetrics.active }}</div>
          <div class="metric-detail">{{ projectMetrics.activePercentage }}% of total</div>
        </div>
      </div>
      
      <div class="metric-card">
        <div class="metric-icon">👥</div>
        <div class="metric-content">
          <h3>Total Stakeholders</h3>
          <div class="metric-number">{{ projectMetrics.stakeholders }}</div>
          <div class="metric-detail">Across all projects</div>
        </div>
      </div>
      
      <div class="metric-card">
        <div class="metric-icon">✅</div>
        <div class="metric-content">
          <h3>Completed</h3>
          <div class="metric-number">{{ projectMetrics.completed }}</div>
          <div class="metric-detail">{{ projectMetrics.completionRate }}% completion rate</div>
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="section-card">
      <div class="section-header">
        <h2 class="section-title">Quick Actions</h2>
      </div>
      <div class="quick-actions-grid">
        <button @click="showCreateModal = true" class="action-card">
          <div class="action-icon">📝</div>
          <div class="action-content">
            <h3>Create Project</h3>
            <p>Start a new documentation project</p>
          </div>
        </button>
        
        <button @click="filterByStatus('active')" class="action-card">
          <div class="action-icon">🎯</div>
          <div class="action-content">
            <h3>View Active</h3>
            <p>See all currently active projects</p>
          </div>
        </button>
        
        <button @click="showTemplateModal = true" class="action-card">
          <div class="action-icon">📋</div>
          <div class="action-content">
            <h3>Use Template</h3>
            <p>Create from project template</p>
          </div>
        </button>
        
        <button @click="exportProjects" class="action-card">
          <div class="action-icon">📤</div>
          <div class="action-content">
            <h3>Export Data</h3>
            <p>Download project reports</p>
          </div>
        </button>
      </div>
    </div>

    <!-- Projects List -->
    <div class="section-card">
      <div class="section-header">
        <h2 class="section-title">All Projects</h2>
        <div class="filter-controls">
          <select v-model="statusFilter" @change="applyFilters" class="filter-select">
            <option value="">All Statuses</option>
            <option value="planning">Planning</option>
            <option value="active">Active</option>
            <option value="on_hold">On Hold</option>
            <option value="completed">Completed</option>
          </select>
        </div>
      </div>
      
      <div v-if="filteredProjects.length === 0" class="empty-state">
        <div class="empty-content">
          <div class="empty-icon">🎯</div>
          <h3>{{ projects.length === 0 ? 'No Projects Yet' : 'No Projects Match Filter' }}</h3>
          <p>{{ projects.length === 0 ? 'Get started by creating your first project to organize topics, stakeholders, and review workflows.' : 'Try adjusting your filters or create a new project.' }}</p>
          <button @click="showCreateModal = true" class="create-first-btn">
            ➕ {{ projects.length === 0 ? 'Create Your First Project' : 'Create New Project' }}
          </button>
        </div>
      </div>

      <div v-else class="projects-grid">
        <div
          v-for="project in filteredProjects"
          :key="project.id"
          class="project-card"
        >
          <div class="project-header">
            <h3>{{ project.name }}</h3>
            <span class="status-badge" :class="project.status">
              {{ formatStatus(project.status) }}
            </span>
          </div>
          <p class="project-description">{{ project.description }}</p>
          
          <!-- Project Summary -->
          <div class="project-summary">
            <div class="summary-item" v-if="project.stakeholders && project.stakeholders.length > 0">
              <span class="summary-icon">👥</span>
              <span>{{ project.stakeholders.length }} Stakeholder{{ project.stakeholders.length > 1 ? 's' : '' }}</span>
            </div>
            <div class="summary-item" v-if="project.collections && project.collections.length > 0">
              <span class="summary-icon">📁</span>
              <span>{{ project.collections.length }} Collection{{ project.collections.length > 1 ? 's' : '' }}</span>
            </div>
            <div class="summary-item" v-if="project.publishedDocuments && project.publishedDocuments.length > 0">
              <span class="summary-icon">📄</span>
              <span>{{ project.publishedDocuments.length }} Document{{ project.publishedDocuments.length > 1 ? 's' : '' }}</span>
            </div>
          </div>

          <!-- Milestone Dates -->
          <div class="project-milestones" v-if="hasActiveMilestones(project)">
            <div class="milestone-item" v-if="project.milestones?.projectedStart">
              <strong>Start:</strong> {{ formatDate(project.milestones.projectedStart) }}
            </div>
            <div class="milestone-item" v-if="project.milestones?.projectedEnd">
              <strong>End:</strong> {{ formatDate(project.milestones.projectedEnd) }}
            </div>
            <div class="milestone-item" v-if="project.milestones?.dryRunDate">
              <strong>Dry Run:</strong> {{ formatDate(project.milestones.dryRunDate) }}
            </div>
          </div>

          <div class="project-meta">
            <small>Created: {{ formatDate(project.created_at) }}</small>
          </div>
          <div class="project-actions">
            <button @click="editProject(project)" class="edit-btn">
              ✏️ Edit
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Project Modal -->
    <div v-if="showCreateModal" class="modal-overlay" @click="showCreateModal = false">
      <div class="modal large-modal" @click.stop>
        <div class="modal-header">
          <h2>Create New Project</h2>
          <button @click="showCreateModal = false" class="close-btn">×</button>
        </div>
        <form @submit.prevent="createProject" class="modal-body">
          <!-- Basic Information -->
          <div class="form-section">
            <h3>Basic Information</h3>
            <div class="form-row">
              <div class="form-group">
                <label for="projectName">Project Name *</label>
                <input
                  id="projectName"
                  v-model="newProject.name"
                  type="text"
                  required
                  placeholder="Enter project name"
                />
              </div>
              <div class="form-group">
                <label for="projectStatus">Status</label>
                <select id="projectStatus" v-model="newProject.status">
                  <option value="planning">Planning</option>
                  <option value="active">Active</option>
                  <option value="on_hold">On Hold</option>
                  <option value="completed">Completed</option>
                </select>
              </div>
            </div>
            <div class="form-group">
              <label for="projectDescription">Description</label>
              <textarea
                id="projectDescription"
                v-model="newProject.description"
                placeholder="Project description"
                rows="3"
              ></textarea>
            </div>
          </div>

          <!-- Stakeholders -->
          <div class="form-section">
            <h3>Stakeholders</h3>
            <div class="stakeholders-list">
              <div v-for="(stakeholder, index) in newProject.stakeholders" :key="index" class="stakeholder-item">
                <input
                  v-model="stakeholder.name"
                  type="text"
                  placeholder="Stakeholder name"
                  class="stakeholder-input"
                />
                <input
                  v-model="stakeholder.role"
                  type="text"
                  placeholder="Role/Title"
                  class="stakeholder-input"
                />
                <input
                  v-model="stakeholder.email"
                  type="email"
                  placeholder="Email"
                  class="stakeholder-input"
                />
                <button type="button" @click="removeStakeholder(index, 'new')" class="remove-btn">✕</button>
              </div>
              <button type="button" @click="addStakeholder('new')" class="add-btn">+ Add Stakeholder</button>
            </div>
          </div>

          <!-- Milestone Dates -->
          <div class="form-section">
            <h3>Milestone Dates</h3>
            <div class="form-row">
              <div class="form-group">
                <label for="projectedStart">Projected Start</label>
                <input
                  id="projectedStart"
                  v-model="newProject.milestones.projectedStart"
                  type="date"
                />
              </div>
              <div class="form-group">
                <label for="projectedEnd">Projected End</label>
                <input
                  id="projectedEnd"
                  v-model="newProject.milestones.projectedEnd"
                  type="date"
                />
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label for="actualStart">Actual Start</label>
                <input
                  id="actualStart"
                  v-model="newProject.milestones.actualStart"
                  type="date"
                />
              </div>
              <div class="form-group">
                <label for="actualEnd">Actual End</label>
                <input
                  id="actualEnd"
                  v-model="newProject.milestones.actualEnd"
                  type="date"
                />
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label for="dryRunDate">Dry Run Date</label>
                <input
                  id="dryRunDate"
                  v-model="newProject.milestones.dryRunDate"
                  type="date"
                />
              </div>
              <div class="form-group">
                <label for="reviewDeadline">Review Deadline</label>
                <input
                  id="reviewDeadline"
                  v-model="newProject.milestones.reviewDeadline"
                  type="date"
                />
              </div>
            </div>
          </div>

          <!-- Collections -->
          <div class="form-section">
            <h3>Collections</h3>
            <div class="collections-list">
              <div v-for="(collection, index) in newProject.collections" :key="index" class="collection-item">
                <input
                  v-model="collection.name"
                  type="text"
                  placeholder="Collection name"
                  class="collection-input"
                />
                <textarea
                  v-model="collection.description"
                  placeholder="Description"
                  rows="2"
                  class="collection-input"
                ></textarea>
                <button type="button" @click="removeCollection(index, 'new')" class="remove-btn">✕</button>
              </div>
              <button type="button" @click="addCollection('new')" class="add-btn">+ Add Collection</button>
            </div>
          </div>

          <!-- Published Documents -->
          <div class="form-section">
            <h3>Published Documents</h3>
            <div class="documents-list">
              <div v-for="(document, index) in newProject.publishedDocuments" :key="index" class="document-item">
                <input
                  v-model="document.title"
                  type="text"
                  placeholder="Document title"
                  class="document-input"
                />
                <input
                  v-model="document.url"
                  type="url"
                  placeholder="Document URL"
                  class="document-input"
                />
                <select v-model="document.type" class="document-input">
                  <option value="">Select type</option>
                  <option value="pdf">PDF</option>
                  <option value="docx">Word Document</option>
                  <option value="html">HTML</option>
                  <option value="markdown">Markdown</option>
                  <option value="other">Other</option>
                </select>
                <button type="button" @click="removeDocument(index, 'new')" class="remove-btn">✕</button>
              </div>
              <button type="button" @click="addDocument('new')" class="add-btn">+ Add Document</button>
            </div>
          </div>

          <div class="modal-actions">
            <button type="button" @click="showCreateModal = false" class="cancel-btn">
              Cancel
            </button>
            <button type="submit" class="create-btn">Create Project</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Edit Project Modal -->
    <div v-if="showEditModal" class="modal-overlay" @click="showEditModal = false">
      <div class="modal large-modal" @click.stop>
        <div class="modal-header">
          <h2>Edit Project</h2>
          <button @click="showEditModal = false" class="close-btn">×</button>
        </div>
        <form @submit.prevent="updateProject" class="modal-body">
          <!-- Basic Information -->
          <div class="form-section">
            <h3>Basic Information</h3>
            <div class="form-row">
              <div class="form-group">
                <label for="editProjectName">Project Name *</label>
                <input
                  id="editProjectName"
                  v-model="editingProject.name"
                  type="text"
                  required
                  placeholder="Enter project name"
                />
              </div>
              <div class="form-group">
                <label for="editProjectStatus">Status</label>
                <select id="editProjectStatus" v-model="editingProject.status">
                  <option value="planning">Planning</option>
                  <option value="active">Active</option>
                  <option value="on_hold">On Hold</option>
                  <option value="completed">Completed</option>
                </select>
              </div>
            </div>
            <div class="form-group">
              <label for="editProjectDescription">Description</label>
              <textarea
                id="editProjectDescription"
                v-model="editingProject.description"
                placeholder="Project description"
                rows="3"
              ></textarea>
            </div>
          </div>

          <!-- Stakeholders -->
          <div class="form-section">
            <h3>Stakeholders</h3>
            <div class="stakeholders-list">
              <div v-for="(stakeholder, index) in editingProject.stakeholders" :key="index" class="stakeholder-item">
                <input
                  v-model="stakeholder.name"
                  type="text"
                  placeholder="Stakeholder name"
                  class="stakeholder-input"
                />
                <input
                  v-model="stakeholder.role"
                  type="text"
                  placeholder="Role/Title"
                  class="stakeholder-input"
                />
                <input
                  v-model="stakeholder.email"
                  type="email"
                  placeholder="Email"
                  class="stakeholder-input"
                />
                <button type="button" @click="removeStakeholder(index, 'edit')" class="remove-btn">✕</button>
              </div>
              <button type="button" @click="addStakeholder('edit')" class="add-btn">+ Add Stakeholder</button>
            </div>
          </div>

          <!-- Milestone Dates -->
          <div class="form-section">
            <h3>Milestone Dates</h3>
            <div class="form-row">
              <div class="form-group">
                <label for="editProjectedStart">Projected Start</label>
                <input
                  id="editProjectedStart"
                  v-model="editingProject.milestones.projectedStart"
                  type="date"
                />
              </div>
              <div class="form-group">
                <label for="editProjectedEnd">Projected End</label>
                <input
                  id="editProjectedEnd"
                  v-model="editingProject.milestones.projectedEnd"
                  type="date"
                />
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label for="editActualStart">Actual Start</label>
                <input
                  id="editActualStart"
                  v-model="editingProject.milestones.actualStart"
                  type="date"
                />
              </div>
              <div class="form-group">
                <label for="editActualEnd">Actual End</label>
                <input
                  id="editActualEnd"
                  v-model="editingProject.milestones.actualEnd"
                  type="date"
                />
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label for="editDryRunDate">Dry Run Date</label>
                <input
                  id="editDryRunDate"
                  v-model="editingProject.milestones.dryRunDate"
                  type="date"
                />
              </div>
              <div class="form-group">
                <label for="editReviewDeadline">Review Deadline</label>
                <input
                  id="editReviewDeadline"
                  v-model="editingProject.milestones.reviewDeadline"
                  type="date"
                />
              </div>
            </div>
          </div>

          <!-- Collections -->
          <div class="form-section">
            <h3>Collections</h3>
            <div class="collections-list">
              <div v-for="(collection, index) in editingProject.collections" :key="index" class="collection-item">
                <input
                  v-model="collection.name"
                  type="text"
                  placeholder="Collection name"
                  class="collection-input"
                />
                <textarea
                  v-model="collection.description"
                  placeholder="Description"
                  rows="2"
                  class="collection-input"
                ></textarea>
                <button type="button" @click="removeCollection(index, 'edit')" class="remove-btn">✕</button>
              </div>
              <button type="button" @click="addCollection('edit')" class="add-btn">+ Add Collection</button>
            </div>
          </div>

          <!-- Published Documents -->
          <div class="form-section">
            <h3>Published Documents</h3>
            <div class="documents-list">
              <div v-for="(document, index) in editingProject.publishedDocuments" :key="index" class="document-item">
                <input
                  v-model="document.title"
                  type="text"
                  placeholder="Document title"
                  class="document-input"
                />
                <input
                  v-model="document.url"
                  type="url"
                  placeholder="Document URL"
                  class="document-input"
                />
                <select v-model="document.type" class="document-input">
                  <option value="">Select type</option>
                  <option value="pdf">PDF</option>
                  <option value="docx">Word Document</option>
                  <option value="html">HTML</option>
                  <option value="markdown">Markdown</option>
                  <option value="other">Other</option>
                </select>
                <button type="button" @click="removeDocument(index, 'edit')" class="remove-btn">✕</button>
              </div>
              <button type="button" @click="addDocument('edit')" class="add-btn">+ Add Document</button>
            </div>
          </div>

          <div class="modal-actions">
            <button type="button" @click="showEditModal = false" class="cancel-btn">
              Cancel
            </button>
            <button type="submit" class="create-btn">Update Project</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import Breadcrumbs from '../components/Breadcrumbs.vue'

export default {
  name: 'ProjectsView',
  components: {
    Breadcrumbs
  },
  data() {
    return {
      projects: [],
      statusFilter: '',
      showCreateModal: false,
      showEditModal: false,
      showTemplateModal: false,
      newProject: {
        name: '',
        description: '',
        status: 'planning',
        stakeholders: [],
        milestones: {
          projectedStart: '',
          projectedEnd: '',
          actualStart: '',
          actualEnd: '',
          dryRunDate: '',
          reviewDeadline: ''
        },
        collections: [],
        publishedDocuments: []
      },
      editingProject: {
        id: null,
        name: '',
        description: '',
        status: 'planning',
        stakeholders: [],
        milestones: {
          projectedStart: '',
          projectedEnd: '',
          actualStart: '',
          actualEnd: '',
          dryRunDate: '',
          reviewDeadline: ''
        },
        collections: [],
        publishedDocuments: []
      }
    }
  },
  computed: {
    projectMetrics() {
      const total = this.projects.length
      const active = this.projects.filter(p => p.status === 'active').length
      const completed = this.projects.filter(p => p.status === 'completed').length
      const stakeholders = this.projects.reduce((sum, p) => sum + (p.stakeholders?.length || 0), 0)
      
      return {
        total,
        active,
        completed,
        stakeholders,
        newThisMonth: Math.floor(total * 0.2), // Mock data
        activePercentage: total > 0 ? Math.round((active / total) * 100) : 0,
        completionRate: total > 0 ? Math.round((completed / total) * 100) : 0
      }
    },
    filteredProjects() {
      if (!this.statusFilter) {
        return this.projects
      }
      return this.projects.filter(project => project.status === this.statusFilter)
    }
  },
  methods: {
    async createProject() {
      try {
        // For now, just add to local array - later we'll connect to API
        const project = {
          id: Date.now(),
          name: this.newProject.name,
          description: this.newProject.description,
          status: this.newProject.status,
          stakeholders: [...this.newProject.stakeholders],
          milestones: { ...this.newProject.milestones },
          collections: [...this.newProject.collections],
          publishedDocuments: [...this.newProject.publishedDocuments],
          created_at: new Date().toISOString()
        }
        
        this.projects.push(project)
        this.showCreateModal = false
        this.resetNewProject()
      } catch (error) {
        console.error('Failed to create project:', error)
      }
    },

    // Dashboard specific methods
    filterByStatus(status) {
      this.statusFilter = status
    },

    applyFilters() {
      // Filters are automatically applied through computed property
    },

    exportProjects() {
      // Mock export functionality
      alert('Export functionality would be implemented here')
    },
    
    resetNewProject() {
      this.newProject = {
        name: '',
        description: '',
        status: 'planning',
        stakeholders: [],
        milestones: {
          projectedStart: '',
          projectedEnd: '',
          actualStart: '',
          actualEnd: '',
          dryRunDate: '',
          reviewDeadline: ''
        },
        collections: [],
        publishedDocuments: []
      }
    },
    
    formatStatus(status) {
      const statusMap = {
        'planning': 'Planning',
        'active': 'Active',
        'completed': 'Completed',
        'on_hold': 'On Hold'
      }
      return statusMap[status] || status
    },

    formatDate(dateString) {
      if (!dateString) return ''
      return new Date(dateString).toLocaleDateString()
    },

    editProject(project) {
      this.editingProject = {
        id: project.id,
        name: project.name,
        description: project.description,
        status: project.status,
        stakeholders: project.stakeholders ? [...project.stakeholders] : [],
        milestones: project.milestones ? { ...project.milestones } : {
          projectedStart: '',
          projectedEnd: '',
          actualStart: '',
          actualEnd: '',
          dryRunDate: '',
          reviewDeadline: ''
        },
        collections: project.collections ? [...project.collections] : [],
        publishedDocuments: project.publishedDocuments ? [...project.publishedDocuments] : []
      }
      this.showEditModal = true
    },

    async updateProject() {
      try {
        // Find and update the project in the array
        const index = this.projects.findIndex(p => p.id === this.editingProject.id)
        if (index !== -1) {
          this.projects[index] = {
            ...this.projects[index],
            name: this.editingProject.name,
            description: this.editingProject.description,
            status: this.editingProject.status,
            stakeholders: [...this.editingProject.stakeholders],
            milestones: { ...this.editingProject.milestones },
            collections: [...this.editingProject.collections],
            publishedDocuments: [...this.editingProject.publishedDocuments]
          }
        }
        
        this.showEditModal = false
        this.resetEditingProject()
      } catch (error) {
        console.error('Failed to update project:', error)
      }
    },

    resetEditingProject() {
      this.editingProject = {
        id: null,
        name: '',
        description: '',
        status: 'planning',
        stakeholders: [],
        milestones: {
          projectedStart: '',
          projectedEnd: '',
          actualStart: '',
          actualEnd: '',
          dryRunDate: '',
          reviewDeadline: ''
        },
        collections: [],
        publishedDocuments: []
      }
    },

    // Stakeholder management methods
    addStakeholder(type) {
      const target = type === 'new' ? this.newProject : this.editingProject
      target.stakeholders.push({
        name: '',
        role: '',
        email: ''
      })
    },

    removeStakeholder(index, type) {
      const target = type === 'new' ? this.newProject : this.editingProject
      target.stakeholders.splice(index, 1)
    },

    // Collection management methods
    addCollection(type) {
      const target = type === 'new' ? this.newProject : this.editingProject
      target.collections.push({
        name: '',
        description: ''
      })
    },

    removeCollection(index, type) {
      const target = type === 'new' ? this.newProject : this.editingProject
      target.collections.splice(index, 1)
    },

    // Document management methods
    addDocument(type) {
      const target = type === 'new' ? this.newProject : this.editingProject
      target.publishedDocuments.push({
        title: '',
        url: '',
        type: ''
      })
    },

    removeDocument(index, type) {
      const target = type === 'new' ? this.newProject : this.editingProject
      target.publishedDocuments.splice(index, 1)
    },

    hasActiveMilestones(project) {
      if (!project.milestones) return false
      return project.milestones.projectedStart || 
             project.milestones.projectedEnd || 
             project.milestones.dryRunDate ||
             project.milestones.reviewDeadline
    }
  }
}
</script>

<style scoped>
/* Dashboard Layout */
.projects-dashboard {
  padding: 0;
  max-width: 1200px;
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

/* Section Cards */
.section-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid #f0f4f8;
}

.section-title {
  margin: 0;
  color: #112e51;
  font-size: 1.5rem;
  font-weight: 600;
}

.filter-controls {
  display: flex;
  gap: 1rem;
}

.filter-select {
  padding: 0.5rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  background: white;
  color: #374151;
  font-size: 0.9rem;
  cursor: pointer;
}

.filter-select:focus {
  outline: none;
  border-color: #005a9c;
  box-shadow: 0 0 0 3px rgba(0, 90, 156, 0.1);
}

/* Quick Actions Grid */
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

/* Empty State */
.empty-state {
  text-align: center;
  padding: 3rem 1rem;
}

.empty-content {
  max-width: 400px;
  margin: 0 auto;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
  opacity: 0.6;
}

.empty-content h3 {
  margin: 0 0 1rem 0;
  color: #112e51;
  font-size: 1.5rem;
}

.empty-content p {
  margin: 0 0 1.5rem 0;
  color: #666;
  line-height: 1.6;
}

.create-first-btn {
  background: #005a9c;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.create-first-btn:hover {
  background: #004080;
  transform: translateY(-1px);
}

/* Projects Grid */
.projects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
}

.project-card {
  background: white;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  padding: 1.5rem;
  transition: all 0.2s ease;
  position: relative;
}

.project-card:hover {
  border-color: #005a9c;
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 90, 156, 0.15);
}

.project-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.project-header h3 {
  margin: 0;
  color: #112e51;
  font-size: 1.25rem;
  font-weight: 600;
  line-height: 1.3;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.status-badge.planning {
  background: #fef3c7;
  color: #92400e;
}

.status-badge.active {
  background: #d1fae5;
  color: #065f46;
}

.status-badge.completed {
  background: #e5e7eb;
  color: #374151;
}

.status-badge.on_hold {
  background: #fed7d7;
  color: #c53030;
}

.project-description {
  color: #6b7280;
  margin-bottom: 1rem;
  line-height: 1.5;
}

.project-summary {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.summary-item {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  background: #f1f5f9;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  font-size: 0.8rem;
  color: #475569;
}

.summary-icon {
  font-size: 0.9rem;
}

.project-milestones {
  background: #fef7cd;
  border: 1px solid #fde047;
  border-radius: 6px;
  padding: 0.75rem;
  margin-bottom: 1rem;
}

.milestone-item {
  font-size: 0.8rem;
  color: #a16207;
  margin-bottom: 0.25rem;
}

.milestone-item:last-child {
  margin-bottom: 0;
}

.project-meta {
  color: #9ca3af;
  font-size: 0.8rem;
  margin-bottom: 1rem;
}

.project-actions {
  display: flex;
  gap: 0.5rem;
}

.edit-btn {
  background: #005a9c;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.edit-btn:hover {
  background: #004080;
}

/* Modal Styles - Keeping existing modal styles but with updated colors */
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
  transition: border-color 0.2s ease;
}

.form-group input:focus, .form-group textarea:focus, .form-group select:focus {
  outline: none;
  border-color: #005a9c;
  box-shadow: 0 0 0 3px rgba(0, 90, 156, 0.1);
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid #e5e7eb;
}

.cancel-btn {
  padding: 0.75rem 1.5rem;
  border: 1px solid #d1d5db;
  background: white;
  color: #374151;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s ease;
}

.cancel-btn:hover {
  background: #f9fafb;
  border-color: #9ca3af;
}

/* Enhanced Modal Styles */
.large-modal {
  min-width: 800px;
  max-width: 95vw;
}

.form-section {
  margin-bottom: 2rem;
  padding: 1.5rem;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  background: #f9fafb;
}

.form-section h3 {
  margin: 0 0 1rem 0;
  color: #112e51;
  font-size: 1.1rem;
  font-weight: 600;
  border-bottom: 2px solid #005a9c;
  padding-bottom: 0.5rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 1rem;
}

/* Stakeholder, Collection, Document Styles */
.stakeholders-list, .collections-list, .documents-list {
  background: white;
  border-radius: 6px;
  padding: 1rem;
}

.stakeholder-item, .collection-item, .document-item {
  display: grid;
  gap: 0.75rem;
  margin-bottom: 1rem;
  padding: 1rem;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  background: #fafafa;
}

.stakeholder-item {
  grid-template-columns: 1fr 1fr 1fr auto;
  align-items: center;
}

.collection-item {
  grid-template-columns: 1fr 2fr auto;
  align-items: start;
}

.document-item {
  grid-template-columns: 1fr 1fr 1fr auto;
  align-items: center;
}

.stakeholder-input, .collection-input, .document-input {
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-size: 0.9rem;
  box-sizing: border-box;
}

.stakeholder-input:focus, .collection-input:focus, .document-input:focus {
  outline: none;
  border-color: #005a9c;
  box-shadow: 0 0 0 2px rgba(0, 90, 156, 0.1);
}

.add-btn {
  background: #059669;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  transition: background 0.2s ease;
}

.add-btn:hover {
  background: #047857;
}

.remove-btn {
  background: #dc2626;
  color: white;
  border: none;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.8rem;
  transition: background 0.2s ease;
}

.remove-btn:hover {
  background: #b91c1c;
}

/* Responsive Design */
@media (max-width: 768px) {
  .dashboard-header {
    flex-direction: column;
    gap: 1rem;
  }
  
  .metrics-grid {
    grid-template-columns: 1fr;
  }
  
  .quick-actions-grid {
    grid-template-columns: 1fr;
  }
  
  .projects-grid {
    grid-template-columns: 1fr;
  }
  
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .stakeholder-item {
    grid-template-columns: 1fr;
  }
  
  .collection-item {
    grid-template-columns: 1fr;
  }
  
  .document-item {
    grid-template-columns: 1fr;
  }
}
</style>
