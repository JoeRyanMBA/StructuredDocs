<template>
  <div class="feedback-widget">
    <button @click="showFeedbackModal = true" class="feedback-btn">
      <i class="fas fa-comment-dots"></i> Feedback
    </button>
    <button @click="showBugModal = true" class="bug-btn">
      <i class="fas fa-bug"></i> Report Bug
    </button>

    <!-- Feedback Modal -->
    <teleport to="body">
  <div v-if="showFeedbackModal" class="modal-overlay feedback-overlay" @click.self="showFeedbackModal = false">
        <div class="overlay-center" @click.stop>
          <div class="sd-modal small-modal feedback-modal" @click.stop>
          <div class="sd-modal-header">
            <h2>Provide Feedback</h2>
            <button @click="showFeedbackModal = false" class="close-btn">×</button>
          </div>
          <form @submit.prevent="submitFeedback" class="sd-modal-body">
            <div class="form-group">
              <label for="feedbackType">Feedback Type</label>
              <select id="feedbackType" v-model="feedback.type">
                <option value="general">General Feedback</option>
                <option value="suggestion">Suggestion</option>
                <option value="praise">Praise</option>
              </select>
            </div>
            <div class="form-group">
              <label for="feedbackMessage">Message</label>
              <textarea id="feedbackMessage" v-model="feedback.message" required rows="5"></textarea>
            </div>
            <div class="sd-modal-actions">
              <button type="submit" class="primary-btn">Submit Feedback</button>
            </div>
          </form>
          </div>
        </div>
      </div>
    </teleport>

    <!-- Bug Report Modal -->
    <teleport to="body">
  <div v-if="showBugModal" class="modal-overlay feedback-overlay" @click.self="showBugModal = false">
        <div class="overlay-center" @click.stop>
          <div class="sd-modal small-modal feedback-modal" @click.stop>
          <div class="sd-modal-header">
            <h2>Report a Bug</h2>
            <button @click="showBugModal = false" class="close-btn">×</button>
          </div>
          <form @submit.prevent="submitBugReport" class="sd-modal-body">
            <div class="form-group">
              <label for="bugArea">Area of Application</label>
              <input type="text" id="bugArea" v-model="bugReport.area" placeholder="e.g., Projects Dashboard, Topic Editor" required />
            </div>
            <div class="form-group">
              <label for="bugDescription">Description of Bug</label>
              <textarea id="bugDescription" v-model="bugReport.description" required rows="5" placeholder="Please be as detailed as possible."></textarea>
            </div>
             <div class="form-group">
              <label for="bugReproduction">Steps to Reproduce</label>
              <textarea id="bugReproduction" v-model="bugReport.reproduction_steps" rows="5" placeholder="1. Go to '...' page. 2. Click on '....' button. 3. See error."></textarea>
            </div>
            <div class="sd-modal-actions">
              <button type="submit" class="primary-btn">Submit Bug Report</button>
            </div>
          </form>
          </div>
        </div>
      </div>
    </teleport>
  </div>
</template>

<script>
export default {
  name: 'FeedbackWidget',
  data() {
    return {
      showFeedbackModal: false,
      showBugModal: false,
      feedback: { type: 'general', message: '' },
      bugReport: { area: '', description: '', reproduction_steps: '' }
    }
  },
  methods: {
    async submitFeedback() {
      try {
        const payload = {
          type: this.feedback.type || 'general',
          page: typeof window !== 'undefined' ? window.location.pathname : undefined,
          message: this.feedback.message,
          metadata: { source: 'FeedbackWidget' }
        }
        const res = await fetch('/api/feedback', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        })
        if (!res.ok) throw new Error('Submit failed')
        this.showFeedbackModal = false
        this.feedback = { type: 'general', message: '' }
        alert('Thank you for your feedback!')
      } catch (err) {
        console.error('Failed to submit feedback', err)
        alert('Failed to submit feedback')
      }
    },
    async submitBugReport() {
      try {
        const payload = {
          type: 'bug',
          page: this.bugReport.area || (typeof window !== 'undefined' ? window.location.pathname : undefined),
          message: `${this.bugReport.description || ''}\n\nRepro:\n${this.bugReport.reproduction_steps || ''}`.trim(),
          metadata: { source: 'FeedbackWidget' }
        }
        const res = await fetch('/api/feedback', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        })
        if (!res.ok) throw new Error('Submit failed')
        this.showBugModal = false
        this.bugReport = { area: '', description: '', reproduction_steps: '' }
        alert('Thank you for reporting this bug!')
      } catch (err) {
        console.error('Failed to submit bug', err)
        alert('Failed to submit bug report')
      }
    }
  }
}
</script>

<style scoped>
.feedback-widget {
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 1050;
  display: flex;
  gap: 10px;
}

.feedback-btn, .bug-btn {
  padding: 10px 15px;
  border-radius: 20px;
  border: none;
  cursor: pointer;
  box-shadow: 0 2px 10px rgba(0,0,0,0.2);
  transition: all 0.3s ease;
}

.feedback-btn {
  background-color: var(--primary-medium-teal);
  color: white;
}

.bug-btn {
  background-color: var(--error-coral-red);
  color: white;
}

.feedback-btn:hover, .bug-btn:hover {
  transform: translateY(-2px);
}

/* Ensure the modal content centers horizontally even if an external style changes overlay flex alignment */
.sd-modal {
  margin-left: auto;
  margin-right: auto;
  background: var(--bg-primary-white);
  border-radius: var(--border-radius-lg);
  border: 1px solid var(--border-light-gray);
  box-shadow: var(--box-shadow-lg);
}

.small-modal {
  max-width: 600px;
  width: 90%;
}

/* Ensure overlay horizontally centers while keeping top alignment (as requested) */
.feedback-overlay {
  display: flex !important;
  justify-content: center !important;
  align-items: flex-start !important;
}

.overlay-center {
  width: 100%;
  position: relative;
  pointer-events: none; /* allow background click to close */
  display: grid;              /* robust centering */
  justify-items: center;      /* center horizontally */
  align-content: start;       /* stick to top */
  min-height: 100%;
}

.overlay-center > .sd-modal {
  pointer-events: auto; /* re-enable interaction within modal */
  /* Allow the modal to use most of the viewport height and scroll internally */
  max-height: calc(100vh - 4rem);
  display: flex !important;
  flex-direction: column;
  overflow: hidden; /* header stays, body scrolls */
  /* Top spacing; grid handles horizontal centering */
  margin: 2rem 0 0;
}

/* Stronger centering guard for these modals */
.feedback-modal {
  margin-left: auto !important;
  margin-right: auto !important;
}

.sd-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid var(--border-light-gray);
}

.sd-modal-body {
  padding: 1.5rem;
  overflow-y: auto;
  flex: 1 1 auto;
}

.sd-modal-actions {
  padding: 1rem 1.5rem;
  border-top: 1px solid var(--border-light-gray);
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}

/* Ensure the modal body scrolls when content is long */
.modal-body {
  overflow-y: auto;
  flex: 1 1 auto;
}

.modal-header,
.modal-actions {
  flex: 0 0 auto;
}
</style>
