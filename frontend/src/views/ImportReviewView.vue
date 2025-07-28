<template>
  <div class="import-review-view">
    <!-- Loading -->
    <div v-if="loading" class="loading">Loading…</div>

    <!-- Error -->
    <div v-else-if="error" class="error">{{ error }}</div>

    <!-- Data Loaded -->
    <div v-else>
      <h2>Review Import: {{ doc.items && doc.items.length > 0 ? doc.items[0].title : doc.filename }}</h2>
      <p>Status: {{ doc.status }}</p>

      <table class="items-table">
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
              <textarea
                v-model="item.content"
                rows="4"
                placeholder="Edit content"
              ></textarea>
            </td>
          </tr>
        </tbody>
      </table>

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
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        this.doc = await res.json()
        console.log('Import data received:', this.doc) // Debug log
        console.log('Items array:', this.doc.items) // Debug log
      } catch (err) {
        console.error(err)
        this.error = 'Failed to load import data'
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
.import-review-view { padding: 2rem; }
.loading { font-style: italic; }
.error { color: #c00; margin-bottom: 1rem; font-weight: bold; }

.review-status {
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  padding: 1rem;
  margin-bottom: 1.5rem;
  border-radius: 4px;
}

.status-pending { color: #856404; background: #fff3cd; padding: 0.25rem 0.5rem; border-radius: 3px; }
.status-approved { color: #155724; background: #d4edda; padding: 0.25rem 0.5rem; border-radius: 3px; }
.status-final { color: #004085; background: #cce7ff; padding: 0.25rem 0.5rem; border-radius: 3px; }
.status-unknown { color: #6c757d; background: #e9ecef; padding: 0.25rem 0.5rem; border-radius: 3px; }

.items-table { width:100%; border-collapse:collapse; margin-bottom:1rem; }
.items-table th, .items-table td { border:1px solid #ccc; padding:0.5rem; }
.items-table th:first-child, .items-table td:first-child { width: 5%; }
.items-table th:nth-child(2), .items-table td:nth-child(2) { width: 25%; }
.items-table th:nth-child(3), .items-table td:nth-child(3) { width: 70%; }
.items-table input, .items-table textarea {
  width:100%; box-sizing:border-box; padding:0.25rem;
}

.actions {
  display:flex;
  gap:1rem;
  align-items: center;
}

.primary-action {
  padding:0.75rem 1.5rem;
  border:none;
  background:#28a745;
  color:#fff;
  cursor:pointer;
  border-radius:4px;
  font-weight: bold;
}

.primary-action:hover {
  background:#218838;
}

.reject-action {
  padding:0.75rem 1.5rem;
  border:none;
  background:#dc3545;
  color:#fff;
  cursor:pointer;
  border-radius:4px;
}

.reject-action:hover {
  background:#c82333;
}

.completed-message {
  color: #155724;
  background: #d4edda;
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  font-weight: bold;
}
</style>