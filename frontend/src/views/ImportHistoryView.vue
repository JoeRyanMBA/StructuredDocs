<template>
  <div class="import-history">
    <Breadcrumbs />
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
      
      <div v-else class="no-imports" style="text-align: center; padding: 40px; color: #666;">
        <h3>No Import Documents Found</h3>
        <p>No import documents are currently in the system.</p>
      </div>
    </div>
  </div>
</template>

<script>
import Breadcrumbs from '@/components/Breadcrumbs.vue'

export default {
  name: 'ImportHistoryView',
  components: { Breadcrumbs },

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
      console.log('📊 Fetching import history...')
      console.log('🌐 Current URL:', window.location.href)
      console.log('🔗 API URL will be:', `${window.location.origin}/api/import/history`)
      
      this.loading = true
      this.error = null

      try {
        console.log('📡 Making request to /api/import/history')
        const res = await fetch('/api/import/history')
        console.log('📋 Response status:', res.status, 'OK:', res.ok)
        console.log('📋 Response headers:', Object.fromEntries(res.headers.entries()))
        
        if (!res.ok) {
          const errorText = await res.text()
          console.log('❌ Error response text:', errorText)
          throw new Error(`HTTP ${res.status}: ${errorText}`)
        }
        
        const data = await res.json()
        console.log('📄 Received data:', data)
        console.log('📊 Number of imports:', Array.isArray(data) ? data.length : 'Not an array')
        
        this.docs = Array.isArray(data) ? data : []
      } catch (e) {
        console.error('❌ Error fetching import history:', e)
        this.error = `Failed to load import history: ${e.message}`
      } finally {
        this.loading = false
      }
    }
  },

  created() {
    this.fetchHistory()
  },

  // Refresh data when entering this route
  beforeRouteEnter(to, from, next) {
    next(vm => {
      vm.fetchHistory()
    })
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
  padding-top: 0px; /* Top padding to account for fixed header */
  padding-left: 2rem;
  padding-right: 2rem;
  padding-bottom: 2rem;
}

.guidance-text {
  background: #f8f9fa;
  border-left: 4px solid #007acc;
  padding: 1rem;
  margin-bottom: 1.5rem;
  color: #495057;
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