<template>
  
  <div class="projects-dashboard">
    
    
    <!-- Dashboard Header -->
    <div class="dashboard-header">
      <h1>Projects Dashboard</h1>
      <p class="subtitle">Manage projects, stakeholders, and review workflows</p>
    </div>
    <!-- Metrics Overview -->
    <div class="dashboard-section">
      <h2>Key Metrics</h2>
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
    </div>

    <!-- Quick Actions -->
    <div class="section-card">
      <div class="section-header">
        <h2 class="section-title">Quick Actions</h2>
      </div>
      <div class="quick-actions-grid">
        <button @click="showCreateModal = true" class="quick-action-card">
          <div class="action-icon">📝</div>
          <div class="action-content" title="Start a new documentation project">
            <h3>Create Project</h3>
          </div>
        </button>
        
        <button @click="filterByStatus('active')" class="quick-action-card">
          <div class="action-icon">🎯</div>
          <div class="action-content" title="See all currently active projects">
            <h3>View Active</h3>
          </div>
        </button>
        
        
        <button @click="exportProjects" class="quick-action-card" :disabled="exporting">
          <div class="action-icon">📤</div>
          <div class="action-content" :title="exporting ? 'Exporting...' : 'Download comprehensive project reports & analytics'">
            <h3>Export Data</h3>
          </div>
        </button>
      </div>
    </div>

    <!-- Project Calendar -->
    <div class="section-card">
      <div class="section-header">
        <h2 class="section-title">Project Calendar</h2>
      </div>
      <CalendarWidget :events="calendarEvents" />
    </div>

  <!-- Projects List -->
  <div class="section-card" id="projectsSection" ref="projectsSection">
      <div class="section-header">
        <h2 class="section-title">Projects List</h2>
      </div>

      <!-- Combined Search/Filter Panel -->
      <div class="projects-list-panel">
        <div class="filter-row">
          <div class="filter-group">
            <label>Search:</label>
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search projects..."
              class="filter-input"
              @input="applyFilters"
            />
          </div>
          <div class="filter-group">
            <label>Status:</label>
            <select v-model="statusFilter" @change="applyFilters" class="filter-input">
              <option value="">All Statuses</option>
              <option value="planning">Planning</option>
              <option value="active">Active</option>
              <option value="on_hold">On Hold</option>
              <option value="completed">Completed</option>
            </select>
          </div>
          <div class="filter-group">
            <div class="button-group">
              <button @click="applyFilters" class="btn btn-primary btn-sm search-btn">
                <i class="fas fa-search"></i> Search
              </button>
              <button @click="clearFilter" class="btn btn-secondary btn-sm clear-btn"><i class="fas fa-times"></i> Clear Filters</button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Loading State -->
      <div v-if="loading" class="loading-overlay">
        <div class="loading-container">
          <div class="loading-spinner"></div>
          <p class="loading-text">Loading...</p>
        </div>
      </div>
      <!-- Error State -->
      <div v-else-if="error" class="error-state">
        <div class="error-content">
          <div class="error-icon">⚠️</div>
          <h3>Error Loading Projects</h3>
          <p>{{ error }}</p>
          <button @click="fetchProjects" class="retry-btn">🔄 Retry</button>
        </div>
      </div>
      <!-- Empty State -->
      <div v-else-if="filteredProjects.length === 0" class="empty-state">
        <div class="empty-content">
          <div class="empty-icon">🎯</div>
          <h3>{{ projects.length === 0 ? 'No Projects Yet' : 'No Projects Match Filter' }}</h3>
          <p>{{ projects.length === 0 ? 'Get started by creating your first project to organize topics, stakeholders, and review workflows.' : 'Try adjusting your filters or create a new project.' }}</p>
          <button @click="showCreateModal = true" class="btn btn-primary create-first-btn">
            ➕ {{ projects.length === 0 ? 'Create Your First Project' : 'Create New Project' }}
          </button>
        </div>
      </div>
      <!-- Projects List -->
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
            <div class="milestone-item" v-for="milestone in project.milestones.slice(0, 3)" :key="milestone.name">
              <strong>{{ milestone.name }}:</strong> 
              <span :class="['milestone-date', milestone.status]">
                {{ formatDate(milestone.date) }}
                <span class="milestone-status">({{ formatMilestoneStatus(milestone.status) }})</span>
              </span>
            </div>
            <div v-if="project.milestones.length > 3" class="milestone-more">
              +{{ project.milestones.length - 3 }} more milestones
            </div>
          </div>
          <div class="project-card-footer">
            <div class="project-meta">Project {{ project.id }} was created on {{ formatDate(project.created_at) }}</div>
            <button @click="editProject(project)" class="edit-btn">✏️ Edit</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Project Modal -->
    <div v-if="showCreateModal" class="modal-overlay" @click.self="showCreateModal = false">
      <div class="modal large-modal" @click.stop>
        <div class="modal-header">
          <h2>Create New Project</h2>
          <button @click="showCreateModal = false" class="close-btn">×</button>
        </div>
    <form @submit.prevent="handleCreateProject" class="modal-body">
          <p v-if="createdProjectId" class="subtitle" style="margin-top:0;margin-bottom:0.75rem;">
            Project created — click Next to add stakeholders.
          </p>
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

          <div class="modal-actions">
            <button type="button" @click="showCreateModal = false" class="btn btn-secondary">
              Cancel
            </button>
            <button type="submit" class="btn btn-primary" :disabled="creatingProject">Next</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Stakeholder Modal (Step 2) -->
    <div v-if="showStakeholderModal" class="modal-overlay" @click.self="showStakeholderModal = false">
      <div class="modal large-modal" @click.stop>
        <div class="modal-header">
          <h2>Add Stakeholders to Project</h2>
          <button @click="showStakeholderModal = false" class="close-btn">×</button>
        </div>
        <div class="modal-body">
          <div class="form-section">
            <h3>Add Existing Stakeholder</h3>
            <div class="selector-row">
              <select v-model="selectedStakeholderId" class="stakeholder-select">
                <option value="">Select a stakeholder...</option>
                <option v-for="stakeholder in availableStakeholders" :key="stakeholder.id" :value="stakeholder.id">
                  {{ stakeholder.name }} ({{ stakeholder.organization }})
                </option>
              </select>
              <select v-model="selectedStakeholderRole" class="role-select">
                <option value="">Select role...</option>
                <option value="project_manager">Project Manager</option>
                <option value="subject_matter_expert">Subject Matter Expert</option>
                <option value="reviewer">Reviewer</option>
                <option value="stakeholder">Stakeholder</option>
                <option value="sponsor">Sponsor</option>
              </select>
              <button type="button" @click="addSelectedStakeholderToProject" :disabled="!selectedStakeholderId || !selectedStakeholderRole" class="btn btn-primary btn-sm add-btn">
                + Add Selected
              </button>
            </div>
          </div>
          <div class="form-section">
            <h3>Or Add New Stakeholder</h3>
            <div class="form-row">
              <input v-model="newStakeholder.name" type="text" placeholder="Name *" required class="stakeholder-input" />
              <input v-model="newStakeholder.email" type="email" placeholder="Email *" required class="stakeholder-input" />
              <input v-model="newStakeholder.title" type="text" placeholder="Title" class="stakeholder-input" />
              <input v-model="newStakeholder.organization" type="text" placeholder="Organization" class="stakeholder-input" />
              <select v-model="newStakeholder.role" class="role-select stakeholder-input" required>
                <option value="">Select role...</option>
                <option value="project_manager">Project Manager</option>
                <option value="subject_matter_expert">Subject Matter Expert</option>
                <option value="reviewer">Reviewer</option>
                <option value="stakeholder">Stakeholder</option>
                <option value="sponsor">Sponsor</option>
              </select>
              <button type="button" @click="addNewStakeholderToProject" :disabled="!newStakeholder.name || !newStakeholder.email || !newStakeholder.role" class="btn btn-primary btn-sm add-btn">
                + Add Stakeholder
              </button>
            </div>
          </div>
          <div class="form-section">
            <h3>Current Project Stakeholders</h3>
            <ul>
              <li v-for="s in projectStakeholders" :key="s.id || s.email">
                {{ s.name }} ({{ s.role }}) <span v-if="s.email">- {{ s.email }}</span>
              </li>
            </ul>
          </div>
          <div class="modal-actions">
            <button type="button" class="btn btn-primary" @click="proceedToMilestones">Add Stakeholders</button>
            <button type="button" class="btn btn-secondary ml-1" @click="skipStakeholders">Not Now</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Milestone Modal (Step 3) -->
    <div v-if="showMilestoneModal" class="modal-overlay" @click.self="showMilestoneModal = false">
      <div class="modal large-modal" @click.stop>
        <div class="modal-header">
          <h2>Add Project Milestones</h2>
          <button @click="showMilestoneModal = false" class="close-btn">×</button>
        </div>
        <div class="modal-body">
          <div class="form-section">
            <h3>Milestones</h3>
            <div v-for="(milestone, idx) in newMilestones" :key="idx" class="milestone-row">
              <input v-model="milestone.name" type="text" placeholder="Milestone Name *" required class="milestone-input" />
              <input v-model="milestone.date" type="date" placeholder="Due Date" class="milestone-input" />
              <select v-model="milestone.status" class="milestone-input">
                <option value="planned">Planned</option>
                <option value="in-progress">In Progress</option>
                <option value="completed">Completed</option>
                <option value="overdue">Overdue</option>
              </select>
              <button type="button" @click="removeMilestone(idx)" class="btn btn-danger btn-sm remove-btn">×</button>
            </div>
            <button type="button" @click="addMilestoneRow" class="btn btn-primary btn-sm add-btn">+ Add Milestone</button>
          </div>
          <div class="modal-actions">
            <button type="button" class="btn btn-primary" @click="saveMilestonesAndFinish">Add Milestones</button>
            <button type="button" class="btn btn-secondary ml-1" @click="skipMilestones">Not Now</button>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Edit Project Modal -->
  <div v-if="showEditModal" class="modal-overlay" @click.self="showEditModal = false">
    <div class="modal large-modal" @click.stop>
      <div class="modal-header">
        <h2>Edit Project: {{ editingProject.name || 'Loading...' }}</h2>
        <button @click="showEditModal = false" class="close-btn">×</button>
      </div>
      <form @submit.prevent="handleUpdateProject" class="modal-body">
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

        <!-- Stakeholders Section -->
        <div class="form-section">
          <h3>Stakeholders</h3>
          
          <!-- Add from existing stakeholders -->
          <div class="stakeholder-selector">
            <h4>Add Existing Stakeholder</h4>
            <div class="selector-row">
              <select v-model="selectedStakeholderId" class="stakeholder-select">
                <option value="">Select a stakeholder...</option>
                <option 
                  v-for="stakeholder in availableStakeholders" 
                  :key="stakeholder.id" 
                  :value="stakeholder.id"
                >
                  {{ stakeholder.name }} ({{ stakeholder.organization }})
                </option>
              </select>
              <select v-model="selectedStakeholderRole" class="role-select">
                <option value="">Select role...</option>
                <option value="project_manager">Project Manager</option>
                <option value="subject_matter_expert">Subject Matter Expert</option>
                <option value="reviewer">Reviewer</option>
                <option value="stakeholder">Stakeholder</option>
                <option value="sponsor">Sponsor</option>
              </select>
              <button 
                type="button" 
                @click="addExistingStakeholder('edit')" 
                :disabled="!selectedStakeholderId || !selectedStakeholderRole"
                class="btn btn-primary btn-sm add-btn"
              >
                + Add Selected
              </button>
            </div>
          </div>

          <!-- Current project stakeholders -->
          <div class="stakeholders-list">
            <h4>Project Stakeholders</h4>
            <div v-for="(stakeholder, index) in editingProject.stakeholders" :key="index" class="stakeholder-item">
              <div class="stakeholder-info">
                <strong>{{ stakeholder.name }}</strong>
                <span class="stakeholder-details">{{ stakeholder.email }} | {{ stakeholder.organization }}</span>
              </div>
              <select
                v-model="stakeholder.role"
                class="stakeholder-role-input"
              >
                <option value="project_manager">Project Manager</option>
                <option value="subject_matter_expert">Subject Matter Expert</option>
                <option value="reviewer">Reviewer</option>
                <option value="stakeholder">Stakeholder</option>
                <option value="sponsor">Sponsor</option>
              </select>
              <input
                v-model="stakeholder.notes"
                type="text"
                placeholder="Notes (optional)"
                class="stakeholder-input"
              />
              <button type="button" @click="removeStakeholder(index, 'edit')" class="remove-btn">✕</button>
            </div>
            
            <!-- Add new stakeholder manually -->
            <div class="add-new-stakeholder">
              <h4>Or Add New Stakeholder</h4>
              <div class="new-stakeholder-form">
                <input
                  v-model="newStakeholderName"
                  type="text"
                  placeholder="Full name"
                  class="stakeholder-input"
                />
                <input
                  v-model="newStakeholderEmail"
                  type="email"
                  placeholder="Email address"
                  class="stakeholder-input"
                />
                <input
                  v-model="newStakeholderTitle"
                  type="text"
                  placeholder="Title"
                  class="stakeholder-input"
                />
                <input
                  v-model="newStakeholderOrganization"
                  type="text"
                  placeholder="Organization"
                  class="stakeholder-input"
                />
                <select v-model="newStakeholderRole" class="stakeholder-input">
                  <option value="">Select role...</option>
                  <option value="project_manager">Project Manager</option>
                  <option value="subject_matter_expert">Subject Matter Expert</option>
                  <option value="reviewer">Reviewer</option>
                  <option value="stakeholder">Stakeholder</option>
                  <option value="sponsor">Sponsor</option>
                </select>
                <button 
                  type="button" 
                  @click="addNewStakeholder('edit')"
                  :disabled="!newStakeholderName || !newStakeholderEmail || !newStakeholderRole"
                  class="btn btn-primary btn-sm add-btn"
                >
                  + Add New Stakeholder
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Milestones Section -->
        <div class="form-section">
          <h3>Milestones</h3>
          <div class="milestones-list">
            <div v-for="(milestone, index) in editingProject.milestones" :key="index" class="milestone-item">
              <input
                v-model="milestone.name"
                type="text"
                placeholder="Milestone name"
                class="milestone-input"
              />
              <input
                v-model="milestone.date"
                type="date"
                class="milestone-input"
                placeholder="Target date"
              />
              <select
                v-model="milestone.status"
                class="milestone-input"
              >
                <option value="planned">Planned</option>
                <option value="in_progress">In Progress</option>
                <option value="completed">Completed</option>
                <option value="delayed">Delayed</option>
              </select>
              <button type="button" @click="removeMilestone(index, 'edit')" class="btn btn-danger btn-sm remove-btn">✕</button>
            </div>
            <button type="button" @click="addMilestone('edit')" class="btn btn-primary btn-sm add-btn">+ Add Milestone</button>
          </div>
        </div>

        <div class="modal-actions">
          <button type="button" @click="showEditModal = false" class="btn btn-secondary">
            Cancel
          </button>
          <button type="submit" class="btn btn-primary">
            Update Project
          </button>
        </div>
      </form>
    </div>
  </div>

