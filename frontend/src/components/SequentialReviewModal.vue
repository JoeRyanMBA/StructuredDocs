<template>
  <div class="modal fade" id="sequentialReviewModal" tabindex="-1" aria-labelledby="sequentialReviewModalLabel" aria-hidden="true">
    <div class="modal-dialog modal-lg">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title" id="sequentialReviewModalLabel">
            <i class="bi bi-arrow-right-circle me-2"></i>Set Up Sequential Review
          </h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        
        <div class="modal-body">
          <div v-if="error" class="alert alert-danger" role="alert">
            {{ error }}
          </div>
          
          <div v-if="success" class="alert alert-success" role="alert">
            {{ success }}
          </div>
          
          <!-- Topic Info -->
          <div class="mb-4 p-3 bg-light rounded">
            <h6 class="text-primary mb-2">
              <i class="bi bi-file-text me-1"></i>Topic: {{ topic?.title }}
            </h6>
            <p class="text-muted small mb-0">
              Current Status: <span class="badge bg-secondary">{{ formatStatus(topic?.status) }}</span>
            </p>
          </div>
          
          <!-- Sequence Settings -->
          <div class="mb-4">
            <h6 class="mb-3">Review Sequence Settings</h6>
            
            <div class="row">
              <div class="col-md-6 mb-3">
                <label class="form-label">Sequence Name <span class="text-muted">(Optional)</span></label>
                <input 
                  v-model="form.name" 
                  type="text" 
                  class="form-control" 
                  placeholder="e.g., Technical Review Process"
                />
              </div>
              
              <div class="col-md-6 mb-3">
                <label class="form-label">Priority</label>
                <select v-model="form.priority" class="form-select">
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                  <option value="urgent">Urgent</option>
                </select>
              </div>
            </div>
            
            <div class="mb-3">
              <label class="form-label">Description <span class="text-muted">(Optional)</span></label>
              <textarea 
                v-model="form.description" 
                class="form-control" 
                rows="2" 
                placeholder="Describe the purpose of this review sequence..."
              ></textarea>
            </div>
            
            <div class="mb-3">
              <label class="form-label">Initial Message to First Reviewer</label>
              <textarea 
                v-model="form.initial_message" 
                class="form-control" 
                rows="3" 
                placeholder="Please review this topic for technical accuracy and clarity..."
                required
              ></textarea>
            </div>
          </div>
          
          <!-- Reviewer Sequence -->
          <div class="mb-4">
            <div class="d-flex justify-content-between align-items-center mb-3">
              <h6 class="mb-0">
                <i class="bi bi-people me-1"></i>Reviewer Sequence
                <small class="text-muted">(Expert First Strategy)</small>
              </h6>
              <button 
                @click="addReviewer" 
                type="button" 
                class="btn btn-outline-primary btn-sm"
              >
                <i class="bi bi-plus me-1"></i>Add Reviewer
              </button>
            </div>
            
            <div class="alert alert-info small">
              <i class="bi bi-info-circle me-1"></i>
              <strong>Expert-First Strategy:</strong> Place your most expert reviewer first. They'll catch major issues, 
              then subsequent reviewers will only see the improved version after changes are incorporated.
            </div>
            
            <div v-if="form.reviewers.length === 0" class="text-center text-muted py-4">
              <i class="bi bi-person-plus fs-3 d-block mb-2"></i>
              No reviewers added yet. Click "Add Reviewer" to get started.
            </div>
            
            <div v-for="(reviewer, index) in form.reviewers" :key="index" class="card mb-3">
              <div class="card-body">
                <div class="d-flex justify-content-between align-items-start mb-3">
                  <div class="d-flex align-items-center">
                    <span class="badge bg-primary me-2">{{ index + 1 }}</span>
                    <span v-if="index === 0" class="badge bg-warning text-dark me-2">
                      <i class="bi bi-star me-1"></i>Expert First
                    </span>
                    <h6 class="mb-0">
                      {{ reviewer.step_name || `Reviewer ${index + 1}` }}
                    </h6>
                  </div>
                  <button 
                    @click="removeReviewer(index)" 
                    type="button" 
                    class="btn btn-outline-danger btn-sm"
                  >
                    <i class="bi bi-trash"></i>
                  </button>
                </div>
                
                <div class="row">
                  <div class="col-md-6 mb-3">
                    <label class="form-label">Reviewer</label>
                    <select 
                      v-model="reviewer.reviewer_id" 
                      class="form-select" 
                      required
                    >
                      <option value="">Select Reviewer...</option>
                      <option 
                        v-for="r in availableReviewers" 
                        :key="r.id" 
                        :value="r.id"
                      >
                        {{ r.name }} ({{ r.role }})
                      </option>
                    </select>
                  </div>
                  
                  <div class="col-md-6 mb-3">
                    <label class="form-label">Step Name</label>
                    <input 
                      v-model="reviewer.step_name" 
                      type="text" 
                      class="form-control" 
                      :placeholder="index === 0 ? 'Expert Technical Review' : 'Editorial Review'"
                    />
                  </div>
                </div>
                
                <div class="mb-3">
                  <label class="form-label">Special Instructions <span class="text-muted">(Optional)</span></label>
                  <textarea 
                    v-model="reviewer.instructions" 
                    class="form-control" 
                    rows="2" 
                    :placeholder="index === 0 ? 'Focus on technical accuracy and completeness' : 'Focus on clarity and readability after technical improvements'"
                  ></textarea>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Advanced Settings -->
          <div class="mb-4">
            <h6 class="mb-3">
              <i class="bi bi-gear me-1"></i>Advanced Settings
            </h6>
            
            <div class="form-check mb-2">
              <input 
                v-model="form.auto_advance_on_approve" 
                class="form-check-input" 
                type="checkbox" 
                id="autoAdvanceApprove"
              >
              <label class="form-check-label" for="autoAdvanceApprove">
                Auto-advance on "Approve" (no changes needed)
              </label>
            </div>
            
            <div class="form-check mb-2">
              <input 
                v-model="form.pause_on_changes" 
                class="form-check-input" 
                type="checkbox" 
                id="pauseOnChanges"
              >
              <label class="form-check-label" for="pauseOnChanges">
                Pause sequence when changes are requested (recommended)
              </label>
            </div>
            
            <small class="text-muted">
              When paused, you can incorporate changes and manually advance to the next reviewer.
            </small>
          </div>
        </div>
        
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
            Cancel
          </button>
          <button 
            @click="createSequence" 
            type="button" 
            class="btn btn-primary"
            :disabled="loading || !isFormValid"
          >
            <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
            <i v-else class="bi bi-check-circle me-2"></i>
            {{ loading ? 'Creating...' : 'Start Sequential Review' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'SequentialReviewModal',
  props: {
    topic: {
      type: Object,
      default: null
    }
  },
  data() {
    return {
      loading: false,
      error: null,
      success: null,
      availableReviewers: [],
      hasActiveSequence: false,
      form: {
        name: '',
        description: '',
        initial_message: '',
        priority: 'medium',
        reviewers: [],
        auto_advance_on_approve: true,
        pause_on_changes: true
      }
    }
  },
  computed: {
    isFormValid() {
      return this.form.reviewers.length > 0 && 
             this.form.reviewers.every(r => r.reviewer_id) &&
             this.form.initial_message.trim() &&
             !this.hasActiveSequence
    }
  },
  async mounted() {
    await this.loadAvailableReviewers()
    await this.checkExistingSequences()
  },
  methods: {
    async checkExistingSequences() {
      try {
        if (this.topic?.id) {
          const response = await axios.get(`/api/sequences/topic/${this.topic.id}`)
          const activeSequences = response.data.filter(seq => seq.status === 'active')
          
          if (activeSequences.length > 0) {
            this.hasActiveSequence = true
            this.error = `This topic already has an active review sequence: "${activeSequences[0].name || 'Unnamed sequence'}". Please complete or pause the existing sequence before creating a new one.`
            return
          } else {
            this.hasActiveSequence = false
            this.error = null
          }
        }
      } catch (error) {
        console.error('Failed to check existing sequences:', error)
        // Don't show error for this check, just log it
      }
    },

    async loadAvailableReviewers() {
      try {
        const response = await axios.get('/api/reviews/reviewers')
        this.availableReviewers = response.data
      } catch (error) {
        console.error('Failed to load reviewers:', error)
        this.error = 'Failed to load available reviewers'
      }
    },

    addReviewer() {
      this.form.reviewers.push({
        reviewer_id: '',
        step_name: '',
        instructions: ''
      })
    },

    removeReviewer(index) {
      this.form.reviewers.splice(index, 1)
    },

    async createSequence() {
      if (!this.isFormValid) return

      try {
        this.loading = true
        this.error = null
        this.success = null

        const payload = {
          topic_id: this.topic.id,
          created_by: 1, // TODO: Get from current user
          name: this.form.name || null,
          description: this.form.description || null,
          initial_message: this.form.initial_message,
          priority: this.form.priority,
          reviewers: this.form.reviewers,
          auto_advance_on_approve: this.form.auto_advance_on_approve,
          pause_on_changes: this.form.pause_on_changes,
          auto_start: true
        }

        const response = await axios.post('/api/sequences/', payload)
        
        this.success = 'Sequential review created successfully! First reviewer has been notified.'
        
        // Emit event to parent component
        this.$emit('sequence-created', response.data.sequence)
        
        // Close modal after short delay
        setTimeout(() => {
          const modal = document.getElementById('sequentialReviewModal')
          const bootstrapModal = bootstrap.Modal.getInstance(modal)
          if (bootstrapModal) {
            bootstrapModal.hide()
          }
        }, 2000)

      } catch (error) {
        console.error('Failed to create sequence:', error)
        
        if (error.response?.status === 400) {
          // Handle specific 400 errors
          const errorMessage = error.response.data?.error || 'Bad request'
          if (errorMessage.includes('already has an active review sequence')) {
            this.error = 'This topic already has an active review sequence. Please complete or pause the existing sequence before creating a new one.'
            // Refresh the check
            await this.checkExistingSequences()
          } else if (errorMessage.includes('reviewers list is required')) {
            this.error = 'Please add at least one reviewer to the sequence.'
          } else if (errorMessage.includes('At least one reviewer is required')) {
            this.error = 'Please add at least one reviewer to the sequence.'
          } else {
            this.error = `Validation error: ${errorMessage}`
          }
        } else if (error.response?.status === 500) {
          this.error = 'Server error occurred while creating the review sequence. Please try again or contact support.'
        } else if (error.response?.status === 404) {
          this.error = 'Topic or reviewer not found. Please refresh the page and try again.'
        } else {
          this.error = error.response?.data?.error || 'Failed to create review sequence. Please try again.'
        }
      } finally {
        this.loading = false
      }
    },

    formatStatus(status) {
      if (!status) return 'Unknown'
      return status.split('_').map(word => 
        word.charAt(0).toUpperCase() + word.slice(1)
      ).join(' ')
    },

    resetForm() {
      this.form = {
        name: '',
        description: '',
        initial_message: '',
        priority: 'medium',
        reviewers: [],
        auto_advance_on_approve: true,
        pause_on_changes: true
      }
      this.error = null
      this.success = null
    }
  },
  watch: {
    topic(newTopic) {
      if (newTopic) {
        this.resetForm()
        this.form.initial_message = `Please review "${newTopic.title}" for technical accuracy and clarity.`
      }
    }
  }
}
</script>

<style scoped>
.card {
  border: 1px solid #dee2e6;
}

.badge {
  font-size: 0.75em;
}

.alert {
  border-radius: 0.375rem;
}

.modal-lg {
  max-width: 800px;
}

.form-check-label {
  font-weight: 500;
}

.spinner-border-sm {
  width: 1rem;
  height: 1rem;
}
</style>
