<template>
  <div class="topics-list">
    <NotificationTicker
      :notifications="mergedNotifications"
      contextType="global"
      @mark-read="markNotificationRead"
    />
    <Breadcrumbs />
    <h2>All Topics</h2>
    
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
              <option value="in_review">In Review</option>
              <option value="published">Published</option>
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
            <button @click="clearFilters" class="btn btn-secondary btn-sm">Clear Filters</button>
          </div>
        </div>
      </div>

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
              {{ t.status }}
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
            >
              <i class="fas fa-eye"></i> Review
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

    <!-- Review Submission Modal -->
    <div v-if="showReviewModal" class="modal-overlay" @click="closeReviewModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Submit "{{ selectedTopic?.title }}" for Review</h3>
          <button @click="closeReviewModal" class="close-button">&times;</button>
        </div>
        
        <div class="modal-body">
          <div class="form-group">
            <label for="project-select">Project:</label>
            <select id="project-select" v-model="reviewData.project_id" @change="onProjectChange" required>
              <option value="">Select a project...</option>
              <option v-for="project in availableProjects" :key="project.id" :value="project.id">
                {{ project.name }}
              </option>
            </select>
          </div>

          <div class="form-group" v-if="reviewData.project_id">
            <label for="reviewer-select">Assign to Reviewer:</label>
            <select id="reviewer-select" v-model="reviewData.assigned_stakeholder_id" required>
              <option value="">Select a reviewer...</option>
              <option 
                v-for="stakeholder in projectStakeholders" 
                :key="stakeholder.id" 
                :value="stakeholder.id"
                v-if="stakeholder.can_review !== false"
              >
                {{ stakeholder.name }} ({{ stakeholder.role || 'Stakeholder' }})
              </option>
            </select>
            <small v-if="projectStakeholders.length === 0" class="text-muted">
              Loading stakeholders...
            </small>
            <small v-else-if="projectStakeholders.filter(s => s.can_review !== false).length === 0" class="text-warning">
              No stakeholders with review permissions found for this project.
            </small>
          </div>

          <div class="form-group">
            <label for="due-date">Due by close-of-business:</label>
            <input 
              id="due-date" 
              type="date" 
              v-model="reviewData.due_date" 
              :min="todayDate"
              required
            />
          </div>

          <div class="form-group">
            <label for="review-notes">Notes to the reviewer (optional):</label>
            <textarea 
              id="review-notes" 
              v-model="reviewData.submitter_notes" 
              rows="4" 
              placeholder="Add any specific instructions or context for the reviewer..."
            ></textarea>
          </div>

          <!-- Debug information (remove in production) -->
          <div class="debug-info" style="background: #f8f9fa; padding: 1rem; border-radius: 4px; margin-top: 1rem; font-size: 0.75rem;">
            <strong>Form Status:</strong><br>
            Project ID: {{ reviewData.project_id || 'Not selected' }}<br>
            Stakeholder ID: {{ reviewData.assigned_stakeholder_id || 'Not selected' }}<br>
            Due Date: {{ reviewData.due_date || 'Not set' }}<br>
            Available Stakeholders: {{ projectStakeholders.length }}<br>
            Reviewable Stakeholders: {{ projectStakeholders.filter(s => s.can_review !== false).length }}<br>
            Form Valid: {{ !!(reviewData.project_id && reviewData.assigned_stakeholder_id && reviewData.due_date) }}
          </div>
        </div>

        <div class="modal-footer">
          <button @click="closeReviewModal" class="btn btn-secondary">Cancel</button>
          <button @click="confirmSubmitForReview" class="btn btn-primary" :disabled="!reviewData.project_id || !reviewData.assigned_stakeholder_id || !reviewData.due_date">
            Submit for Review
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Breadcrumbs from '@/components/Breadcrumbs.vue'
import NotificationTicker from '../components/NotificationTicker.vue'

export default {
  name: 'TopicListView',
  components: { Breadcrumbs, NotificationTicker },
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
      topics: [],
      filteredTopics: [],
      searchQuery: '',
      statusFilter: '',
      collectionFilter: '',
      loading: true,
      error: null,
      showReviewModal: false,
      selectedTopic: null,
      availableReviewers: [],
      availableProjects: [],
      projectStakeholders: [],
      reviewData: {
        project_id: '',
        assigned_stakeholder_id: '',
        due_date: '',
        submitter_notes: ''
      }
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
        console.error(err)
        this.error = 'Failed to load topics'
      } finally {
        this.loading = false
      }
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
        this.projectStakeholders = await res.json()
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
        this.reviewData.assigned_stakeholder_id = ''
      } else {
        this.projectStakeholders = []
      }
      console.log('Project stakeholders after change:', this.projectStakeholders)
    },

    async publish(id) {
      try {
        const res = await fetch(`/api/topics/${id}/publish`, {
          method: 'POST'
        })
        if (!res.ok) throw new Error(`Publish failed (${res.status})`)
        await this.fetchTopics()
      } catch (err) {
        console.error(err)
        this.error = 'Publish action failed'
      }
    },

    async submitForReview(id) {
      // Find the topic and open the modal
      const topic = this.topics.find(t => t.id === id)
      if (!topic) {
        alert('Topic not found')
        return
      }

      this.selectedTopic = topic
      this.showReviewModal = true
      
      // Reset form data
      this.reviewData = {
        project_id: '',
        assigned_stakeholder_id: '',
        due_date: '',
        submitter_notes: ''
      }
      
      // Clear project stakeholders
      this.projectStakeholders = []
    },

    closeReviewModal() {
      this.showReviewModal = false
      this.selectedTopic = null
    },

    async confirmSubmitForReview() {
      try {
        if (!this.selectedTopic || !this.reviewData.project_id) return

        // Submit review to project-based endpoint
        const reviewPayload = {
          topic_id: this.selectedTopic.id,
          assigned_stakeholder_id: this.reviewData.assigned_stakeholder_id,
          due_date: this.reviewData.due_date,
          submitter_notes: this.reviewData.submitter_notes
        }

        const res = await fetch(`/api/projects/${this.reviewData.project_id}/reviews`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(reviewPayload)
        })

        if (!res.ok) throw new Error(`Submit for review failed (${res.status})`)

        // Close modal and refresh topics
        this.closeReviewModal()
        await this.fetchTopics()
        
        alert(`"${this.selectedTopic.title}" has been submitted for review successfully!`)

      } catch (err) {
        console.error('Submit for review failed:', err)
        alert('Failed to submit topic for review. Please try again.')
      }
    }
  }
}
</script>

<style scoped>
.topics-list {
  padding: 70px 2rem 2rem 2rem; /* Top padding to account for fixed header */
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