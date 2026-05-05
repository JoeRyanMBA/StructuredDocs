<template>
  <div class="review-feedback-container">
    <div v-if="loading" class="text-center py-5">
      <p class="text-muted">Loading review feedback…</p>
    </div>

    <div v-else-if="error" class="alert alert-danger" role="alert">{{ error }}</div>

    <div v-else class="review-feedback-content">
      <div class="dashboard-header">
        <h1>Incorporate Feedback <HelpIcon feature="reviews.feedback" /></h1>
        <p class="subtitle">Review requested changes and update the topic content.</p>
      </div>

      <!-- Breadcrumb -->
      <nav aria-label="breadcrumb" class="mb-3">
        <ol class="breadcrumb">
          <li class="breadcrumb-item"><router-link to="/reviews">Reviews</router-link></li>
          <li class="breadcrumb-item active" aria-current="page">
            {{ topic?.title || 'Topic' }} — Review Feedback
          </li>
        </ol>
      </nav>

      <div class="summary-card mb-4">
        <div class="summary-grid">
          <div class="summary-main">
            <p class="summary-topic"><strong>Topic:</strong> {{ topic?.title || '—' }}</p>
            <div class="summary-meta">
              <span><strong>Status:</strong> {{ formatStatus(topic?.status) }}</span>
              <span><strong>Reviewer:</strong> {{ review?.reviewer_name || '—' }}</span>
              <span><strong>Priority:</strong> {{ review?.priority || '—' }}</span>
            </div>
          </div>
          <div class="summary-side">
            <p class="mb-1"><strong>Requested By:</strong> {{ review?.requester_name || '—' }}</p>
            <p class="mb-0"><strong>Last Updated:</strong> {{ formatDate(topic?.updated_at) }}</p>
          </div>
        </div>
      </div>

      <!-- Reviewer's overall feedback -->
      <div class="card section-card mb-4">
        <div class="card-header section-card-header">
          <h4 class="card-title mb-0">
            <i class="bi bi-chat-square-text me-2"></i>
            Review Feedback
          </h4>
        </div>
        <div class="card-body">
          <div v-if="review?.feedback" class="mb-3">
            <h6 class="fw-semibold">Comments:</h6>
            <div class="feedback-note feedback-note--warning">{{ review.feedback }}</div>
          </div>
          <div v-if="review?.review_notes" class="mb-3">
            <h6 class="fw-semibold">Internal Notes:</h6>
            <div class="feedback-note feedback-note--info">{{ review.review_notes }}</div>
          </div>
          <p v-if="!review?.feedback && !review?.review_notes" class="text-muted fst-italic mb-0">
            No general feedback provided.
          </p>
        </div>
      </div>

      <!-- ── Word-level content diff ── -->
      <div v-if="review?.edited_content" class="card section-card mb-4">
        <div class="card-header section-card-header">
          <h4 class="card-title mb-0">
            <i class="bi bi-pencil-square me-2"></i>
            Content Edits
            <span class="section-hint">Select a change to accept or reject.</span>
          </h4>
        </div>
        <div class="card-body">
          <ReviewDiffEditor
            :original-html="originalHtml"
            :edited-html="review.edited_content"
            v-model:finalHtml="finalContentHtml"
          />
        </div>
      </div>

      <!-- ── Structured feedback items ── -->
      <div v-if="review?.feedback_items?.length" class="card section-card mb-4">
        <div class="card-header section-card-header">
          <h4 class="card-title mb-0">
            <i class="bi bi-list-check me-2"></i>
            Requested Changes ({{ review.feedback_items.length }})
          </h4>
        </div>
        <div class="card-body p-0">
          <div
            v-for="(item, index) in review.feedback_items"
            :key="item.id"
            class="feedback-item"
            :class="'priority-border-' + item.priority"
          >
            <div class="feedback-item-header">
              <span class="feedback-index">#{{ index + 1 }}</span>
              <span class="feedback-type-badge">{{ formatFeedbackType(item.feedback_type) }}</span>
              <span v-if="item.section_title" class="feedback-section">
                <i class="bi bi-bookmark me-1"></i>{{ item.section_title }}
              </span>
              <span class="ms-auto d-flex gap-2">
                <span class="priority-pill" :class="'priority-' + item.priority">{{ item.priority }}</span>
                <span class="impact-pill"   :class="'impact-' + item.impact">{{ item.impact }}</span>
              </span>
            </div>

            <!-- Original / Suggested text side-by-side -->
            <div v-if="item.original_text || item.suggested_text" class="text-comparison">
              <div v-if="item.original_text" class="text-block original">
                <div class="text-block-label">Original</div>
                <div class="text-block-content">{{ item.original_text }}</div>
              </div>
              <div v-if="item.suggested_text" class="text-block suggested">
                <div class="text-block-label">Suggested</div>
                <div class="text-block-content">{{ item.suggested_text }}</div>
              </div>
            </div>

            <div v-if="item.comment" class="feedback-comment">
              <strong>Comment:</strong> {{ item.comment }}
            </div>
            <div v-if="item.rationale" class="feedback-rationale">
              <strong>Rationale:</strong> {{ item.rationale }}
            </div>

            <!-- Accept / Reject controls -->
            <div class="feedback-respond mt-3">
              <div class="respond-btns mb-2">
                <button
                  class="btn btn-sm me-2"
                  :class="itemResponses[item.id]?.status === 'accepted' ? 'btn-success' : 'btn-outline-success'"
                  @click="setItemStatus(item.id, 'accepted')"
                >
                  <i class="bi bi-check-lg me-1"></i>Accept
                </button>
                <button
                  class="btn btn-sm me-2"
                  :class="itemResponses[item.id]?.status === 'rejected' ? 'btn-danger' : 'btn-outline-danger'"
                  @click="setItemStatus(item.id, 'rejected')"
                >
                  <i class="bi bi-x-lg me-1"></i>Reject
                </button>
                <button
                  class="btn btn-sm"
                  :class="itemResponses[item.id]?.status === 'modified' ? 'btn-warning' : 'btn-outline-warning'"
                  @click="setItemStatus(item.id, 'modified')"
                >
                  <i class="bi bi-pencil me-1"></i>Modify
                </button>
              </div>
              <textarea
                v-if="itemResponses[item.id]?.status"
                v-model="itemResponses[item.id].response"
                class="form-control form-control-sm"
                rows="2"
                :placeholder="itemResponses[item.id].status === 'modified' ? 'Describe your modification…' : 'Optional response note…'"
              ></textarea>
            </div>
          </div>
        </div>
      </div>

      <!-- ── Apply / action bar ── -->
      <div class="action-bar">
        <button
          v-if="hasReviewUpdates && canAdvanceSequence"
          @click="applyChanges({ advanceSequence: true })"
          class="btn btn-primary"
          :disabled="applying"
        >
          <span v-if="applying && applyMode === 'advance'" class="spinner-border spinner-border-sm me-2" aria-hidden="true"></span>
          <i v-else class="bi bi-fast-forward-circle me-2"></i>
          Update Topic & Advance Review
        </button>
        <button
          v-if="hasReviewUpdates"
          @click="applyChanges()"
          class="btn btn-secondary"
          :disabled="applying"
        >
          <span v-if="applying && applyMode === 'update'" class="spinner-border spinner-border-sm me-2" aria-hidden="true"></span>
          <i v-else class="bi bi-check2-circle me-2"></i>
          Update Topic
        </button>
        <button @click="editTopicManually" class="btn btn-secondary">
          <i class="bi bi-pencil-square me-2"></i>Open in Editor
        </button>
        <button @click="goBack" class="btn btn-secondary">
          <i class="bi bi-arrow-left me-2"></i>Back to Reviews
        </button>
      </div>

      <div v-if="applyError" class="alert alert-danger mt-3">{{ applyError }}</div>
      <div v-if="applySuccess" class="alert alert-success mt-3">
        <i class="bi bi-check-circle-fill me-2"></i>Topic updated successfully.
      </div>
    </div>
  </div>
