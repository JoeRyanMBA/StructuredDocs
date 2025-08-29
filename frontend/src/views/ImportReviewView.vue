<template>
  <div class="import-review-view">
    <!-- Loading -->
    <div v-if="loading" class="loading">Loading…</div>

    <!-- Error -->
    <div v-else-if="error" class="error">{{ error }}</div>

    <!-- Data Loaded -->
    <div v-else>
      <h2>Review Import: {{ doc.filename }}</h2>
      <div class="status-row">
        <span>Status: {{ doc.status }}</span>
        <span class="topics-count">Total Topics: {{ doc.topics_count || (doc.items ? doc.items.length : 0) }}</span>
      </div>

      <table class="items-table" v-if="doc.items && doc.items.length > 0">
        <thead>
          <tr>
            <th>#</th><th>Title</th><th>Content</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in doc.items" :key="item.id">
            <td>{{ item.heading_order + 1 }}</td>
            <td><input v-model="item.title" placeholder="Edit title" /></td>
            <td>
              <div class="content-cell">
                <textarea
                  v-model="item.content"
                  rows="8"
                  placeholder="Edit content"
                  class="content-textarea"
                ></textarea>
                <div class="content-info">
                  {{ item.content ? item.content.length : 0 }} characters
                </div>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
      
      <!-- Show message if no items -->
      <div v-else class="no-items">
        <strong>No content items found for this import.</strong><br>
        This document may need to be re-imported with proper parsing, or the original file may not have had recognizable headings.
      </div>

      <!-- Review Step Information -->
      <div class="review-status">
        <strong>Current Review Step:</strong> 
        <span v-if="doc.review_step === 'pending'" class="status-pending">Pending Review</span>
        <span v-else-if="doc.review_step === 'sme_approved'" class="status-approved">Approved - Ready for Final Commit</span>
        <span v-else-if="doc.review_step === 'final_approved'" class="status-final">Final Approved</span>
        <span v-else class="status-unknown">{{ doc.review_step }}</span>
      </div>

      <div class="actions">
        <!-- Review Step -->
        <button
          v-if="doc.review_step === 'pending'"
          @click="smeApprove"
          class="primary-action"
        >
          Submit for Review
        </button>

        <!-- Final Commit Step -->
        <button
          v-else-if="doc.review_step === 'sme_approved'"
          @click="commitImport"
          class="primary-action"
        >
          Final Commit
        </button>

        <!-- Already Final Approved -->
        <div v-else-if="doc.review_step === 'final_approved'" class="completed-message">
          This import has been completed and committed.
        </div>

        <!-- Reject button (always available unless final approved) -->
        <button 
          v-if="doc.review_step !== 'final_approved'"
          @click="rejectImport"
          class="reject-action"
        >
          Reject Import
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ImportReviewView',

  props: {
    id: {
      type: [String, Number],
      required: true
    }
  },

  data() {
    return {
      doc: null,
      loading: false,
      error: null
    }
  },

  created() {
    this.fetchImport()
  },

  methods: {
    async fetchImport() {
      this.loading = true
      this.error = null
      try {
        const res = await fetch(`/api/import/staging/${this.id}`)
        
        if (!res.ok) {
          const errorText = await res.text()
          throw new Error(`HTTP ${res.status}: ${errorText}`)
        }
        
        this.doc = await res.json()
      } catch (err) {
        console.error('❌ Error fetching import:', err)
        this.error = `Failed to load import data: ${err.message}`
      } finally {
        this.loading = false
      }
    },

    // SME Approve method (renamed for clarity)
    async smeApprove() {
      this.error = null
      try {
        console.log('Approve Import clicked')  // debug log
        const res = await fetch(
          `/api/import/staging/${this.id}/sme_approve`,
          { method: 'POST' }
        )
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        this.$router.push({ name: 'ImportHistory' })
      } catch (err) {
        console.error(err)
        this.error = 'Import approval failed'
      }
    },

    async commitImport() {
      this.error = null
      try {
        const res = await fetch(
          `/api/import/staging/${this.id}/commit`,
          { method: 'POST' }
        )
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        this.$router.push({ name: 'ImportHistory' })
      } catch (err) {
        console.error(err)
        this.error = 'Commit failed'
      }
    },

    async rejectImport() {
      this.error = null
      try {
        const res = await fetch(
          `/api/import/staging/${this.id}/reject`,
          { method: 'POST' }
        )
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        this.$router.push({ name: 'ImportHistory' })
      } catch (err) {
        console.error(err)
        this.error = 'Reject failed'
      }
    }
  }
}
</script>

<style scoped>
.import-review-view { padding: 2rem; background-color: var(--bg-light-mist-gray); }
.loading { font-style: italic; }
.error { color: var(--error-coral-red); margin-bottom: 1rem; font-weight: bold; }

.status-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  font-weight: 500;
}

.topics-count {
  color: var(--text-secondary-cool-gray);
  font-size: 0.95em;
}

.review-status {
  background: var(--bg-light-mist-gray);
  border: 1px solid var(--extended-lavender-gray);
  padding: 1rem;
  margin-bottom: 1.5rem;
  border-radius: 4px;
}

.status-pending { color: var(--warning-amber); background: var(--extended-warm-taupe); padding: 0.25rem 0.5rem; border-radius: 3px; }
.status-approved { color: var(--success-mint-green); background: var(--extended-cool-mint); padding: 0.25rem 0.5rem; border-radius: 3px; }
.status-final { color: var(--primary-deep-teal); background: var(--extended-sky-blue); padding: 0.25rem 0.5rem; border-radius: 3px; }
.status-unknown { color: var(--text-secondary-cool-gray); background: var(--extended-lavender-gray); padding: 0.25rem 0.5rem; border-radius: 3px; }

.items-table { width:100%; border-collapse:collapse; margin-bottom:1rem; }
.items-table th, .items-table td { border:1px solid var(--border-gray); padding:0.5rem; }
.items-table th:first-child, .items-table td:first-child { width: 5%; }
.items-table th:nth-child(2), .items-table td:nth-child(2) { width: 25%; }
.items-table th:nth-child(3), .items-table td:nth-child(3) { width: 70%; }
.items-table input, .items-table textarea {
  width:100%; box-sizing:border-box; padding:0.25rem;
}

.content-textarea {
  min-height: 120px;
  resize: vertical;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  font-size: 14px;
  line-height: 1.4;
}

.content-cell {
  position: relative;
}

.content-info {
  font-size: 12px;
  color: var(--text-secondary-cool-gray);
  text-align: right;
  margin-top: 4px;
}

.actions {
  display:flex;
  gap:1rem;
  align-items: center;
}

.primary-action {
  padding:0.75rem 1.5rem;
  border:none;
  background:var(--success-mint-green);
  color:#fff;
  cursor:pointer;
  border-radius:4px;
  font-weight: bold;
}

.primary-action:hover {
  background: #25a25a;
}

.reject-action {
  padding:0.75rem 1.5rem;
  border:none;
  background:var(--error-coral-red);
  color:#fff;
  cursor:pointer;
  border-radius:4px;
}

.reject-action:hover {
  background:#c0392b;
}

.completed-message {
  color: var(--success-mint-green);
  background: var(--extended-cool-mint);
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  font-weight: bold;
}

.no-items {
  background: var(--extended-warm-taupe);
  padding: 1rem;
  margin: 1rem 0;
  border-radius: 4px;
  color: var(--warning-amber);
}
</style>