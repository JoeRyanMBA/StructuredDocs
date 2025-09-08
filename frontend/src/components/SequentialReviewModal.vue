<template>
  <div class="modal-overlay" @click.self="closeModal">
    <div class="modal-content seq-modal-content" @click.stop>
      <div class="modal-header-row">
        <h3 class="modal-heading">
          <i class="bi bi-arrow-right-circle me-2" aria-hidden="true"></i>
          Sequential Review Setup
        </h3>
        <button type="button" class="plain-close" @click="closeModal" aria-label="Close sequential review setup" title="Close">
          <i class="bi bi-x-lg" aria-hidden="true"></i>
        </button>
      </div>
      <div class="modal-body seq-modal-body">
          <div v-if="error" class="alert alert-danger" role="alert" style="margin-bottom: 1.5rem;">
            {{ error }}
          </div>
          
          <div v-if="success" class="alert alert-success" role="alert" style="margin-bottom: 1.5rem;">
            {{ success }}
          </div>
          
          <!-- Topic Info -->
          <div class="topic-info-box mb-4">
            <h6 class="mb-2 topic-info-heading">
              <i class="bi bi-file-text me-1"></i>Topic: {{ topic?.title }}
            </h6>
            <p class="small mb-0 text-muted">
              Current Status: <span class="badge topic-status-badge">{{ formatStatus(topic?.status) }}</span>
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
            <div v-for="(reviewer, index) in form.reviewers" :key="index" class="card reviewer-card mb-3">
              <div class="card-body reviewer-card-body">
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
                    class="btn btn-outline-danger btn-sm remove-reviewer-btn"
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
            <div class="d-flex justify-content-center mt-3">
                          <button @click="addReviewer" type="button" class="btn btn-primary add-reviewer-btn">
                            <i class="bi bi-plus-circle me-1" aria-hidden="true"></i> Add Reviewer
                          </button>
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

      <div class="modal-footer seq-modal-footer">
        <div class="flex-spacer"></div>
        <button type="button" class="btn btn-secondary" @click="closeModal" :disabled="loading">Cancel</button>
        <button @click="createSequence" type="button" class="btn btn-primary start-seq-btn" :disabled="loading || !isFormValid">
          <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
          <i v-else class="bi bi-check-circle me-2" aria-hidden="true"></i>
          {{ loading ? 'Creating...' : 'Start Sequential Review' }}
        </button>
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
    // Load reviewers on mount
    await this.loadAvailableReviewers()
    
    // Only check sequences if we have a topic
    if (this.topic?.id) {
      await this.checkExistingSequences()
    }
  },
  methods: {
    closeModal() {
      this.$emit('close')
    },

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
        // Provide fallback reviewers for testing when backend is unavailable
        this.availableReviewers = [
          { id: 1, name: 'Expert Reviewer', email: 'expert@census.gov', role: 'senior_analyst' },
          { id: 2, name: 'Technical Reviewer', email: 'tech@census.gov', role: 'analyst' },
          { id: 3, name: 'Editorial Reviewer', email: 'editor@census.gov', role: 'editor' }
        ]
        // Don't show error to user for reviewer loading - just use fallback data
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
        
  // Close modal after short delay via emitted event (consistent with other modals)
  setTimeout(() => { this.$emit('close') }, 1600)

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
    async topic(newTopic) {
      if (newTopic) {
        this.resetForm()
        this.form.initial_message = `Please review "${newTopic.title}" for technical accuracy and clarity.`
        // Check for existing sequences when topic changes
        await this.checkExistingSequences()
      }
    }
  }
}
</script>

<style>
/* Sequential Review Modal refined styling for consistency */
.seq-modal-content {
  max-width: 880px; /* widened for better horizontal space */
  width: 100%;
  display: flex;
  flex-direction: column;
  max-height: 90vh;
  padding: 0; /* rely on inner sections */
  /* Allow focus box-shadows to render outside without clipping */
  overflow: visible;
  scrollbar-gutter: stable; /* avoid right shift on scrollbar */
}

.modal-header-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
  padding: 1rem 1.25rem .75rem;
  border-bottom: 1px solid var(--border-light-gray, #e2e6ea);
}

.modal-heading {
  margin: 0;
  font-size: 1.15rem;
  font-weight: 600;
  display: flex;
  align-items: center;
}

