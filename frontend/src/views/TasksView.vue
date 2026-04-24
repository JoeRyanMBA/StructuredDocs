<template>
  
  <div class="tasks-page">
    
    <!-- Compact Toolbar -->
    <CompactToolbar :show-metrics="true">
      <template #metrics>
        <div class="metric-card">
          <div class="metric-icon">📋</div>
          <div class="metric-content">
            <h3>Total Tasks</h3>
            <div class="metric-number">{{ taskMetrics.total }}</div>
            <div class="metric-detail">All tasks</div>
          </div>
        </div>

        <div class="metric-card">
          <div class="metric-icon">⏳</div>
          <div class="metric-content">
            <h3>To Do</h3>
            <div class="metric-number">{{ taskMetrics.todo }}</div>
            <div class="metric-detail">To do</div>
          </div>
        </div>

        <div class="metric-card">
          <div class="metric-icon">🚀</div>
          <div class="metric-content">
            <h3>In Progress</h3>
            <div class="metric-number">{{ taskMetrics.in_progress }}</div>
            <div class="metric-detail">In progress</div>
          </div>
        </div>

        <div class="metric-card">
          <div class="metric-icon">💬</div>
          <div class="metric-content">
            <h3>In Review</h3>
            <div class="metric-number">{{ taskMetrics.review }}</div>
            <div class="metric-detail">In review</div>
          </div>
        </div>

        <div class="metric-card">
          <div class="metric-icon">✅</div>
          <div class="metric-content">
            <h3>Completed</h3>
            <div class="metric-number">{{ taskMetrics.completed }}</div>
            <div class="metric-detail">Completed</div>
          </div>
        </div>

        <div class="metric-card">
          <div class="metric-icon">⚠️</div>
          <div class="metric-content">
            <h3>Overdue</h3>
            <div class="metric-number">{{ taskMetrics.overdue }}</div>
            <div class="metric-detail">Past due</div>
          </div>
        </div>
      </template>
    </CompactToolbar>

    <!-- Page Header -->
    <div class="page-header">
      <div class="page-header-content">
  <h1>Task Management <HelpIcon feature="projects.tasks" /></h1>
  <p class="subtitle">Organize and track tasks across projects, collections, and topics</p>
      </div>
      <div class="header-actions">
        <button @click="showCreateModal = true" class="primary-btn">
          <span class="action-icon"><IconPlus size="28" /></span> Create Task
        </button>
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
          class="btn btn-secondary btn-sm"
        >
          <i class="bi bi-x"></i> Clear Filters
        </button>
      </div>
    </div>

    <!-- Tasks List -->
    <div class="tasks-section">
      <!-- Loading State -->
      <div v-if="loading" class="loading-overlay">
        <div class="loading-spinner"></div>
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
            <span class="action-icon"><IconPlus size="28" /></span> {{ tasks.length === 0 ? 'Create Your First Task' : 'Create New Task' }}
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
                  <i class="bi bi-diagram-3"></i> {{ task.project_name }}
                </span>
                <span v-else-if="task.collection_name" class="association-tag collection">
                  <i class="bi bi-folder"></i> {{ task.collection_name }}
                </span>
                <span v-else-if="task.topic_name" class="association-tag topic">
                  <i class="bi bi-file-text"></i> {{ task.topic_name }}
                </span>
                <span v-else class="association-tag none">-</span>
              </td>
              <td class="due-date-cell">
                <div v-if="task.due_date" class="due-date" :class="{ overdue: isOverdue(task) }">
                  <i class="bi bi-calendar-event"></i> {{ formatDate(task.due_date) }}
                </div>
                <span v-else class="no-date">-</span>
              </td>
              <td class="assigned-cell">
                <div v-if="task.assigned_to" class="assigned-to">
                  <i class="bi bi-person"></i> {{ task.assigned_to }}
                </div>
                <span v-else class="no-assignment">-</span>
              </td>
              <td class="actions-cell">
                <div class="task-actions">
                  <button @click="editTask(task)" class="btn btn-secondary btn-sm">
                    <i class="bi bi-pencil-square"></i> Edit
                  </button>
                  <button 
                    v-if="getNextStatus(task.status)"
                    @click="advanceStatus(task.id)" 
                    class="btn btn-sm"
                    :class="getStatusButtonClass(task.status)"
                  >
                    <i v-if="getStatusButtonIcon(task.status)" :class="getStatusButtonIcon(task.status)" class="me-1"></i>{{ getStatusButtonText(task.status) }}
                  </button>
                  <button 
                    v-if="isAdmin" 
                    @click="deleteTask(task)" 
                    class="btn btn-sm btn-danger"
                  >
                    <i class="bi bi-trash"></i> Delete
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Create/Edit Task Modal -->
  <div v-if="showCreateModal || showEditModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal large-modal" @click.stop>
        <div class="modal-header-row modal-header">
          <h2>{{ showCreateModal ? 'Create New Task' : 'Edit Task' }}</h2>
          <button @click="closeModal" class="plain-close close-btn">×</button>
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

          <div class="modal-footer modal-actions">
            <button type="button" @click="closeModal" class="btn btn-secondary cancel-btn">
              Cancel
            </button>
            <button type="submit" class="btn btn-primary save-btn">
              {{ showCreateModal ? 'Create Task' : 'Update Task' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import CompactToolbar from '../components/CompactToolbar.vue'
import HelpIcon from '@/components/HelpIcon.vue'
import IconPlus from '@/components/icons/IconPlus.vue'
import { toast } from '@/composables/useToast'
import { apiDelete, apiGet, apiPost, apiPut } from '@/api/base'

export default {
  name: 'TasksView',
  components: { CompactToolbar, HelpIcon, IconPlus },
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
      
      // Task summary is now computed from this.tasks (see taskMetrics computed property)
      
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
    taskMetrics() {
      const today = new Date()
      today.setHours(0, 0, 0, 0)
      return {
        total: this.tasks.length,
        todo: this.tasks.filter(t => t.status === 'todo').length,
        in_progress: this.tasks.filter(t => t.status === 'in_progress').length,
        review: this.tasks.filter(t => t.status === 'review').length,
        completed: this.tasks.filter(t => t.status === 'completed').length,
        overdue: this.tasks.filter(t =>
          t.due_date && new Date(t.due_date) < today && t.status !== 'completed'
        ).length
      }
    },
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
        const data = await apiGet('/api/tasks/')
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
        this.allStoredTags = await apiGet('/api/tasks/tags')
      } catch (error) {
        console.error('Error fetching tags:', error)
        this.allStoredTags = []
      }
    },
    
    async fetchAssociations() {
      try {
        this.availableAssociations = await apiGet('/api/tasks/associations')
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
        
        const result = this.showCreateModal
          ? await apiPost('/api/tasks/', taskData)
          : await apiPut(`/api/tasks/${this.taskForm.id}`, taskData)
        console.log('Task saved successfully:', result);

        if (result && result.task) {
          const savedTask = result.task;
          // Ensure tags are an array
          if (typeof savedTask.tags === 'string') {
            try {
              savedTask.tags = JSON.parse(savedTask.tags);
            } catch (e) {
              console.error('Error parsing tags on saved task:', e);
              savedTask.tags = [];
            }
          } else if (!Array.isArray(savedTask.tags)) {
            savedTask.tags = [];
          }

          if (this.showCreateModal) {
            // Add new task to the main list
            this.tasks.unshift(savedTask);
          } else {
            // Update existing task in the main list
            const index = this.tasks.findIndex(t => t.id === savedTask.id);
            if (index !== -1) {
              this.tasks.splice(index, 1, savedTask);
            } else {
              // If for some reason it wasn't in the list, add it
              this.tasks.unshift(savedTask);
            }
          }

          // Re-apply filters and update summary
          this.applyFilters();
          this.fetchTaskSummary();
          this.fetchAllTags();
          this.closeModal();
          toast.success(this.showCreateModal ? 'Task created.' : 'Task updated.')
        } else {
          // Fallback to refetching if the response format is not as expected
          await this.fetchTasks();
          await this.fetchTaskSummary();
          await this.fetchAllTags();
          this.closeModal();
          toast.success('Task saved.')
        }
        
      } catch (error) {
        console.error('Failed to save task:', error)
        this.error = 'Failed to save task. Please try again.'
        toast.error(this.error)
      }
    },
    
    async deleteTask(task) {
      if (!confirm(`Are you sure you want to delete "${task.title}"?`)) {
        return
      }
      
      try {
        await apiDelete(`/api/tasks/${task.id}`)
        
        // Refresh tasks
        await this.fetchTasks()
        await this.fetchTaskSummary()
  toast.success('Task deleted.')
        
      } catch (error) {
        console.error('Failed to delete task:', error)
        this.error = 'Failed to delete task. Please try again.'
  toast.error(this.error)
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
        
        await apiPut(`/api/tasks/${task.id}`, { status: nextStatus })
        
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
  toast.info('Task status updated.')
        
      } catch (error) {
        console.error('Failed to advance task status:', error)
        this.error = 'Failed to update task status. Please try again.'
  toast.error(this.error)
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
        'in_progress': 'btn-primary',
        'review': 'btn-warning', 
        'completed': 'btn-success'
      }
      return classMap[nextStatus] || 'advance-btn'
    },

    getStatusButtonIcon(currentStatus) {
      const nextStatus = this.getNextStatus(currentStatus)
      if (!nextStatus) return ''

      const iconMap = {
        'in_progress': 'bi bi-arrow-right-circle',
        'review': 'bi bi-chat-square-text',
        'completed': 'bi bi-check-circle'
      }
      return iconMap[nextStatus] || ''
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
    this.fetchAssociations()
    this.fetchAllTags()
  }
}
</script>

