<template>
  <div class="topics-list">
    
    <div class="dashboard-header">
      <h1>All Topics</h1>
      <p class="subtitle">Browse, review, and manage topics</p>
    </div>
    <div v-if="loading" class="loading">Loading…</div>
    <div v-else-if="error" class="error">{{ error }}</div>

    <div v-else class="topics-content">
      <!-- Filters -->
      <div class="filters-section">
        <div class="filter-row">
          <div class="filter-group">
            <label>Search:</label>
            <input
              v-model="searchQuery"
              type="text"
              class="filter-input"
              placeholder="Search topics..."
              @input="applyFilters"
            />
          </div>
          <div class="filter-group">
            <label>Status:</label>
            <select v-model="statusFilter" @change="applyFilters" class="filter-input">
              <option value="">All Statuses</option>
              <option value="draft">Draft</option>
              <option value="pending_review">Pending Review</option>
              <option value="approved">Approved</option>
              <option value="revisions_requested">Revisions Requested</option>
              <option value="published">Published</option>
              <option value="rejected">Rejected</option>
              <option value="archived">Archived</option>
            </select>
          </div>
          <div class="filter-group">
            <label>Collection:</label>
            <select v-model="collectionFilter" @change="applyFilters" class="filter-input">
              <option value="">All Collections</option>
              <option v-for="collection in uniqueCollections" :key="collection" :value="collection">{{ collection }}</option>
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

      <p class="table-instruction">Select a topic to edit.</p>

      <div class="topics-table-container">
        <table class="topics-table">
      <thead>
        <tr>
          <th>ID</th>
          <th>Title</th>
          <th>Status</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="t in filteredTopics" :key="t.id">
          <td>{{ t.id }}</td>
          <td>{{ t.title }}</td>
          <td>
            <span :class="`badge badge--${t.status}`">
              {{ formatStatus(t.status) }}
            </span>
          </td>
          <td class="actions-cell">
            <router-link
              :to="{ name: 'EditTopic', params: { id: t.id } }"
              class="btn btn-sm btn-secondary"
            >
              <i class="fas fa-edit"></i> Edit
            </router-link>

            <button
              v-if="t.status === 'draft'"
              @click="submitForReview(t.id)"
              class="btn btn-sm btn-warning"
              style="position: relative; z-index: 10;"
              title="Click to submit for review"
            >
              <i class="fas fa-eye"></i> Review
            </button>

            <button
              v-if="t.status === 'draft'"
              @click="openSequentialReview(t)"
              class="btn btn-sm btn-info"
              title="Set up a sequential review workflow where expert reviewer goes first, then others see the improved version"
            >
              <i class="bi bi-arrow-right-circle"></i> Sequential Review
            </button>

            <button
              v-if="t.status === 'draft'"
              @click="publish(t.id)"
              class="btn btn-sm btn-success"
            >
              <i class="fas fa-share"></i> Publish
            </button>
          </td>
        </tr>
      </tbody>
    </table>
      </div>
    </div>

    <!-- Sequential Review Modal - Using Vue reactivity instead of Bootstrap modal events -->
    <SequentialReviewModal
      v-if="showSequentialModal"
      :topic="selectedTopicForSequence"
      :availableReviewers="availableReviewers"
      :availableProjects="availableProjects"
      @sequence-created="onSequenceCreated"
      @close="closeSequentialModal"
    />
  </div>
</template>

<script>
import SequentialReviewModal from '@/components/SequentialReviewModal.vue'

