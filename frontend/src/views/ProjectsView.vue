<template>
  <div class="projects-view">
    <Breadcrumbs />
    <h1>🎯 Projects</h1>
    <p>Manage projects, stakeholders, and review workflows.</p>
    
    <div class="actions-bar">
      <button @click="showCreateModal = true" class="create-btn">
        + New Project
      </button>
    </div>
    
    <!-- Projects List -->
    <div v-if="projects.length === 0" class="empty-projects">
      <div class="empty-content">
        <div class="empty-icon">🎯</div>
        <h2>No Projects Yet</h2>
        <p>Get started by creating your first project to organize topics, stakeholders, and review workflows.</p>
        <button @click="showCreateModal = true" class="create-first-btn">
          + Create Your First Project
        </button>
      </div>
    </div>

    <div v-else class="projects-grid">
      <div
        v-for="project in projects"
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
      showCreateModal: false,
      showEditModal: false,
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
.projects-view {
  padding: 70px 20px 20px 20px;
}

.actions-bar {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 30px;
}

.create-btn {
  background: #3498db;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
}

.empty-projects {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  min-height: 300px;
  margin: 20px 0;
  padding-top: 40px;
}

.empty-content {
  text-align: center;
  max-width: 500px;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 20px;
}

.create-first-btn {
  background: #27ae60;
  color: white;
  border: none;
  padding: 15px 30px;
  border-radius: 8px;
  cursor: pointer;
  margin: 0 auto;
}

.projects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.project-card {
  border: 2px solid #e1e8ed;
  border-radius: 8px;
  padding: 20px;
  background: white;
  transition: all 0.2s;
}

.project-card:hover {
  border-color: #3498db;
  box-shadow: 0 4px 12px rgba(52, 152, 219, 0.1);
}

.project-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 10px;
}

.project-header h3 {
  margin: 0;
  color: #2c3e50;
  line-height: 1.3;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
}

.status-badge.planning {
  background: #f39c12;
  color: white;
}

.status-badge.active {
  background: #27ae60;
  color: white;
}

.status-badge.completed {
  background: #95a5a6;
  color: white;
}

.status-badge.on_hold {
  background: #e67e22;
  color: white;
}

.project-description {
  color: #7f8c8d;
  margin-bottom: 15px;
  line-height: 1.4;
}

.project-summary {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 15px;
}

.summary-item {
  display: flex;
  align-items: center;
  gap: 5px;
  background: #f8f9fa;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  color: #495057;
}

.summary-icon {
  font-size: 14px;
}

.project-milestones {
  background: #fff3cd;
  border: 1px solid #ffeaa7;
  border-radius: 4px;
  padding: 10px;
  margin-bottom: 15px;
}

.milestone-item {
  font-size: 12px;
  color: #856404;
  margin-bottom: 5px;
}

.milestone-item:last-child {
  margin-bottom: 0;
}

.project-meta {
  color: #95a5a6;
  font-size: 12px;
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
  border-radius: 8px;
  min-width: 500px;
  max-width: 90vw;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #e1e8ed;
}

.modal-header h2 {
  margin: 0;
  color: #2c3e50;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #95a5a6;
}

.close-btn:hover {
  color: #2c3e50;
}

.modal-body {
  padding: 20px;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 600;
  color: #2c3e50;
}

.form-group input, .form-group textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  box-sizing: border-box;
}

.form-group input:focus, .form-group textarea:focus {
  outline: none;
  border-color: #3498db;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #e1e8ed;
}

.cancel-btn {
  padding: 10px 20px;
  border: 1px solid #95a5a6;
  background: white;
  color: #95a5a6;
  border-radius: 4px;
  cursor: pointer;
}

.cancel-btn:hover {
  background: #95a5a6;
  color: white;
}

/* Enhanced Modal Styles */
.large-modal {
  min-width: 800px;
  max-width: 95vw;
}

.form-section {
  margin-bottom: 30px;
  padding: 20px;
  border: 1px solid #e1e8ed;
  border-radius: 6px;
  background: #f8f9fa;
}

.form-section h3 {
  margin: 0 0 20px 0;
  color: #2c3e50;
  font-size: 18px;
  border-bottom: 2px solid #3498db;
  padding-bottom: 8px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
  margin-bottom: 15px;
}

.form-group select {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  box-sizing: border-box;
  background: white;
}

.form-group select:focus {
  outline: none;
  border-color: #3498db;
}

/* Stakeholder Styles */
.stakeholders-list, .collections-list, .documents-list {
  background: white;
  border-radius: 6px;
  padding: 15px;
}

.stakeholder-item, .collection-item, .document-item {
  display: grid;
  gap: 10px;
  margin-bottom: 15px;
  padding: 15px;
  border: 1px solid #e1e8ed;
  border-radius: 4px;
  background: #fafbfc;
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
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  box-sizing: border-box;
}

.stakeholder-input:focus, .collection-input:focus, .document-input:focus {
  outline: none;
  border-color: #3498db;
}

.add-btn {
  background: #27ae60;
  color: white;
  border: none;
  padding: 10px 15px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  margin-top: 10px;
}

.add-btn:hover {
  background: #229954;
}

.remove-btn {
  background: #e74c3c;
  color: white;
  border: none;
  padding: 6px 10px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}

.remove-btn:hover {
  background: #c0392b;
}

.project-actions {
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #e1e8ed;
}

.edit-btn {
  background: #3498db;
  color: white;
  border: none;
  padding: 8px 15px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.edit-btn:hover {
  background: #2980b9;
}
</style>
