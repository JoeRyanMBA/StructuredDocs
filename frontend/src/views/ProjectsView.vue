<template>
  <NotificationTicker
    :notifications="mergedNotifications"
    contextType="global"
    @mark-read="markNotificationRead"
  />
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
        
        
        <button @click="exportProjects" class="action-card">
          <div class="action-icon">📤</div>
          <div class="action-content">
            <h3>Export Data</h3>
            <p>Download project reports</p>
          </div>
        </button>
      </div>
    </div>

    <!-- Project Calendar -->
    <div class="section-card">
      <div class="section-header">
        <h2 class="section-title">Project Calendar</h2>
        <div class="calendar-controls">
          <button @click="toggleCalendarView" class="filter-select">
            {{ calendarView === 'milestones' ? 'Show All Events' : 'Milestones Only' }}
          </button>
        </div>
      </div>
      <CalendarWidget :events="calendarEvents" />
    </div>

    <!-- Filters -->
    <div class="filters-section">
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
            <button @click="applyFilters" class="btn btn-primary btn-sm">
              <i class="fas fa-search"></i> Search
            </button>
            <button @click="clearFilter" class="btn btn-secondary btn-sm">Clear Filters</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Projects List -->
    <!-- Projects List -->
    <div class="section-card" ref="projectsSection">
      <div class="section-header">
        <h2 class="section-title">
          {{ statusFilter ? `${formatStatus(statusFilter)} Projects` : 'All Projects' }}
          <span v-if="statusFilter" class="filter-badge">{{ filteredProjects.length }}</span>
        </h2>
      </div>
      
      <!-- Loading State -->
      <div v-if="loading" class="loading-state">
        <p>Please wait while we fetch your projects.</p>
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
          <button @click="showCreateModal = true" class="create-first-btn">
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
          <div class="project-card-footer" style="display: flex; justify-content: space-between; align-items: center; margin-top: 1.25rem;">
            <div class="project-meta">Project {{ project.id }} was created on {{ formatDate(project.created_at) }}</div>
            <button @click="editProject(project)" class="edit-btn">✏️ Edit</button>
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
    <form @submit.prevent="handleCreateProject" class="modal-body">
          <!-- Basic Information -->
          <div class="form-section">
            <h3>Basic Information</h3>
            <div v-if="confirmationMessage" class="confirmation-message" style="margin-bottom:1rem; color: #155724; background: #d4edda; border: 1px solid #c3e6cb; padding: 0.75rem; border-radius: 4px;">
              {{ confirmationMessage }}
              <div style="margin-top: 1rem; text-align: right;">
                <button type="button" class="primary-btn" @click="proceedToStakeholders">OK</button>
              </div>
            </div>
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
            <button type="button" @click="showCreateModal = false" class="secondary-btn">
              Cancel
            </button>
            <button type="submit" class="primary-btn" :disabled="creatingProject || !!confirmationMessage">Next</button>
          </div>
        </form>
      </div>

    <!-- Stakeholder Modal (Step 2) -->
    <div v-if="showStakeholderModal" class="modal-overlay" @click="showStakeholderModal = false">
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
              <button type="button" @click="addSelectedStakeholderToProject" :disabled="!selectedStakeholderId || !selectedStakeholderRole" class="add-btn">
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
              <button type="button" @click="addNewStakeholderToProject" :disabled="!newStakeholder.name || !newStakeholder.email || !newStakeholder.role" class="add-btn">
                + Add New Stakeholder
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
            <button type="button" class="primary-btn" @click="proceedToMilestones">Add Stakeholders</button>
            <button type="button" class="secondary-btn" @click="skipStakeholders" style="margin-left: 1rem;">Not Now</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Milestone Modal (Step 3) -->
    <div v-if="showMilestoneModal" class="modal-overlay" @click="showMilestoneModal = false">
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
              <button type="button" @click="removeMilestone(idx)" class="remove-btn">×</button>
            </div>
            <button type="button" @click="addMilestoneRow" class="add-btn">+ Add Milestone</button>
          </div>
          <div class="modal-actions">
            <button type="button" class="primary-btn" @click="saveMilestonesAndFinish">Add Milestones</button>
            <button type="button" class="secondary-btn" @click="skipMilestones" style="margin-left: 1rem;">Not Now</button>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Edit Project Modal -->
  <div v-if="showEditModal" class="modal-overlay" @click="showEditModal = false">
    <div class="modal large-modal" @click.stop>
      <div class="modal-header">
        <h2>Edit Project</h2>
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

        <div class="modal-actions">
          <button type="button" @click="showEditModal = false" class="secondary-btn">
            Cancel
          </button>
          <button type="submit" class="primary-btn">
            Update Project
          </button>
        </div>
      </form>
    </div>
  </div>
