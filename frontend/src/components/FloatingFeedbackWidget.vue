<template>
  <div class="floating-feedback">
    <div class="btn-group-vertical">
      <button class="btn btn-danger btn-sm" @click="open('bug')"><i class="fas fa-bug"></i> Report Bug</button>
      <button class="btn btn-primary btn-sm" @click="open('suggestion')"><i class="fas fa-lightbulb"></i> Suggest Improvement</button>
    </div>

    <div class="modal fade" id="feedbackModal" tabindex="-1" aria-hidden="true" ref="modal">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{title}}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <div class="mb-2">
              <label class="form-label">Page / Component</label>
              <input class="form-control" v-model="page" placeholder="e.g., Topic Editor, Home Page" />
            </div>
            <div class="mb-2">
              <label class="form-label">Your contact (optional)</label>
              <input class="form-control" v-model="contact" placeholder="email or handle" />
            </div>
            <div class="mb-2">
              <label class="form-label">Description</label>
              <textarea class="form-control" v-model="message" rows="6"></textarea>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
            <button class="btn btn-primary" @click="submit" :disabled="submitting">
              <span v-if="submitting" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
              {{ submitting ? 'Sending...' : 'Send' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import { toast } from '@/composables/useToast'
export default {
  name: 'FloatingFeedbackWidget',
  data() {
    return {
      type: 'other',
      page: '',
      component: '',
      contact: '',
      message: '',
      title: 'Submit Feedback',
      submitting: false
    }
  },
  methods: {
    open(t) {
      this.type = t || 'other'
      this.title = t === 'bug' ? 'Report a Bug' : 'Suggest an Improvement'
      // Try to auto-capture a page path if running in browser
      if (typeof window !== 'undefined' && window.location) {
        this.page = window.location.pathname
      }
      // Show bootstrap modal
      const modalEl = this.$refs.modal
      const modal = new window.bootstrap.Modal(modalEl)
      modal.show()
    },
    async submit() {
      if (!this.message || !this.message.trim()) {
        toast.error('Please enter a description')
        return
      }
      this.submitting = true;
      try {
        const payload = {
          type: this.type,
          page: this.page,
          component: this.component,
          contact: this.contact,
          message: this.message,
          metadata: { userAgent: navigator.userAgent }
        }
        await axios.post('/api/feedback', payload)
        // Hide modal
        const modalEl = this.$refs.modal
        const modal = window.bootstrap.Modal.getInstance(modalEl)
        modal.hide()
        this.message = ''
        this.contact = ''
        toast.success('Thanks — your report has been submitted.')
      } catch (err) {
        console.error(err)
        toast.error('Failed to submit feedback')
      } finally {
        this.submitting = false;
      }
    }
  }
}
</script>

<style>
.floating-feedback {
  position: fixed;
  right: 18px;
  bottom: 28px;
  z-index: 1050;
}
.floating-feedback .btn-group-vertical .btn {
  margin-bottom: 6px;
  border-radius: 6px;
}
</style>
