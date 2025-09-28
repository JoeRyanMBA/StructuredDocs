<template>
  <div class="all-tasks">
  <h1>All Tasks</h1>
    
  <p class="subtitle">
      Comprehensive task management view. Create, edit, and organize all tasks across projects, collections, and topics.
    </p>

    <div class="page-actions" style="margin-top: 2rem;">
      <button @click="openCreateModal" class="btn btn-primary">
        <span class="icon-plus">➕︎</span> Create New Task
      </button>
    </div>

    <div v-if="loading" class="loading">Loading tasks...</div>
    <div v-else-if="error" class="error">{{ error }}</div>

    <div v-else class="tasks-content">
      <!-- Filters -->
      <div class="filters-section">
        <div class="filter-row">
          <div class="search-box">
            <input
              v-model="searchQuery"
              type="text"
              class="search-input"
              placeholder="Search tasks..."
              @keyup.enter="applyFilters"
            />
            <span class="search-icon" @click="applyFilters">🔍</span>
          </div>
          <select v-model="statusFilter" @change="applyFilters" class="filter-select">
            <option value="">All Statuses</option>
            <option value="todo">To Do</option>
            <option value="in_progress">In Progress</option>
            <option value="completed">Completed</option>
          </select>
          <select v-model="priorityFilter" @change="applyFilters" class="filter-select">
            <option value="">All Priorities</option>
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
          </select>
          <select v-model="associationFilter" @change="applyFilters" class="filter-select">
            <option value="">All Associations</option>
            <option value="project">Project</option>
            <option value="collection">Collection</option>
            <option value="topic">Topic</option>
          </select>
        </div>
      </div>

      <div class="table-instructions">
        <p>Select a task to edit.</p>
      </div>

      <div class="tasks-table-container">
        <table class="tasks-table">
          <thead>
            <tr>
              <th class="id-column">ID</th>
              <th>Task</th>
              <th>Association</th>
              <th class="status-column">Status</th>
              <th>Priority</th>
              <th>Due Date</th>
              <th>Assigned To</th>
              <th>Tags</th>
              <th class="actions-column"></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="task in filteredTasks" :key="task.id" @click="editTask(task)" class="task-row">
              <td class="id-cell">{{ task.id }}</td>
              <td class="task-cell">
                <div class="task-title">{{ task.title }}</div>
                <div class="task-desc" v-if="task.description">{{ task.description }}</div>
              </td>
              <td>
                <div v-if="task.project_name" class="association">
                  <i class="bi bi-diagram-3"></i> {{ task.project_name }}
                </div>
                <div v-else-if="task.collection_name" class="association">
                  <i class="bi bi-folder"></i> {{ task.collection_name }}
                </div>
                <div v-else-if="task.topic_name" class="association">
                  <i class="bi bi-file-text"></i> {{ task.topic_name }}
                </div>
                <div v-else class="association">-</div>
              </td>
              <td class="status-column">
                <span :class="`status-badge status-${task.status.replace('_', '-')}`">
                  {{ formatStatus(task.status) }}
                </span>
              </td>
              <td>
                <span :class="`priority-badge priority-${task.priority}`">
                  {{ formatPriority(task.priority) }}
                </span>
              </td>
              <td class="due-date-cell">{{ formatDate(task.due_date) || '-' }}</td>
              <td class="assigned-to-cell">{{ getAssignedToDisplayName(task.assigned_to) }}</td>
              <td>
                <div class="tags-cell">
                  <span v-for="tag in parseTaskTags(task.tags)" :key="tag" class="tag-badge">
                    {{ tag }}
                  </span>
                  <button 
                    class="btn btn-secondary btn-sm edit-inline-btn"
                    @click.stop="editTask(task)"
                    title="Edit task"
                  >
                    <i class="bi bi-pencil-square"></i> Edit
                  </button>
                </div>
              </td>
              <td class="actions-cell" @click.stop>
                <button @click="deleteTask(task)" class="btn-delete">
                  <i class="bi bi-x"></i>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="filteredTasks.length === 0" class="no-data">
        <p v-if="tasks.length === 0">No tasks found. Create your first task to get started.</p>
        <p v-else>No tasks match your current filters.</p>
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h3>{{ isEditing ? 'Edit Task' : 'Create New Task' }}</h3>
          <button @click="closeModal" class="close-btn">&times;</button>
        </div>
        
        <div class="modal-body">
          <form @submit.prevent="saveTask">
            <div class="form-group">
              <label for="taskTitle">Task Title *</label>
              <input
                id="taskTitle"
                v-model="taskForm.title"
                type="text"
                class="form-input"
                placeholder="Enter task title"
                required
              />
            </div>

            <div class="form-group">
              <label for="taskDescription">Description</label>
              <textarea
                id="taskDescription"
                v-model="taskForm.description"
                class="form-input"
                placeholder="Describe the task"
                rows="3"
              ></textarea>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label for="taskStatus">Status *</label>
                <select id="taskStatus" v-model="taskForm.status" class="form-input" required>
                  <option value="">Select Status</option>
                  <option value="todo">To Do</option>
                  <option value="in_progress">In Progress</option>
                  <option value="completed">Completed</option>
                </select>
              </div>
              <div class="form-group">
                <label for="taskPriority">Priority</label>
                <select id="taskPriority" v-model="taskForm.priority" class="form-input">
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                </select>
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label for="taskDueDate">Due Date</label>
                <input
                  id="taskDueDate"
                  v-model="taskForm.due_date"
                  type="date"
                  class="form-input"
                />
              </div>
              <div class="form-group">
                <label for="taskAssignedTo">Assigned To</label>
                <select
                  id="taskAssignedTo"
                  v-model="taskForm.assigned_to"
                  class="form-input"
                >
                  <option value="">Unassigned</option>
                  <option v-for="stakeholder in stakeholders" :key="stakeholder.id" :value="stakeholder.name">
                    {{ stakeholder.name }} ({{ stakeholder.email }})
                  </option>
                </select>
              </div>
            </div>

            <div class="form-group">
              <label for="taskAssociation">Association</label>
              <select id="taskAssociation" v-model="taskForm.associationType" @change="resetAssociation" class="form-input">
                <option value="">No Association</option>
                <option value="project">Project</option>
                <option value="collection">Collection</option>
                <option value="topic">Topic</option>
              </select>
            </div>

            <div v-if="taskForm.associationType === 'project'" class="form-group">
              <label for="taskProject">Project</label>
              <select id="taskProject" v-model="taskForm.project_id" class="form-input">
                <option value="">Select project</option>
                <option v-for="project in availableAssociations.projects" :key="project.id" :value="project.id">
                  {{ project.name }}
                </option>
              </select>
            </div>

            <div v-if="taskForm.associationType === 'collection'" class="form-group">
              <label for="taskCollection">Collection</label>
              <select id="taskCollection" v-model="taskForm.collection_id" class="form-input">
                <option value="">Select collection</option>
                <option v-for="collection in availableAssociations.collections" :key="collection.id" :value="collection.id">
                  {{ collection.name }}
                </option>
              </select>
            </div>

            <div v-if="taskForm.associationType === 'topic'" class="form-group">
              <label for="taskTopic">Topic</label>
              <select id="taskTopic" v-model="taskForm.topic_id" class="form-input">
                <option value="">Select topic</option>
                <option v-for="topic in availableAssociations.topics" :key="topic.id" :value="topic.id">
                  {{ topic.name }}
                </option>
              </select>
            </div>

            <!-- Tags Section -->
            <div class="form-group">
              <label>Tags</label>
              <div class="tags-input">
                <!-- Selected Tags -->
                <div v-if="taskForm.tags.length > 0" class="selected-tags">
                  <span v-for="tag in taskForm.tags" :key="tag" class="selected-tag">
                    {{ tag }}
                    <button type="button" @click="removeTag(tag)" class="remove-tag-btn">&times;</button>
                  </span>
                </div>

                <!-- Existing Tags Selector -->
                <div class="existing-tags-section" v-if="allTags.length > 0">
                  <label>Select from existing tags:</label>
                  <select v-model="selectedExistingTag" @change="addExistingTag" class="form-input">
                    <option value="">Choose a tag...</option>
                    <option v-for="tag in allTags" :key="tag" :value="tag" :disabled="taskForm.tags.includes(tag)">
                      {{ tag }} {{ taskForm.tags.includes(tag) ? '(already selected)' : '' }}
                    </option>
                  </select>
                </div>

                <!-- Add New Tag -->
                <div class="new-tag-section">
                  <label>Or add a new tag:</label>
                  <div class="new-tag-input-row">
                    <input
                      v-model="newTag"
                      type="text"
                      class="form-input"
                      placeholder="Enter new tag"
                      @keydown.enter.prevent="addNewTag"
                    />
                    <button type="button" @click="addNewTag" class="btn btn-sm btn-secondary">Add</button>
                  </div>
                </div>
              </div>
            </div>
          </form>
        </div>
        
        <div class="modal-footer">
          <button @click="closeModal" class="btn btn-secondary">Cancel</button>
          <button @click="saveTask" class="btn btn-primary" :disabled="!taskForm.title.trim() || !taskForm.status">
            {{ isEditing ? 'Update Task' : 'Create Task' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteModal" class="modal-overlay" @click.self="closeDeleteModal">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h3>Confirm Delete</h3>
          <button @click="closeDeleteModal" class="close-btn">&times;</button>
        </div>
        
        <div class="modal-body">
          <p>Are you sure you want to delete the task "{{ taskToDelete?.title }}"?</p>
          <p class="warning">This action cannot be undone.</p>
        </div>
        
        <div class="modal-footer">
          <button @click="closeDeleteModal" class="btn btn-secondary">Cancel</button>
          <button @click="confirmDelete" class="btn btn-danger">Delete Task</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { toast } from '@/composables/useToast'
import unsavedChangesGuard from '@/mixins/unsavedChangesGuard.js'
export default {
  name: 'AllTasksView',
  mixins: [unsavedChangesGuard],
  data() {
    return {
      tasks: [],
      filteredTasks: [],
      allTags: [],
      availableAssociations: {
        projects: [],
        collections: [],
        topics: []
      },
      loading: false,
      error: null,
      showModal: false,
      showDeleteModal: false,
      isEditing: false,
      taskToDelete: null,
      
      // Data for lookups
      stakeholders: [],
      
      // Filters
      searchQuery: '',
  statusFilter: '',
  priorityFilter: '',
  associationFilter: '',
      
      // Form data
      taskForm: {
        id: null,
        title: '',
        description: '',
        status: 'todo',
        priority: 'medium',
        due_date: '',
        assigned_to: '',
        associationType: '',
        project_id: null,
        collection_id: null,
        topic_id: null,
        tags: []
      },
      
      // Tags input
      newTag: '',
  selectedExistingTag: '',
  // snapshot for unsaved-changes detection
  lastSavedTaskSnapshot: ''
    }
  },
  
  mounted() {
    this.fetchTasks()
    this.fetchAllTags()
    this.fetchAssociations()
    this.fetchStakeholders()
  },
  
  methods: {
    async fetchTasks() {
      this.loading = true
      this.error = null
      try {
        const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || ''}/api/tasks/`)
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        const data = await response.json()
        this.tasks = data.tasks || []
        this.applyFilters()
      } catch (error) {
        console.error('Failed to fetch tasks:', error)
        this.error = 'Failed to load tasks. Please try again.'
  toast.error(this.error)
      } finally {
        this.loading = false
      }
    },

    async fetchAllTags() {
      try {
        const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || ''}/api/tags/`)
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        const tags = await response.json()
        this.allTags = tags.map(tag => tag.name).sort()
      } catch (error) {
        console.error('Failed to fetch tags:', error)
      }
    },

    async fetchAssociations() {
      try {
        const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || ''}/api/tasks/associations`)
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        this.availableAssociations = await response.json()
      } catch (error) {
        console.error('Failed to fetch associations:', error)
      }
    },
    
    applyFilters() {
      let filtered = [...this.tasks]
      
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase()
        filtered = filtered.filter(task => 
          task.title.toLowerCase().includes(query) ||
          (task.description && task.description.toLowerCase().includes(query))
        )
      }
      
      if (this.statusFilter) {
        filtered = filtered.filter(task => task.status === this.statusFilter)
      }
      
      if (this.priorityFilter) {
        filtered = filtered.filter(task => task.priority === this.priorityFilter)
      }
      
      this.filteredTasks = filtered
    },
    
    clearFilters() {
      this.searchQuery = ''
      this.statusFilter = ''
      this.priorityFilter = ''
      this.applyFilters()
    },
    
  openCreateModal() {
      this.isEditing = false
      this.taskForm = {
        id: null,
        title: '',
        description: '',
        status: 'todo',
        priority: 'medium',
        due_date: '',
        assigned_to: '',
        associationType: '',
        project_id: null,
        collection_id: null,
        topic_id: null,
        tags: []
      }
      this.newTag = ''
      this.selectedExistingTag = ''
      this.showModal = true
      // establish snapshot after next tick so bindings updated
      this.$nextTick(() => { this.lastSavedTaskSnapshot = JSON.stringify(this.taskForm) })
    },
    
  editTask(task) {
      this.isEditing = true
      
      // Convert email to name for the dropdown if needed
      let assignedTo = task.assigned_to || ''
      if (assignedTo && assignedTo.includes('@')) {
        const stakeholder = this.stakeholders.find(s => s.email === assignedTo)
        assignedTo = stakeholder ? stakeholder.name : assignedTo
      }
      
      this.taskForm = {
        id: task.id,
        title: task.title,
        description: task.description || '',
        status: task.status,
        priority: task.priority,
        due_date: task.due_date || '',
        assigned_to: assignedTo,
        associationType: task.project_id ? 'project' : task.collection_id ? 'collection' : task.topic_id ? 'topic' : '',
        project_id: task.project_id,
        collection_id: task.collection_id,
        topic_id: task.topic_id,
        tags: this.parseTaskTags(task.tags)
      }
      this.newTag = ''
      this.selectedExistingTag = ''
      this.showModal = true
      this.$nextTick(() => { this.lastSavedTaskSnapshot = JSON.stringify(this.taskForm) })
    },
    
  closeModal() {
      this.showModal = false
      this.taskForm = {
        id: null,
        title: '',
        description: '',
        status: 'todo',
        priority: 'medium',
        due_date: '',
        assigned_to: '',
        associationType: '',
        project_id: null,
        collection_id: null,
        topic_id: null,
        tags: []
      }
      this.newTag = ''
      this.selectedExistingTag = ''
      this.lastSavedTaskSnapshot = ''
    },

    resetAssociation() {
      this.taskForm.project_id = null
      this.taskForm.collection_id = null
      this.taskForm.topic_id = null
    },
    
  async saveTask() {
      try {
        const url = this.isEditing ? `/api/tasks/${this.taskForm.id}` : '/api/tasks/'
        const method = this.isEditing ? 'PUT' : 'POST'
        
        // Send tags as an array; backend now normalizes both array and JSON-string inputs.
        const taskData = {
          title: this.taskForm.title,
          description: this.taskForm.description,
          status: this.taskForm.status,
          priority: this.taskForm.priority,
          due_date: this.taskForm.due_date,
          assigned_to: this.taskForm.assigned_to,
          tags: this.taskForm.tags
        }
        
        // Set association based on type
        if (this.taskForm.associationType === 'project') {
          taskData.project_id = this.taskForm.project_id
        } else if (this.taskForm.associationType === 'collection') {
          taskData.collection_id = this.taskForm.collection_id
        } else if (this.taskForm.associationType === 'topic') {
          taskData.topic_id = this.taskForm.topic_id
        }
        
        const response = await fetch(url, {
          method: method,
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(taskData)
        })
        
        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}))
          throw new Error(errorData.error || `HTTP error! status: ${response.status}`)
        }
        
  await this.fetchTasks()
  await this.fetchAllTags()
  // update snapshot to reflect saved state before closing
  this.lastSavedTaskSnapshot = JSON.stringify(this.taskForm)
  this.closeModal()
  toast.success(this.isEditing ? 'Task updated.' : 'Task created.')
        
      } catch (error) {
        console.error('Failed to save task:', error)
  this.error = error.message || 'Failed to save task. Please try again.'
  toast.error(this.error)
      }
    },
    
    deleteTask(task) {
      this.taskToDelete = task
      this.showDeleteModal = true
    },
    
    closeDeleteModal() {
      this.showDeleteModal = false
      this.taskToDelete = null
    },
    
    async confirmDelete() {
      try {
        const response = await fetch(`/api/tasks/${this.taskToDelete.id}`, {
          method: 'DELETE'
        })
        
        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}))
          throw new Error(errorData.error || `HTTP error! status: ${response.status}`)
        }
        
        await this.fetchTasks()
        this.closeDeleteModal()
        
      } catch (error) {
        console.error('Failed to delete task:', error)
  this.error = error.message || 'Failed to delete task. Please try again.'
  toast.error(this.error)
      }
    },

    // Tag management methods
    addNewTag() {
      if (this.newTag.trim() && !this.taskForm.tags.includes(this.newTag.trim())) {
        this.taskForm.tags.push(this.newTag.trim())
        this.newTag = ''
      }
    },

    addExistingTag() {
      if (this.selectedExistingTag && !this.taskForm.tags.includes(this.selectedExistingTag)) {
        this.taskForm.tags.push(this.selectedExistingTag)
        this.selectedExistingTag = ''
      }
    },

    removeTag(tag) {
      const index = this.taskForm.tags.indexOf(tag)
      if (index > -1) {
        this.taskForm.tags.splice(index, 1)
      }
    },

    parseTaskTags(tags) {
      if (Array.isArray(tags)) {
        return tags
      } else if (typeof tags === 'string') {
        try {
          return JSON.parse(tags || '[]')
        } catch (e) {
          return []
        }
      }
      return []
    },

    async fetchStakeholders() {
      try {
        const response = await fetch('/api/stakeholders/')
        if (response.ok) {
          const data = await response.json()
          // Backend returns direct array, not wrapped in object
          this.stakeholders = Array.isArray(data) ? data : (data.stakeholders || [])
        }
      } catch (error) {
        console.error('Failed to fetch stakeholders:', error)
      }
    },

    getAssignedToDisplayName(assignedTo) {
      if (!assignedTo) return '-'
      
      // If it's an email, try to find the stakeholder name
      if (assignedTo.includes('@')) {
        const stakeholder = this.stakeholders.find(s => s.email === assignedTo)
        return stakeholder ? stakeholder.name : assignedTo
      }
      
      // If it's already a name, return it
      return assignedTo
    },
    
    formatDate(dateString) {
      if (!dateString) return null
      return new Date(dateString).toLocaleDateString()
    },
    
    formatStatus(status) {
      const statusMap = {
        'todo': 'To Do',
        'in_progress': 'In Progress',
        'completed': 'Completed'
      }
      return statusMap[status] || status
    },
    
    formatPriority(priority) {
      const priorityMap = {
        'low': 'Low',
        'medium': 'Medium',
        'high': 'High'
      }
      return priorityMap[priority] || priority
    },
    // Dirty detection for mixin
    isDirty() {
      if (!this.showModal) return false
      try {
        return JSON.stringify(this.taskForm) !== this.lastSavedTaskSnapshot
      } catch (e) { return false }
    }
  }
}
</script>

<style>
.all-tasks {
  padding: 2rem;
  max-width: 1600px;
  margin: 0 auto;
}

.all-tasks > .subtitle {
  margin-bottom: 1rem; /* add space below subtitle */
}

.guidance-text {
  color: #666;
  margin-bottom: 2rem;
  font-size: 1.1rem;
  line-height: 1.5;
}


.filters-section {
  background: var(--bg-white);
  padding: 1rem;
  border-radius: var(--border-radius-lg);
  margin-bottom: 2rem;
  border: 1px solid var(--border-light-gray);
  box-shadow: var(--box-shadow-sm);
}

.filter-row {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr auto;
  gap: 1rem;
  align-items: center;
}

.filter-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #333;
}

.button-group {
  display: flex;
  gap: 0.5rem;
  align-items: center !important; /* Force center alignment, override parent flex-end */
}

.filter-input {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.9rem;
  box-sizing: border-box;
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

.tasks-table-container {
  overflow-x: auto;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  padding: 0.75rem 1rem; /* add inner horizontal padding so edges aren’t flush */
}

.table-instructions {
  margin: 1rem 0 0.5rem 0;
  text-align: left;
}

.table-instructions p {
  color: #666;
  font-style: italic;
  margin: 0;
  font-size: 0.9rem;
}

.tasks-table {
  width: 100%;
  border-collapse: collapse;
}

.tasks-table th,
.tasks-table td {
  padding: .1rem;
  text-align: left;
  border-bottom: 1px solid #e0e0e0;
}

/* Extra padding on table edges */
.tasks-table th:first-child,
.tasks-table td:first-child {
  padding-left: 1rem;
}

.tasks-table th:last-child,
.tasks-table td:last-child {
  padding-right: 1rem;
}

.tasks-table th {
  background-color: #f8f9fa;
  font-weight: 600;
  color: #495057;
}

.task-row {
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.task-row:hover {
  background-color: #f8f9fa;
}

.task-cell {
  max-width: 250px;
}

.task-title {
  font-weight: 400;
  color: #333;
  margin-bottom: 0.25rem;
}

.task-desc {
  font-size: 0.9rem;
  color: #666;
  line-height: 1.4;
}

.association {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
}

.status-badge, .priority-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 400;
  text-transform: uppercase;
}

.status-todo {
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

.priority-low {
  background-color: #f3e5f5;
  color: #7b1fa2;
}

.priority-medium {
  background-color: #fff3e0;
  color: #f57c00;
}

.priority-high {
  background-color: #ffebee;
  color: #d32f2f;
}

.tags-cell {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem;
}

.edit-inline-btn {
  margin-left: 0.5rem;
  align-self: center;
}

.tag-badge {
  background-color: #e8f4f8;
  color: #0277bd;
  padding: 0.2rem 0.5rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
}

.actions-column,
.actions-cell {
  white-space: nowrap;
  text-align: center !important;
  vertical-align: middle;
  width: 30px;
  padding: .1rem .1rem;
}

.btn-delete {
  background-color: #dc3545;
  border: none;
  color: white;
  width: 28px;
  height: 28px;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.2s ease;
  font-size: 0.9rem;
}

.btn-delete:hover {
  background-color: #c82333;
}

.due-date-cell,
.assigned-to-cell {
  font-size: 0.85rem;
  color: #666;
}

.id-column,
.id-cell {
  width: 60px;
  text-align: center;
  font-size: 0.85rem;
  color: #666;
  white-space: nowrap;
}

.status-column {
  white-space: nowrap;
  width: 1%;
  font-weight: 400;
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

/* Modal and form styles follow the same pattern as other views */
.custom-modal {
  background: white;
  border-radius: 8px;
  min-width: 700px;
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

/* Tags input styles */
.tags-input {
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 1rem;
  background-color: #f9f9f9;
}

.selected-tags {
  margin-bottom: 1rem;
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.selected-tag {
  background-color: #e8f4f8;
  color: #0277bd;
  padding: 0.2rem 0.5rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 0.3rem;
}

.remove-tag-btn {
  background: none;
  border: none;
  color: #0b3954; /* darker icon color for visibility */
  cursor: pointer;
  font-size: 1rem;
  line-height: 1;
  padding: 0;
}

.existing-tags-section,
.new-tag-section {
  margin-bottom: 1rem;
}

.existing-tags-section label,
.new-tag-section label {
  font-size: 0.9rem;
  margin-bottom: 0.5rem;
}

.new-tag-input-row {
  display: flex;
  gap: 0.5rem;
}

.warning {
  color: #f57c00;
  font-style: italic;
}

@media (max-width: 768px) {
  .filter-row {
    grid-template-columns: 1fr;
  }
  
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .custom-modal {
    min-width: 95vw;
  }
}
</style>