export default {
  name: 'TopicListView',
  components: { SequentialReviewModal },
  props: {
    globalNotifications: {
      type: Array,
      default: () => []
    },
    markNotificationRead: {
      type: Function,
      default: () => {}
    }
  },

  data() {
    return {
      topics: [],
      filteredTopics: [],
      searchQuery: '',
      statusFilter: '',
      collectionFilter: '',
      loading: true,
      error: null,
      showReviewModal: false,
      showSequentialModal: false,
      selectedTopic: null,
      selectedTopicForSequence: null,
      availableReviewers: [],
      availableProjects: [],
      projectStakeholders: [],
      reviewData: {
        project_id: '',
        assigned_stakeholder_ids: [],  // Changed to array for multiple selection
        isSequential: false,  // New property for sequential review option
        due_date: (() => {
          const d = new Date();
          d.setDate(d.getDate() + 7);
          return d.toISOString().split('T')[0];
        })(),
        submitter_notes: ''
      }
    }
  },

  computed: {
    // Safe stakeholders for template rendering
    safeProjectStakeholders() {
      const projectStakeholders = (this.projectStakeholders || []).filter(s => s && s.id && s.name && s.can_review !== false)
      
      // If project has specific stakeholders with review permissions, use them
      if (projectStakeholders.length > 0) {
        return projectStakeholders
      }
      
      // Otherwise, fall back to general reviewers if project is selected but has no stakeholders
      if (this.reviewData.project_id && this.availableReviewers.length > 0) {
        return (this.availableReviewers || []).filter(s => s && s.id && s.name).map(reviewer => ({
          ...reviewer,
          can_review: true // Mark general reviewers as able to review
        }))
      }
      
      return []
    },

    mergedNotifications() {
      // Use global notifications since we only have globalNotifications prop now
      return (this.globalNotifications || []).filter(n => n && n.id)
    },

    uniqueCollections() {
      const collections = [...new Set(this.topics.map(t => t.collection_name).filter(col => col))]
      return collections.sort()
    },
    todayDate() {
      const today = new Date()
      return today.toISOString().split('T')[0]
    }
  },

  created() {
    // Force reset modal states to prevent blocking overlay
    this.showReviewModal = false
    this.selectedTopicForSequence = null
    
    // Initialize data loading
    this.fetchTopics()
    this.fetchProjects()
    this.fetchReviewers()
  },

  methods: {
    async fetchTopics() {
      this.loading = true
      this.error = null

      try {
        const res = await fetch('/api/topics/')
        if (!res.ok) throw new Error(`Status ${res.status}`)
        this.topics = await res.json()
        this.applyFilters() // Initialize filtered data
      } catch (err) {
        console.error('API fetch failed, using sample data:', err)
        // Provide mock data when backend is unavailable
        this.topics = [
          {
            id: 1,
            title: 'Sample Topic 1',
            status: 'draft',
            summary: 'This is a sample topic for testing',
            collection_name: 'Test Collection'
          },
          {
            id: 2,
            title: 'Sample Topic 2',
            status: 'pending_review',
            summary: 'Another sample topic',
            collection_name: 'Test Collection'
          },
          {
            id: 3,
            title: 'Sample Topic 3',
            status: 'approved',
            summary: 'Final sample topic',
            collection_name: 'Sample Collection'
          }
        ]
        this.applyFilters()
        this.error = 'Using sample data - backend unavailable'
      } finally {
        this.loading = false
      }
    },

    formatStatus(status) {
      // Convert status like "pending_review" to "Pending review"
      return status
        .split('_')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ')
    },

    applyFilters() {
      let filtered = [...this.topics]
      
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase()
        filtered = filtered.filter(topic => 
          topic.title.toLowerCase().includes(query) ||
          (topic.summary && topic.summary.toLowerCase().includes(query)) ||
          (topic.collection_name && topic.collection_name.toLowerCase().includes(query))
        )
      }
      
      if (this.statusFilter) {
        filtered = filtered.filter(topic => topic.status === this.statusFilter)
      }
      
      if (this.collectionFilter) {
        filtered = filtered.filter(topic => topic.collection_name === this.collectionFilter)
      }
      
      this.filteredTopics = filtered
    },
    
    clearFilters() {
      this.searchQuery = ''
      this.statusFilter = ''
      this.collectionFilter = ''
      this.applyFilters()
    },

    async fetchReviewers() {
      try {
        const res = await fetch('/api/reviews/reviewers')
        if (!res.ok) throw new Error(`Status ${res.status}`)
        this.availableReviewers = await res.json()
      } catch (err) {
        console.error('Failed to fetch reviewers:', err)
        // Set fallback reviewers if API fails
        this.availableReviewers = [
          { id: 1, name: 'Default Reviewer', email: 'reviewer@census.gov' }
        ]
      }
    },

    async fetchProjects() {
      try {
        const res = await fetch('/api/projects/')
        if (!res.ok) throw new Error(`Status ${res.status}`)
        this.availableProjects = await res.json()
      } catch (err) {
        console.error('Failed to fetch projects:', err)
        this.availableProjects = []
      }
    },

    async fetchProjectStakeholders(projectId) {
      try {
        console.log('Fetching stakeholders for project:', projectId)
        const res = await fetch(`/api/projects/${projectId}/stakeholders`)
        if (!res.ok) throw new Error(`Status ${res.status}`)
        const stakeholders = await res.json()
        // Filter out any invalid stakeholder objects
        this.projectStakeholders = (stakeholders || []).filter(s => s && s.id && s.name)
        console.log('Loaded stakeholders:', this.projectStakeholders)
      } catch (err) {
        console.error('Failed to fetch project stakeholders:', err)
        this.projectStakeholders = []
      }
    },

    async onProjectChange() {
      console.log('Project changed to:', this.reviewData.project_id)
      if (this.reviewData.project_id) {
        await this.fetchProjectStakeholders(this.reviewData.project_id)
        // Reset stakeholder selection when project changes
        this.reviewData.assigned_stakeholder_ids = []
      } else {
        this.projectStakeholders = []
        this.reviewData.assigned_stakeholder_ids = []
      }
      console.log('Project stakeholders after change:', this.projectStakeholders)
    },

    async publish(id) {
      console.log('🔥 publish called with ID:', id)
      alert(`Publish clicked! Topic ID: ${id}`)
      
      try {
        const res = await fetch(`/api/topics/${id}/publish`, {
          method: 'POST'
        })
        if (!res.ok) throw new Error(`Publish failed (${res.status})`)
        await this.fetchTopics()
        alert('Topic published successfully!')
      } catch (err) {
        console.error(err)
        this.error = 'Publish action failed'
        alert('Publish failed - backend not available')
      }
    },

    async submitForReview(id) {
      console.log('🔥 submitForReview called with ID:', id)
      alert(`Submit for review clicked! Topic ID: ${id}`)
      
      // Find the topic and open the modal
      const topic = this.topics.find(t => t.id === id)
      if (!topic) {
        alert('Topic not found')
        return
      }

      this.selectedTopic = topic
      this.showReviewModal = true
      
      // Reset form data with default due date (7 days from now)
      const defaultDueDate = new Date()
      defaultDueDate.setDate(defaultDueDate.getDate() + 7)
      
      this.reviewData = {
        project_id: '',
        assigned_stakeholder_ids: [],
        due_date: defaultDueDate.toISOString().split('T')[0],
        submitter_notes: ''
      }
      
      // Clear project stakeholders
      this.projectStakeholders = []
    },

    closeReviewModal() {
      this.showReviewModal = false
      this.selectedTopic = null
      this.selectedTopicForSequence = null  // Also clear sequential review state
      // Reset form data
      this.reviewData = {
        project_id: '',
        assigned_stakeholder_ids: [],
        isSequential: false,
        due_date: '',
        submitter_notes: ''
      }
      this.projectStakeholders = []
    },

    async confirmSubmitForReview() {
      try {
        console.log('Starting review submission...')
        console.log('Selected topic:', this.selectedTopic)
        console.log('Review data:', this.reviewData)
        
        if (!this.selectedTopic || !this.reviewData.project_id || this.reviewData.assigned_stakeholder_ids.length === 0) {
          console.error('Validation failed:', {
            selectedTopic: !!this.selectedTopic,
            project_id: this.reviewData.project_id,
            stakeholder_ids: this.reviewData.assigned_stakeholder_ids
          })
          return
        }

        // Check if sequential review was requested
        if (this.reviewData.isSequential && this.reviewData.assigned_stakeholder_ids.length > 1) {
          console.log('Creating sequential review...')
          
          // Create sequential review
          const sequencePayload = {
            topic_id: this.selectedTopic.id,
            created_by: 1, // TODO: Get current user ID from auth context
            name: `Review Sequence for ${this.selectedTopic.title}`,
            description: 'Expert-first sequential review workflow',
            initial_message: this.reviewData.submitter_notes || `Please review "${this.selectedTopic.title}" for technical accuracy and clarity.`,
            priority: 'medium',
            reviewers: this.reviewData.assigned_stakeholder_ids.map((stakeholderId, index) => ({
              reviewer_id: stakeholderId,
              step_name: index === 0 ? 'Expert Review' : `Review Step ${index + 1}`,
              instructions: index === 0 ? 'Focus on technical accuracy and completeness' : 'Focus on clarity and readability after technical improvements'
            })),
            auto_advance_on_approve: true,
            pause_on_changes: true,
            auto_start: true
          }

          console.log('Sending sequential review request:', sequencePayload)

          const res = await fetch('/api/sequences/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(sequencePayload)
          })

          if (!res.ok) {
            const errorData = await res.json()
            console.error('Sequential review request failed:', errorData)
            throw new Error(`Sequential review request failed: ${errorData.error || res.status}`)
          }

          const result = await res.json()
          console.log('Sequential review created:', result)
          
          // Store topic title before closing modal
          const topicTitle = this.selectedTopic.title
          
          // Close modal and refresh topics
          this.closeReviewModal()
          await this.fetchTopics()
          
          alert(`"${topicTitle}" has been submitted for sequential review! First reviewer has been notified.`)
          
        } else {
          // Regular parallel review process
          console.log('Creating regular review requests for stakeholders:', this.reviewData.assigned_stakeholder_ids)

          // Create multiple review requests - one for each selected reviewer
          const reviewPromises = this.reviewData.assigned_stakeholder_ids.map(async (stakeholderId) => {
            const reviewPayload = {
              topic_id: this.selectedTopic.id,
              reviewer_id: stakeholderId,
              requested_by: 1, // TODO: Get current user ID from auth context
              priority: 'medium',
              due_date: this.reviewData.due_date,
              message: this.reviewData.submitter_notes || `Review requested for: ${this.selectedTopic.title}`
            }

            console.log('Sending review request:', reviewPayload)

            const res = await fetch('/api/reviews/request', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify(reviewPayload)
            })

            console.log('Review request response status:', res.status)

            if (!res.ok) {
              const errorData = await res.json()
              console.error('Review request failed:', errorData)
              throw new Error(`Review request failed: ${errorData.error || res.status}`)
            }

            return await res.json()
          })

          // Wait for all review requests to complete
          console.log('Waiting for all review requests to complete...')
          const results = await Promise.all(reviewPromises)
          console.log('All review requests completed:', results)
          
          // Store topic title before closing modal (which sets selectedTopic to null)
          const topicTitle = this.selectedTopic.title
          const reviewerCount = this.reviewData.assigned_stakeholder_ids.length
          
          // Close modal and refresh topics
          this.closeReviewModal()
          await this.fetchTopics()
          
          alert(`"${topicTitle}" has been submitted for review to ${reviewerCount} reviewer(s) successfully!`)
        }

      } catch (err) {
        console.error('Submit for review failed:', err)
        alert('Failed to submit topic for review. Please try again.')
      }
    },

    openSequentialReview(topic) {
      console.log('🔥 openSequentialReview called with topic:', topic)
      
      // Use Vue reactivity instead of Bootstrap modal to avoid overlay issues
      this.selectedTopicForSequence = topic
      this.showSequentialModal = true
    },

    closeSequentialModal() {
      this.showSequentialModal = false
      this.selectedTopicForSequence = null
    },

    fallbackSequentialReview(topic) {
      const confirmed = confirm(
        `Set up Sequential Review for "${topic.title}"?\n\n` +
        `This will create a multi-stage review process where:\n` +
        `1. Expert reviewer reviews first\n` +
        `2. Other reviewers see the improved version\n\n` +
        `Click OK to proceed or Cancel to abort.`
      )
      
      if (confirmed) {
        this.createSequentialReview(topic)
      }
    },

    async createSequentialReview(topic) {
      try {
        console.log('Creating sequential review for topic:', topic.id)
        
        // Simple implementation - just submit for regular review for now
        // TODO: Implement full sequential review logic
        await this.submitForReview(topic.id)
        
        alert(`Sequential review process started for "${topic.title}".\n\nNote: This is a simplified implementation. Full sequential review features will be restored in a future update.`)
      } catch (error) {
        console.error('Error creating sequential review:', error)
        alert('Error creating sequential review - please try again')
      }
    },

    onSequenceCreated(sequence) {
      console.log('Sequence created:', sequence)
      
      // Refresh topics to update status
      this.fetchTopics()
      
      // Show success message
      alert(`Sequential review created for "${sequence.topic_title}"! First reviewer has been notified.`)
    }
  }
}
</script>

