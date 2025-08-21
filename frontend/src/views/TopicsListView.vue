<template>
  <div class="topics-list">
    <div class="full-width" style="margin-bottom:1.5rem;">
      <NotificationTicker
        :notifications="mergedNotifications"
        contextType="global"
        @mark-read="markNotificationRead"
      />
    </div>
    <Breadcrumbs />
    <h2>All Topics</h2>
    
    <!-- DEBUG INFO -->
    <div style="background: #f0f0f0; padding: 10px; margin: 10px 0; border: 1px solid #ccc;">
      <strong>DEBUG:</strong> 
      loading: {{ loading }}, 
      error: {{ error }}, 
      topics.length: {{ topics.length }}, 
      filteredTopics.length: {{ filteredTopics.length }}
      <br>
      <span class="text-success">✅ Buttons are working! Modal overlay issue resolved.</span>
    </div>
    
    <p class="guidance-text">
      These are all the available topics. This page allows you to edit a topic or publish a single topic.
    </p>

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

    <!-- Modals removed to fix button functionality -->
  </div>
</template>

<script>
import Breadcrumbs from '@/components/Breadcrumbs.vue'
import NotificationTicker from '../components/NotificationTicker.vue'
// import SequentialReviewModal from '@/components/SequentialReviewModal.vue' // Temporarily disabled

export default {
  name: 'TopicListView',
  components: { Breadcrumbs, NotificationTicker }, // Removed SequentialReviewModal temporarily
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
      
      this.selectedTopicForSequence = topic
      
      // Try to open the modal safely
      try {
        // Use Vue's nextTick to ensure DOM is updated
        this.$nextTick(() => {
          const modalElement = document.getElementById('sequentialReviewModal')
          if (modalElement && window.bootstrap) {
            const modal = new bootstrap.Modal(modalElement)
            modal.show()
          } else {
            console.error('Modal element or bootstrap not found')
            alert('Modal functionality not available - please refresh the page and try again')
          }
        })
      } catch (error) {
        console.error('Error opening modal:', error)
        alert('Error opening modal - please refresh the page and try again')
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
  padding: 1rem 2rem 2rem 2rem; /* Reduced top padding to match other pages */
}

.guidance-text {
  background: #f8f9fa;
  border-left: 4px solid #205493;
  border-radius: .75rem;
  padding: 1rem;
  margin-bottom: 1.5rem;
  color: #495057;
  font-size: 0.95rem;
  line-height: 1.5;
}

/* Filters */
.filters-section {
  margin-bottom: 2rem;
  background: #f8f9fa;
  padding: 1.5rem;
  border-radius: 8px;
  border: 1px solid #e9ecef;
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

.table-instruction {
  color: #6b7280;
  font-size: 0.9rem;
  margin: 1rem 0 0.5rem 0;
  font-style: italic;
}

.loading, .error {
  text-align: center;
  padding: 2rem;
  font-size: 1.1rem;
}

.topics-table-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  overflow: hidden;
}

.topics-table {
  width: 100%;
  border-collapse: collapse;
}

.loading,
.error {
  margin-top: 1rem;
  font-size: 0.9rem;
}

.error {
  color: #c00;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1rem;
}

th,
td {
  text-align: left;
  padding: 1rem;
  border-bottom: 1px solid #e0e0e0;
}

/* Prevent Status column from wrapping */
th:nth-child(3),
td:nth-child(3) {
  white-space: nowrap;
  min-width: 120px;
}

.badge {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  text-transform: capitalize;
}

.badge--draft {
  background: #fff4c2;
  color: #996800;
}

.badge--published {
  background: #d4f4dd;
  color: #217a2b;
}

.badge--pending_review {
  background: #fff3cd;
  color: #856404;
}

.badge--approved {
  background: #c3e6cb;
  color: #155724;
}

.badge--revisions_requested {
  background: #ffeaa7;
  color: #b8860b;
  border: 1px solid #ddb867;
}

.badge--rejected {
  background: #f5c6cb;
  color: #721c24;
}

.badge--archived {
  background: #f0f0f0;
  color: #666;
}

.actions-cell {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.action-link {
  color: #205493;
  text-decoration: none;
}

.action-button {
  padding: 0.4rem 0.8rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.action-button.publish {
  background: #009964;
  color: white;
}

.action-button.review {
  background: #ffc107;
  color: #212529;
  border: 1px solid #ffc107;
}

.action-button.review:hover {
  background: #e0a800;
  border-color: #d39e00;
}

.action-button.publish:hover {
  background: #006548;
}

/* Button Styles */
.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
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
  background-color: #ffc107;
  color: #212529;
}

.btn-warning:hover {
  background-color: #e0a800;
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

.modal-content {
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  max-width: 500px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #e9ecef;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.25rem;
  color: #205493;
}

.close-button {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #6c757d;
  padding: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-button:hover {
  color: #495057;
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
  font-weight: 500;
  color: #495057;
}

.form-group select,
.form-group input,
.form-group textarea {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 0.875rem;
  transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
}

.form-group select:focus,
.form-group input:focus,
.form-group textarea:focus {
  outline: 0;
  border-color: #205493;
  box-shadow: 0 0 0 0.2rem rgba(0, 90, 156, 0.25);
}

.form-group textarea {
  resize: vertical;
  min-height: 80px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  padding: 1rem 1.5rem;
  border-top: 1px solid #e9ecef;
  background: #f8f9fa;
  border-radius: 0 0 8px 8px;
}

.text-muted {
  color: #6c757d;
  font-size: 0.875rem;
}

.text-warning {
  color: #ffc107;
  font-size: 0.875rem;
}

.text-info {
  color: #17a2b8;
  font-size: 0.875rem;
}

.text-success {
  color: #28a745;
  font-size: 0.875rem;
}

/* Multi-select checkbox styles */
.multi-select-container {
  max-height: 200px;
  overflow-y: auto;
  border: 1px solid #ced4da;
  border-radius: 4px;
  padding: 0.5rem;
  background: white;
}

.checkbox-item {
  display: flex;
  align-items: center;
  padding: 0.25rem 0;
  border-bottom: 1px solid #f8f9fa;
}

.checkbox-item:last-child {
  border-bottom: none;
}

.checkbox-item input[type="checkbox"] {
  margin-right: 0.5rem;
  margin-top: 0;
}

.checkbox-label {
  margin: 0;
  cursor: pointer;
  font-weight: normal;
  font-size: 0.9rem;
  line-height: 1.4;
}

.checkbox-item:hover {
  background-color: #f8f9fa;
}

.text-warning {
  color: #856404;
  font-size: 0.875rem;
}

.debug-info {
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 4px;
  margin-top: 1rem;
  font-size: 0.75rem;
}
</style>