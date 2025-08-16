<template>
  <div class="tasks-page">
    <NotificationTicker
      :notifications="mergedNotifications"
      contextType="global"
      @mark-read="markNotificationRead"
    />
    <!-- Page Header -->
    <div class="page-header">
      <div class="page-header-content">
        <h1>Task Management</h1>
        <p class="page-description">Organize and track tasks across projects, collections, and topics</p>
      </div>
      <div class="header-actions">
        <button @click="showCreateModal = true" class="primary-btn">
          ➕ Create Task
        </button>
      </div>
    </div>

    <!-- Task Summary Cards -->
    <div class="summary-grid">
      <div class="summary-card">
        <div class="summary-icon">📋</div>
        <div class="summary-content">
          <h3>Total Tasks</h3>
          <div class="summary-number">{{ taskSummary.total }}</div>
        </div>
      </div>
      
      <div class="summary-card todo">
        <div class="summary-icon">⏳</div>
        <div class="summary-content">
          <h3>To Do</h3>
          <div class="summary-number">{{ taskSummary.todo }}</div>
        </div>
      </div>
      
      <div class="summary-card in-progress">
        <div class="summary-icon">🚀</div>
        <div class="summary-content">
          <h3>In Progress</h3>
          <div class="summary-number">{{ taskSummary.in_progress }}</div>
        </div>
      </div>
      
      <div class="summary-card completed">
        <div class="summary-icon">✅</div>
        <div class="summary-content">
          <h3>Completed</h3>
          <div class="summary-number">{{ taskSummary.completed }}</div>
        </div>
      </div>
      
      <div class="summary-card overdue">
        <div class="summary-icon">⚠️</div>
        <div class="summary-content">
          <h3>Overdue</h3>
          <div class="summary-number">{{ taskSummary.overdue }}</div>
        </div>
      </div>
    </div>

    <!-- Filters and Search -->
    <div class="filters-section">
      <div class="filter-row">
        <div class="search-box">
          <input
            v-model="searchQuery"
            @input="applyFilters"
            type="text"
            placeholder="Search tasks..."
            class="search-input"
          />
          <span class="search-icon">🔍</span>
        </div>
        
        <select v-model="statusFilter" @change="applyFilters" class="filter-select">
          <option value="">All Statuses</option>
          <option value="todo">To Do</option>
          <option value="in_progress">In Progress</option>
          <option value="review">Review</option>
          <option value="completed">Completed</option>
          <option value="cancelled">Cancelled</option>
        </select>
        
        <select v-model="priorityFilter" @change="applyFilters" class="filter-select">
          <option value="">All Priorities</option>
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
          <option value="urgent">Urgent</option>
        </select>
        
        <select v-model="associationFilter" @change="applyFilters" class="filter-select">
          <option value="">All Associations</option>
          <option value="project">Projects</option>
          <option value="collection">Collections</option>
          <option value="topic">Topics</option>
        </select>
        
        <button 
          v-if="hasActiveFilters" 
          @click="clearFilters" 
          class="clear-filters-btn"
        >
          ✕ Clear Filters
        </button>
      </div>
    </div>

    <!-- Tasks List -->
    <div class="tasks-section">
      <!-- Loading State -->
      <div v-if="loading" class="loading-state">
        <div class="loading-content">
          <div class="loading-spinner">⏳</div>
          <h3>Loading Tasks...</h3>
          <p>Please wait while we fetch your tasks.</p>
        </div>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="error-state">
        <div class="error-content">
          <div class="error-icon">⚠️</div>
          <h3>Error Loading Tasks</h3>
          <p>{{ error }}</p>
          <button @click="fetchTasks" class="retry-btn">🔄 Retry</button>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else-if="filteredTasks.length === 0" class="empty-state">
        <div class="empty-content">
          <div class="empty-icon">📝</div>
          <h3>{{ tasks.length === 0 ? 'No Tasks Yet' : 'No Tasks Match Filter' }}</h3>
          <p>{{ tasks.length === 0 ? 'Get started by creating your first task.' : 'Try adjusting your filters or create a new task.' }}</p>
          <button @click="showCreateModal = true" class="create-first-btn">
            ➕ {{ tasks.length === 0 ? 'Create Your First Task' : 'Create New Task' }}
          </button>
        </div>
      </div>

      <!-- Tasks Table -->
      <div v-else class="tasks-table-container">
        <table class="tasks-table">
          <thead>
            <tr>
              <th class="id-column">ID</th>
              <th>Task</th>
              <th>Status</th>
              <th>Priority</th>
              <th>Association</th>
              <th>Due Date</th>
              <th>Assigned To</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="task in filteredTasks"
              :key="task.id + '-' + task.status + '-' + refreshKey"
              class="task-row"
              :class="[task.status, task.priority, { overdue: isOverdue(task) }]"
            >
              <td class="id-cell">{{ task.id }}</td>
              <td class="task-cell">
                <div class="task-title">{{ task.title }}</div>
                <div class="task-id">ID: {{ task.id }}</div>
                <div v-if="task.description" class="task-description">{{ task.description }}</div>
              </td>
              <td>
                <span class="status-badge" :class="task.status">
                  {{ formatStatus(task.status) }}
                </span>
              </td>
              <td>
                <span class="priority-badge" :class="task.priority">
                  {{ formatPriority(task.priority) }}
                </span>
              </td>
              <td class="association-cell">
                <span v-if="task.project_name" class="association-tag project">
                  <i class="fas fa-project-diagram"></i> {{ task.project_name }}
                </span>
                <span v-else-if="task.collection_name" class="association-tag collection">
                  <i class="fas fa-folder"></i> {{ task.collection_name }}
                </span>
                <span v-else-if="task.topic_name" class="association-tag topic">
                  <i class="fas fa-file-alt"></i> {{ task.topic_name }}
                </span>
                <span v-else class="association-tag none">-</span>
              </td>
              <td class="due-date-cell">
                <div v-if="task.due_date" class="due-date" :class="{ overdue: isOverdue(task) }">
                  <i class="fas fa-calendar"></i> {{ formatDate(task.due_date) }}
                </div>
                <span v-else class="no-date">-</span>
              </td>
              <td class="assigned-cell">
                <div v-if="task.assigned_to" class="assigned-to">
                  <i class="fas fa-user"></i> {{ task.assigned_to }}
                </div>
                <span v-else class="no-assignment">-</span>
              </td>
              <td class="actions-cell">
                <div class="task-actions">
                  <button @click="editTask(task)" class="btn btn-sm btn-secondary">
                    <i class="fas fa-edit"></i> Edit
                  </button>
                  <button 
                    v-if="getNextStatus(task.status)"
                    @click="advanceStatus(task.id)" 
                    class="btn btn-sm"
                    :class="getStatusButtonClass(task.status)"
                  >
                    {{ getStatusButtonText(task.status) }}
                  </button>
                  <button 
                    v-if="isAdmin" 
                    @click="deleteTask(task)" 
                    class="btn btn-sm btn-danger"
                  >
                    <i class="fas fa-trash"></i> Delete
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Create/Edit Task Modal -->
    <div v-if="showCreateModal || showEditModal" class="modal-overlay" @click="closeModal">
      <div class="modal large-modal" @click.stop>
        <div class="modal-header">
          <h2>{{ showCreateModal ? 'Create New Task' : 'Edit Task' }}</h2>
          <button @click="closeModal" class="close-btn">×</button>
        </div>
        
        <form @submit.prevent="saveTask" class="modal-body">
          <!-- Basic Information -->
          <div class="form-section">
            <h3>Basic Information</h3>
            
            <div class="form-group">
              <label for="taskTitle">Title *</label>
              <input
                id="taskTitle"
                v-model="taskForm.title"
                type="text"
                required
                placeholder="Enter task title"
                class="form-input"
              />
            </div>
            
            <div class="form-group">
              <label for="taskDescription">Description</label>
              <textarea
                id="taskDescription"
                v-model="taskForm.description"
                placeholder="Task description (optional)"
                rows="3"
                class="form-input"
              ></textarea>
            </div>
            
            <div class="form-row">
              <div class="form-group">
                <label for="taskStatus">Status</label>
                <select id="taskStatus" v-model="taskForm.status" class="form-input">
                  <option value="todo">To Do</option>
                  <option value="in_progress">In Progress</option>
                  <option value="review">Review</option>
                  <option value="completed">Completed</option>
                  <option value="cancelled">Cancelled</option>
                </select>
              </div>
              
              <div class="form-group">
                <label for="taskPriority">Priority</label>
                <select id="taskPriority" v-model="taskForm.priority" class="form-input">
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                  <option value="urgent">Urgent</option>
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
                <input
                  id="taskAssignedTo"
                  v-model="taskForm.assigned_to"
                  type="text"
                  placeholder="Email or name"
                  class="form-input"
                />
              </div>
            </div>
          </div>

          <!-- Association -->
          <div class="form-section">
            <h3>Association</h3>
            <p class="form-hint">Associate this task with a project, collection, or topic</p>
            
            <div class="association-selector">
              <div class="association-type">
                <input
                  id="assoc-project"
                  v-model="taskForm.associationType"
                  type="radio"
                  value="project"
                />
                <label for="assoc-project">Project</label>
              </div>
              
              <div class="association-type">
                <input
                  id="assoc-collection"
                  v-model="taskForm.associationType"
                  type="radio"
                  value="collection"
                />
                <label for="assoc-collection">Collection</label>
              </div>
              
              <div class="association-type">
                <input
                  id="assoc-topic"
                  v-model="taskForm.associationType"
                  type="radio"
                  value="topic"
                />
                <label for="assoc-topic">Topic</label>
              </div>
              
              <div class="association-type">
                <input
                  id="assoc-none"
                  v-model="taskForm.associationType"
                  type="radio"
                  value=""
                />
                <label for="assoc-none">No Association</label>
              </div>
            </div>
            
            <!-- Project Selector -->
            <div v-if="taskForm.associationType === 'project'" class="form-group">
              <label for="taskProject">Select Project</label>
              <select id="taskProject" v-model="taskForm.project_id" class="form-input">
                <option value="">Choose a project...</option>
                <option 
                  v-for="project in availableAssociations.projects" 
                  :key="project.id" 
                  :value="project.id"
                >
                  {{ project.name }}
                </option>
              </select>
            </div>
            
            <!-- Collection Selector -->
            <div v-if="taskForm.associationType === 'collection'" class="form-group">
              <label for="taskCollection">Select Collection</label>
              <select id="taskCollection" v-model="taskForm.collection_id" class="form-input">
                <option value="">Choose a collection...</option>
                <option 
                  v-for="collection in availableAssociations.collections" 
                  :key="collection.id" 
                  :value="collection.id"
                >
                  {{ collection.name }}
                </option>
              </select>
            </div>
            
            <!-- Topic Selector -->
            <div v-if="taskForm.associationType === 'topic'" class="form-group">
              <label for="taskTopic">Select Topic</label>
              <select id="taskTopic" v-model="taskForm.topic_id" class="form-input">
                <option value="">Choose a topic...</option>
                <option 
                  v-for="topic in availableAssociations.topics" 
                  :key="topic.id" 
                  :value="topic.id"
                >
                  {{ topic.name }}
                </option>
              </select>
            </div>
          </div>

          <!-- Tags -->
          <div class="form-section">
            <h3>Tags (Optional)</h3>
            <div class="tags-input">
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
                    @keyup.enter="addNewTag"
                    type="text"
                    placeholder="Enter new tag name"
                    class="form-input"
                  />
                  <button type="button" @click="addNewTag" class="add-tag-btn" :disabled="!newTag.trim()">
                    Add Tag
                  </button>
                </div>
              </div>
              
              <!-- Selected Tags Display -->
              <div class="tags-list" v-if="taskForm.tags.length > 0">
                <label>Selected tags:</label>
                <div class="tags-display">
                  <span 
                    v-for="(tag, index) in taskForm.tags" 
                    :key="index" 
                    class="tag"
                  >
                    {{ tag }}
                    <button type="button" @click="removeTag(index)" class="tag-remove">×</button>
                  </span>
                </div>
              </div>
            </div>
          </div>

          <div class="modal-actions">
            <button type="button" @click="closeModal" class="cancel-btn">
              Cancel
            </button>
            <button type="submit" class="save-btn">
              {{ showCreateModal ? 'Create Task' : 'Update Task' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import NotificationTicker from '../components/NotificationTicker.vue'

export default {
  name: 'TasksView',
  components: { NotificationTicker },
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
      // Tasks data
      tasks: [],
      filteredTasks: [],
      loading: false,
      error: null,
      refreshKey: 0, // Add refresh key to force re-rendering
      
      // User role (simplified for now - in real app this would come from auth)
      isAdmin: false, // Set to true for admin users, false for regular users
      
      // Task summary
      taskSummary: {
        total: 0,
        todo: 0,
        in_progress: 0,
        completed: 0,
        overdue: 0
      },
      
      // Filters
      searchQuery: '',
      statusFilter: '',
      priorityFilter: '',
      associationFilter: '',
      
      // Modals
      showCreateModal: false,
      showEditModal: false,
      
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
      
      // Available associations
      availableAssociations: {
        projects: [],
        collections: [],
        topics: []
      },
      
      // Tags input
      newTag: '',
      selectedExistingTag: '',
      allStoredTags: [] // Tags fetched from the database
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
    hasActiveFilters() {
      return this.searchQuery || this.statusFilter || this.priorityFilter || this.associationFilter
    },
    allTags() {
      // Combine tags from tasks and stored tags from database
      const tags = new Set()
      
      // Add tags from existing tasks
      this.tasks.forEach(task => {
        let taskTags = []
        if (Array.isArray(task.tags)) {
          taskTags = task.tags
        } else if (typeof task.tags === 'string') {
          try {
            taskTags = JSON.parse(task.tags || '[]')
          } catch (e) {
            taskTags = []
          }
        }
        taskTags.forEach(t => tags.add(t))
      })
      
      // Add stored tags from database (extract name from tag objects)
      this.allStoredTags.forEach(tag => {
        if (typeof tag === 'object' && tag.name) {
          tags.add(tag.name)
        } else if (typeof tag === 'string') {
          tags.add(tag)
        }
      })
      
      console.log('All tags computed:', Array.from(tags), 'from tasks:', this.tasks.length, 'from stored:', this.allStoredTags.length)
      return Array.from(tags).sort()
    },
    availableExistingTags() {
      // This computed property is no longer used in the template, 
      // but keeping it for backward compatibility
      const available = this.allTags.filter(tag => !this.taskForm.tags.includes(tag))
      console.log('Available existing tags:', available, 'allTags:', this.allTags, 'taskForm.tags:', this.taskForm.tags)
      return available
    }
  },
  
  methods: {
    async fetchTasks() {
      this.loading = true
      this.error = null
      try {
        const response = await fetch('/api/tasks/')
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        const data = await response.json()
        this.tasks = data.tasks || []
        this.applyFilters()
      } catch (error) {
        console.error('Failed to fetch tasks:', error)
        this.error = 'Failed to load tasks. Please try again.'
      } finally {
        this.loading = false
      }
    },
    
    async fetchAllTags() {
      try {
        const response = await fetch('/api/tasks/tags')
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        this.allStoredTags = await response.json()
      } catch (error) {
        console.error('Error fetching tags:', error)
        this.allStoredTags = []
      }
    },
    
    async fetchTaskSummary() {
      try {
        const response = await fetch('/api/tasks/summary')
        if (response.ok) {
          this.taskSummary = await response.json()
        }
      } catch (error) {
        console.error('Failed to fetch task summary:', error)
      }
    },
    
    async fetchAssociations() {
      try {
        const response = await fetch('/api/tasks/associations')
        if (response.ok) {
          this.availableAssociations = await response.json()
        }
      } catch (error) {
        console.error('Failed to fetch associations:', error)
      }
    },
    
    applyFilters() {
      let filtered = [...this.tasks]
      
      // Search filter
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase()
        filtered = filtered.filter(task =>
          task.title.toLowerCase().includes(query) ||
          (task.description && task.description.toLowerCase().includes(query))
        )
      }
      
      // Status filter
      if (this.statusFilter) {
        filtered = filtered.filter(task => task.status === this.statusFilter)
      }
      
      // Priority filter
      if (this.priorityFilter) {
        filtered = filtered.filter(task => task.priority === this.priorityFilter)
      }
      
      // Association filter
      if (this.associationFilter) {
        filtered = filtered.filter(task => {
          switch (this.associationFilter) {
            case 'project':
              return task.project_id !== null
            case 'collection':
              return task.collection_id !== null
            case 'topic':
              return task.topic_id !== null
            default:
              return true
          }
        })
      }
      
      this.filteredTasks = filtered
    },
    
    clearFilters() {
      this.searchQuery = ''
      this.statusFilter = ''
      this.priorityFilter = ''
      this.associationFilter = ''
      this.applyFilters()
    },
    
    editTask(task) {
      this.taskForm = {
        id: task.id,
        title: task.title,
        description: task.description || '',
        status: task.status,
        priority: task.priority,
        due_date: task.due_date || '',
        assigned_to: task.assigned_to || '',
        associationType: task.project_id ? 'project' : task.collection_id ? 'collection' : task.topic_id ? 'topic' : '',
        project_id: task.project_id,
        collection_id: task.collection_id,
        topic_id: task.topic_id,
        tags: Array.isArray(task.tags) ? task.tags : (typeof task.tags === 'string' ? JSON.parse(task.tags || '[]') : [])
      }
      console.log('Editing task, tags loaded:', this.taskForm.tags)
      this.showEditModal = true
    },
    
    async saveTask() {
      try {
        const taskData = {
          title: this.taskForm.title,
          description: this.taskForm.description,
          status: this.taskForm.status,
          priority: this.taskForm.priority,
          due_date: this.taskForm.due_date,
          assigned_to: this.taskForm.assigned_to,
          tags: JSON.stringify(this.taskForm.tags) // Convert tags array to JSON string
        }
        
        // Set association based on type
        if (this.taskForm.associationType === 'project') {
          taskData.project_id = this.taskForm.project_id
        } else if (this.taskForm.associationType === 'collection') {
          taskData.collection_id = this.taskForm.collection_id
        } else if (this.taskForm.associationType === 'topic') {
          taskData.topic_id = this.taskForm.topic_id
        }
        
        const url = this.showCreateModal ? '/api/tasks/' : `/api/tasks/${this.taskForm.id}`
        const method = this.showCreateModal ? 'POST' : 'PUT'
        
        console.log('Saving task:', {
          url,
          method,
          taskData,
          formData: this.taskForm
        })
        
        const response = await fetch(url, {
          method: method,
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(taskData)
        })
        
        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}))
          console.error('API Error Response:', errorData)
          throw new Error(`HTTP error! status: ${response.status}, message: ${errorData.message || response.statusText}`)
        }
        
        const result = await response.json()
        console.log('Task saved successfully:', result)
        
        // Refresh tasks and tags
        await this.fetchTasks()
        await this.fetchTaskSummary()
        await this.fetchAllTags() // Refresh tags in case new ones were added
        this.closeModal()
        
      } catch (error) {
        console.error('Failed to save task:', error)
        this.error = 'Failed to save task. Please try again.'
      }
    },
    
    async deleteTask(task) {
      if (!confirm(`Are you sure you want to delete "${task.title}"?`)) {
        return
      }
      
      try {
        const response = await fetch(`/api/tasks/${task.id}`, {
          method: 'DELETE'
        })
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        
        // Refresh tasks
        await this.fetchTasks()
        await this.fetchTaskSummary()
        
      } catch (error) {
        console.error('Failed to delete task:', error)
        this.error = 'Failed to delete task. Please try again.'
      }
    },
    
    async advanceStatus(taskId) {
      try {
        // Find the current task in filteredTasks to get latest state
        const task = this.filteredTasks.find(t => t.id === taskId)
        if (!task) {
          console.error('Task not found:', taskId)
          return
        }
        
        const nextStatus = this.getNextStatus(task.status)
        if (!nextStatus) {
          return
        }
        
        const response = await fetch(`/api/tasks/${task.id}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ status: nextStatus })
        })
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        
        // Update tasks array
        const taskIndex = this.tasks.findIndex(t => t.id === task.id)
        if (taskIndex !== -1) {
          const newTasks = [...this.tasks]
          newTasks[taskIndex] = { ...newTasks[taskIndex], status: nextStatus }
          this.tasks = newTasks
        }
        
        // Update filteredTasks array
        const filteredIndex = this.filteredTasks.findIndex(t => t.id === task.id)
        if (filteredIndex !== -1) {
          const newFilteredTasks = [...this.filteredTasks]
          newFilteredTasks[filteredIndex] = { ...newFilteredTasks[filteredIndex], status: nextStatus }
          this.filteredTasks = newFilteredTasks
        }
        
        // Force re-render
        this.refreshKey++
        
        // Refresh summary after status change
        await this.fetchTaskSummary()
        
      } catch (error) {
        console.error('Failed to advance task status:', error)
        this.error = 'Failed to update task status. Please try again.'
      }
    },
    
    closeModal() {
      this.showCreateModal = false
      this.showEditModal = false
      this.resetForm()
      // Clear tag input fields
      this.newTag = ''
      this.selectedExistingTag = ''
    },
    
    resetForm() {
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
    },
    
    addNewTag() {
      const tag = this.newTag.trim()
      if (tag && !this.taskForm.tags.includes(tag)) {
        this.taskForm.tags.push(tag)
        this.newTag = ''
      }
    },
    
    addExistingTag() {
      if (this.selectedExistingTag && !this.taskForm.tags.includes(this.selectedExistingTag)) {
        this.taskForm.tags.push(this.selectedExistingTag)
        this.selectedExistingTag = ''
      }
    },
    
    removeTag(index) {
      this.taskForm.tags.splice(index, 1)
    },
    
    formatStatus(status) {
      const statusMap = {
        'todo': 'To Do',
        'in_progress': 'In Progress',
        'review': 'Review',
        'completed': 'Completed',
        'cancelled': 'Cancelled'
      }
      return statusMap[status] || status
    },
    
    getNextStatus(currentStatus) {
      const statusFlow = {
        'todo': 'in_progress',
        'in_progress': 'review',
        'review': 'completed',
        'completed': null, // No next status
        'cancelled': null  // No next status
      }
      return statusFlow[currentStatus] || null
    },
    
    getStatusButtonText(currentStatus) {
      const nextStatus = this.getNextStatus(currentStatus)
      if (!nextStatus) return ''
      
      const buttonTextMap = {
        'in_progress': '🚀 Start',
        'review': '👀 Review',
        'completed': '✅ Complete'
      }
      return buttonTextMap[nextStatus] || '➡️ Next'
    },
    
    getStatusButtonClass(currentStatus) {
      const nextStatus = this.getNextStatus(currentStatus)
      if (!nextStatus) return ''
      
      const classMap = {
        'in_progress': 'start-btn',
        'review': 'review-btn', 
        'completed': 'complete-btn'
      }
      return classMap[nextStatus] || 'advance-btn'
    },
    
    formatPriority(priority) {
      const priorityMap = {
        'low': 'Low',
        'medium': 'Medium',
        'high': 'High',
        'urgent': 'Urgent'
      }
      return priorityMap[priority] || priority
    },
    
    formatDate(dateString) {
      if (!dateString) return ''
      return new Date(dateString).toLocaleDateString()
    },
    
    isOverdue(task) {
      if (!task.due_date || task.status === 'completed') return false
      return new Date(task.due_date) < new Date()
    }
  },
  
  mounted() {
    this.fetchTasks()
    this.fetchTaskSummary()
    this.fetchAssociations()
    this.fetchAllTags()
  }
}
</script>

<style scoped>
/* Page Layout */
.tasks-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid #f0f4f8;
}

.page-header-content {
  flex: 1;
}

.page-header h1 {
  color: #205493;
  margin-bottom: 0.5rem;
  font-size: 2.5rem;
  font-weight: 300;
}

.page-description {
  color: #6c757d;
  font-size: 1.1rem;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 1rem;
}

.primary-btn {
  background: #205493;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.primary-btn:hover {
  background: #112e51;
  transform: translateY(-1px);
}

/* Summary Cards */
.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.summary-card {
  background: white;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.summary-card.todo {
  border-left: 4px solid #FF7043;
}

.summary-card.in-progress {
  border-left: 4px solid #205493;
}

.summary-card.completed {
  border-left: 4px solid #009964;
}

.summary-card.overdue {
  border-left: 4px solid #9B2743;
}

.summary-icon {
  font-size: 2rem;
  min-width: 60px;
  text-align: center;
}

.summary-content h3 {
  margin: 0 0 0.25rem 0;
  color: #495057;
  font-size: 0.875rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.summary-number {
  font-size: 2rem;
  font-weight: 700;
  color: #205493;
  line-height: 1;
}

/* Filters */
.filters-section {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.filter-row {
  display: flex;
  gap: 1rem;
  align-items: center;
  flex-wrap: wrap;
}

.search-box {
  flex: 1;
  min-width: 250px;
  position: relative;
}

.filter-select {
  flex: 0 0 auto;
  min-width: 150px;
  width: 180px;
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  background: white;
  font-size: 0.9rem;
}

.clear-filters-btn {
  flex: 0 0 auto;
  background: #f3f4f6;
  color: #6b7280;
  border: 1px solid #d1d5db;
  padding: 0.75rem 1rem;
  border-radius: 6px;
  font-size: 0.9rem;
  cursor: pointer;
  white-space: nowrap;
}

@media (max-width: 1200px) {
  .filter-row {
    flex-wrap: wrap;
  }
  
  .search-box {
    flex-basis: 100%;
  }
}

@media (max-width: 900px) {
  .filter-row {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-box,
  .filter-select {
    width: 100%;
  }
}

.search-input {
  width: 80%;
  max-width: 400px;
  padding: 0.75rem 2.5rem 0.75rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.9rem;
}

.search-icon {
  position: absolute;
  right: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  color: #9ca3af;
}

.clear-filters-btn:hover {
  background: #e5e7eb;
}

/* Tasks Grid */
.tasks-section {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

/* Tasks Table */
.tasks-table-container {
  overflow-x: auto;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  border: 1px solid #e2e8f0;
}

.tasks-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 1200px;
}

.tasks-table th,
.tasks-table td {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid #e2e8f0;
}

.tasks-table th {
  background-color: #f8fafc;
  font-weight: 600;
  color: #112e51;
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

.tasks-table tbody tr {
  transition: background-color 0.2s ease;
}

.tasks-table tbody tr:hover {
  background-color: #f8fafc;
}

.tasks-table tbody tr.overdue {
  background-color: #fef2f2;
}

.tasks-table tbody tr.urgent {
  border-left: 4px solid #9B2743;
}

.tasks-table tbody tr.high {
  border-left: 4px solid #FF7043;
}

.tasks-table tbody tr.medium {
  border-left: 4px solid #205493;
}

.tasks-table tbody tr.low {
  border-left: 4px solid #009964;
}

.task-cell {
  max-width: 300px;
}

.task-title {
  margin: 0 0 0.5rem 0;
  color: #112e51;
  font-size: 1rem;
  font-weight: 600;
  line-height: 1.3;
}

.task-id {
  color: #6b7280;
  font-size: 0.75rem;
  margin-bottom: 0.5rem;
}

.task-description {
  color: #6b7280;
  font-size: 0.875rem;
  line-height: 1.4;
  margin: 0;
}

.status-badge, .priority-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  text-align: center;
}

.status-badge.todo {
  background: #fef3c7;
  color: #92400e;
}

.status-badge.in_progress {
  background: #dbeafe;
  color: #205493;
}

.status-badge.review {
  background: #e0e7ff;
  color: #5b21b6;
}

.status-badge.completed {
  background: #d1fae5;
  color: #065f46;
}

.status-badge.cancelled {
  background: #fee2e2;
  color: #991b1b;
}

.priority-badge.urgent {
  background: #fee2e2;
  color: #991b1b;
}

.priority-badge.high {
  background: #fef3c7;
  color: #92400e;
}

.priority-badge.medium {
  background: #dbeafe;
  color: #205493;
}

.priority-badge.low {
  background: #d1fae5;
  color: #065f46;
}

.association-cell {
  max-width: 200px;
}

.association-tag {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 500;
}

.association-tag.project {
  background: #e0f2fe;
  color: #005E7B;
}

.association-tag.collection {
  background: #f0f9ff;
  color: #0284c7;
}

.association-tag.topic {
  background: #fef7cd;
  color: #a16207;
}

.association-tag.none {
  color: #6b7280;
  background: transparent;
  padding: 0;
}

.due-date-cell, .assigned-cell {
  color: #6b7280;
  font-size: 0.875rem;
}

.due-date {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
}

.due-date.overdue {
  color: #ef4444;
  font-weight: 600;
}

.assigned-to {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
}

.no-date, .no-assignment {
  color: #9ca3af;
}

.actions-cell {
  min-width: 200px;
}

.task-actions {
  display: flex;
  gap: 0.5rem;
  align-items: center;
  flex-wrap: wrap;
}

.task-actions {
  display: flex;
  gap: 0.5rem;
  align-items: center;
  flex-wrap: wrap;
}

/* Button Styles */
.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.875rem;
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

.btn-success {
  background-color: #009964;
  color: white;
}

.btn-success:hover {
  background-color: #006548;
}

.btn-warning {
  background-color: #f57c00;
  color: white;
}

.btn-warning:hover {
  background-color: #ef6c00;
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
  border-radius: 12px;
  min-width: 600px;
  max-width: 90vw;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
}

.large-modal {
  min-width: 800px;
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
}

.close-btn:hover {
  color: #112e51;
}

.modal-body {
  padding: 1.5rem;
}

.form-section {
  margin-bottom: 2rem;
  padding: 1rem;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  background: #fafafa;
}

.form-section h3 {
  margin: 0 0 1rem 0;
  color: #112e51;
  font-size: 1.1rem;
  font-weight: 600;
}

.form-hint {
  color: #6b7280;
  font-size: 0.9rem;
  margin-bottom: 1rem;
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

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.form-input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.9rem;
  font-family: inherit;
  box-sizing: border-box;
}

.form-input:focus {
  outline: none;
  border-color: #205493;
  box-shadow: 0 0 0 3px rgba(0, 90, 156, 0.1);
}

.association-selector {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 1rem;
  margin-bottom: 1rem;
}

.association-type {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.tags-input {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.existing-tags-section,
.new-tag-section {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.new-tag-input-row {
  display: flex;
  gap: 0.5rem;
  align-items: end;
}

.add-tag-btn {
  padding: 0.75rem 1rem;
  background: #205493;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 0.9rem;
  cursor: pointer;
  white-space: nowrap;
}

.add-tag-btn:hover:not(:disabled) {
  background: #005E7B;
}

.add-tag-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.tags-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.tags-display {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.tag {
  background: #e0f2fe;
  color: #005E7B;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.8rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.tag-remove {
  background: none;
  border: none;
  color: #005E7B;
  cursor: pointer;
  font-weight: bold;
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
  border: 1px solid #d5d7db;
  background: white;
  color: #374151;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
}

.cancel-btn:hover {
  background: #f9fafb;
}

.save-btn {
  padding: 0.75rem 1.5rem;
  background: #205493;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
}

.save-btn:hover {
  background: #005E7B;
}

/* States */
.loading-state, .error-state, .empty-state {
  text-align: center;
  padding: 3rem 1rem;
}

.loading-spinner, .error-icon, .empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
  opacity: 0.6;
}

.loading-state h3, .error-state h3, .empty-state h3 {
  margin: 0 0 1rem 0;
  color: #112e51;
  font-size: 1.5rem;
}

.retry-btn, .create-first-btn {
  background: #205493;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  margin-top: 1rem;
}

.retry-btn:hover, .create-first-btn:hover {
  background: #005E7B;
}

/* Responsive Design */
@media (max-width: 768px) {
  .tasks-page {
    padding: 1rem;
  }
  
  .page-header {
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;
  }
  
  .page-header-content {
    text-align: left;
  }
  
  .header-actions {
    align-self: flex-start;
    width: 100%;
  }
  
  .primary-btn {
    width: 100%;
    justify-content: center;
    display: flex;
    align-items: center;
    padding: 0.5rem 1rem;
    font-size: 0.9rem;
    background: #f8f9fa;
    color: #205493;
    border: 1px solid #dee2e6;
    box-shadow: none;
  }
  
  .primary-btn:hover {
    background: #e9ecef;
    transform: none;
    color: #112e51;
  }
  
  .summary-grid {
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
  }
  
  .tasks-table-container {
    margin: 0 -1rem;
    border-radius: 0;
  }
  
  .tasks-table {
    min-width: 800px;
  }
  
  .tasks-table th,
  .tasks-table td {
    padding: 0.75rem 0.5rem;
    font-size: 0.875rem;
  }
  
  .task-actions {
    flex-direction: column;
    gap: 0.25rem;
    align-items: stretch;
  }
  
  .task-actions .btn {
    width: 100%;
    justify-content: center;
  }
  
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .association-selector {
    grid-template-columns: 1fr;
  }
  
  .modal {
    min-width: 95vw;
  }
}

/* Extra small screens */
@media (max-width: 480px) {
  .page-header {
    margin-bottom: 1.5rem;
  }
  
  .page-header h1 {
    font-size: 2rem;
  }
  
  .page-description {
    font-size: 1rem;
  }
  
  .primary-btn {
    padding: 0.4rem 0.8rem;
    font-size: 0.85rem;
    border-radius: 4px;
    background: #f1f3f4;
    color: #495057;
    border: 1px solid #ced4da;
    font-weight: 500;
  }
  
  .primary-btn:hover {
    background: #e9ecef;
    color: #205493;
  }
  
  .summary-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  
  .summary-card {
    padding: 1rem;
  }
  
  .summary-number {
    font-size: 1.5rem;
  }
}

/* Very small screens - compact drawer style */
@media (max-width: 360px) {
  .page-header {
    margin-bottom: 1rem;
  }
  
  .page-header h1 {
    font-size: 1.75rem;
  }
  
  .page-description {
    font-size: 0.9rem;
    margin-bottom: 0.5rem;
  }
  
  .header-actions {
    margin-top: 0.5rem;
  }
  
  .primary-btn {
    padding: 0.35rem 0.7rem;
    font-size: 0.8rem;
    border-radius: 3px;
    background: #f8f9fa;
    color: #6c757d;
    border: 1px solid #e9ecef;
    font-weight: 400;
    letter-spacing: 0.25px;
  }
  
  .primary-btn:hover {
    background: #e9ecef;
    color: #495057;
  }
}
</style>