</template>

<script>
import { marked } from 'marked'
import { apiGet, apiPost, apiPut } from '@/api/base'
import ReviewDiffEditor from '@/components/ReviewDiffEditor.vue'
import HelpIcon from '@/components/HelpIcon.vue'

export default {
  name: 'ReviewFeedbackView',
  components: { ReviewDiffEditor, HelpIcon },
  props: {
    topicId:  { type: Number, required: true },
    reviewId: { type: Number, required: true }
  },
  data() {
    return {
      loading:         true,
      error:           null,
      topic:           null,
      review:          null,
      // The reconstructed final HTML after accept/reject in the diff editor
      finalContentHtml: '',
      // Per feedback-item responses: { [itemId]: { status, response } }
      itemResponses:   {},
      applying:        false,
      applyMode:       null,
      applyError:      null,
      applySuccess:    false,
    }
  },
  computed: {
    // Render the original topic markdown to HTML for the diff input
    originalHtml() {
      if (!this.topic?.content) return ''
      const md = this.topic.content.replace(/(\!\[[^\]]*\]\([^)]+\))\{[^}]*\}/g, '$1')
      return marked.parse(md)
    },
    hasReviewUpdates() {
      return Boolean(this.review?.edited_content || this.review?.feedback_items?.length)
    },
    canAdvanceSequence() {
      return Boolean(this.review?.sequence_id)
    }
  },
  async mounted() {
    await this.loadData()
  },
  methods: {
    async loadData() {
      try {
        this.loading = true
        this.error   = null
        const [topicData, reviewData] = await Promise.all([
          apiGet(`/api/topics/${this.topicId}`),
          apiGet(`/api/reviews/${this.reviewId}`)
        ])
        this.topic  = topicData
        this.review = reviewData
        if (this.review.topic_id !== this.topicId) {
          throw new Error('Review does not belong to this topic')
        }
        // Pre-populate the final content with the reviewer's edit (all changes accepted by default)
        this.finalContentHtml = this.review.edited_content || this.originalHtml
      } catch (err) {
        console.error('Error loading review feedback:', err)
        this.error = err.message || 'Failed to load review feedback'
      } finally {
        this.loading = false
      }
    },

    setItemStatus(itemId, status) {
      const existing = this.itemResponses[itemId] || { response: '' }
      this.itemResponses = {
        ...this.itemResponses,
        [itemId]: { ...existing, status }
      }
    },

    async advanceSequentialReview() {
      if (!this.review?.sequence_id) return null

      const sequence = await apiGet(`/api/sequences/${this.review.sequence_id}`)
      const status = sequence?.status

      if (status === 'completed') {
        return sequence
      }

      if (status === 'paused') {
        await apiPost(`/api/sequences/${this.review.sequence_id}/resume`, {})
      } else if (status !== 'active') {
        throw new Error(`Sequential review is ${this.formatStatus(status)} and cannot be advanced from this page.`)
      }

      return apiPost(`/api/sequences/${this.review.sequence_id}/advance`, {
        message: `Topic updated after incorporating feedback for "${this.topic?.title || 'this topic'}".`
      })
    },

    async applyChanges({ advanceSequence = false } = {}) {
      this.applying     = true
      this.applyMode    = advanceSequence ? 'advance' : 'update'
      this.applyError   = null
      this.applySuccess = false
      try {
        // 1. Update the topic content. Sequential reviews should remain in the
        //    review flow after incorporation so the author can resume/advance
        //    the paused sequence. Non-sequential reviews go back to draft.
        const nextTopicStatus = this.review?.sequence_id ? 'pending_review' : 'draft'
        await apiPut(`/api/topics/${this.topicId}`, {
          title:   this.topic.title,
          content: this.review?.edited_content ? this.finalContentHtml : this.topic.content,
          status:  nextTopicStatus
        })

        // 2. Persist each feedback-item response that was set
        const pending = Object.entries(this.itemResponses).filter(([, v]) => v.status)
        await Promise.all(pending.map(([id, val]) =>
          apiPut(`/api/feedback/${id}/respond`, {
            status:          val.status,
            author_response: val.response || ''
          })
        ))

        if (advanceSequence && this.review?.sequence_id) {
          await this.advanceSequentialReview()
        }

        this.applySuccess = true
        this.$router.push({ name: 'IncorporateFeedback' })
      } catch (err) {
        console.error('Error applying changes:', err)
        this.applyError = err.message || 'Failed to update topic. Please try again.'
      } finally {
        this.applying = false
        this.applyMode = null
      }
    },

    editTopicManually() {
      this.$router.push(`/topics/${this.topicId}/edit?reviewId=${this.reviewId}`)
    },

    goBack() {
      this.$router.push({ name: 'ReviewsHome' })
    },

    formatFeedbackType(type) {
      const labels = {
        general_comment: 'General Comment', text_edit: 'Text Edit',
        text_addition: 'Addition', text_deletion: 'Deletion',
        structural_change: 'Structural Change', technical_correction: 'Technical Correction',
        style_suggestion: 'Style Suggestion'
      }
      return labels[type] || type
    },
    formatStatus(status) {
      if (!status) return 'Unknown'
      return status.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')
    },
    formatRecommendation(rec) {
      const labels = {
        approve: 'Approve', approve_with_changes: 'Approve with Changes',
        needs_more_info: 'Needs More Info', reject: 'Reject'
      }
      return labels[rec] || rec || 'Unknown'
    },
    formatDate(dateString) {
      if (!dateString) return 'Unknown'
      const d = new Date(dateString)
      return d.toLocaleDateString() + ' ' + d.toLocaleTimeString()
    }
  }
}
</script>

