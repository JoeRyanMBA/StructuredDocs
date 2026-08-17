<template>
  <div v-if="isVisible" class="modal-overlay" @click.self="closeModal">
    <div class="modal-content seq-modal-content" @click.stop>
      <div class="modal-header-row">
        <h3 class="modal-heading">
          <i class="bi bi-arrow-right-circle me-2" aria-hidden="true"></i>
          {{ modalTitle }}
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

        <!-- Stakeholder Management -->
        <div class="mb-4">
          <h6 class="mb-3"><i class="bi bi-person-plus me-1"></i>Stakeholder Management</h6>
          
          <div class="form-section mb-3">
            <h6 class="mb-2">Add Existing Stakeholder as Reviewer</h6>
            <div class="selector-row d-flex gap-2 mb-3">
              <select v-model="selectedStakeholderId" class="form-select flex-grow-1">
                <option value="">Select a stakeholder...</option>
                <option v-for="stakeholder in availableStakeholders" :key="stakeholder.id" :value="stakeholder.id">
                  {{ stakeholder.name }} ({{ stakeholder.organization || 'N/A' }})
                </option>
              </select>
              <button type="button" @click="addSelectedStakeholderAsReviewer" :disabled="!selectedStakeholderId" class="btn btn-primary btn-sm">
                <i class="bi bi-plus-circle me-1"></i>Add
              </button>
            </div>
          </div>

          <div class="form-section">
            <h6 class="mb-2">Or Create New Stakeholder</h6>
            <div class="mb-3">
              <div class="row mb-2">
                <div class="col-md-6">
                  <input v-model="newStakeholder.name" type="text" placeholder="Name *" required class="form-control form-control-sm" />
                </div>
                <div class="col-md-6">
                  <input v-model="newStakeholder.email" type="email" placeholder="Email *" required class="form-control form-control-sm" />
                </div>
              </div>
              <div class="row mb-2">
                <div class="col-md-6">
                  <input v-model="newStakeholder.title" type="text" placeholder="Title (optional)" class="form-control form-control-sm" />
                </div>
                <div class="col-md-6">
                  <input v-model="newStakeholder.organization" type="text" placeholder="Organization (optional)" class="form-control form-control-sm" />
                </div>
              </div>
              <div class="row mb-2">
                <div class="col-md-6">
                  <input v-model="newStakeholder.division" type="text" placeholder="Division (optional)" class="form-control form-control-sm" />
                </div>
                <div class="col-md-6">
                  <input v-model="newStakeholder.department" type="text" placeholder="Department (optional)" class="form-control form-control-sm" />
                </div>
              </div>
              <div class="row mb-2">
                <div class="col-md-6">
                  <input v-model="newStakeholder.phone" type="tel" placeholder="Phone (optional)" class="form-control form-control-sm" />
                </div>
              </div>
              <div class="mb-2">
                <textarea v-model="newStakeholder.bio" placeholder="Bio (optional)" class="form-control form-control-sm" rows="2"></textarea>
              </div>
              <div class="mb-2">
                <textarea v-model="newStakeholder.expertiseText" placeholder="Expertise areas (one per line, optional)" class="form-control form-control-sm" rows="2"></textarea>
              </div>
              <button type="button" @click="createNewStakeholder" :disabled="!newStakeholder.name || !newStakeholder.email || creatingStakeholder" class="btn btn-primary btn-sm">
                <span v-if="creatingStakeholder" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                <i v-else class="bi bi-plus-circle me-1"></i>
                {{ creatingStakeholder ? 'Creating...' : 'Create Stakeholder' }}
              </button>
            </div>
            <div v-if="stakeholderError" class="alert alert-danger alert-sm mt-2 mb-0">{{ stakeholderError }}</div>
            <div v-if="stakeholderSuccess" class="alert alert-success alert-sm mt-2 mb-0">{{ stakeholderSuccess }}</div>
          </div>
        </div>

        <!-- Existing Sequence Management -->
        <div v-if="existingSequence" class="existing-sequence-box mb-4">
          <div class="d-flex justify-content-between align-items-start gap-3">
            <div>
              <h6 class="mb-1">
                <i class="bi bi-diagram-3 me-1"></i>
                Existing Sequence: {{ existingSequence.name || 'Unnamed sequence' }}
              </h6>
              <p class="small mb-1 text-muted">
                Status:
                <span class="badge" :class="statusBadgeClass(existingSequence.status)">
                  {{ formatStatus(existingSequence.status) }}
                </span>
              </p>
              <p class="small mb-2 text-muted">
                Current step: {{ (existingSequence.current_position ?? 0) + 1 }} of {{ (existingSequence.steps || []).length || 1 }}
              </p>
            </div>
            <div class="sequence-controls">
              <button type="button" class="btn btn-outline-secondary btn-sm" @click="reloadExistingSequence" :disabled="sequenceBusy">
                <i class="bi bi-arrow-clockwise me-1"></i>Refresh
              </button>
              <button
                type="button"
                class="btn btn-outline-primary btn-sm"
                @click="resumeExistingSequence"
                :disabled="sequenceBusy || existingSequence.status !== 'paused'"
              >
                <i class="bi bi-play-circle me-1"></i>Resume
              </button>
              <button
                type="button"
                class="btn btn-primary btn-sm"
                @click="advanceExistingSequence"
                :disabled="sequenceBusy || existingSequence.status !== 'active'"
              >
                <i class="bi bi-skip-forward me-1"></i>Advance to Next
              </button>
            </div>
          </div>

          <div v-if="(existingSequence.steps || []).length" class="sequence-steps-list mt-3">
            <div
              v-for="step in existingSequence.steps"
              :key="step.id"
              class="sequence-step-item"
              :class="{ 'is-current': step.step_order === existingSequence.current_position }"
            >
              <div class="step-main">
                <strong>Step {{ step.step_order + 1 }}:</strong>
                {{ step.step_name || ('Review Step ' + (step.step_order + 1)) }}
                <span class="text-muted"> - {{ step.reviewer_name || 'Unassigned reviewer' }}</span>
              </div>
              <span class="badge" :class="statusBadgeClass(step.status)">{{ formatStatus(step.status) }}</span>
            </div>
          </div>
          <small class="text-muted d-block mt-2">
            Use Resume if the sequence is paused. Use Advance to force assignment to the next reviewer when the current step is complete.
          </small>
        </div>

        <!-- Sequence Settings -->
        <div class="mb-4">
          <h6 class="mb-3">Review Sequence Settings</h6>
          <div class="row">
            <div class="col-md-6 mb-3">
              <label class="form-label">Sequence Name <span class="text-muted">(Optional)</span></label>
              <input v-model="form.name" type="text" class="form-control" placeholder="e.g., Technical Review Process" />
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
            <textarea v-model="form.description" class="form-control" rows="2" placeholder="Describe the purpose of this review sequence..."></textarea>
          </div>

          <div class="mb-3">
            <label class="form-label">Initial Message to First Reviewer</label>
            <textarea v-model="form.initial_message" class="form-control" rows="3" placeholder="Please review this topic for technical accuracy and clarity..." required></textarea>
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
            <strong>Expert-First Strategy:</strong> Place your most expert reviewer first. They'll catch major issues, then subsequent reviewers will only see the improved version after changes are incorporated.
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
                  <h6 class="mb-0">{{ reviewer.step_name || ('Reviewer ' + (index + 1)) }}</h6>
                </div>
                <button @click="removeReviewer(index)" type="button" class="btn btn-outline-danger btn-sm remove-reviewer-btn">
                  <i class="bi bi-trash"></i>
                </button>
              </div>

              <div class="row">
                <div class="col-md-6 mb-3">
                  <label class="form-label">Reviewer</label>
                  <select v-model="reviewer.reviewer_id" class="form-select" required @focus="ensureReviewerChoices">
                    <option value="">Select Reviewer...</option>
                    <option v-for="r in reviewerOptions" :key="r.id" :value="r.id">{{ r.name }} ({{ r.role }})</option>
                  </select>
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label">Step Name</label>
                  <input v-model="reviewer.step_name" type="text" class="form-control" :placeholder="index === 0 ? 'Expert Technical Review' : 'Editorial Review'" />
                </div>
              </div>

              <div class="mb-3">
                <label class="form-label">Special Instructions <span class="text-muted">(Optional)</span></label>
                <textarea v-model="reviewer.instructions" class="form-control" rows="2" :placeholder="index === 0 ? 'Focus on technical accuracy and completeness' : 'Focus on clarity and readability after technical improvements'"></textarea>
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
          <h6 class="mb-3"><i class="bi bi-gear me-1"></i>Advanced Settings</h6>
          <div class="form-check mb-2">
            <input v-model="form.auto_advance_on_approve" class="form-check-input" type="checkbox" id="autoAdvanceApprove" />
            <label class="form-check-label" for="autoAdvanceApprove">Auto-advance on "Approve" (no changes needed)</label>
          </div>
          <div class="form-check mb-2">
            <input v-model="form.pause_on_changes" class="form-check-input" type="checkbox" id="pauseOnChanges" />
            <label class="form-check-label" for="pauseOnChanges">Pause sequence when changes are requested (recommended)</label>
          </div>
          <small class="text-muted">When paused, you can incorporate changes and manually advance to the next reviewer.</small>
        </div>
      </div>

      <div class="modal-footer seq-modal-footer">
        <div class="flex-spacer"></div>
        <button type="button" class="btn btn-secondary" @click="closeModal" :disabled="loading">{{ effectiveMode === 'manage' ? 'Close' : 'Cancel' }}</button>
        <button
          v-if="effectiveMode === 'manage' && existingSequence"
          @click="saveSequenceChanges"
          type="button"
          class="btn btn-primary"
          :disabled="loading || form.reviewers.length === 0 || !form.reviewers.every(r => r.reviewer_id)"
        >
          <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
          <i v-else class="bi bi-save me-2" aria-hidden="true"></i>
          {{ loading ? 'Saving...' : 'Save Changes' }}
        </button>
        <button v-if="effectiveMode !== 'manage'" @click="createSequence" type="button" class="btn btn-primary start-seq-btn" :disabled="loading || !isFormValid">
          <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
          <i v-else class="bi bi-check-circle me-2" aria-hidden="true"></i>
          {{ loading ? 'Creating...' : 'Start Sequential Review' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { apiGet, apiPost } from '@/api/base'

export default {
  name: 'SequentialReviewModal',
  props: {
    topicId: { type: [String, Number], default: null },
    isVisible: { type: Boolean, default: false },
    topic: { type: Object, default: null },
    mode: { type: String, default: 'setup' },
    availableReviewers: { type: Array, default: () => [] },
    topicProjectIds: { type: Array, default: () => [] }
  },
  data() {
    return {
      loading: false,
      sequenceBusy: false,
      error: null,
      success: null,
      reviewerChoices: [],
      apiReviewerChoices: [],
      hasActiveSequence: false,
      existingSequence: null,
      form: {
        name: '',
        description: '',
        initial_message: '',
        priority: 'medium',
        reviewers: [],
        auto_advance_on_approve: true,
        pause_on_changes: true
      },
      selectedStakeholderId: '',
      newStakeholder: {
        name: '',
        email: '',
        title: '',
        organization: '',
        division: '',
        department: '',
        phone: '',
        bio: '',
        expertiseText: ''
      },
      creatingStakeholder: false,
      stakeholderError: null,
      stakeholderSuccess: null,
      allStakeholders: []
    }
  },
  computed: {
    modalTitle() {
      if (this.effectiveMode === 'manage') return 'Manage Sequential Review'
      return this.existingSequence ? 'Manage Sequential Review' : 'Sequential Review Setup'
    },
    effectiveMode() {
      return this.mode === 'manage' && this.existingSequence ? 'manage' : 'setup'
    },
    isFormValid() {
      return (
        this.form.reviewers.length > 0 &&
        this.form.reviewers.every(r => r.reviewer_id) &&
        this.form.initial_message.trim() &&
        !this.hasActiveSequence
      )
    },
    reviewerOptions() {
      if (this.reviewerChoices.length > 0) return this.reviewerChoices
      return this.mergeReviewerChoices(this.apiReviewerChoices)
    },
    availableStakeholders() {
      // Return all stakeholders that aren't already in the reviewer list
      const reviewerIds = new Set(this.form.reviewers.map(r => r.reviewer_id).filter(id => id))
      return this.allStakeholders.filter(s => !reviewerIds.has(s.id))
    }
  },
  async mounted() {
    await this.loadAvailableReviewers()
    await this.loadAllStakeholders()
    if (this.topic?.id) await this.checkExistingSequences()
  },
  methods: {
    closeModal() { this.$emit('close') },
    toReviewerList(value) {
      if (Array.isArray(value)) return value
      if (value && typeof value === 'object') {
        if (Array.isArray(value.reviewers)) return value.reviewers
        if (Array.isArray(value.items)) return value.items
        if (Array.isArray(value.results)) return value.results
        if (Array.isArray(value.data)) return value.data
      }
      return []
    },
    normalizeReviewerId(value) {
      const numeric = Number(value)
      return Number.isFinite(numeric) && numeric > 0 ? numeric : ''
    },
    mergeReviewerChoices(reviewers) {
      const map = new Map()
      this.toReviewerList(reviewers).forEach((reviewer) => {
        if (!reviewer || reviewer.id == null) return
        map.set(Number(reviewer.id), {
          id: Number(reviewer.id),
          name: reviewer.name || `Reviewer ${reviewer.id}`,
          role: reviewer.role || reviewer.reviewer_role || 'reviewer'
        })
      })
      return Array.from(map.values())
    },
    syncFormFromExistingSequence(sequence) {
      if (!sequence) return false

      const mappedSteps = (sequence.steps || [])
        .slice()
        .sort((a, b) => (a.step_order ?? 0) - (b.step_order ?? 0))
        .map((step, index) => ({
          reviewer_id: this.normalizeReviewerId(step.reviewer_id),
          step_name: step.step_name || `Review Step ${index + 1}`,
          instructions: step.instructions || ''
        }))

      if (mappedSteps.length) {
        this.form.reviewers = mappedSteps
      }

      if (sequence.name) this.form.name = sequence.name
      if (sequence.description) this.form.description = sequence.description

      const sequenceReviewers = (sequence.steps || []).map((step) => ({
        id: step.reviewer_id,
        name: step.reviewer_name,
        role: step.reviewer_role
      }))

      this.reviewerChoices = this.mergeReviewerChoices([
        ...this.reviewerChoices,
        ...sequenceReviewers
      ])

      return mappedSteps.length > 0
    },
    async hydrateStepsFromReviews(sequence) {
      if (!sequence?.id || !this.topic?.id) return false

      try {
        const reviews = await apiGet(`/api/reviews/topic/${this.topic.id}/reviews`)
        const sequenceReviews = (Array.isArray(reviews) ? reviews : [])
          .filter((review) => review.sequence_id === sequence.id)
          .sort((left, right) => (left.sequence_position ?? 0) - (right.sequence_position ?? 0))

        if (!sequenceReviews.length) return false

        const fallbackSteps = sequenceReviews.map((review, index) => ({
          id: review.id,
          step_order: review.sequence_position ?? index,
          reviewer_id: this.normalizeReviewerId(review.reviewer_id),
          reviewer_name: review.reviewer_name,
          reviewer_role: null,
          step_name: `Review Step ${(review.sequence_position ?? index) + 1}`,
          instructions: null,
          status: review.status === 'completed' ? 'completed' : 'active',
          review_id: review.id,
          assigned_at: review.requested_at,
          completed_at: review.completed_at
        }))

        this.existingSequence = {
          ...sequence,
          steps: fallbackSteps
        }
        this.syncFormFromExistingSequence(this.existingSequence)
        return true
      } catch (e) {
        console.error('Failed to hydrate sequence reviewers from reviews:', e)
        return false
      }
    },
    statusBadgeClass(status) {
      const value = (status || '').toLowerCase()
      if (value === 'active') return 'bg-primary'
      if (value === 'paused') return 'bg-warning text-dark'
      if (value === 'completed') return 'bg-success'
      if (value === 'pending') return 'bg-secondary'
      if (value === 'skipped') return 'bg-light text-dark border'
      return 'bg-secondary'
    },
    getManagedSequenceCandidates(sequenceList) {
      const byStatus = (status) => sequenceList.filter((seq) => seq?.status === status)
      const others = sequenceList.filter((seq) => !['active', 'paused'].includes(seq?.status))
      const ordered = [
        ...byStatus('active'),
        ...byStatus('paused'),
        ...others
      ]

      // De-duplicate while preserving the priority order above.
      const seen = new Set()
      return ordered.filter((seq) => {
        if (!seq?.id || seen.has(seq.id)) return false
        seen.add(seq.id)
        return true
      })
    },
    async checkExistingSequences() {
      try {
        if (this.topic?.id) {
          const sequences = await apiGet(`/api/sequences/topic/${this.topic.id}`)
          const sequenceList = Array.isArray(sequences) ? sequences : []
          const activeSequences = sequenceList.filter(seq => seq.status === 'active')
          const pausedSequences = sequenceList.filter(seq => seq.status === 'paused')
          let managedSequence = null

          if (this.mode === 'manage') {
            const candidates = this.getManagedSequenceCandidates(sequenceList)

            for (const candidate of candidates) {
              this.existingSequence = candidate
              const hasInlineSteps = this.syncFormFromExistingSequence(candidate)
              const hasResolvedSteps = hasInlineSteps || await this.loadSequenceDetails(candidate.id)
              if (hasResolvedSteps) {
                managedSequence = this.existingSequence
                break
              }
            }

            if (!managedSequence && candidates.length) {
              // Fall back to highest-priority sequence even if no step metadata is available.
              managedSequence = candidates[0]
              this.existingSequence = managedSequence
              this.syncFormFromExistingSequence(managedSequence)
            }
          } else {
            managedSequence = activeSequences[0] || pausedSequences[0] || null
            if (managedSequence) {
              this.existingSequence = managedSequence
              const hasInlineSteps = this.syncFormFromExistingSequence(managedSequence)
              if (!hasInlineSteps) {
                await this.loadSequenceDetails(managedSequence.id)
              }
            }
          }

          if (!managedSequence) {
            this.existingSequence = null
            this.form.reviewers = []
            this.error = null
          } else {
            this.error = null
          }

          if (activeSequences.length > 0) {
            this.hasActiveSequence = true
            this.error = `This topic already has an active review sequence: "${activeSequences[0].name || 'Unnamed sequence'}". You can monitor progress and manually advance/resume it below.`
            return
          }
          this.hasActiveSequence = false
          if (this.mode !== 'manage' || managedSequence) {
            this.error = null
          }
        }
      } catch (e) {
        console.error('Failed to check existing sequences:', e)
      }
    },
    async loadSequenceDetails(sequenceId) {
      try {
        const details = await apiGet(`/api/sequences/${sequenceId}`)
        this.existingSequence = details
        const hasSteps = this.syncFormFromExistingSequence(details)
        if (!hasSteps) {
          return await this.hydrateStepsFromReviews(details)
        }
        return true
      } catch (e) {
        console.error('Failed to load sequence details:', e)
        return false
      }
    },
    async reloadExistingSequence() {
      if (!this.existingSequence?.id) return
      this.sequenceBusy = true
      this.success = null
      try {
        await this.loadSequenceDetails(this.existingSequence.id)
      } finally {
        this.sequenceBusy = false
      }
    },
    async resumeExistingSequence() {
      if (!this.existingSequence?.id || this.existingSequence.status !== 'paused') return
      this.sequenceBusy = true
      this.error = null
      this.success = null
      try {
        const response = await apiPost(`/api/sequences/${this.existingSequence.id}/resume`, {})
        this.success = response?.message || 'Review sequence resumed.'
        await this.reloadExistingSequence()
      } catch (e) {
        this.error = e?.message || 'Failed to resume sequence.'
      } finally {
        this.sequenceBusy = false
      }
    },
    async advanceExistingSequence() {
      if (!this.existingSequence?.id || this.existingSequence.status !== 'active') return
      const confirmed = confirm('Force this sequence to the next reviewer? This should only be used when the current step is complete.')
      if (!confirmed) return

      this.sequenceBusy = true
      this.error = null
      this.success = null
      try {
        const response = await apiPost(`/api/sequences/${this.existingSequence.id}/advance`, {
          message: 'Manually advanced by an authorized user.'
        })
        this.success = response?.message || 'Sequence advanced to next reviewer.'
        await this.reloadExistingSequence()
        this.$emit('sequence-created', this.existingSequence)
      } catch (e) {
        this.error = e?.message || 'Failed to advance sequence.'
      } finally {
        this.sequenceBusy = false
      }
    },
    async loadAvailableReviewers() {
      try {
        this.reviewerChoices = this.mergeReviewerChoices(this.availableReviewers)

        const projectIds = (this.topicProjectIds || [])
          .map((id) => Number(id))
          .filter((id) => Number.isInteger(id) && id > 0)

        if (projectIds.length > 0) {
          const stakeholderResponses = await Promise.allSettled(
            projectIds.map((projectId) => apiGet(`/api/projects/${projectId}/stakeholders`))
          )
          const projectReviewers = stakeholderResponses
            .filter((result) => result.status === 'fulfilled')
            .flatMap((result) => this.toReviewerList(result.value))
            .filter((stakeholder) => stakeholder && stakeholder.id != null && stakeholder.can_review !== false)

          this.reviewerChoices = this.mergeReviewerChoices([
            ...this.reviewerChoices,
            ...projectReviewers
          ])
        }

        this.reviewerChoices = this.mergeReviewerChoices([
          ...this.reviewerChoices,
          ...this.toReviewerList(this.availableReviewers)
        ])

        try {
          const response = await apiGet('/api/reviews/reviewers')
          this.apiReviewerChoices = this.mergeReviewerChoices(this.toReviewerList(response))
          this.reviewerChoices = this.mergeReviewerChoices([
            ...this.reviewerChoices,
            ...this.toReviewerList(response)
          ])
        } catch (e) {
          console.error('Failed to load reviewers:', e)
        }

        if (this.reviewerChoices.length === 0) {
          try {
            const stakeholders = await apiGet('/api/stakeholders/')
            const eligibleStakeholders = this.toReviewerList(stakeholders)
              .filter((stakeholder) => stakeholder && stakeholder.id != null && stakeholder.active !== false && stakeholder.can_review !== false)

            this.apiReviewerChoices = this.mergeReviewerChoices(eligibleStakeholders)
            this.reviewerChoices = this.mergeReviewerChoices(eligibleStakeholders)
          } catch (e) {
            console.error('Failed to load fallback stakeholders:', e)
          }
        }
      } catch (e) {
        console.error('Unexpected error while loading sequential reviewers:', e)
      }

      if (this.reviewerChoices.length === 0) {
        const fallbackChoices = this.mergeReviewerChoices([
          { id: 1, name: 'Expert Reviewer', email: 'expert@example.com', role: 'senior_analyst' },
          { id: 2, name: 'Technical Reviewer', email: 'tech@example.com', role: 'analyst' },
          { id: 3, name: 'Editorial Reviewer', email: 'editor@example.com', role: 'editor' }
        ])
        this.apiReviewerChoices = fallbackChoices
        this.reviewerChoices = fallbackChoices
      }
    },
    async ensureReviewerChoices() {
      if (this.reviewerChoices.length > 0) return
      await this.loadAvailableReviewers()
    },
    async loadAllStakeholders() {
      try {
        const response = await apiGet('/api/stakeholders/')
        this.allStakeholders = this.toReviewerList(response)
          .map(stakeholder => ({
            id: stakeholder.id,
            name: stakeholder.name,
            email: stakeholder.email,
            organization: stakeholder.organization,
            title: stakeholder.title,
            role: 'reviewer'
          }))
      } catch (error) {
        console.error('Failed to load stakeholders:', error)
      }
    },
    async createNewStakeholder() {
      if (!this.newStakeholder.name || !this.newStakeholder.email) return

      this.creatingStakeholder = true
      this.stakeholderError = null
      this.stakeholderSuccess = null

      try {
        // Parse expertise areas from textarea
        const expertise_areas = this.newStakeholder.expertiseText
          .split('\n')
          .map(area => area.trim())
          .filter(area => area.length > 0)

        const payload = {
          name: this.newStakeholder.name,
          email: this.newStakeholder.email,
          title: this.newStakeholder.title || null,
          organization: this.newStakeholder.organization || null,
          division: this.newStakeholder.division || null,
          department: this.newStakeholder.department || null,
          phone: this.newStakeholder.phone || null,
          bio: this.newStakeholder.bio || null,
          expertise_areas: expertise_areas,
          active: true
        }

        const response = await apiPost('/api/stakeholders/', payload)
        
        // Add new stakeholder to the list
        const newStakeholderData = {
          id: response.id,
          name: response.name,
          email: response.email,
          organization: response.organization,
          title: response.title,
          role: 'reviewer'
        }

        this.allStakeholders.push(newStakeholderData)
        this.reviewerChoices = this.mergeReviewerChoices([...this.reviewerChoices, newStakeholderData])

        this.stakeholderSuccess = `${this.newStakeholder.name} has been created successfully. You can now add them to the review sequence.`
        
        // Reset form
        this.newStakeholder = {
          name: '',
          email: '',
          title: '',
          organization: '',
          division: '',
          department: '',
          phone: '',
          bio: '',
          expertiseText: ''
        }

        setTimeout(() => {
          this.stakeholderSuccess = null
        }, 3000)
      } catch (error) {
        this.stakeholderError = error?.message || 'Failed to create stakeholder. Please try again.'
        console.error('Failed to create stakeholder:', error)
      } finally {
        this.creatingStakeholder = false
      }
    },
    addSelectedStakeholderAsReviewer() {
      if (!this.selectedStakeholderId) return

      // Find the stakeholder
      const stakeholder = this.allStakeholders.find(s => s.id === Number(this.selectedStakeholderId))
      if (!stakeholder) return

      // Add to reviewers list
      this.form.reviewers.push({
        reviewer_id: stakeholder.id,
        step_name: `${stakeholder.name} Review`,
        instructions: ''
      })

      this.selectedStakeholderId = ''
    },
    async saveSequenceChanges() {
      if (!this.existingSequence?.id) return

      try {
        this.loading = true
        this.error = null
        this.success = null

        const payload = {
          name: this.form.name || null,
          description: this.form.description || null,
          reviewers: this.form.reviewers,
          auto_advance_on_approve: this.form.auto_advance_on_approve,
          pause_on_changes: this.form.pause_on_changes
        }

        const response = await apiPost(`/api/sequences/${this.existingSequence.id}/update`, payload)
        this.success = response?.message || 'Sequence updated successfully.'
        if (response?.sequence) {
          this.existingSequence = response.sequence
          this.syncFormFromExistingSequence(response.sequence)
        }
      } catch (error) {
        this.error = error?.message || 'Failed to save sequence changes.'
      } finally {
        this.loading = false
      }
    },
    addReviewer() { this.form.reviewers.push({ reviewer_id: '', step_name: '', instructions: '' }) },
    removeReviewer(index) { this.form.reviewers.splice(index, 1) },
    async createSequence() {
      if (!this.isFormValid) return
      try {
        this.loading = true
        this.error = null
        this.success = null
        const payload = {
          topic_id: this.topic.id,
          created_by: 1,
          name: this.form.name || null,
          description: this.form.description || null,
          initial_message: this.form.initial_message,
          priority: this.form.priority,
          reviewers: this.form.reviewers,
          auto_advance_on_approve: this.form.auto_advance_on_approve,
          pause_on_changes: this.form.pause_on_changes,
          auto_start: true
        }
        const response = await apiPost('/api/sequences/', payload)
        this.success = 'Sequential review created successfully! First reviewer has been notified.'
        this.$emit('sequence-created', response.sequence)
        setTimeout(() => this.$emit('close'), 1600)
      } catch (error) {
        console.error('Failed to create sequence:', error)
        const msg = error?.message || 'Failed to create review sequence. Please try again.'
        if (msg.includes('already has an active review sequence')) {
          this.error = 'This topic already has an active review sequence. Please complete or pause the existing sequence before creating a new one.'
          await this.checkExistingSequences()
        } else if (msg.includes('reviewers list is required') || msg.includes('At least one reviewer is required')) {
          this.error = 'Please add at least one reviewer to the sequence.'
        } else {
          this.error = msg
        }
      } finally {
        this.loading = false
      }
    },
    formatStatus(value) {
      if (!value) return 'Unknown'
      return value.split('_').map(p => p.charAt(0).toUpperCase() + p.slice(1)).join(' ')
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
        await this.loadAvailableReviewers()
        await this.checkExistingSequences()
      } else {
        this.existingSequence = null
        this.reviewerChoices = []
      }
    },
    async mode() {
      await this.checkExistingSequences()
    },
    async topicProjectIds() {
      await this.loadAvailableReviewers()
    },
    availableReviewers(newReviewers) {
      this.reviewerChoices = this.mergeReviewerChoices([
        ...this.reviewerChoices,
        ...this.toReviewerList(newReviewers)
      ])
    }
  }
}
</script>

<style scoped>
/* Component-specific tweaks; shared modal styles live in src/styles/modal.css */
.seq-modal-content { max-width: 880px; }
.seq-modal-body { padding: 0 1.25rem .75rem; }
.start-seq-btn { min-width: 190px; }

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

/* Badge refinement */
.topic-status-badge {
  background-color: #6c757d;
  color: #fff;
  padding: 0.25rem 0.5rem;
  font-weight: 400;
  letter-spacing: .2px;
  -webkit-font-smoothing: antialiased;
  text-rendering: optimizeLegibility;
}

.existing-sequence-box {
  background: #f8fafc;
  border: 1px solid #dbe3ef;
  border-radius: 6px;
  padding: .85rem .95rem;
}

.sequence-controls {
  display: flex;
  gap: .5rem;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.sequence-steps-list {
  display: flex;
  flex-direction: column;
  gap: .45rem;
}

.sequence-step-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: .75rem;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  padding: .45rem .6rem;
  background: #fff;
}

.sequence-step-item.is-current {
  border-color: #205493;
  box-shadow: 0 0 0 1px rgba(32, 84, 147, .15);
}

.step-main {
  font-size: .9rem;
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
</style>
