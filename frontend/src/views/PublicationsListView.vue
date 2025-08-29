<template>
  <div class="publications-list-view">
    <h1>Manage Publications</h1>
    <div v-if="loading" class="loading">Loading publications...</div>
    <div v-else-if="publications.length === 0" class="empty-state">
      <p>No publications found. <button @click="createPublication" class="link-btn">Create your first publication</button></p>
    </div>
    <div v-else class="publications-table-wrapper">
      <table class="publications-table">
        <thead>
          <tr>
            <th class="id-column">ID</th>
            <th>Title</th>
            <th>Type</th>
            <th>Status</th>
            <th>Pages</th>
            <th>Topics</th>
            <th>Last Updated</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="pub in publications" :key="pub.id">
            <td class="id-cell">{{ pub.id }}</td>
            <td>{{ pub.title }}</td>
            <td>{{ pub.type || 'N/A' }}</td>
            <td>{{ formatStatus(pub.status) }}</td>
            <td>{{ pub.pages_count || 0 }}</td>
            <td>{{ pub.topics_count || 0 }}</td>
            <td>{{ formatRelativeTime(pub.updated_at || pub.created_at) }}</td>
            <td>
              <button @click="viewPublication(pub)" class="table-btn">View</button>
              <button @click="editPublication(pub)" class="table-btn">Edit</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PublicationsListView',
  data() {
    return {
      loading: true,
      publications: []
    }
  },
  async created() {
    await this.loadPublications()
  },
  methods: {
    async loadPublications() {
      this.loading = true
      try {
        const res = await fetch('/api/publications')
        if (res.ok) {
          this.publications = await res.json()
        } else {
          this.publications = []
        }
      } catch {
        this.publications = []
      } finally {
        this.loading = false
      }
    },
    viewPublication(pub) {
      this.$router.push(`/publications/${pub.id}`)
    },
    editPublication(pub) {
      this.$router.push(`/publications/${pub.id}/edit`)
    },
    createPublication() {
      this.$router.push('/publications?template=new')
    },
    formatStatus(status) {
      const statusMap = {
        'draft': 'Draft',
        'published': 'Published',
        'archived': 'Archived',
        'processing': 'Processing'
      }
      return statusMap[status] || status
    },
    formatRelativeTime(timestamp) {
      if (!timestamp) return 'Unknown'
      const now = new Date()
      const time = new Date(timestamp)
      const diffMs = now - time
      const diffMins = Math.floor(diffMs / 60000)
      const diffHours = Math.floor(diffMs / 3600000)
      const diffDays = Math.floor(diffMs / 86400000)
      if (diffMins < 1) return 'Just now'
      if (diffMins < 60) return `${diffMins}m ago`
      if (diffHours < 24) return `${diffHours}h ago`
      if (diffDays < 7) return `${diffDays}d ago`
      return time.toLocaleDateString()
    }
  }
}
</script>

<style scoped>
.publications-list-view {
  max-width: 1100px;
  margin: 0 auto;
  padding: 2rem;
}
.publications-list-view h1 {
  color: var(--primary-deep-teal);
  margin-bottom: 2rem;
}
.publications-table-wrapper {
  overflow-x: auto;
}
.publications-table {
  width: 100%;
  border-collapse: collapse;
  background: var(--bg-primary-white);
  border-radius: 8px;
  box-shadow: var(--shadow-sm);
}
.publications-table th, .publications-table td {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--border-color-gray);
  text-align: left;
}
.publications-table th {
  background: var(--bg-light-mist-gray);
  font-weight: 600;
  color: var(--text-primary-charcoal);
}

.id-column,
.id-cell {
  width: 60px;
  text-align: center;
  font-size: 0.85rem;
  color: var(--text-secondary-cool-gray);
  white-space: nowrap;
}

.table-btn {
  background: var(--primary-deep-teal);
  color: white;
  border: none;
  border-radius: 4px;
  padding: 0.25rem 0.75rem;
  margin-right: 0.5rem;
  cursor: pointer;
  font-size: 0.85rem;
  transition: background 0.2s;
}
.table-btn:hover {
  background: var(--primary-medium-teal);
}
.empty-state {
  text-align: center;
  color: var(--text-secondary-cool-gray);
  padding: 2rem;
}
.link-btn {
  background: none;
  border: none;
  color: var(--primary-deep-teal);
  text-decoration: underline;
  cursor: pointer;
  font-size: inherit;
}
.link-btn:hover {
  color: var(--primary-medium-teal);
}
.loading {
  color: var(--primary-deep-teal);
  font-size: 1.1rem;
  text-align: center;
  margin-top: 2rem;
}
</style>