<style scoped>
.review-feedback-container {
  max-width: 1100px;
  margin: 0 auto;
  padding: 2rem 1.5rem;
}

.dashboard-header {
  margin-bottom: 1rem;
}

.dashboard-header h1 {
  margin: 0;
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-dark-gray, #2c3e50);
}

.summary-card {
  background: var(--bg-white, #fff);
  border: 1px solid var(--border-light-gray, #dee2e6);
  border-radius: var(--border-radius-lg, 10px);
  box-shadow: var(--box-shadow-sm, 0 1px 3px rgba(0, 0, 0, 0.08));
  padding: 1.25rem 1.5rem;
}

.summary-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.4fr) minmax(260px, 1fr);
  gap: 1.25rem 2rem;
  align-items: start;
}

.summary-topic {
  margin: 0 0 0.75rem;
  font-size: 1.1rem;
  color: var(--text-dark-gray, #2c3e50);
}

.summary-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem 1.25rem;
  color: var(--text-medium-gray, #495057);
  font-size: 0.95rem;
}

.summary-side {
  color: var(--text-medium-gray, #495057);
  font-size: 0.95rem;
}

.section-card {
  border: 1px solid var(--border-light-gray, #dee2e6);
  border-radius: var(--border-radius-lg, 10px);
  box-shadow: var(--box-shadow-sm, 0 1px 3px rgba(0, 0, 0, 0.08));
}

.section-card-header {
  background: var(--bg-white, #fff);
  color: var(--text-dark-gray, #2c3e50);
  border-bottom: 1px solid var(--border-light-gray, #dee2e6);
}

.section-hint {
  margin-left: 0.5rem;
  color: var(--text-medium-gray, #6c757d);
  font-size: 0.875rem;
  font-weight: 400;
}

.feedback-note {
  padding: 0.875rem 1rem;
  border-radius: 8px;
  background: #f8f9fa;
  border-left: 4px solid #cbd5e1;
  color: var(--text-dark-gray, #2c3e50);
}

.feedback-note--warning {
  border-left-color: #f59e0b;
}

.feedback-note--info {
  border-left-color: #0ea5e9;
}

.feedback-item {
  border-bottom: 1px solid #dee2e6;
  padding: 1rem 1.25rem;
}
.feedback-item:last-child { border-bottom: none; }
.priority-border-critical { border-left: 4px solid #dc3545; }
.priority-border-high     { border-left: 4px solid #fd7e14; }
.priority-border-medium   { border-left: 4px solid #ffc107; }
.priority-border-low      { border-left: 4px solid #198754; }

.feedback-item-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
  flex-wrap: wrap;
}
.feedback-index { font-weight: 700; color: #6c757d; font-size: 0.85rem; }
.feedback-type-badge {
  background: #e9ecef; color: #495057;
  font-size: 0.75rem; font-weight: 600;
  padding: 0.2rem 0.55rem; border-radius: 4px;
}
.feedback-section { font-size: 0.82rem; color: #0d6efd; }

.priority-pill, .impact-pill {
  font-size: 0.7rem; font-weight: 700;
  text-transform: uppercase;
  padding: 0.15rem 0.45rem; border-radius: 3px;
}
.priority-critical { background:#f8d7da; color:#842029; }
.priority-high     { background:#ffe5d0; color:#7c3a00; }
.priority-medium   { background:#fff3cd; color:#664d03; }
.priority-low      { background:#d1e7dd; color:#0a3622; }
.impact-major      { background:#f8d7da; color:#842029; }
.impact-moderate   { background:#fff3cd; color:#664d03; }
.impact-minor      { background:#d1e7dd; color:#0a3622; }

.text-comparison {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
}
@media (max-width: 600px) { .text-comparison { grid-template-columns: 1fr; } }

.text-block { border-radius: 4px; overflow: hidden; }
.text-block-label { font-size: 0.72rem; font-weight: 700; text-transform: uppercase; padding: 0.2rem 0.6rem; }
.text-block-content { padding: 0.5rem 0.75rem; font-size: 0.88rem; white-space: pre-wrap; word-break: break-word; }
.text-block.original .text-block-label  { background:#f8d7da; color:#842029; }
.text-block.original .text-block-content { background:#fff5f5; border:1px solid #f5c2c7; }
.text-block.suggested .text-block-label  { background:#d1e7dd; color:#0a3622; }
.text-block.suggested .text-block-content { background:#f0fff4; border:1px solid #badbcc; }

.feedback-comment, .feedback-rationale {
  font-size: 0.88rem; margin-top: 0.4rem; color: #343a40;
}

.feedback-respond {
  border-top: 1px dashed #dee2e6;
  padding-top: 0.75rem;
}
.respond-btns { display: flex; flex-wrap: wrap; gap: 0.25rem; }

.action-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 1px solid #dee2e6;
}

@media (max-width: 600px) {
  .action-bar { flex-direction: column; }
  .action-bar .btn { width: 100%; }
}

@media (max-width: 768px) {
  .summary-grid {
    grid-template-columns: 1fr;
  }
}
</style>