<style scoped>
/* Page Layout */
.tasks-page {
  max-width: 1600px;
  margin: 0 auto;
  padding: 0 2rem 2rem; /* remove top space before header */
  background-color: var(--bg-white);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--border-light-gray);
  text-align: center;
}

.page-header-content h1 {
  margin: 0;
  color: var(--primary-deep-teal);
  font-size: 2.5rem;
  font-weight: 300;
}

.page-header-content {
  flex: 1;
  text-align: center;
}

.header-actions {
  margin-right: 120px; /* Create space for CompactToolbar floating icons */
}

.page-description {
  margin: 0.5rem 0 0;
  color: var(--text-secondary-cool-gray);
  font-size: 1.1rem;
  text-align: center;
}

.primary-btn {
  background-color: var(--primary-deep-teal);
  color: var(--bg-white);
  padding: 0.75rem 1.5rem;
  border-radius: var(--border-radius-md);
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;
  border: none;
}

.primary-btn:hover {
  background-color: var(--primary-medium-teal);
}

/* Summary Cards */
.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.summary-card {
  background: var(--bg-white);
  border: 1px solid var(--border-light-gray);
  border-radius: var(--border-radius-lg);
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: var(--box-shadow-sm);
}

.summary-icon {
  font-size: 2rem;
  background-color: var(--bg-white);
  border-radius: 50%;
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.summary-content h3 {
  margin: 0 0 0.25rem;
  color: var(--text-medium-gray);
  font-size: 0.9rem;
  font-weight: 600;
  text-transform: uppercase;
}

.summary-number {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--text-dark-gray);
}