</div>

</template>
<style scoped>
.milestone-row input[type="date"] {
  font-family: inherit;
  font-size: 1rem;
  color: #374151;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  border: 1px solid #d1d5db;
  background: #fff;
  box-sizing: border-box;
}
.milestone-row input[type="text"],
.milestone-row input[type="date"],
.milestone-row select,
.milestone-row .remove-btn {
  margin-bottom: 0.75rem;
}
.milestone-row input[type="text"]:last-child,
.milestone-row input[type="date"]:last-child,
.milestone-row select:last-child,
.milestone-row .remove-btn:last-child {
  margin-bottom: 0;
}
/* Milestone Modal Styling */
.milestone-row {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  background: #f8fafc;
  border: 1px solid #e0e7ef;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1rem;
  min-height: 80px;
  box-sizing: border-box;
}
.milestone-row input[type="text"],
.milestone-row input[type="date"],
.milestone-row select {
  margin-bottom: 0;
}
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
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

.metric-content {
  text-align: left;
}

.metric-content h3 {
  margin: 0 0 0.25rem 0;
  color: #495057;
  font-size: 0.875rem;
  font-weight: 600;
}

.metric-number {
  font-size: 2rem;
  font-weight: 700;
  color: #205493;
  margin-bottom: 0.15rem;
}

.metric-detail {
  font-size: 0.95rem;
  color: #64748b;
}
</style>

<script>
import Breadcrumbs from '../components/Breadcrumbs.vue'
import CalendarWidget from '../components/CalendarWidget.vue'
import NotificationTicker from '../components/NotificationTicker.vue'
import { createStakeholder, addStakeholderToProject } from '../api/stakeholders';
import { getCollections, updateCollection } from '../api/collections';
import { createPublication, deletePublication, updatePublication } from '../api/publications';
import { createMilestone, deleteMilestone, updateMilestone } from '../api/milestones';

export default {
  components: { Breadcrumbs, CalendarWidget, NotificationTicker },
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
      calendarView: '',
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
      confirmationMessage: '',
      projectStakeholders: [],
      newMilestones: [{ name: '', date: '', status: 'planned' }],
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
      if (this.calendarView === 'milestones') {
        return events.filter(event => event.type === 'milestone')
      }
      return events
    }
  },
  methods: {
    proceedToStakeholders() {
      this.confirmationMessage = '';
      this.showStakeholderModal = true;
    },
    handleCreateProject() {
      this.createProjectBasic();
    },

    async handleUpdateProject() {
      try {
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
        
        // Update the project in the local array
        const index = this.projects.findIndex(p => p.id === this.editingProject.id)
        if (index !== -1) {
          this.projects[index] = {
            ...this.projects[index],
            ...updatedProject
          }
        }

        this.showEditModal = false
        this.resetEditingProject()
        
      } catch (error) {
        console.error('Failed to update project:', error)
        alert('Failed to update project. Please try again.')
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
  this.confirmationMessage = `Project #${createdProject.id} (${createdProject.name}) was created successfully!`;
  this.createProjectStep = 2
  // Only close the modal after user clicks OK (handled in proceedToStakeholders)
  // this.showStakeholderModal = true
  // this.showCreateModal = false
  // Optionally, store createdProject in newProject for later steps
  this.newProject.id = createdProject.id
      } catch (error) {
        console.error('Failed to create project:', error)
        alert('Failed to create project: ' + error.message)
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
      // Mock export functionality
      alert('Export functionality would be implemented here')
    },

    toggleCalendarView() {
      this.calendarView = this.calendarView === 'milestones' ? 'all' : 'milestones'
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
      this.showEditModal = true
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
        alert('This stakeholder is already added to the project.')
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
        alert('A stakeholder with this email is already added to the project.')
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
        alert('Failed to add collection: ' + error.message)
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
        alert('Failed to remove collection: ' + error.message)
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
        alert('Failed to update collection: ' + error.message)
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
        alert('Failed to add document: ' + error.message)
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
        alert('Failed to remove document: ' + error.message)
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
        alert('Failed to update document: ' + error.message)
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
        alert('Failed to add milestone: ' + error.message)
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
        alert('Failed to remove milestone: ' + error.message)
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
        alert('Failed to update milestone: ' + error.message)
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
        alert('Please add at least one stakeholder before proceeding, or click Not Now to skip.');
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
      this.confirmationMessage = `Project #${this.createdProjectId} (${this.createdProjectName}) was created successfully!`;
      this.createProjectStep = 1;
      this.createdProjectId = null;
      this.createdProjectName = '';
      this.projectStakeholders = [];
      this.newMilestones = [{ name: '', date: '', status: 'planned' }];
      alert(this.confirmationMessage);
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
        alert('Failed to add stakeholder: ' + err.message)
      }
    },
    async addNewStakeholderToProject() {
      if (!this.createdProjectId || !this.newStakeholder.name || !this.newStakeholder.email || !this.newStakeholder.role) return
      try {
        const newStakeholder = await createStakeholder({
          name: this.newStakeholder.name,
          email: this.newStakeholder.email,
          title: this.newStakeholder.title,
          organization: this.newStakeholder.organization
        })
        await addStakeholderToProject(this.createdProjectId, newStakeholder.id, this.newStakeholder.role)
        this.projectStakeholders.push({ ...newStakeholder, role: this.newStakeholder.role })
        this.newStakeholder = { name: '', email: '', title: '', organization: '', role: '' }
      } catch (err) {
        alert('Failed to add new stakeholder: ' + err.message)
      }
    },
    addMilestoneRow() {
      this.newMilestones.push({ name: '', date: '', status: 'planned' })
    },
    removeMilestone(idx) {
      this.newMilestones.splice(idx, 1)
    },
    async saveMilestonesAndFinish() {
      if (!this.createdProjectId) return
      try {
        for (const m of this.newMilestones) {
          if (m.name) {
            await fetch(`/api/projects/${this.createdProjectId}/milestones`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                name: m.name,
                date: m.date,
                status: m.status
              })
            })
          }
        }
        // Close all modals and reset state, return to dashboard
        this.showMilestoneModal = false
        this.showStakeholderModal = false
        this.showCreateModal = false
        this.confirmationMessage = ''
        this.createProjectStep = 1
        this.createdProjectId = null
        this.createdProjectName = ''
        this.projectStakeholders = []
        this.newMilestones = [{ name: '', date: '', status: 'planned' }]
        // Optionally, you could show a toast here if desired
      } catch (err) {
        alert('Failed to add milestones: ' + err.message)
      }
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
/* Dashboard Layout */
.projects-dashboard {
  margin: 0 auto;
}

