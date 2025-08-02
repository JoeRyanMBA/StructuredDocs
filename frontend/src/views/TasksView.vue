<template>
  <div class="tasks-page">
    <!-- Page Header -->
    <div class="page-header">
      <h1>Task Management</h1>
      <p class="page-description">Organize and track tasks across projects, collections, and topics</p>
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

      <!-- Tasks Grid -->
      <div v-else class="tasks-grid">
        <div
          v-for="task in filteredTasks"
          :key="task.id + '-' + task.status + '-' + refreshKey"
          class="task-card"
          :class="[task.status, task.priority]"
        >
          <div class="task-header">
            <h3 class="task-title">{{ task.title }}</h3>
            <div class="task-badges">
              <span class="status-badge" :class="task.status">
                {{ formatStatus(task.status) }}
              </span>
              <span class="priority-badge" :class="task.priority">
                {{ formatPriority(task.priority) }}
              </span>
            </div>
          </div>

          <p v-if="task.description" class="task-description">{{ task.description }}</p>

          <!-- Association Info -->
          <div class="task-association">
            <span v-if="task.project_name" class="association-tag project">
              📁 {{ task.project_name }}
            </span>
            <span v-else-if="task.collection_name" class="association-tag collection">
              📚 {{ task.collection_name }}
            </span>
            <span v-else-if="task.topic_name" class="association-tag topic">
              📄 {{ task.topic_name }}
            </span>
          </div>

          <!-- Task Meta -->
          <div class="task-meta">
            <div v-if="task.due_date" class="due-date" :class="{ overdue: isOverdue(task) }">
              📅 Due: {{ formatDate(task.due_date) }}
            </div>
            <div v-if="task.assigned_to" class="assigned-to">
              👤 {{ task.assigned_to }}
            </div>
          </div>

          <!-- Task Actions -->
          <div class="task-actions">
            <button @click="editTask(task)" class="edit-btn">
              ✏️ Edit
            </button>
            <button 
              v-if="getNextStatus(task.status)"
              @click="advanceStatus(task.id)" 
              class="advance-btn"
              :class="getStatusButtonClass(task.status)"
            >
              {{ getStatusButtonText(task.status) }}
            </button>
            <button 
              v-if="isAdmin" 
              @click="deleteTask(task)" 
              class="delete-btn"
            >
              🗑️ Delete
            </button>
          </div>
        </div>
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
              <input
                v-model="newTag"
                @keyup.enter="addTag"
                type="text"
                placeholder="Add tag and press Enter"
                class="form-input"
              />
              <div class="tags-list">
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
export default {
  name: 'TasksView',
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
      newTag: ''
    }
  },
  
  computed: {
    hasActiveFilters() {
      return this.searchQuery || this.statusFilter || this.priorityFilter || this.associationFilter
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
        tags: task.tags ? JSON.parse(task.tags) : []
      }
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
        
        const url = this.showCreateModal ? '/api/tasks/' : `/api/tasks/${this.taskForm.id}`
        const method = this.showCreateModal ? 'POST' : 'PUT'
        
        const response = await fetch(url, {
          method: method,
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(taskData)
        })
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        
        // Refresh tasks
        await this.fetchTasks()
        await this.fetchTaskSummary()
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
    },
    
    addTag() {
      if (this.newTag.trim() && !this.taskForm.tags.includes(this.newTag.trim())) {
        this.taskForm.tags.push(this.newTag.trim())
        this.newTag = ''
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

.page-header h1 {
  color: #005a9c;
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
  background: #005a9c;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.primary-btn:hover {
  background: #004080;
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
  border-left: 4px solid #fbbf24;
}

.summary-card.in-progress {
  border-left: 4px solid #3b82f6;
}

.summary-card.completed {
  border-left: 4px solid #10b981;
}

.summary-card.overdue {
  border-left: 4px solid #ef4444;
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
  color: #005a9c;
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

.tasks-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
}

.task-card {
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  padding: 1.5rem;
  transition: all 0.2s ease;
  position: relative;
}

.task-card:hover {
  border-color: #005a9c;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 90, 156, 0.15);
}

.task-card.urgent {
  border-left: 4px solid #ef4444;
}

.task-card.high {
  border-left: 4px solid #f59e0b;
}

.task-card.medium {
  border-left: 4px solid #3b82f6;
}

.task-card.low {
  border-left: 4px solid #10b981;
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.task-title {
  margin: 0;
  color: #112e51;
  font-size: 1.1rem;
  font-weight: 600;
  line-height: 1.3;
  flex: 1;
}

.task-badges {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  margin-left: 1rem;
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
  color: #1e40af;
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
  color: #1e40af;
}

.priority-badge.low {
  background: #d1fae5;
  color: #065f46;
}

.task-description {
  color: #6b7280;
  margin-bottom: 1rem;
  line-height: 1.5;
  font-size: 0.9rem;
}

.task-association {
  margin-bottom: 1rem;
}

.association-tag {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 500;
}

.association-tag.project {
  background: #e0f2fe;
  color: #0369a1;
}

.association-tag.collection {
  background: #f0f9ff;
  color: #0284c7;
}

.association-tag.topic {
  background: #fef7cd;
  color: #a16207;
}

.task-meta {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1rem;
  font-size: 0.8rem;
  color: #6b7280;
}

.due-date.overdue {
  color: #ef4444;
  font-weight: 600;
}

.task-actions {
  display: flex;
  gap: 0.5rem;
}

.edit-btn, .complete-btn, .delete-btn, .advance-btn, .start-btn, .review-btn {
  padding: 0.4rem 0.8rem;
  border: none;
  border-radius: 4px;
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.edit-btn {
  background: #e0f2fe;
  color: #0369a1;
}

.edit-btn:hover {
  background: #bae6fd;
}

.start-btn {
  background: #fef3c7;
  color: #92400e;
}

.start-btn:hover {
  background: #fde68a;
}

.review-btn {
  background: #e0e7ff;
  color: #3730a3;
}

.review-btn:hover {
  background: #c7d2fe;
}

.complete-btn {
  background: #d1fae5;
  color: #065f46;
}

.complete-btn:hover {
  background: #a7f3d0;
}

.delete-btn {
  background: #fee2e2;
  color: #991b1b;
}

.delete-btn:hover {
  background: #fecaca;
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
  box-sizing: border-box;
}

.form-input:focus {
  outline: none;
  border-color: #005a9c;
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

.tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.tag {
  background: #e0f2fe;
  color: #0369a1;
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
  color: #0369a1;
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
  border: 1px solid #d1d5db;
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
  background: #005a9c;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
}

.save-btn:hover {
  background: #004080;
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
  background: #005a9c;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  margin-top: 1rem;
}

.retry-btn:hover, .create-first-btn:hover {
  background: #004080;
}

/* Responsive Design */
@media (max-width: 768px) {
  .tasks-page {
    padding: 1rem;
  }
  
  .page-header {
    flex-direction: column;
    gap: 1rem;
  }
  
  .summary-grid {
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
  }
  
  .tasks-grid {
    grid-template-columns: 1fr;
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
</style>