<style scoped>
.topics-list {
  padding: 2rem;
  background-color: var(--bg-light-gray);
}

.guidance-text {
  background: var(--info-light-blue);
  border-left: 4px solid var(--primary-deep-teal);
  border-radius: var(--border-radius-lg);
  padding: 1rem 1.5rem;
  margin-bottom: 1.5rem;
  color: var(--text-dark-gray);
  font-size: 0.95rem;
  line-height: 1.5;
}

/* Filters */
.filters-section {
  margin-bottom: 2rem;
  background: var(--bg-white);
  padding: 1.5rem;
  border-radius: var(--border-radius-lg);
  border: 1px solid var(--border-light-gray);
  box-shadow: var(--box-shadow-sm);
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
  color: var(--text-dark-gray);
  font-size: 0.9rem;
}

.filter-input {
  padding: 0.75rem;
  border: 1px solid var(--border-light-gray);
  border-radius: var(--border-radius-md);
  font-size: 0.9rem;
  background: var(--bg-white);
}

.filter-input:focus {
  outline: none;
  border-color: var(--primary-deep-teal);
  box-shadow: 0 0 0 2px rgba(32, 84, 147, 0.1);
}

.button-group {
  display: flex;
  gap: 0.5rem;
}

.table-instruction {
  color: var(--text-medium-gray);
  font-size: 0.9rem;
  margin: 1rem 0 0.5rem 0;
  font-style: italic;
}

