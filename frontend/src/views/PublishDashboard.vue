<template>
  
  <div class="publish-dashboard">
    <div class="dashboard-header">
      <h1>Publication Dashboard <HelpIcon feature="publish.dashboard" /></h1>
      <p class="subtitle">Manage and download your publications</p>
    </div>
    <!-- Compact Toolbar for Metrics -->
    <CompactToolbar :showMetrics="true" :showCalendar="false">
      <template #metrics>
        <div class="metrics-grid">
          <div class="metric-card">
            <div class="metric-icon">📤</div>
            <div class="metric-content">
              <h3>Publications</h3>
              <div class="metric-number">{{ stats.totalPublications || 0 }}</div>
              <div class="metric-detail">{{ stats.activePublications || 0 }} Active</div>
            </div>
          </div>
          <div class="metric-card">
            <div class="metric-icon">📱</div>
            <div class="metric-content">
              <h3>Mobile KB</h3>
              <div class="metric-number">{{ stats.mobileKBPages || 0 }}</div>
              <div class="metric-detail">Pages published</div>
            </div>
          </div>
          <div class="metric-card">
            <div class="metric-icon">📄</div>
            <div class="metric-content">
              <h3>PDF Documents</h3>
              <div class="metric-number">{{ stats.pdfDocuments || 0 }}</div>
              <div class="metric-detail">Ready for download</div>
            </div>
          </div>
          <div class="metric-card">
            <div class="metric-icon">🗓️</div>
            <div class="metric-content">
              <h3>This Month</h3>
              <div class="metric-number">{{ stats.publishedThisMonth || 0 }}</div>
              <div class="metric-detail">New publications</div>
            </div>
          </div>
        </div>
      </template>
    </CompactToolbar>
    <!-- Audience tag selector -->
    <div class="audience-bar">
      <label class="audience-label">🎯 Audience Tags:</label>
      <div class="tag-checkboxes">
        <label v-for="tag in allTags" :key="tag.id" class="tag-check">
          <input type="checkbox" :value="tag.id" v-model="selectedTagIds" />
          {{ tag.name }}
        </label>
        <span v-if="allTags.length === 0" class="no-tags-hint">No tags defined yet.</span>
      </div>
      <span class="audience-hint">Only snippets tagged with the selected audiences will be included in exports.</span>
    </div>
    <!-- Publications Table (replaces quick actions) -->
    <div class="dashboard-section publications-table-section">
      <h2>Manage Publications</h2>
      <div v-if="publications.length === 0" class="empty-state">
        <p>No publications found. <button @click="navigateTo('/publications?template=new')" class="link-btn">Create your first publication</button></p>
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
            <tr v-for="publication in publications" :key="publication.id">
              <td class="id-cell">{{ publication.id }}</td>
              <td>{{ publication.title }}</td>
              <td>{{ publication.type || 'N/A' }}</td>
              <td>{{ formatStatus(publication.status) }}</td>
              <td>{{ publication.pages_count || 0 }}</td>
              <td>{{ publication.topics_count || 0 }}</td>
              <td>{{ formatRelativeTime(publication.updated_at || publication.created_at) }}</td>
              <td>
                <button @click="viewPublication(publication)" class="table-btn">View</button>
                <button @click="editPublication(publication)" class="table-btn">Edit</button>
                <button @click="downloadMobileKB(publication)" class="table-btn" :disabled="exportingKb.has(publication.id)">
                  <span v-if="exportingKb.has(publication.id)"><i class="bi bi-arrow-clockwise spin"></i> Exporting…</span>
                  <span v-else>Export KB</span>
                </button>
                <button @click="downloadPDF(publication)" class="table-btn" :disabled="exportingPdf.has(publication.id)">
                  <span v-if="exportingPdf.has(publication.id)"><i class="bi bi-arrow-clockwise spin"></i> Exporting…</span>
                  <span v-else>Export PDF</span>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Main Content Grid -->
    <div class="content-grid">
      <!-- Recent Publications -->
      <div class="dashboard-section">
        <h2>Recent Publications</h2>
        <div class="publications-list">
          <div v-if="recentPublications.length === 0" class="empty-state">
            <p>No publications yet. Create your first publication!</p>
          </div>
          <div v-else>
            <div v-for="publication in recentPublications" :key="publication.id" class="publication-item" @click="viewPublication(publication)">
              <div class="publication-icon">{{ getPublicationIcon(publication.type) }}</div>
              <div class="publication-content">
                <div class="publication-title">{{ publication.title }}</div>
                <div class="publication-description">{{ publication.type }} • {{ publication.pages_count || 0 }} pages</div>
                <div class="publication-meta">{{ formatRelativeTime(publication.updated_at) }}</div>
              </div>
              <div class="publication-status" :class="publication.status">{{ formatStatus(publication.status) }}</div>
            </div>
          </div>
        </div>
      </div>
      <!-- Publication Analytics -->
      <div class="dashboard-section full-width">
        <h2>Publication Overview</h2>
        <div class="publications-overview">
          <div v-if="publications.length === 0" class="empty-state">
            <p>No publications found. <button @click="navigateTo('/publications')" class="link-btn">Create your first publication</button></p>
          </div>
          <div v-else class="publications-grid">
            <div v-for="publication in publications" :key="publication.id" class="publication-card" @click="viewPublication(publication)">
              <div class="card-header">
                <div class="card-title">
                  <h3>{{ publication.title }}</h3>
                  <span class="card-badge">{{ publication.type }}</span>
                </div>
                <span class="card-status" :class="publication.status">{{ formatStatus(publication.status) }}</span>
              </div>
              <div class="card-content">
                <p class="card-description">{{ publication.description || 'No description available' }}</p>
                <div class="card-metrics">
                  <span class="card-metric">
                    <span class="metric-label">Pages:</span>
                    {{ publication.pages_count || 0 }}
                  </span>
                  <span class="card-metric">
                    <span class="metric-label">Topics:</span>
                    {{ publication.topics_count || 0 }}
                  </span>
                  <span class="card-metric">
                    <span class="metric-label">Size:</span>
                    {{ formatFileSize(publication.file_size) }}
                  </span>
                </div>
              </div>
              <div class="card-footer">
                <span class="card-date">Updated {{ formatRelativeTime(publication.updated_at || publication.created_at) }}</span>
                <div class="card-actions">
                  <button v-if="publication.status === 'published'" @click.stop="downloadPublication(publication)" class="card-action-btn primary" :disabled="exportingPdf.has(publication.id)">
                    <span v-if="exportingPdf.has(publication.id)"><i class="bi bi-arrow-clockwise spin"></i> Exporting…</span>
                    <span v-else>Export PDF</span>
                  </button>
                  <button v-else-if="publication.status === 'draft'" @click.stop="publishNow(publication)" class="card-action-btn primary">Save Snapshot</button>
                  <button @click.stop="editPublication(publication)" class="card-action-btn">Edit</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <!-- Loading State -->
    <div v-if="loading" class="loading-overlay">
      <div class="loading-spinner"></div>
    </div>
  </div>
