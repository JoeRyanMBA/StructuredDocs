<template>
  <div class="topics-list">
    <Breadcrumbs />
    <h2>All Topics</h2>
    
    <p class="guidance-text">
      These are all the available topics. This page allows you to edit a topic or publish a single topic.
    </p>

    <div v-if="loading" class="loading">Loading…</div>
    <div v-else-if="error" class="error">{{ error }}</div>

    <table v-else>
      <thead>
        <tr>
          <th>ID</th>
          <th>Title</th>
          <th>Status</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="t in topics" :key="t.id">
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
              class="action-link"
            >
              Edit
            </router-link>

            <button
              v-if="t.status === 'draft'"
              @click="submitForReview(t.id)"
              class="action-button review"
            >
              Review
            </button>

            <button
              v-if="t.status === 'draft'"
              @click="publish(t.id)"
              class="action-button publish"
            >
              Publish
            </button>
          </td>
        </tr>
      </tbody>
    </table>

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

export default {
  name: 'TopicListView',
  components: { Breadcrumbs },

  data() {
    return {
      topics: [],
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
      } catch (err) {
        console.error(err)
        this.error = 'Failed to load topics'
      } finally {
        this.loading = false
      }
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
        const res = await fetch(`/api/projects/${projectId}/stakeholders`)
        if (!res.ok) throw new Error(`Status ${res.status}`)
        this.projectStakeholders = await res.json()
      } catch (err) {
        console.error('Failed to fetch project stakeholders:', err)
        this.projectStakeholders = []
      }
    },

    async onProjectChange() {
      if (this.reviewData.project_id) {
        await this.fetchProjectStakeholders(this.reviewData.project_id)
        // Reset stakeholder selection when project changes
        this.reviewData.assigned_stakeholder_id = ''
      } else {
        this.projectStakeholders = []
      }
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
  border-left: 4px solid #007acc;
  padding: 1rem;
  margin-bottom: 1.5rem;
  color: #495057;
  font-size: 0.95rem;
  line-height: 1.5;
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
  padding: 0.5rem;
  border-bottom: 1px solid #ddd;
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
  color: #005a9c;
  text-decoration: none;
}

.action-button {
  padding: 0.4rem 0.8rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.action-button.publish {
  background: #28a745;
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
  background: #218838;
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
  color: #112e51;
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
  border-color: #005a9c;
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

.btn {
  padding: 0.5rem 1rem;
  border: 1px solid transparent;
  border-radius: 4px;
  font-size: 0.875rem;
  font-weight: 400;
  text-align: center;
  cursor: pointer;
  transition: all 0.15s ease-in-out;
}

.btn-secondary {
  color: #6c757d;
  background-color: #f8f9fa;
  border-color: #6c757d;
}

.btn-secondary:hover {
  color: #545b62;
  background-color: #e2e6ea;
  border-color: #545b62;
}

.btn-primary {
  color: #fff;
  background-color: #005a9c;
  border-color: #005a9c;
}

.btn-primary:hover:not(:disabled) {
  background-color: #004a82;
  border-color: #004a82;
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>