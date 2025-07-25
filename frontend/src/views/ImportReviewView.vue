<template>
  <div class="import-review-view">
    <!-- Loading -->
    <div v-if="loading" class="loading">Loading…</div>

    <!-- Error -->
    <div v-else-if="error" class="error">{{ error }}</div>

    <!-- Data Loaded -->
    <div v-else>
      <h2>Review Import: {{ doc.filename }}</h2>
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

      <div class="actions">
        <button @click="exportImport">
          Export as Markdown
        </button>

        <!-- Corrected v-if syntax (no trailing space) -->
        <button
          v-if="doc.review_step === 'pending'"
          @click="smeApprove"
        >
          SME Approve
        </button>

        <!-- Corrected v-else-if syntax -->
        <button
          v-else-if="doc.review_step === 'sme_approved'"
          @click="commitImport"
        >
          Final Commit
        </button>

        <button @click="rejectImport">
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
      } catch (err) {
        console.error(err)
        this.error = 'Failed to load import data'
      } finally {
        this.loading = false
      }
    },

    // Added exportImport method
    async exportImport() {
      this.error = null
      try {
        console.log('Export clicked')  // debug log
        const res = await fetch(`/api/import/staging/${this.id}/export`)
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        const blob = await res.blob()
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = ''
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        URL.revokeObjectURL(url)
      } catch (err) {
        console.error(err)
        this.error = 'Export failed'
      }
    },

    // Added smeApprove method
    async smeApprove() {
      this.error = null
      try {
        console.log('SME clicked')  // debug log
        const res = await fetch(
          `/api/import/staging/${this.id}/sme_approve`,
          { method: 'POST' }
        )
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        await this.fetchImport()
      } catch (err) {
        console.error(err)
        this.error = 'SME approval failed'
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
.items-table { width:100%; border-collapse:collapse; margin-bottom:1rem; }
.items-table th, .items-table td { border:1px solid #ccc; padding:0.5rem; }
.items-table input, .items-table textarea {
  width:100%; box-sizing:border-box; padding:0.25rem;
}
.actions {
  display:flex;
  gap:1rem;
}
.actions button {
  padding:0.75rem 1.5rem;
  border:none;
  background:#005a9c;
  color:#fff;
  cursor:pointer;
  border-radius:4px;
}
.actions button:last-child { background:#c00; }
</style>