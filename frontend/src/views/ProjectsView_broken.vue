<template>
  <div class="projects-view">
    <Breadcrumbs />
    
    <div class="page-header">
        <h1>
          <span class="page-icon">🎯</span>
          Projects
        </h1>
        <p class="page-description">
          Manage projects, stakeholders, and review workflows. Projects provide the organizational structure 
          for your document reviews and team collaboration.
        </p>
      </div>

      <div class="actions-bar">
        <button @click="showCreateModal = true" class="create-btn">
          <i class="icon">+</i>
          New Project
        </button>
      </div>

      <!-- Projects List -->
      <div v-if="projects.length === 0" class="empty-projects">
        <div class="empty-content">
          <div class="empty-icon">🎯</div>
          <h2>No Projects Yet</h2>
          <p>Get started by creating your first project to organize topics, stakeholders, and review workflows.</p>
          <button @click="showCreateModal = true" class="create-first-btn">
            <i class="icon">+</i>
            Create Your First Project
          </button>
        </div>
      </div>

      <div v-else class="projects-grid">
        <div
          v-for="project in projects"
          :key="project.id"
          class="project-card"
          @click="selectProject(project)"
          :class="{ 'selected': selectedProject?.id === project.id }"
        >
          <div class="project-header">
            <h3>{{ project.name }}</h3>
            <span class="status-badge" :class="project.status">
              {{ formatStatus(project.status) }}
            </span>
          </div>
          <p class="project-description">{{ project.description }}</p>
          <div class="project-stats">
            <div class="stat">
              <span class="label">Stakeholders:</span>
              <span class="value">{{ project.stakeholders_count || 0 }}</span>
            </div>
            <div class="stat">
              <span class="label">Collections:</span>
              <span class="value">{{ project.collections_count || 0 }}</span>
            </div>
            <div class="stat">
              <span class="label">Active Reviews:</span>
              <span class="value">{{ project.active_reviews_count || 0 }}</span>
            </div>
          </div>
          <div class="project-dates">
            <div v-if="project.start_date">
              Started: {{ formatDate(project.start_date) }}
            </div>
            <div v-if="project.target_completion">
              Target: {{ formatDate(project.target_completion) }}
            </div>
          </div>
        </div>
      </div>

      <!-- Project Details Panel -->
      <div v-if="selectedProject" class="project-details">
        <div class="details-header">
          <h2>{{ selectedProject.name }}</h2>
          <div class="actions">
            <button @click="editProject" class="edit-btn">Edit</button>
            <button @click="manageStakeholders" class="stakeholders-btn">Manage Stakeholders</button>
          </div>
        </div>

        <div class="details-content">
          <div class="details-section">
            <h3>Overview</h3>
            <p>{{ selectedProject.description }}</p>
            <div class="project-info">
              <div><strong>Status:</strong> {{ formatStatus(selectedProject.status) }}</div>
              <div v-if="selectedProject.start_date">
                <strong>Start Date:</strong> {{ formatDate(selectedProject.start_date) }}
              </div>
              <div v-if="selectedProject.target_completion">
                <strong>Target Completion:</strong> {{ formatDate(selectedProject.target_completion) }}
              </div>
            </div>
          </div>

          <div class="details-section">
            <h3>Stakeholders ({{ projectDetails?.stakeholders?.length || 0 }})</h3>
            <div v-if="projectDetails?.stakeholders?.length" class="stakeholders-list">
              <div
                v-for="stakeholder in projectDetails.stakeholders"
                :key="stakeholder.id"
                class="stakeholder-item"
              >
                <div class="stakeholder-info">
                  <strong>{{ stakeholder.name }}</strong>
                  <span class="role">{{ formatRole(stakeholder.role) }}</span>
                </div>
                <div class="stakeholder-meta">
                  <span class="email">{{ stakeholder.email }}</span>
                  <span v-if="stakeholder.can_review" class="can-review">Can Review</span>
                </div>
              </div>
            </div>
            <p v-else class="empty-state">No stakeholders added yet.</p>
          </div>

          <div class="details-section">
            <h3>Milestones ({{ projectDetails?.milestones?.length || 0 }})</h3>
            <div v-if="projectDetails?.milestones?.length" class="milestones-list">
              <div
                v-for="milestone in projectDetails.milestones"
                :key="milestone.id"
                class="milestone-item"
                :class="milestone.status"
              >
                <div class="milestone-info">
                  <strong>{{ milestone.title }}</strong>
                  <span class="milestone-status">{{ formatStatus(milestone.status) }}</span>
                </div>
                <p v-if="milestone.description" class="milestone-description">
                  {{ milestone.description }}
                </p>
                <div v-if="milestone.due_date" class="milestone-date">
                  Due: {{ formatDate(milestone.due_date) }}
                </div>
              </div>
            </div>
            <p v-else class="empty-state">No milestones defined yet.</p>
          </div>

          <div class="details-section">
            <h3>Active Reviews ({{ projectReviews.length }})</h3>
            <div v-if="projectReviews.length" class="reviews-list">
              <div
                v-for="review in projectReviews"
                :key="review.id"
                class="review-item"
                :class="review.status"
              >
                <div class="review-info">
                  <strong>{{ review.topic?.title }}</strong>
                  <span class="review-status">{{ formatStatus(review.status) }}</span>
                </div>
                <div class="review-meta">
                  <div>Assigned to: {{ review.assigned_stakeholder?.name }}</div>
                  <div v-if="review.due_date">Due: {{ formatDate(review.due_date) }}</div>
                  <div>Submitted: {{ formatDate(review.submitted_at) }}</div>
                </div>
                <p v-if="review.submitter_notes" class="review-notes">
                  {{ review.submitter_notes }}
                </p>
              </div>
            </div>
            <p v-else class="empty-state">No active reviews.</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Project Modal -->
  <div v-if="showCreateModal" class="modal-overlay" @click="showCreateModal = false">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h2>Create New Project</h2>
          <button @click="showCreateModal = false" class="close-btn">×</button>
        </div>
        <form @submit.prevent="createProject" class="modal-body">
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
            <label for="projectDescription">Description</label>
            <textarea
              id="projectDescription"
              v-model="newProject.description"
              placeholder="Project description"
              rows="3"
            ></textarea>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label for="startDate">Start Date</label>
              <input
                id="startDate"
                v-model="newProject.start_date"
                type="date"
              />
            </div>
            <div class="form-group">
              <label for="targetDate">Target Completion</label>
              <input
                id="targetDate"
                v-model="newProject.target_completion"
                type="date"
              />
            </div>
          </div>
          <div class="form-group">
            <label for="projectStatus">Status</label>
            <select id="projectStatus" v-model="newProject.status">
              <option value="planning">Planning</option>
              <option value="active">Active</option>
              <option value="on_hold">On Hold</option>
            </select>
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

    <!-- Stakeholders Management Modal -->
  <div v-if="showStakeholdersModal" class="modal-overlay" @click="showStakeholdersModal = false">
      <div class="modal stakeholders-modal" @click.stop>
        <div class="modal-header">
          <h2>Manage Stakeholders - {{ selectedProject?.name }}</h2>
          <button @click="showStakeholdersModal = false" class="close-btn">×</button>
        </div>
        <div class="modal-body">
          <!-- Add New Stakeholder Form -->
          <form @submit.prevent="addStakeholder" class="add-stakeholder-form">
            <h3>Add New Stakeholder</h3>
            <div class="form-row">
              <div class="form-group">
                <label>Name *</label>
                <input v-model="newStakeholder.name" type="text" required />
              </div>
              <div class="form-group">
                <label>Email *</label>
                <input v-model="newStakeholder.email" type="email" required />
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label>Role *</label>
                <select v-model="newStakeholder.role" required>
                  <option value="project_manager">Project Manager</option>
                  <option value="subject_matter_expert">Subject Matter Expert</option>
                  <option value="reviewer">Reviewer</option>
                  <option value="stakeholder">Stakeholder</option>
                </select>
              </div>
              <div class="form-group">
                <label class="checkbox-label">
                  <input v-model="newStakeholder.can_review" type="checkbox" />
                  Can Review Topics
                </label>
              </div>
            </div>
            <div class="form-group">
              <label>Notes</label>
              <textarea v-model="newStakeholder.notes" rows="2"></textarea>
            </div>
            <button type="submit" class="add-btn">Add Stakeholder</button>
          </form>

          <!-- Current Stakeholders List -->
          <div class="current-stakeholders">
            <h3>Current Stakeholders</h3>
            <div v-if="projectDetails?.stakeholders?.length" class="stakeholders-table">
              <div
                v-for="stakeholder in projectDetails.stakeholders"
                :key="stakeholder.id"
                class="stakeholder-row"
              >
                <div class="stakeholder-main">
                  <strong>{{ stakeholder.name }}</strong>
                  <span class="role-badge">{{ formatRole(stakeholder.role) }}</span>
                  <span v-if="stakeholder.can_review" class="review-badge">Can Review</span>
                </div>
                <div class="stakeholder-details">
                  <span class="email">{{ stakeholder.email }}</span>
                  <span v-if="stakeholder.notes" class="notes">{{ stakeholder.notes }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
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
      selectedProject: null,
      projectDetails: null,
      projectReviews: [],
      showCreateModal: false,
      showStakeholdersModal: false,
      newProject: {
        name: '',
        description: '',
        status: 'planning',
        start_date: '',
        target_completion: ''
      },
      newStakeholder: {
        name: '',
        email: '',
        role: 'reviewer',
        can_review: true,
        notes: ''
      }
    }
  },
  async mounted() {
    await this.loadProjects()
  },
  methods: {
    async loadProjects() {
      try {
        const response = await fetch('/api/projects/')
        if (response.ok) {
          this.projects = await response.json()
        }
      } catch (error) {
        console.error('Failed to load projects:', error)
      }
    },

    async selectProject(project) {
      this.selectedProject = project
      await this.loadProjectDetails(project.id)
      await this.loadProjectReviews(project.id)
    },

    async loadProjectDetails(projectId) {
      try {
        const response = await fetch(`/api/projects/${projectId}`)
        if (response.ok) {
          this.projectDetails = await response.json()
        }
      } catch (error) {
        console.error('Failed to load project details:', error)
      }
    },

    async loadProjectReviews(projectId) {
      try {
        const response = await fetch(`/api/projects/${projectId}/reviews`)
        if (response.ok) {
          this.projectReviews = await response.json()
        }
      } catch (error) {
        console.error('Failed to load project reviews:', error)
      }
    },

    async createProject() {
      try {
        const response = await fetch('/api/projects/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(this.newProject)
        })
        
        if (response.ok) {
          const project = await response.json()
          this.projects.unshift(project)
          this.showCreateModal = false
          this.resetNewProject()
        }
      } catch (error) {
        console.error('Failed to create project:', error)
      }
    },

    async addStakeholder() {
      if (!this.selectedProject) return
      
      try {
        const response = await fetch(`/api/projects/${this.selectedProject.id}/stakeholders`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(this.newStakeholder)
        })
        
        if (response.ok) {
          const stakeholder = await response.json()
          if (!this.projectDetails.stakeholders) {
            this.projectDetails.stakeholders = []
          }
          this.projectDetails.stakeholders.push(stakeholder)
          this.resetNewStakeholder()
        }
      } catch (error) {
        console.error('Failed to add stakeholder:', error)
      }
    },

    manageStakeholders() {
      this.showStakeholdersModal = true
    },

    editProject() {
      // TODO: Implement project editing
      console.log('Edit project:', this.selectedProject)
    },

    resetNewProject() {
      this.newProject = {
        name: '',
        description: '',
        status: 'planning',
        start_date: '',
        target_completion: ''
      }
    },

    resetNewStakeholder() {
      this.newStakeholder = {
        name: '',
        email: '',
        role: 'reviewer',
        can_review: true,
        notes: ''
      }
    },

    formatStatus(status) {
      const statusMap = {
        'planning': 'Planning',
        'active': 'Active',
        'review': 'In Review',
        'completed': 'Completed',
        'on_hold': 'On Hold',
        'pending': 'Pending',
        'in_progress': 'In Progress',
        'delayed': 'Delayed',
        'in_review': 'In Review',
        'approved': 'Approved',
        'rejected': 'Rejected',
        'revision_requested': 'Revision Requested'
      }
      return statusMap[status] || status
    },

    formatRole(role) {
      const roleMap = {
        'project_manager': 'Project Manager',
        'subject_matter_expert': 'Subject Matter Expert',
        'reviewer': 'Reviewer',
        'stakeholder': 'Stakeholder'
      }
      return roleMap[role] || role
    },

    formatDate(dateString) {
      if (!dateString) return ''
      return new Date(dateString).toLocaleDateString()
    }
  }
}
</script>