.dashboard-header {
  margin-bottom: 2rem;
  text-align: center;
}

.dashboard-header h1 {
  color: #205493;
  margin-bottom: 0.5rem;
  font-size: 2.5rem;
  font-weight: 300;
}

.welcome-text {
  color: #6c757d;
  font-size: 1.1rem;
  margin: 0;
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

.metric-number {
  font-size: 2rem;
  font-weight: 700;
  color: #205493;
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

.calendar-controls {
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
  font-family: 'Roboto', sans-serif;
  cursor: pointer;
}

.filter-select:focus {
  outline: none;
  border-color: #205493;
  box-shadow: 0 0 0 3px rgba(0, 90, 156, 0.1);
}

.filter-controls {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.filter-badge {
  background: #205493;
  color: white;
  font-size: 0.75rem;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  margin-left: 0.5rem;
  font-weight: 600;
}

.clear-filter-btn {
  background: #f3f4f6;
  color: #6b7280;
  border: 1px solid #d1d5db;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.clear-filter-btn:hover {
  background: #e5e7eb;
  color: #374151;
  border-color: #9ca3af;
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
  background: #205493;
  border-color: #205493;
  color: white;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(32, 84, 147, 0.2);
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
  background: #205493;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.create-first-btn:hover {
  background: #005E7B;
  transform: translateY(-1px);
}

/* Loading State */
.loading-state {
  text-align: center;
  padding: 3rem 1rem;
}

.loading-content {
  max-width: 400px;
  margin: 0 auto;
}

.loading-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
  opacity: 0.6;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { opacity: 0.6; }
  50% { opacity: 0.3; }
  100% { opacity: 0.6; }
}

.loading-content h3 {
  margin: 0 0 1rem 0;
  color: #112e51;
  font-size: 1.5rem;
}

.loading-content p {
  margin: 0;
  color: #666;
  line-height: 1.6;
}

/* Error State */
.error-state {
  text-align: center;
  padding: 3rem 1rem;
}

.error-content {
  max-width: 400px;
  margin: 0 auto;
}

.error-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
  opacity: 0.6;
}

.error-content h3 {
  margin: 0 0 1rem 0;
  color: #b91c1c;
  font-size: 1.5rem;
}

.error-content p {
  margin: 0 0 1.5rem 0;
  color: #666;
  line-height: 1.6;
}

.retry-btn {
  background: #205493;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.retry-btn:hover {
  background: #005E7B;
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
  border-color: #205493;
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

.project-milestones .milestone-item {
  font-size: 0.8rem;
  color: #6b7280;
  margin-bottom: 0.25rem;
}

.milestone-date.completed {
  color: #009964;
  font-weight: 500;
}

.milestone-date.in-progress {
  color: #005E7B;
  font-weight: 500;
}

.milestone-date.overdue {
  color: #dc2626;
  font-weight: 500;
}

.milestone-date.planned {
  color: #6b7280;
}

.milestone-row {
  display: flex;
  flex-direction: row;
  align-items: flex-start;
  gap: 1rem;
  background: #f8fafc;
  border: 1px solid #e0e7ef;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1rem;
  min-height: 80px;
  box-sizing: border-box;
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
  background: #205493;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.edit-btn:hover {
  background: #005E7B;
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
  font-family: 'Roboto', sans-serif;
  box-sizing: border-box;
  transition: border-color 0.2s ease;
}

.form-group input:focus, .form-group textarea:focus, .form-group select:focus {
  outline: none;
  border-color: #205493;
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
  border-bottom: 2px solid #205493;
  padding-bottom: 0.5rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 1rem;
}

/* Stakeholder, Collection, Document, Milestone Styles */
.stakeholders-list, .collections-list, .documents-list, .milestones-list {
  background: white;
  border-radius: 6px;
  padding: 1rem;
}

.stakeholder-item, .collection-item, .document-item, .milestone-item {
  display: grid;
  gap: 0.75rem;
  margin-bottom: 1rem;
  padding: 1rem;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  background: #fafafa;
}

.stakeholder-item {
  grid-template-columns: 1fr auto 1fr auto;
  align-items: center;
}

/* New stakeholder selector styles */
.stakeholder-selector {
  background: #f8fafc;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1.5rem;
}

.stakeholder-selector h4 {
  margin: 0 0 1rem 0;
  color: #205493;
  font-size: 1rem;
  font-weight: 600;
}

.selector-row {
  display: grid;
  grid-template-columns: 2fr 1fr auto;
  gap: 0.75rem;
  align-items: center;
}

.stakeholder-select, .role-select {
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  background: white;
  font-size: 0.9rem;
  font-family: 'Roboto', sans-serif;
}

.stakeholder-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.stakeholder-details {
  font-size: 0.8rem;
  color: #6b7280;
}

.stakeholder-role-input {
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-size: 0.9rem;
}

.add-new-stakeholder {
  margin-top: 1.5rem;
  padding: 1rem;
  background: #fef7cd;
  border: 1px solid #fde047;
  border-radius: 6px;
}

.add-new-stakeholder h4 {
  margin: 0 0 1rem 0;
  color: #a16207;
  font-size: 1rem;
  font-weight: 600;
}

.new-stakeholder-form {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 0.75rem;
  align-items: end;
}

.collection-item {
  grid-template-columns: 1fr 2fr auto;
  align-items: start;
}

.document-item {
  grid-template-columns: 1fr 1fr 1fr auto;
  align-items: center;
}

.milestone-item {
  grid-template-columns: 2fr 1fr 1fr auto;
  align-items: center;
}

.stakeholder-input, .collection-input, .document-input, .milestone-input {
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-size: 0.9rem;
  font-family: 'Roboto', sans-serif;
  box-sizing: border-box;
}

.stakeholder-input:focus, .collection-input:focus, .document-input:focus, .milestone-input:focus {
  outline: none;
  border-color: #205493;
  box-shadow: 0 0 0 2px rgba(0, 90, 156, 0.1);
}

.add-btn {
  background: #009964;
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
  background: #006548;
}

.remove-btn {
  background: #dc2626;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  transition: background 0.2s ease;
  margin-left: .5rem;
}

.remove-btn:hover {
  background: #b91c1c;
  color: #fff;
  border-color: #b91c1c;
}

.primary-btn {
  padding: 0.75rem 1.5rem;
  border: none;
  background: #205493;
  color: white;
  border-radius: 8px;
  font-weight: 600;
  font-size: 1rem;
  cursor: pointer;
  transition: background 0.2s ease;
}
.primary-btn:disabled {
  background: #cbd5e1;
  color: #6b7280;
  cursor: not-allowed;
  opacity: 0.7;
}
.primary-btn:hover {
  background: #005E7B;
}
.secondary-btn {
  padding: 0.75rem 1.5rem;
  border: 1px solid #d1d5db;
  background: white;
  color: #374151;
  border-radius: 8px;
  font-weight: 600;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.2s ease;
}
.secondary-btn:hover {
  background: #f3f4f6;
  border-color: #9ca3af;
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
