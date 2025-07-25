<template>
  <div class="import-history">
    <h2>Import History</h2>

    <div v-if="loading" class="loading">Loading…</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else>
      <table class="history-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>File</th>
            <th>Type</th>
            <th>Status</th>
            <th>When</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="doc in docs" :key="doc.id">
            <td>{{ doc.id }}</td>
            <td>{{ doc.filename }}</td>
            <td>{{ doc.type }}</td>
            <td>{{ doc.status }}</td>
            <td>{{ formatDate(doc.created_at) }}</td>
            <td>
              <router-link
                v-if="doc.status === 'staging'"
                :to="{ name: 'ImportReview', params: { id: doc.id } }"
              >
                Review
              </router-link>
              <span v-else>—</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ImportHistoryView',

  data() {
    return {
      docs: [],
      loading: true,
      error: null
    }
  },

  methods: {
    formatDate(iso) {
      // e.g. "7/23/2025, 11:30:44 PM"
      return new Date(iso).toLocaleString()
    },

    async fetchHistory() {
      this.loading = true
      this.error = null

      try {
        const res = await fetch('/api/import/history')
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        this.docs = await res.json()
      } catch (e) {
        console.error(e)
        this.error = 'Failed to load import history'
      } finally {
        this.loading = false
      }
    }
  },

  created() {
    this.fetchHistory()
  }
}
</script>

<style scoped>
.history-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1rem;
}

.history-table th,
.history-table td {
  border: 1px solid #ccc;
  padding: 0.5rem;
}

.loading {
  font-style: italic;
}

.error {
  color: #c00;
  margin-top: 1rem;
}
</style>