</template>


<script>
import CalendarWidget from '../components/CalendarWidget.vue'
import { createStakeholder, addStakeholderToProject } from '../api/stakeholders';
import { getCollections, updateCollection } from '../api/collections';
import { createPublication, deletePublication, updatePublication } from '../api/publications';
import { createMilestone, deleteMilestone, updateMilestone } from '../api/milestones';
import unsavedChangesGuard from '@/mixins/unsavedChangesGuard.js'
import { toast } from '@/composables/useToast'

export default {
  components: { CalendarWidget },
  mixins: [unsavedChangesGuard],
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
      // ...existing data properties...
      projects: [],
      loading: false,
      error: null,
      showEditModal: false,
      statusFilter: '',
      searchQuery: '',
      
      showCreateModal: false,
      showTemplateModal: false,
      
      // Available stakeholders from API
      availableStakeholders: [],
      loadingStakeholders: false,
      
      // Stakeholder selection
      selectedStakeholderId: '',
      selectedStakeholderRole: '',
      
      // New stakeholder form
      newStakeholder: { name: '', email: '', title: '', organization: '', role: '' },
      
      // Individual new stakeholder properties for form binding
      newStakeholderName: '',
      newStakeholderEmail: '',
      newStakeholderTitle: '',
      newStakeholderOrganization: '',
      newStakeholderRole: '',
      
      newProject: {
        name: '',
        description: '',
        status: 'planning',
        stakeholders: [],
        milestones: [],
        collections: [],
        publishedDocuments: []
      },
      editingProject: {
        id: null,
        name: '',
        description: '',
        status: 'planning',
        stakeholders: [],
        milestones: [],
        collections: [],
        publishedDocuments: []
      },
      // Multi-step project creation
      createProjectStep: 1,
      createdProjectId: null,
      createdProjectName: '',
      showStakeholderModal: false,
      showMilestoneModal: false,
      projectStakeholders: [],
      newMilestones: [{ name: '', date: '', status: 'planned' }],
      creatingProject: false,
      exporting: false,
  
  createProjectSnapshot: '',
  editProjectSnapshot: '',
  stakeholderModalSnapshot: '',
  milestoneModalSnapshot: ''
    }
  },
  computed: {
    mergedNotifications() {
      // Combine global and dashboard-specific notifications, removing duplicates by id
      const all = [...(this.globalNotifications || []), ...(this.notifications || [])]
      const seen = new Set()
      return all.filter(n => {
        if (!n || !n.id) return true
        if (seen.has(n.id)) return false
        seen.add(n.id)
        return true
      })
    },
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
        newThisMonth: Math.floor(total * 0.2),
        activePercentage: total > 0 ? Math.round((active / total) * 100) : 0,
        completionRate: total > 0 ? Math.round((completed / total) * 100) : 0
      }
    },
    filteredProjects() {
      let filtered = [...this.projects]
      
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase()
        filtered = filtered.filter(project =>
          project.name.toLowerCase().includes(query) ||
          (project.description && project.description.toLowerCase().includes(query)) ||
          (project.project_manager && project.project_manager.toLowerCase().includes(query))
        )
      }
      
      if (this.statusFilter) {
        filtered = filtered.filter(project => project.status === this.statusFilter)
      }
      
      return filtered
    },
  calendarEvents() {
      const events = []
      this.projects.forEach(project => {
        if (project.milestones && Array.isArray(project.milestones)) {
          project.milestones.forEach(milestone => {
            if (milestone.date) {
              events.push({
                id: `${project.id}-${milestone.name}`,
                title: `${project.name}: ${milestone.name} (${milestone.status})`,
                date: milestone.date,
                type: 'milestone',
                project: project.name,
                status: milestone.status
              })
            }
          })
        }
        if (project.created_at) {
          events.push({
            id: `${project.id}-created`,
            title: `Project Created: ${project.name}`,
            date: project.created_at.split('T')[0],
            type: 'meeting',
            project: project.name
          })
        }
      })
      return events
    }
  },
  methods: {
    proceedToStakeholders() {
      this.showStakeholderModal = true;
    },
    handleCreateProject() {
      // If a project was just created, the Next button should advance to Stakeholders
      if (this.createdProjectId) {
        this.proceedToStakeholders();
      } else {
        this.createProjectBasic();
      }
    },

    async handleUpdateProject() {
      try {
        // First, update the basic project information
        const response = await fetch(`/api/projects/${this.editingProject.id}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            name: this.editingProject.name,
            description: this.editingProject.description,
            status: this.editingProject.status
          })
        })

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }

        const updatedProject = await response.json()
        
        // Handle stakeholder updates
        const newStakeholders = this.editingProject.stakeholders.filter(s => s.isNew)
        for (const stakeholder of newStakeholders) {
          try {
            if (stakeholder.stakeholder_id) {
              // Add existing stakeholder to project
              await fetch(`/api/projects/${this.editingProject.id}/stakeholders`, {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                  stakeholder_id: stakeholder.stakeholder_id,
                  role: stakeholder.role,
                  notes: stakeholder.notes
                })
              })
            } else {
              // Create new stakeholder and add to project
              await fetch(`/api/projects/${this.editingProject.id}/stakeholders`, {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                  name: stakeholder.name,
                  email: stakeholder.email,
                  title: stakeholder.title,
                  organization: stakeholder.organization,
                  role: stakeholder.role,
                  notes: stakeholder.notes
                })
              })
            }
          } catch (stakeholderError) {
            console.error('Failed to add stakeholder:', stakeholder, stakeholderError)
            // Continue with other stakeholders even if one fails
          }
        }
        
        // Update the project in the local array
        const index = this.projects.findIndex(p => p.id === this.editingProject.id)
        if (index !== -1) {
          this.projects[index] = {
            ...this.projects[index],
            ...updatedProject
          }
        }

        // Refresh the projects list to get updated stakeholder information
        await this.fetchProjects()

  // Show success toast and close modal
  toast.success('Project updated successfully.')
  this.showEditModal = false
  this.resetEditingProject()
        
      } catch (error) {
        console.error('Failed to update project:', error)
  toast.error('Failed to update project. Please check the fields and try again.')
      }
    },
    async fetchProjects() {
      this.loading = true
      this.error = null
      try {
        const response = await fetch('/api/projects/')
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        const projects = await response.json()
        
        // Transform API data to match frontend expectations
        this.projects = projects.map(project => ({
          ...project,
          stakeholders: project.stakeholders || [],
          milestones: project.milestones || [],
          collections: project.collections || [],
          publishedDocuments: project.publishedDocuments || []
        }))
        
        console.log('Loaded projects:', this.projects)
      } catch (error) {
        console.error('Failed to fetch projects:', error)
        this.error = 'Failed to load projects. Please try again.'
        
  // Fallback to empty array if API fails
  this.projects = []
      } finally {
        this.loading = false
      }
    },

  // Removed getSampleProjects - no more sample/demo data

    async fetchStakeholders() {
      this.loadingStakeholders = true
      try {
        const response = await fetch('/api/stakeholders/')
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        const stakeholders = await response.json()
        this.availableStakeholders = stakeholders
        console.log('Loaded stakeholders:', this.availableStakeholders)
      } catch (error) {
        console.error('Failed to fetch stakeholders:', error)
        // Fallback data if API fails
        this.availableStakeholders = [
          {
            id: 1,
            name: "Dr. Sarah Johnson",
            email: "sarah.johnson@census.gov",
            title: "Senior Project Manager",
            organization: "U.S. Census Bureau"
          },
          {
            id: 2,
            name: "Prof. Michael Chen",
            email: "michael.chen@statistics.gov",
            title: "Chief Statistician",
            organization: "Bureau of Labor Statistics"
          },
          {
            id: 3,
            name: "Dr. Amanda Rodriguez",
            email: "amanda.rodriguez@census.gov",
            title: "Quality Assurance Specialist",
            organization: "U.S. Census Bureau"
          }
        ]
      } finally {
        this.loadingStakeholders = false
      }
    },


  async createProjectBasic() {
      this.creatingProject = true;
      try {
        const payload = {
          name: this.newProject.name,
          description: this.newProject.description,
          status: this.newProject.status,
          start_date: this.newProject.start_date || null,
          target_completion: this.newProject.target_completion || null
        }
        const response = await fetch('/api/projects/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        })
        if (!response.ok) {
          const errorText = await response.text()
          throw new Error(`Failed to create project: ${response.status} ${errorText}`)
        }
        const createdProject = await response.json()
        this.createdProjectId = createdProject.id
        this.createdProjectName = createdProject.name
        // Immediately reflect in dashboard list/metrics
        this.projects = [createdProject, ...this.projects]
        // Show success as a toast instead of inline confirmation with OK
        toast.success(`Project #${createdProject.id} (${createdProject.name}) was created successfully!`)
        this.createProjectStep = 2
        // Only close the modal after user clicks OK (handled in proceedToStakeholders)
        // this.showStakeholderModal = true
        // this.showCreateModal = false
        // Optionally, store createdProject in newProject for later steps
        this.newProject.id = createdProject.id
        this.$nextTick(()=>{ this.createProjectSnapshot = JSON.stringify(this.newProject) })
      } catch (error) {
        console.error('Failed to create project:', error)
  toast.error('Failed to create project: ' + error.message)
      } finally {
        this.creatingProject = false;
      }
    },
    filterByStatus(status) {
      console.log('Filtering by status:', status)
      console.log('Available projects:', this.projects.map(p => ({ id: p.id, name: p.name, status: p.status })))
      this.statusFilter = status
      console.log('Status filter set to:', this.statusFilter)
      console.log('Filtered projects:', this.filteredProjects.map(p => ({ id: p.id, name: p.name, status: p.status })))
      
      // Scroll to the projects section with a small delay for better UX
      this.$nextTick(() => {
        setTimeout(() => {
          this.scrollToProjects()
        }, 150) // Small delay to let the filter animation complete
      })
    },

    scrollToProjects() {
      if (this.$refs.projectsSection) {
        this.$refs.projectsSection.scrollIntoView({ 
          behavior: 'smooth',
          block: 'start'
        })
      }
    },

    clearFilter() {
      this.statusFilter = ''
      this.searchQuery = ''
      console.log('Filters cleared - showing all projects')
    },

    applyFilters() {
      // Filters are automatically applied through computed property
    },

    exportProjects() {
      this.exporting = true;
      
      try {
        // Create comprehensive project data export
        const exportData = {
          exportDate: new Date().toISOString(),
          totalProjects: this.projects.length,
          filteredProjects: this.filteredProjects.length,
          projects: this.filteredProjects.map(project => ({
            id: project.id,
            name: project.name,
            description: project.description,
            status: project.status,
            created_at: project.created_at,
            updated_at: project.updated_at,
            stakeholders_count: project.stakeholders?.length || 0,
            collections_count: project.collections?.length || 0,
            milestones_count: project.milestones?.length || 0,
            topics_count: project.topics_count || 0
          })),
          summary: {
            byStatus: this.getProjectsByStatus(),
            recentActivity: this.getRecentActivity(),
            stakeholderStats: this.getStakeholderStats()
          }
        };

        // Convert to JSON and create download
        const dataStr = JSON.stringify(exportData, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        const url = URL.createObjectURL(dataBlob);
        
        const link = document.createElement('a');
        link.href = url;
        link.download = `projects-export-${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        URL.revokeObjectURL(url);
        
        // Show success message
  toast.success(`Successfully exported ${this.filteredProjects.length} projects with comprehensive data!`)
        
      } catch (error) {
        console.error('Export failed:', error);
  toast.error('Export failed. Please try again.');
      } finally {
        this.exporting = false;
      }
    },

    getProjectsByStatus() {
      const statusCounts = {};
      this.filteredProjects.forEach(project => {
        statusCounts[project.status] = (statusCounts[project.status] || 0) + 1;
      });
      return statusCounts;
    },

    getRecentActivity() {
      // Get projects created/updated in last 30 days
      const thirtyDaysAgo = new Date();
      thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
      
      return this.filteredProjects
        .filter(project => new Date(project.updated_at) > thirtyDaysAgo)
        .sort((a, b) => new Date(b.updated_at) - new Date(a.updated_at))
        .slice(0, 10)
        .map(project => ({
          name: project.name,
          status: project.status,
          lastUpdated: project.updated_at
        }));
    },

    getStakeholderStats() {
      const stats = {
        totalStakeholders: 0,
        roles: {}
      };
      
      this.filteredProjects.forEach(project => {
        if (project.stakeholders) {
          stats.totalStakeholders += project.stakeholders.length;
          project.stakeholders.forEach(stakeholder => {
            const role = stakeholder.role || 'unknown';
            stats.roles[role] = (stats.roles[role] || 0) + 1;
          });
        }
      });
      
      return stats;
    },

    
    
    resetNewProject() {
      this.newProject = {
        name: '',
        description: '',
        status: 'planning',
        stakeholders: [],
        milestones: [],
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

    formatMilestoneStatus(status) {
      const statusMap = {
        'planned': 'Planned',
        'in-progress': 'In Progress',
        'completed': 'Completed',
        'overdue': 'Overdue'
      }
      return statusMap[status] || status
    },

  editProject(project) {
      console.log('🔧 Edit Project clicked:', project)
      console.log('🔧 Current showEditModal:', this.showEditModal)
      
      this.editingProject = {
        id: project.id,
        name: project.name,
        description: project.description,
        status: project.status,
        stakeholders: project.stakeholders ? [...project.stakeholders] : [],
        milestones: project.milestones ? [...project.milestones] : [],
        collections: project.collections ? [...project.collections] : [],
        publishedDocuments: project.publishedDocuments ? [...project.publishedDocuments] : []
      }
      
      console.log('🔧 Editing project data:', this.editingProject)
      
      // Load available stakeholders for adding new ones
      this.fetchStakeholders()
      
      this.showEditModal = true
      console.log('🔧 showEditModal set to:', this.showEditModal)
      
      // Force Vue to re-render
  this.$forceUpdate()
  this.$nextTick(()=>{ this.editProjectSnapshot = JSON.stringify(this.editingProject) })
    },



    resetEditingProject() {
      this.editingProject = {
        id: null,
        name: '',
        description: '',
        status: 'planning',
        stakeholders: [],
        milestones: [],
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

    addExistingStakeholder(type) {
      if (!this.selectedStakeholderId || !this.selectedStakeholderRole) return

      const selectedStakeholder = this.availableStakeholders.find(s => s.id === this.selectedStakeholderId)
      if (!selectedStakeholder) return

      const target = type === 'new' ? this.newProject : this.editingProject
      
      // Check if stakeholder is already added
      const alreadyAdded = target.stakeholders.some(s => s.stakeholder_id === selectedStakeholder.id)
      if (alreadyAdded) {
  toast.error('This stakeholder is already added to the project.')
        return
      }

      target.stakeholders.push({
        stakeholder_id: selectedStakeholder.id,
        name: selectedStakeholder.name,
        email: selectedStakeholder.email,
        title: selectedStakeholder.title,
        organization: selectedStakeholder.organization,
        role: this.selectedStakeholderRole,
        notes: ''
      })

      // Reset selection
      this.selectedStakeholderId = ''
      this.selectedStakeholderRole = ''
    },

    addNewStakeholder(type) {
      if (!this.newStakeholderName || !this.newStakeholderEmail || !this.newStakeholderRole) return

      const target = type === 'new' ? this.newProject : this.editingProject
      
      // Check if email is already used
      const emailExists = target.stakeholders.some(s => s.email === this.newStakeholderEmail)
      if (emailExists) {
  toast.error('A stakeholder with this email is already added to the project.')
        return
      }

      target.stakeholders.push({
        name: this.newStakeholderName,
        email: this.newStakeholderEmail,
        title: this.newStakeholderTitle,
        organization: this.newStakeholderOrganization,
        role: this.newStakeholderRole,
        notes: '',
        isNew: true // Flag to indicate this is a new stakeholder
      })

      // Reset form
      this.newStakeholderName = ''
      this.newStakeholderEmail = ''
      this.newStakeholderTitle = ''
      this.newStakeholderOrganization = ''
      this.newStakeholderRole = ''
    },

    // Collection management methods
    async addCollection(type) {
      const target = type === 'new' ? this.newProject : this.editingProject
      // Call backend to create collection
      try {
        const payload = {
          name: '',
          description: '',
          project_id: this.newProject.id || this.editingProject.id
        }
        const res = await fetch('/api/collections', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        })
        if (!res.ok) throw new Error(await res.text())
        const newCollection = await res.json()
        target.collections.push(newCollection)
      } catch (error) {
  toast.error('Failed to add collection: ' + error.message)
      }
    },

    async removeCollection(index, type) {
      const target = type === 'new' ? this.newProject : this.editingProject
      const collection = target.collections[index]
      if (!collection || !collection.id) {
        target.collections.splice(index, 1)
        return
      }
      try {
        const res = await fetch(`/api/collections/${collection.id}`, {
          method: 'DELETE'
        })
        if (!res.ok) throw new Error(await res.text())
        target.collections.splice(index, 1)
      } catch (error) {
  toast.error('Failed to remove collection: ' + error.message)
      }
    },

    async updateCollectionField(index, field, value, type) {
      const target = type === 'new' ? this.newProject : this.editingProject
      const collection = target.collections[index]
      if (!collection || !collection.id) {
        collection[field] = value
        return
      }
      try {
        collection[field] = value
        await updateCollection(collection.id, { [field]: value })
      } catch (error) {
  toast.error('Failed to update collection: ' + error.message)
      }
    },

    // Document management methods
    async addDocument(type) {
      const target = type === 'new' ? this.newProject : this.editingProject
      try {
        const payload = {
          title: '',
          url: '',
          type: '',
          project_id: this.newProject.id || this.editingProject.id
        }
        const newDoc = await createPublication(payload)
        target.publishedDocuments.push(newDoc)
      } catch (error) {
  toast.error('Failed to add document: ' + error.message)
      }
    },

    async removeDocument(index, type) {
      const target = type === 'new' ? this.newProject : this.editingProject
      const doc = target.publishedDocuments[index]
      if (!doc || !doc.id) {
        target.publishedDocuments.splice(index, 1)
        return
      }
      try {
        await deletePublication(doc.id)
        target.publishedDocuments.splice(index, 1)
      } catch (error) {
  toast.error('Failed to remove document: ' + error.message)
      }
    },

    async updateDocumentField(index, field, value, type) {
      const target = type === 'new' ? this.newProject : this.editingProject
      const doc = target.publishedDocuments[index]
      if (!doc || !doc.id) {
        doc[field] = value
        return
      }
      try {
        doc[field] = value
        await updatePublication(doc.id, { [field]: value })
      } catch (error) {
  toast.error('Failed to update document: ' + error.message)
      }
    },

    // Milestone management methods
    async addMilestone(type) {
      const target = type === 'new' ? this.newProject : this.editingProject
      try {
        const payload = {
          name: '',
          date: '',
          status: 'planned',
          project_id: this.newProject.id || this.editingProject.id
        }
        const newMilestone = await createMilestone(payload)
        target.milestones.push(newMilestone)
        this.sortMilestones(type)
      } catch (error) {
  toast.error('Failed to add milestone: ' + error.message)
      }
    },

    async removeMilestone(index, type) {
      const target = type === 'new' ? this.newProject : this.editingProject
      const milestone = target.milestones[index]
      if (!milestone || !milestone.id) {
        target.milestones.splice(index, 1)
        return
      }
      try {
        await deleteMilestone(milestone.id)
        target.milestones.splice(index, 1)
      } catch (error) {
  toast.error('Failed to remove milestone: ' + error.message)
      }
    },

    async updateMilestoneField(index, field, value, type) {
      const target = type === 'new' ? this.newProject : this.editingProject
      const milestone = target.milestones[index]
      if (!milestone || !milestone.id) {
        milestone[field] = value
        return
      }
      try {
        milestone[field] = value
        await updateMilestone(milestone.id, { [field]: value })
      } catch (error) {
  toast.error('Failed to update milestone: ' + error.message)
      }
    },

    sortMilestones(type) {
      const target = type === 'new' ? this.newProject : this.editingProject
      target.milestones.sort((a, b) => {
        const dateA = a.date || '9999-12-31'
        const dateB = b.date || '9999-12-31'
        return dateA.localeCompare(dateB)
      })
    },

    hasActiveMilestones(project) {
      if (!project.milestones || !Array.isArray(project.milestones)) return false
      return project.milestones.some(milestone => milestone.date)
    },

    proceedToMilestones() {
      // Validate that at least one stakeholder is added, unless skipping
      if (!this.projectStakeholders || this.projectStakeholders.length === 0) {
  toast.error('Please add at least one stakeholder before proceeding, or click Not Now to skip.');
        return;
      }
      this.showStakeholderModal = false;
      this.showMilestoneModal = true;
    },

    skipStakeholders() {
      // Always proceed to milestones, regardless of validation
      this.showStakeholderModal = false;
      this.showMilestoneModal = true;
    },

    skipMilestones() {
      // Always finish project creation, regardless of milestones
      this.showMilestoneModal = false;
      this.createProjectStep = 1;
      this.createdProjectId = null;
      this.createdProjectName = '';
      this.projectStakeholders = [];
      this.newMilestones = [{ name: '', date: '', status: 'planned' }];
  toast.success('Project created. You can add milestones later.');
    },

    async addSelectedStakeholderToProject() {
      if (!this.createdProjectId || !this.selectedStakeholderId || !this.selectedStakeholderRole) return
      try {
        await addStakeholderToProject(this.createdProjectId, this.selectedStakeholderId, this.selectedStakeholderRole)
        const stakeholder = this.availableStakeholders.find(s => s.id === this.selectedStakeholderId)
        if (stakeholder) {
          this.projectStakeholders.push({ ...stakeholder, role: this.selectedStakeholderRole })
        }
        this.selectedStakeholderId = ''
        this.selectedStakeholderRole = ''
      } catch (err) {
  toast.error('Failed to add stakeholder: ' + err.message)
      }
    },
  async addNewStakeholderToProject() {
      if (!this.newStakeholder.name || !this.newStakeholder.email || !this.newStakeholder.role) {
  toast.error('Please fill in all required fields for the new stakeholder.');
        return;
      }
      if (!this.createdProjectId) {
        toast.error('Please create the project before adding stakeholders.');
        return;
      }
      try {
        const res = await fetch(`/api/projects/${this.createdProjectId}/stakeholders`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            name: this.newStakeholder.name,
            email: this.newStakeholder.email,
            title: this.newStakeholder.title || undefined,
            organization: this.newStakeholder.organization || undefined,
            role: this.newStakeholder.role
          })
        })
        if (!res.ok) {
          const text = await res.text()
          throw new Error(text || 'Failed to add stakeholder')
        }
        const added = await res.json()
        this.projectStakeholders.push({
          id: added.stakeholder_id || added.id,
          name: added.name,
          email: added.email,
          role: added.role,
          organization: this.newStakeholder.organization || ''
        })
        this.newStakeholder = { name: '', email: '', title: '', organization: '', role: '' }
        toast.success('Stakeholder added to project.')
        this.$nextTick(()=>{ this.stakeholderModalSnapshot = JSON.stringify({ projectStakeholders: this.projectStakeholders }) })
      } catch (e) {
        toast.error('Failed to add stakeholder: ' + (e?.message || e))
      }
    },

    addMilestoneRow() {
      this.newMilestones.push({ name: '', date: '', status: 'planned' })
      this.$nextTick(()=>{ this.milestoneModalSnapshot = JSON.stringify({ newMilestones: this.newMilestones }) })
    },
    removeMilestone(idx) {
      this.newMilestones.splice(idx, 1)
      this.$nextTick(()=>{ this.milestoneModalSnapshot = JSON.stringify({ newMilestones: this.newMilestones }) })
    },
  async saveMilestonesAndFinish() {
      if (!this.createdProjectId) return
      try {
        for (const m of this.newMilestones) {
          if (!m.name) continue
          await createMilestone({
            project_id: this.createdProjectId,
            name: m.name,
            date: m.date || null,
            status: m.status || 'planned'
          })
        }
        await this.fetchProjects()
        // Close all modals and reset state, return to dashboard
        this.showMilestoneModal = false
        this.showStakeholderModal = false
        this.showCreateModal = false
        this.createProjectStep = 1
        this.createdProjectId = null
        this.createdProjectName = ''
        this.projectStakeholders = []
        this.newMilestones = [{ name: '', date: '', status: 'planned' }]
        // Show success toast
  toast.success('Milestones saved successfully.')
  this.$nextTick(()=>{ this.milestoneModalSnapshot = '' })
      } catch (err) {
  toast.error('Failed to add milestones: ' + err.message)
      }
    },
    
    isDirty() {
      try {
        if (this.showEditModal) return JSON.stringify(this.editingProject) !== this.editProjectSnapshot
        if (this.showCreateModal) return JSON.stringify(this.newProject) !== this.createProjectSnapshot
        if (this.showStakeholderModal) return JSON.stringify({ projectStakeholders: this.projectStakeholders }) !== this.stakeholderModalSnapshot
        if (this.showMilestoneModal) return JSON.stringify({ newMilestones: this.newMilestones }) !== this.milestoneModalSnapshot
      } catch(e) { return false }
      return false
    },
  },
  mounted() {
    // Fetch projects and stakeholders from API
    this.fetchProjects()
    this.fetchStakeholders()
  }
}
</script>

<style scoped>
/* General Dashboard Layout */
.projects-dashboard {
  padding: 0 2rem 2rem; /* remove top space before header */
  background-color: var(--bg-white);
  font-family: var(--font-family-sans);
}

.dashboard-header {
  margin-bottom: 2rem;
  text-align: center;
}

.dashboard-header h1 {
  color: var(--primary-deep-teal);
  font-size: 2.5rem;
  font-weight: 300;
  margin: 0 0 0.5rem 0;
}

/* subtitle now uses global .subtitle */

/* Metrics Grid */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 3rem;
}

/* metric-icon uses global shape; only override font-size if needed */
.metric-icon { font-size: 2rem; }

/* metric-content h3 uses global styling from style.css */

/* metric-number and metric-detail now centralized in global style.css */

/* Section Cards */
.section-card {
  background: var(--bg-primary-white);
  border-radius: 12px;
  padding: 1.5rem;
  /* Use global standardized spacing; avoid large local overrides */
  margin-bottom: 0.5rem;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-light-gray);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--border-color-gray);
}

.section-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text-primary-charcoal);
  margin: 0;
}

.filter-badge {
  display: inline-block;
  margin-left: 0.75rem;
  padding: 0.25rem 0.75rem;
  font-size: 0.9rem;
  font-weight: 500;
  background-color: var(--primary-light-teal);
  color: var(--primary-deep-teal);
  border-radius: 16px;
}

/* Quick Actions - use the global sizing so cards match other dashboards */
.quick-actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.quick-action-card[disabled] {
  opacity: 0.6;
  cursor: not-allowed;
}

.action-icon {
  font-size: 1.75rem;
}

.action-content h3 {
  margin: 0 0 0.25rem 0;
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-primary-charcoal);
}

.action-content p {
  margin: 0;
  font-size: 0.9rem;
  color: var(--text-secondary-cool-gray);
}

/* Filters */
.filters-section {
  background: var(--bg-primary-white);
  padding: 1rem 1.5rem;
  border-radius: 12px;
  margin-bottom: 2rem;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-light-gray);
}

.filter-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 1.5rem;
}

.projects-list-panel {
  margin-bottom: 1.25rem; /* space between filter panel and project list */
}

.filter-group {
  display: flex;
  flex-direction: column;
}

.filter-group label {
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--text-secondary-cool-gray);
  margin-bottom: 0.5rem;
}

.filter-input {
  padding: 0.6rem 1rem;
  border: 1px solid var(--border-color-gray);
  border-radius: 6px;
  background: var(--bg-primary-white);
  font-size: 1rem;
  min-width: 200px;
}

.button-group {
  display: flex;
  gap: 0.5rem;
  align-items: center !important; /* Force center alignment, override parent flex-end */
}

/* Projects Grid */
.projects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 1.5rem;
}

.project-card {
  background: var(--bg-primary-white);
  border-radius: 12px;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-color-gray);
  transition: all 0.2s;
}

.project-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-md);
  border-color: var(--primary-medium-teal);
}

.project-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.project-header h3 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-primary-charcoal);
}

.project-description {
  color: var(--text-secondary-cool-gray);
  font-size: 0.95rem;
  margin-bottom: 1.25rem;
  flex-grow: 1;
}

.project-summary {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 1.25rem;
  font-size: 0.9rem;
  color: var(--text-secondary-cool-gray);
}

.summary-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.summary-icon {
  font-size: 1.1rem;
}

.project-milestones {
  margin-bottom: 1.25rem;
  font-size: 0.9rem;
}

.milestone-item {
  margin-bottom: 0.5rem;
}

.milestone-date {
  font-weight: 500;
}

.milestone-date.completed { color: var(--success-mint-green); }
.milestone-date.overdue { color: var(--error-coral-red); }
.milestone-date.planned { color: var(--text-secondary-cool-gray); }

.milestone-status {
  font-style: italic;
  color: var(--text-secondary-cool-gray);
}

.milestone-more {
  font-style: italic;
  color: var(--text-secondary-cool-gray);
  font-size: 0.85rem;
  margin-top: 0.5rem;
}

.project-card-footer {
  display: flex;
  justify-content: space-between;
}

.project-meta {
  font-size: 0.8rem;
  color: var(--text-secondary-cool-gray);
}

.edit-btn {
  background: none;
  border: none;
  color: var(--primary-deep-teal);
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 600;
}

.edit-btn:hover {
  text-decoration: underline;
}

/* Status Badges */
.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 16px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: capitalize;
  white-space: nowrap;
}

.status-badge.planning { background-color: var(--extended-lavender-gray); color: var(--text-primary-charcoal); }
.status-badge.active { background-color: var(--extended-cool-mint); color: var(--success-mint-green); }
.status-badge.on_hold { background-color: var(--extended-warm-taupe); color: var(--warning-amber); }
.status-badge.completed { background-color: var(--extended-slate-purple-light); color: var(--extended-slate-purple); }

/* States (Loading, Error, Empty) */
.loading-state, .error-state, .empty-state {
  text-align: center;
  padding: 4rem 2rem;
  background: var(--bg-white);
  border-radius: 8px;
}

.error-content, .empty-content {
  max-width: 500px;
  margin: 0 auto;
}

.error-icon, .empty-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.error-state h3, .empty-state h3 {
  font-size: 1.5rem;
  color: var(--text-primary-charcoal);
  margin-bottom: 0.5rem;
}

.error-state p, .empty-state p {
  color: var(--text-secondary-cool-gray);
  margin-bottom: 1.5rem;
}

.retry-btn, .create-first-btn { display: inline-block; }

/* Modals - using global .modal-overlay and .modal; add size class if needed */
.modal.large-modal { max-width: 900px; }

.modal-header {
  padding: 1.5rem;
  border-bottom: 1px solid var(--border-color-gray);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h2 {
  margin: 0;
  font-size: 1.5rem;
  color: var(--text-primary-charcoal);
}

.close-btn {
  background: none;
  border: none;
  font-size: 2rem;
  cursor: pointer;
  color: var(--text-secondary-cool-gray);
}

.modal-body {
  padding: 1.5rem;
  overflow-y: auto;
}

.modal-actions {
  padding: 1.5rem;
  border-top: 1px solid var(--border-color-gray);
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  background-color: var(--bg-white);
  border-radius: 0 0 12px 12px;
}

/* Modal Forms */
.form-section {
  margin-bottom: 2rem;
}

.form-section h3 {
  font-size: 1.2rem;
  font-weight: 600;
  color: var(--text-primary-charcoal);
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid var(--border-color-gray);
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
  margin-bottom: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group label {
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: var(--text-primary-charcoal);
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid var(--border-color-gray);
  border-radius: 6px;
  font-size: 1rem;
}

.confirmation-message {
  margin-bottom: 1rem;
  color: var(--success-text-dark-green);
  background: var(--success-bg-light-green);
  border: 1px solid var(--success-border-green);
  padding: 0.75rem;
  border-radius: 6px;
}

.confirmation-actions {
  margin-top: 1rem;
  text-align: right;
}
.selector-row, .milestone-row, .new-stakeholder-form {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  align-items: center;
  margin-bottom: 1rem;
}

.stakeholder-select, .role-select, .stakeholder-input, .milestone-input {
  flex: 1;
  min-width: 150px;
}

.add-btn, .remove-btn { display: inline-block; }

.remove-btn {
  /* Normalize to standard small danger button look */
  background-color: var(--error-coral-red);
  color: #fff;
  border: 1px solid rgba(0,0,0,.125);
  min-width: 28px;
  height: 28px;
  padding: 0 0.5rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.stakeholders-list {
  margin-top: 1.5rem;
}

.stakeholder-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem;
  border-radius: 6px;
  background-color: var(--bg-white);
  margin-bottom: 0.5rem;
}

.stakeholder-info {
  flex-grow: 1;
}

.stakeholder-details {
  font-size: 0.9rem;
  color: var(--text-secondary-cool-gray);
  display: block;
}

/* Buttons use global styles */

.ml-1 {
  margin-left: 1rem;
}
</style>
