<template>
  <div class="bulk-review-modal" v-if="isVisible" @click.self="closeModal">
    <div class="modal-content">
      <div class="modal-header">
        <h3>Request Bulk Review</h3>
        <button @click="closeModal" class="close-btn">&times;</button>
      </div>

      <div class="modal-body">
        <!-- Topics list -->
        <div class="topics-summary">
          <h4>{{ topics.length }} Topics Selected</h4>
          <ul class="topic-list">
            <li v-for="topic in topics" :key="topic.id">{{ topic.title }}</li>
          </ul>
          <p class="note">A single email will be sent to the reviewer with a link to review all topics in one portal.</p>
        </div>

        <form @submit.prevent="submitRequest">
          <div class="form-group">
            <label>Select Reviewer <span class="required">*</span></label>
            <select v-model="selectedReviewer" required class="form-input">
              <option value="">Choose a reviewer…</option>
              <option v-for="r in reviewers" :key="r.id" :value="r.id">
                {{ r.name }} ({{ r.role }}){{ r.division ? ' — ' + r.division : '' }}
              </option>
            </select>
          </div>

          <div class="form-group">
            <label>Priority</label>
            <select v-model="priority" class="form-input">
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
              <option value="urgent">Urgent</option>
            </select>
          </div>

          <div class="form-group">
            <label>Due Date</label>
            <input v-model="dueDate" type="date" class="form-input" :min="today" />
            <small class="form-help">Leave blank for default (7 days from today)</small>
          </div>

          <div class="form-group">
            <label>Message to Reviewer</label>
            <textarea
              v-model="message"
              class="form-input"
              rows="4"
              placeholder="Any specific areas to focus on, or additional context…"
            ></textarea>
          </div>

          <div class="form-actions">
            <button type="button" @click="closeModal" class="btn btn-secondary">Cancel</button>
            <button type="submit" :disabled="loading || !selectedReviewer" class="btn btn-primary">
              {{ loading ? 'Sending…' : `Send to Reviewer (${topics.length} topics)` }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { getReviewers, requestBulkReview } from '@/api/reviews.js'
import { toast } from '@/composables/useToast'

export default {
  name: 'BulkRequestReviewModal',

  props: {
    topics: {
      type: Array,
      required: true,
    },
    isVisible: {
      type: Boolean,
      default: false,
    },
    currentUser: {
      type: Object,
      required: true,
    },
  },

  emits: ['close', 'bulk-review-requested'],

  data() {
    return {
      reviewers: [],
      selectedReviewer: '',
      priority: 'medium',
      dueDate: '',
      message: '',
      loading: false,
    }
  },

  computed: {
    today() {
      return new Date().toISOString().split('T')[0]
    },
  },

  async mounted() {
    try {
      this.reviewers = await getReviewers()
    } catch (err) {
      toast.error('Failed to load reviewers')
    }
  },

  methods: {
    async submitRequest() {
      if (!this.selectedReviewer) return
      this.loading = true
      try {
        const payload = {
          topic_ids: this.topics.map(t => t.id),
          reviewer_id: parseInt(this.selectedReviewer),
          requested_by: this.currentUser?.id,
          priority: this.priority,
          message: this.message,
        }
        if (this.dueDate) {
          payload.due_date = new Date(this.dueDate).toISOString()
        }

        const result = await requestBulkReview(payload)
        toast.success(`Bulk review sent — ${this.topics.length} topics assigned!`)
        this.$emit('bulk-review-requested', result)
        this.closeModal()
      } catch (err) {
        toast.error('Failed to send bulk review: ' + err.message)
      } finally {
        this.loading = false
      }
    },

    closeModal() {
      this.selectedReviewer = ''
      this.priority = 'medium'
      this.dueDate = ''
      this.message = ''
      this.$emit('close')
    },
  },
}
</script>

<style scoped>
.bulk-review-modal {
  position: fixed; inset: 0;
  background: rgba(0,0,0,0.5);
  display: flex; align-items: center; justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: #fff;
  border-radius: 8px;
  width: 90%; max-width: 560px;
  max-height: 90vh; overflow-y: auto;
  box-shadow: 0 4px 24px rgba(0,0,0,0.18);
}

.modal-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 1rem 1.5rem; border-bottom: 1px solid #e5e7eb;
}
.modal-header h3 { margin: 0; color: #1f2937; }
.close-btn { background: none; border: none; font-size: 1.5rem; color: #6b7280; cursor: pointer; }
.close-btn:hover { color: #374151; }

.modal-body { padding: 1.5rem; }

.topics-summary {
  background: #f0f4ff; border: 1px solid #c7d7f9;
  border-radius: 6px; padding: 14px 16px; margin-bottom: 20px;
}
.topics-summary h4 { margin: 0 0 8px; color: #1e40af; font-size: 15px; }
.topic-list {
  margin: 0 0 10px 0; padding-left: 20px;
  max-height: 140px; overflow-y: auto;
}
.topic-list li { font-size: 14px; color: #374151; padding: 2px 0; }
.note { margin: 0; font-size: 12px; color: #6b7280; font-style: italic; }

.form-group { margin-bottom: 1rem; }
.form-group label { display: block; margin-bottom: 4px; font-weight: 500; color: #374151; font-size: 14px; }
.required { color: #dc3545; }
.form-input { width: 100%; padding: 8px 10px; border: 1px solid #d1d5db; border-radius: 4px; font-size: 14px; box-sizing: border-box; }
.form-input:focus { outline: none; border-color: #3b82f6; box-shadow: 0 0 0 3px rgba(59,130,246,0.1); }
.form-help { display: block; margin-top: 3px; font-size: 12px; color: #6b7280; }

.form-actions { display: flex; gap: 10px; justify-content: flex-end; margin-top: 20px; }

.btn { padding: 8px 16px; border-radius: 4px; font-size: 14px; cursor: pointer; border: none; font-weight: 500; }
.btn:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-secondary { background: #f3f4f6; color: #374151; }
.btn-secondary:hover { background: #e5e7eb; }
.btn-primary { background: #3b82f6; color: #fff; }
.btn-primary:hover:not(:disabled) { background: #2563eb; }
</style>