.loading, .error {
  text-align: center;
  padding: 2rem;
  font-size: 1.1rem;
  background-color: var(--bg-white);
  border-radius: var(--border-radius-lg);
}

.error {
  color: var(--error-coral-red);
}

.topics-table-container {
  background: var(--bg-white);
  border-radius: var(--border-radius-lg);
  box-shadow: var(--box-shadow-sm);
  overflow: hidden;
}

.topics-table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  text-align: left;
  padding: 1rem;
  border-bottom: 1px solid var(--border-light-gray);
}

th {
  background-color: var(--bg-light-mist-gray);
}

th:nth-child(3),
td:nth-child(3) {
  white-space: nowrap;
  min-width: 120px;
}

.badge {
  padding: 0.25rem 0.75rem;
  border-radius: var(--border-radius-pill);
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: capitalize;
}

.badge--draft { background: var(--secondary-light-gray); color: var(--secondary-dark-gray); }
.badge--published { background: var(--success-light-green); color: var(--success-dark-green); }
.badge--pending_review { background: var(--warning-light-yellow); color: var(--warning-dark-yellow); }
.badge--approved { background: var(--success-light-green); color: var(--success-dark-green); }
.badge--revisions_requested { background: var(--warning-light-yellow); color: var(--warning-dark-yellow); }
.badge--rejected { background: var(--error-light-red); color: var(--error-dark-red); }
.badge--archived { background: var(--secondary-light-gray); color: var(--secondary-dark-gray); }

.actions-cell {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: var(--border-radius-md);
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

.btn-primary { background-color: var(--primary-deep-teal); color: var(--bg-white); }
.btn-primary:hover:not(:disabled) { background-color: var(--primary-dark-blue); }
.btn-secondary { background-color: var(--secondary-slate-gray); color: var(--bg-white); }
.btn-secondary:hover { background-color: var(--secondary-dark-gray); }
.btn-success { background-color: var(--success-dark-green); color: var(--bg-white); }
.btn-success:hover { background-color: #14532d; }
.btn-warning { background-color: var(--warning-dark-yellow); color: var(--bg-white); }
.btn-warning:hover { background-color: #78350f; }
.btn-danger { background-color: var(--error-coral-red); color: var(--bg-white); }
.btn-danger:hover { background-color: var(--error-dark-red); }
.btn-info { background-color: var(--info-dark-blue); color: var(--bg-white); }
.btn-info:hover { background-color: #1e40af; }

.btn-sm {
  padding: 0.375rem 0.75rem;
  font-size: 0.8rem;
}
</style>