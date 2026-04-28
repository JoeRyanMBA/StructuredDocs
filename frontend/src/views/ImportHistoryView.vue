<template>
  <div class="import-history">
    <h2>Import History</h2>
    
    <p class="guidance-text">
      This is a list of imported topics. Available actions appear in the Actions column.
    </p>

    <div v-if="loading" class="loading">Loading…</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else>
      <table class="history-table" v-if="docs.length > 0">
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
      
      <div v-else class="no-imports">
        <h3>No Import Documents Found</h3>
        <p>No import documents are currently in the system.</p>
      </div>
    </div>
  </div>
</template>

<script>
import { apiGet } from '@/api/base'

export default {
  name: 'ImportHistoryView',

  data() {
    return {
      docs: [],
      loading: true,
      error: null,
      hasLoadedOnce: false
    }
  },

  methods: {
    formatDate(iso) {
      if (!iso) return 'Unknown'
      
      try {
        // Server sends timestamps like "2025-08-01T14:16:53.860038"
        // These are in UTC time, so we need to parse them as UTC
        const date = new Date(iso + 'Z') // Force UTC parsing
        
        // Check if the date is invalid
        if (isNaN(date.getTime())) {
          return 'Invalid Date'
        }
        
        // Format to local timezone with more readable format
        const options = {
          year: 'numeric',
          month: 'numeric', 
          day: 'numeric',
          hour: 'numeric',
          minute: '2-digit',
          second: '2-digit',
          timeZoneName: 'short'
        }
        
        return date.toLocaleString('en-US', options)
      } catch (error) {
        console.error('Error formatting date:', error, 'Input:', iso)
        return 'Invalid Date'
      }
    },

    async fetchHistory() {
      const isInitialLoad = !this.hasLoadedOnce
      if (isInitialLoad) {
        this.loading = true
        this.error = null
      }

      try {
        const data = await apiGet('/api/import/history')
        this.docs = Array.isArray(data) ? data : []
        this.hasLoadedOnce = true
        this.error = null
      } catch (e) {
        console.error('❌ Error fetching import history:', e)
        const raw = String(e?.message || '')
        const lower = raw.toLowerCase()
        if (lower.includes('signature verification failed')) {
          this.error = this.hasLoadedOnce
            ? null
            : 'Your session expired. Please sign in again to view import history.'
          return
        }

        // If data is already visible, avoid replacing it with an error screen.
        this.error = this.hasLoadedOnce ? null : `Failed to load import history: ${raw}`
      } finally {
        if (isInitialLoad) {
          this.loading = false
        }
      }
    }
  },

  created() {
    this.fetchHistory()
  },

  // Refresh data when route updates (same component)
  beforeRouteUpdate(to, from, next) {
    this.fetchHistory()
    next()
  }
}
</script>

<style scoped>
.import-history {
  padding: 2rem;
  background-color: var(--bg-light-mist-gray);
}

.guidance-text {
  background: var(--bg-light-mist-gray);
  border-left: 4px solid var(--primary-deep-teal);
  border-radius: .75rem;
  padding: 1rem;
  margin-bottom: 1.5rem;
  color: var(--text-secondary-cool-gray);
  font-size: 0.95rem;
  line-height: 1.5;
}

.history-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1rem;
}

.history-table th,
.history-table td {
  border: 1px solid var(--border-gray);
  padding: 0.5rem;
}

.loading {
  font-style: italic;
}

.error {
  color: var(--error-coral-red);
  margin-top: 1rem;
}

.no-imports {
  text-align: center;
  padding: 40px;
  color: var(--text-secondary-cool-gray);
}
</style>