<style scoped>
.projects-view {
  padding: 70px 20px 20px 20px; /* Top padding to account for fixed header */
}

.page-header {
  margin-bottom: 20px;
}

.page-header h1 {
  margin: 0 0 10px 0;
  color: #2c3e50;
  font-size: 2rem;
  display: flex;
  align-items: center;
  gap: 12px;
}

.page-icon {
  font-size: 2rem;
  line-height: 1;
}

.page-description {
  margin: 0 0 20px 0;
  color: #7f8c8d;
  font-size: 16px;
  line-height: 1.5;
  max-width: 800px;
}

.actions-bar {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 30px;
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

.empty-content h2 {
  color: #2c3e50;
  margin-bottom: 15px;
}

.empty-content p {
  color: #7f8c8d;
  font-size: 16px;
  line-height: 1.5;
  margin-bottom: 25px;
}

.create-first-btn {
  background: #27ae60;
  color: white;
  border: none;
  padding: 15px 30px;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 600;
  font-size: 16px;
  margin: 0 auto;
  transition: all 0.2s;
}

.create-first-btn:hover {
  background: #219a52;
  transform: translateY(-1px);
}

.create-btn {
  background: #3498db;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
}

.create-btn:hover {
  background: #2980b9;
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
  cursor: pointer;
  transition: all 0.2s;
  background: white;
}

.project-card:hover {
  border-color: #3498db;
  box-shadow: 0 4px 12px rgba(52, 152, 219, 0.1);
}

.project-card.selected {
  border-color: #3498db;
  background: #f8fcff;
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

.status-badge.review {
  background: #e74c3c;
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

.project-stats {
  display: flex;
  gap: 15px;
  margin-bottom: 10px;
}

.stat {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 14px;
}

.stat .label {
  color: #7f8c8d;
}

.stat .value {
  font-weight: 600;
  color: #2c3e50;
}

.project-dates {
  font-size: 12px;
  color: #95a5a6;
}

.project-details {
  border: 1px solid #e1e8ed;
  border-radius: 8px;
  background: white;
  overflow: hidden;
}

.details-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #e1e8ed;
  background: #f8f9fa;
}

.details-header h2 {
  margin: 0;
  color: #2c3e50;
}

.actions {
  display: flex;
  gap: 10px;
}

.edit-btn, .stakeholders-btn {
  padding: 8px 16px;
  border: 1px solid #3498db;
  background: white;
  color: #3498db;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.edit-btn:hover, .stakeholders-btn:hover {
  background: #3498db;
  color: white;
}

.details-content {
  padding: 20px;
}

.details-section {
  margin-bottom: 30px;
}

.details-section h3 {
  margin: 0 0 15px 0;
  color: #2c3e50;
  font-size: 18px;
}

.project-info {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 10px;
  margin-top: 15px;
}

.stakeholders-list, .milestones-list, .reviews-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.stakeholder-item, .milestone-item, .review-item {
  padding: 15px;
  border: 1px solid #e1e8ed;
  border-radius: 6px;
  background: #f8f9fa;
}

.stakeholder-info, .milestone-info, .review-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.stakeholder-meta, .milestone-date, .review-meta {
  font-size: 14px;
  color: #7f8c8d;
}

.role, .milestone-status, .review-status {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  background: #ecf0f1;
  color: #2c3e50;
}

.can-review {
  background: #d5ecd5;
  color: #27ae60;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.empty-state {
  color: #95a5a6;
  font-style: italic;
  text-align: center;
  padding: 20px;
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

.stakeholders-modal {
  min-width: 700px;
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

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 600;
  color: #2c3e50;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.form-group input, .form-group select, .form-group textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.form-group input:focus, .form-group select:focus, .form-group textarea:focus {
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

.add-stakeholder-form {
  margin-bottom: 30px;
  padding-bottom: 30px;
  border-bottom: 1px solid #e1e8ed;
}

.add-stakeholder-form h3 {
  margin: 0 0 20px 0;
  color: #2c3e50;
}

.add-btn {
  background: #27ae60;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
}

.add-btn:hover {
  background: #219a52;
}

.current-stakeholders h3 {
  margin: 0 0 15px 0;
  color: #2c3e50;
}

.stakeholders-table {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.stakeholder-row {
  padding: 15px;
  border: 1px solid #e1e8ed;
  border-radius: 6px;
  background: #f8f9fa;
}

.stakeholder-main {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.role-badge, .review-badge {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.role-badge {
  background: #ecf0f1;
  color: #2c3e50;
}

.review-badge {
  background: #d5ecd5;
  color: #27ae60;
}

.stakeholder-details {
  font-size: 14px;
  color: #7f8c8d;
}

.stakeholder-details .email {
  margin-right: 15px;
}
</style>