</template>
<script>
import CompactToolbar from '@/components/CompactToolbar.vue'
import HelpIcon from '@/components/HelpIcon.vue'

export default {
  components: { 
    CompactToolbar,
    HelpIcon,
  },
  name: 'PublishDashboard',
  props: {
    notifications: {
      type: Array,
      default: () => []
    },
    globalNotifications: {
      type: Array,
      default: () => []
    },
    markNotificationRead: {
      type: Function,
      required: true
    }
  },
  data() {
    return {
      loading: true,
      stats: {
        totalPublications: 0,
        activePublications: 0,
        mobileKBPages: 0,
        pdfDocuments: 0,
        publishedThisMonth: 0
      },
      publications: [],
      recentPublications: [],
      allTags: [],
      selectedTagIds: [],
      exportingPdf: new Set(),
      exportingKb: new Set(),
    }
  },
  
  computed: {
    mergedNotifications() {
      // Combine global and dashboard-specific notifications, removing duplicates by id
      const all = [...(this.globalNotifications || []), ...(this.notifications || [])]
      const seen = new Set()
      return all.filter(n => {
        if (!n || !n.id) return true
        if (seen.has(n.id)) return false
        seen.add(n.id)
        return true
      })
    }
  },
  
  async created() {
    await this.loadDashboardData()
    await this.loadTags()
  },
  methods: {
    async loadDashboardData() {
      this.loading = true
      try {
        await Promise.all([
          this.loadPublications(),
          this.loadStats()
        ])
      } catch (error) {
        console.error('Failed to load publication dashboard:', error)
      } finally {
        this.loading = false
      }
    },
    async loadPublications() {
      try {
        // Fetch real data from backend API
        const res = await fetch('/api/publications')
        if (res.ok) {
          const data = await res.json()
          this.publications = Array.isArray(data) ? data : (data.publications ?? [])
        } else {
          this.publications = []
        }
        // Get recent publications (last 5, sorted by updated_at)
        this.recentPublications = [...this.publications]
          .sort((a, b) => new Date(b.updated_at) - new Date(a.updated_at))
          .slice(0, 5)
      } catch (error) {
        console.error('Failed to load publications:', error)
        this.publications = []
        this.recentPublications = []
      }
    },
    async loadStats() {
      try {
        // Calculate stats from publications data
        const total = this.publications.length
        const active = this.publications.filter(p => p.status === 'published').length
        const mobileKB = this.publications.filter(p => p.type === 'Mobile KB').reduce((sum, p) => sum + (p.pages_count || 0), 0)
        const pdfs = this.publications.filter(p => p.type === 'PDF').length
        // Calculate published this month
        const oneMonthAgo = new Date()
        oneMonthAgo.setMonth(oneMonthAgo.getMonth() - 1)
        const publishedThisMonth = this.publications.filter(p => 
          p.status === 'published' && 
          p.updated_at && 
          new Date(p.updated_at) > oneMonthAgo
        ).length
        this.stats = {
          totalPublications: total,
          activePublications: active,
          mobileKBPages: mobileKB,
          pdfDocuments: pdfs,
          publishedThisMonth
        }
      } catch (error) {
        console.error('Failed to calculate stats:', error)
      }
    },
    createFromTemplate(type) {
      const templates = {
        'mobile': '/publish/mobile-kb?template=new',
        'pdf': '/publish/pdf?template=new', 
        'web': '/publications?template=web'
      }
      this.navigateTo(templates[type])
    },
    viewPublication(publication) {
      this.$router.push(`/publications/${publication.id}`)
    },
    editPublication(publication) {
      this.$router.push(`/publications/${publication.id}`)
    },
    async publishNow(publication) {
      // Persist publish action to backend
      try {
        const res = await fetch(`/api/publications/${publication.id}/publish`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' }
        })
        if (!res.ok) throw new Error('Failed to publish')
        await this.loadPublications()
      } catch (err) {
        console.error('Error publishing:', err)
      }
    },
    async downloadMobileKB(publication) {
      if (this.exportingKb.has(publication.id)) return
      this.exportingKb = new Set([...this.exportingKb, publication.id])
      try {
        const params = this.selectedTagIds.map(id => `tag_ids=${id}`).join('&')
        window.open(`/api/publications/${publication.id}/export/mobile-kb${params ? '?' + params : ''}`, '_blank')
        // Give the browser a moment to initiate the download before re-enabling
        await new Promise(r => setTimeout(r, 2000))
      } finally {
        const next = new Set(this.exportingKb)
        next.delete(publication.id)
        this.exportingKb = next
      }
    },
    async downloadPDF(publication) {
      if (this.exportingPdf.has(publication.id)) return
      this.exportingPdf = new Set([...this.exportingPdf, publication.id])
      try {
        const params = this.selectedTagIds.map(id => `tag_ids=${id}`).join('&')
        const pdfUrl = `/api/publications/${publication.id}/export/pdf${params ? '?' + params : ''}`
        const token = localStorage.getItem('access_token')
        const response = await fetch(pdfUrl, {
          headers: token ? { 'Authorization': `Bearer ${token}` } : {}
        })
        if (!response.ok) throw new Error(`Export failed (${response.status})`)
        const blob = await response.blob()
        const objectUrl = URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = objectUrl
        link.download = `${publication.title || 'publication'}.pdf`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        URL.revokeObjectURL(objectUrl)
      } catch (e) {
        console.error('PDF export failed:', e)
        alert(`Export failed: ${e.message}`)
      } finally {
        const next = new Set(this.exportingPdf)
        next.delete(publication.id)
        this.exportingPdf = next
      }
    },
    downloadPublication(publication) {
      this.downloadPDF(publication)
    },
    async loadTags() {
      try {
        const res = await fetch('/api/tags/')
        if (res.ok) {
          const data = await res.json()
          this.allTags = Array.isArray(data) ? data : (data.tags || [])
        }
      } catch (e) {
        console.error('Failed to load tags', e)
      }
    },
    navigateTo(path) {
      this.$router.push(path)
    },
    getPublicationIcon(type) {
      const icons = {
        'Mobile KB': '📱',
        'PDF': '📄',
        'Web Publication': '🌐'
      }
      return icons[type] || '📄'
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
    formatFileSize(bytes) {
      if (!bytes) return 'Unknown'
      const sizes = ['Bytes', 'KB', 'MB', 'GB']
      if (bytes === 0) return '0 Bytes'
      const i = Math.floor(Math.log(bytes) / Math.log(1024))
      return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i]
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
.audience-bar {
  background: #f0f4ff;
  border: 1px solid #c5d3f0;
  border-radius: 8px;
  padding: 0.75rem 1rem;
  margin-bottom: 1.5rem;
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  gap: 0.5rem;
}
.audience-label { font-weight: 600; font-size: 0.88rem; color: #205493; white-space: nowrap; padding-top: 2px; }
.tag-checkboxes { display: flex; flex-wrap: wrap; gap: 0.5rem; flex: 1; }
.tag-check {
  display: flex; align-items: center; gap: 0.3rem;
  font-size: 0.85rem; cursor: pointer;
  background: #fff; border: 1px solid #c5d3f0; border-radius: 12px;
  padding: 0.2rem 0.6rem;
}
.tag-check input { cursor: pointer; }
.no-tags-hint { color: #6c757d; font-size: 0.82rem; font-style: italic; }
.audience-hint { width: 100%; color: #6c757d; font-size: 0.78rem; margin-top: 0.25rem; }
.publish-dashboard {
  margin: 0 auto;
  padding: 0 2rem 2rem; /* remove top space before header */
  background-color: var(--bg-light-mist-gray);
}

.dashboard-header {
  margin-bottom: 2rem;
  text-align: center;
}

.dashboard-header h1 {
  color: var(--primary-deep-teal);
  margin-bottom: 0.5rem;
  font-size: 2.5rem;
  font-weight: 300;
}

.welcome-text {
  color: var(--text-secondary-cool-gray);
  font-size: 1.1rem;
  margin: 0;
}

/* Metrics Grid */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 3rem;
}

/* Main Content Grid */
.content-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  margin-bottom: 2rem;
}

.content-grid .full-width {
  grid-column: 1 / -1;
}

/* Dashboard Sections: use global .dashboard-section from style.css */



/* Manage Publications Table */
.publications-table-section {
  margin-bottom: 2rem;
}

.publications-table-wrapper {
  overflow-x: auto;
}

.publications-table {
  width: 100%;
  background: var(--bg-primary-white);
  border-radius: 8px;
  box-shadow: var(--shadow-sm);
  border-collapse: collapse;
}

.publications-table th,
.publications-table td {
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
  margin-bottom: 0.35rem;
  cursor: pointer;
  font-size: 0.85rem;
  transition: background 0.2s;
}

.table-btn:hover {
  background: var(--primary-medium-teal);
}

.table-btn:disabled,
.card-action-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
.spin {
  display: inline-block;
  animation: spin 0.75s linear infinite;
}

/* Template Section */
.action-section {
  border-top: 1px solid var(--bg-light-mist-gray);
  padding-top: 1.5rem;
}

.action-section h3 {
  margin: 0 0 1rem 0;
  color: var(--text-primary-charcoal);
  font-size: 1rem;
  font-weight: 600;
}

.template-buttons {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.template-btn {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  border: 1px solid var(--border-color-gray);
  border-radius: 4px;
  background: var(--bg-primary-white);
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: left;
  font-size: 0.85rem;
}

.template-btn:hover {
  border-color: var(--primary-deep-teal);
  background: var(--bg-light-mist-gray);
}

.template-icon {
  font-size: 1rem;
}

/* Publication Items */
.publications-list {
  max-height: 400px;
  overflow-y: auto;
}

.publication-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  border: 1px solid var(--bg-light-mist-gray);
  border-radius: 6px;
  margin-bottom: 0.75rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.publication-item:hover {
  border-color: var(--primary-deep-teal);
  background: var(--bg-light-mist-gray);
}

.publication-item:last-child {
  margin-bottom: 0;
}

.publication-icon {
  font-size: 1.5rem;
  min-width: 30px;
}

.publication-status.draft {
  background: var(--extended-warm-taupe);
  color: var(--warning-amber);
}

.publication-status.published {
  background: var(--extended-cool-mint);
  color: var(--success-mint-green);
}

.publication-status.processing {
  background: var(--extended-lavender-gray);
  color: var(--primary-deep-teal);
}

/* Publication Cards */
.publications-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
}

.publication-card {
  border: 1px solid var(--border-color-gray);
  border-radius: 8px;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.2s ease;
  background: var(--bg-primary-white);
}

.publication-card:hover {
  border-color: var(--primary-deep-teal);
  box-shadow: var(--shadow-md);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  }

.card-status.draft {
  background: var(--extended-warm-taupe);
  color: var(--warning-amber);
}

.card-status.published {
  background: var(--extended-cool-mint);
  color: var(--success-mint-green);
}

.card-status.processing {
  background: var(--extended-lavender-gray);
  color: var(--primary-deep-teal);
}

.card-content {
  margin-bottom: 1rem;
}

.card-description {
  color: var(--text-secondary-cool-gray);
  font-size: 0.875rem;
  line-height: 1.4;
  margin: 0 0 0.75rem 0;
}

.card-metrics {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}

.card-metric {
  font-size: 0.75rem;
  color: var(--text-secondary-cool-gray);
}

/* metric-number and metric-detail now centralized in global style.css */

.card-actions {
  display: flex;
  gap: 0.5rem;
}

.card-action-btn {
  padding: 0.25rem 0.75rem;
  border: 1px solid var(--border-color-gray);
  border-radius: 4px;
  background: var(--bg-primary-white);
  color: var(--text-primary-charcoal);
  cursor: pointer;
  font-size: 0.75rem;
  transition: all 0.2s ease;
}

.card-action-btn:hover {
  border-color: var(--primary-deep-teal);
  background: var(--bg-light-mist-gray);
}

.card-action-btn.primary {
  background: var(--primary-deep-teal);
  color: white;
  border-color: var(--primary-deep-teal);
}

.card-action-btn.primary:hover {
  background: var(--primary-medium-teal);
}

/* Empty States */
.empty-state {
  text-align: center;
  padding: 2rem;
  color: var(--text-secondary-cool-gray);
}

.empty-state p {
  margin: 0;
}

.link-btn {
  background: none;
  border: none;
  color: var(--primary-deep-teal);
  text-decoration: underline;
  cursor: pointer;
  padding: 0;
  font-size: inherit;
}

.link-btn:hover {
  color: var(--primary-medium-teal);
}

/* Loading */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.loading-spinner {
  color: var(--primary-deep-teal);
  font-size: 1.1rem;
}

/* Responsive Design */
@media (max-width: 768px) {
  .publish-dashboard {
    padding: 1rem;
  }
  
  .metrics-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  
  .content-grid {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }
  
  .publications-grid {
    grid-template-columns: 1fr;
  }
  
  .dashboard-header h1 {
    font-size: 2rem;
  }
}
</style>