/* Metrics Grid (reuse global pattern) */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.summary-card.todo .summary-icon { background-color: var(--info-light-blue); color: var(--info-dark-blue); }
.summary-card.in-progress .summary-icon { background-color: var(--primary-light-blue); color: var(--primary-dark-blue); }
.summary-card.completed .summary-icon { background-color: var(--success-light-green); color: var(--success-dark-green); }
.summary-card.overdue .summary-icon { background-color: var(--error-light-red); color: var(--error-dark-red); }

/* Filters */
.filters-section {
  background: var(--bg-white);
  padding: 1rem;
  border-radius: var(--border-radius-lg);
  margin-bottom: 2rem;
  border: 1px solid var(--border-light-gray);
  box-shadow: var(--box-shadow-sm);
}

.filter-row {
  display: flex;
  gap: 1rem;
  align-items: center;
  flex-wrap: wrap;
}

.search-box {
  position: relative;
  flex-grow: 1;
}

.search-input {
  width: 100%;
  padding: 0.75rem 1rem 0.75rem 2.5rem;
  border: 1px solid var(--border-light-gray);
  border-radius: var(--border-radius-md);
  font-size: 1rem;
}

.search-icon {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-light-gray);
}

.filter-select {
  padding: 0.75rem 1rem;
  border: 1px solid var(--border-light-gray);
  border-radius: var(--border-radius-md);
  background-color: var(--bg-white);
}

.clear-filters-btn {
  background: none;
  border: none;
  color: var(--error-coral-red);
  cursor: pointer;
  font-weight: 600;
}

/* Tasks Section */
.tasks-section {
  background: var(--bg-white);
  border-radius: var(--border-radius-lg);
  padding: 1.5rem;
  box-shadow: var(--box-shadow-sm);
}

/* Loading, Error, Empty States */
.loading-state, .error-state, .empty-state {
  text-align: center;
  padding: 4rem 2rem;
}
.loading-icon, .error-icon, .empty-icon { font-size: 3rem; margin-bottom: 1rem; }
.loading-state h3, .error-state h3, .empty-state h3 { color: var(--text-dark-gray); }
.loading-state p, .error-state p, .empty-state p { color: var(--text-medium-gray); }