.plain-close {
  background: transparent;
  border: none;
  color: var(--text-secondary-cool-gray, #666);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 2.25rem;
  height: 2.25rem;
  padding: 0;
  line-height: 1;
  border-radius: 4px;
  font-size: 1.35rem; /* enlarges icon */
}
.plain-close:hover, .plain-close:focus {
  color: var(--text-primary, #205493);
  background: rgba(32,84,147,0.08);
  outline: none;
}
.plain-close:active { background: rgba(32,84,147,0.15); }

.seq-modal-body {
  padding: 0 1.25rem .75rem; /* symmetrical horizontal padding */
  overflow-y: auto;
  flex: 1;
}
.seq-modal-body > .mb-4:first-of-type,
.seq-modal-body > .topic-info-box:first-child { margin-top: .25rem; }

/* Field container to ensure focus halo is not clipped on left */
.seq-modal-body .row, .seq-modal-body .topic-info-box, .seq-modal-body .mb-3, .seq-modal-body .mb-4 {
  position: relative;
}

/* Provide slight inset so box-shadow (focus ring) stays fully visible */
.seq-modal-body .form-control, .seq-modal-body .form-select, .seq-modal-body textarea {
  outline: none;
  box-shadow: none;
  border: 1px solid #ced4da;
  transition: box-shadow .15s ease, border-color .15s ease;
  outline-offset: 2px; /* extra space before any outline (accessibility) */
}

.seq-modal-body .form-control:focus, .seq-modal-body .form-select:focus, .seq-modal-body textarea:focus {
  border-color: #205493;
  box-shadow: 0 0 0 3px rgba(32,84,147,0.25);
}

/* Add a small left internal padding zone to overall body to balance focus halo */
.seq-modal-content { padding-left: 2px; }

/* Remove bootstrap-style negative gutters inside this isolated modal */
.seq-modal-body .row { margin-left: 0; margin-right: 0; row-gap: .5rem; }
.seq-modal-body .row > [class^='col-'] { padding-left: 0; padding-right: 0; }

.seq-modal-footer {
  background: transparent;
  padding: .75rem 1.25rem 1rem;
  border-top: 1px solid var(--border-light-gray, #e2e6ea);
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.seq-modal-content .modal-body > *:first-child { margin-top: 0; }

.start-seq-btn { min-width: 190px; }
/* Ensure cancel button consistent height/spacing */
.seq-modal-footer .btn { padding: 0.55rem 1.1rem; }
.seq-modal-footer .btn-secondary { background:#6c757d; border:1px solid #6c757d; }
.seq-modal-footer .btn-secondary:hover:not(:disabled) { background:#5a6268; }
.seq-modal-footer .btn-primary { background:#205493; border:1px solid #205493; }
.seq-modal-footer .btn-primary:disabled { background:#9cb2cc; border-color:#9cb2cc; opacity:1; }
.seq-modal-footer .btn-primary:not(:disabled):hover { background:#16406d; border-color:#16406d; }

/* Add Reviewer button adopt same palette */
.add-reviewer-btn { background:#205493; border:1px solid #205493; color:#fff; }
.add-reviewer-btn:hover { background:#16406d; border-color:#16406d; }
.add-reviewer-btn:active { background:#113454; border-color:#113454; }
.add-reviewer-btn:focus { box-shadow:0 0 0 3px rgba(32,84,147,0.35); }

/* Topic info */
.topic-info-box {
  background: var(--bg-white, #fff);
  border: 1px solid var(--border-light-gray, #e2e6ea);
  border-left: 4px solid #205493;
  border-radius: 4px;
  padding: .75rem .85rem .5rem;
  margin: 0 0 1.25rem;
}
.topic-info-heading { color: #205493; font-weight: 600; font-size: .9rem; }

/* Badge refinement (remove bold/blur appearance) */
.topic-status-badge {
  background-color: #6c757d;
  color: #fff;
  padding: 0.25rem 0.5rem;
  font-weight: 400 !important;
  letter-spacing: .2px;
  -webkit-font-smoothing: antialiased;
  text-rendering: optimizeLegibility;
}

.reviewer-card { border: 1px solid #dee2e6; border-radius: 6px; }
.reviewer-card-body { padding: 1rem 1rem .5rem; }

.add-reviewer-btn { min-width: 180px; }

.remove-reviewer-btn { padding: .35rem .6rem; }

@media (max-width: 640px) {
  .seq-modal-content { max-width: 96%; }
  .seq-modal-body { padding: 0 .75rem .5rem; }
  .reviewer-card-body { padding: .75rem .65rem .25rem; }
}
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

/* Organizational color scheme */
.btn-primary:hover:not(:disabled) {
  background-color: #005E7B !important;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(32, 84, 147, 0.3);
  transition: all 0.2s ease;
}

.btn-secondary:hover {
  background-color: #5a6268 !important;
  transform: translateY(-1px);
  transition: all 0.2s ease;
}

.form-control:focus {
  border-color: #205493;
  box-shadow: 0 0 0 0.2rem rgba(32, 84, 147, 0.25);
}

.form-select:focus {
  border-color: #205493;
  box-shadow: 0 0 0 0.2rem rgba(32, 84, 147, 0.25);
}

/* Consistent spacing */
.mb-3 {
  margin-bottom: 1.5rem;
}

.mb-4 {
  margin-bottom: 2rem;
}
</style>