/* Tasks Table */
.tasks-table-container {
  overflow-x: auto;
}

.tasks-table {
  min-width: 1000px;
}

.tasks-table th, .tasks-table td {
  padding: 1rem;
  border-bottom: 1px solid var(--border-light-gray);
}

.tasks-table th {
  background-color: var(--bg-white);
  font-weight: 600;
  color: var(--text-dark-gray);
}

.task-row.overdue {
  background-color: var(--error-light-red);
}

.task-title {
  font-weight: 400;
  color: var(--text-dark-gray);
}

.task-description {
  font-size: 0.9rem;
  color: var(--text-medium-gray);
}

.status-badge, .priority-badge {
  padding: 0.25rem 0.75rem;
  border-radius: var(--border-radius-pill);
  font-size: 0.8rem;
  font-weight: 400;
  text-transform: capitalize;
}

.status-badge.todo { background-color: var(--info-light-blue); color: var(--info-dark-blue); }
.status-badge.in_progress { background-color: var(--primary-light-blue); color: var(--primary-dark-blue); }
.status-badge.review { background-color: var(--warning-light-yellow); color: var(--warning-dark-yellow); }
.status-badge.completed { background-color: var(--success-light-green); color: var(--success-dark-green); }
.status-badge.cancelled { background-color: var(--secondary-light-gray); color: var(--secondary-dark-gray); }

.priority-badge.low { background-color: var(--info-light-blue); color: var(--info-dark-blue); }
.priority-badge.medium { background-color: var(--primary-light-blue); color: var(--primary-dark-blue); }
.priority-badge.high { background-color: var(--warning-light-yellow); color: var(--warning-dark-yellow); }
.priority-badge.urgent { background-color: var(--error-light-red); color: var(--error-dark-red); }

.association-tag {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.25rem 0.5rem;
  border-radius: var(--border-radius-sm);
  font-size: 0.8rem;
}
.association-tag.project { background-color: #e0e7ff; color: #3730a3; }
.association-tag.collection { background-color: #d1fae5; color: #065f46; }
.association-tag.topic { background-color: #fef3c7; color: #92400e; }

.due-date-cell {
  font-size: 0.9rem;
}

.due-date.overdue {
  color: var(--error-dark-red);
  font-weight: 500;
}

.task-actions {
  display: flex;
  gap: 0.5rem;
}

/* Status advance buttons use global button system from assets/style.css */

/* Modal Styles */
/* Using global .modal-overlay and .modal styles from assets/style.css */

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid var(--border-light-gray);
}

.modal-header h2 { margin: 0; color: var(--text-dark-gray); }
.close-btn { background: none; border: none; font-size: 1.5rem; cursor: pointer; color: var(--text-light-gray); }

.modal-body { padding: 1.5rem; }
.form-section { margin-bottom: 2rem; }
.form-section h3 { margin-bottom: 1rem; color: var(--text-dark-gray); }
.form-group { margin-bottom: 1rem; }
.form-group label { display: block; margin-bottom: 0.5rem; font-weight: 600; color: var(--text-dark-gray); }
.form-input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid var(--border-light-gray);
  border-radius: var(--border-radius-md);
  font-size: 1rem;
}
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }

.association-selector { display: flex; gap: 1rem; margin-bottom: 1rem; }
.association-type { display: flex; align-items: center; gap: 0.5rem; }

.tags-input { margin-top: 1rem; }
.tags-list { margin-top: 1rem; }
.tags-display { display: flex; flex-wrap: wrap; gap: 0.5rem; }
.tag {
  background-color: var(--primary-light-blue);
  color: var(--primary-dark-blue);
  padding: 0.25rem 0.75rem;
  border-radius: var(--border-radius-pill);
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.tag-remove { background: none; border: none; cursor: pointer; }

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--border-light-gray);
}

.cancel-btn { background-color: var(--secondary-light-gray); color: var(--text-dark-gray); }
.save-btn { background-color: var(--primary-deep-teal); color: var(--bg-white); }

/* Responsive adjustments for CompactToolbar overlap */
@media (max-width: 768px) {
  .header-actions {
    margin-right: 70px; /* Smaller margin on mobile as toolbar icons are smaller */
  }
}

@media (max-width: 480px) {
  .header-actions {
    margin-right: 60px; /* Even smaller margin on very small screens */
  }
}
</style>
