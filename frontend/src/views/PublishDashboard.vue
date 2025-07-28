<template>
  <div class="publish-dashboard">
    <div class="dashboard-header">
      <h1>Publish Dashboard</h1>
      <p class="welcome-text">Create and manage your publications</p>
    </div>

    <!-- Key Metrics Cards -->
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
        <div class="metric-icon">📊</div>
        <div class="metric-content">
          <h3>This Month</h3>
          <div class="metric-number">{{ stats.publishedThisMonth || 0 }}</div>
          <div class="metric-detail">New publications</div>
        </div>
      </div>
    </div>

    <!-- Main Content Grid -->
    <div class="content-grid">
      
      <!-- Quick Actions -->
      <div class="dashboard-section">
        <h2>Quick Actions</h2>
        <div class="quick-actions-grid">
          <button class="action-card" @click="navigateTo('/publications')">
            <div class="action-icon">📋</div>
            <div class="action-content">
              <h3>Manage Publications</h3>
              <p>View and organize publications</p>
            </div>
          </button>
          <button class="action-card" @click="navigateTo('/publish/mobile-kb')">
            <div class="action-icon">📱</div>
            <div class="action-content">
              <h3>Publish Mobile KB</h3>
              <p>Create mobile knowledge base</p>
            </div>
          </button>
          <button class="action-card" @click="navigateTo('/publish/pdf')">
            <div class="action-icon">📄</div>
            <div class="action-content">
              <h3>Generate PDF</h3>
              <p>Export content as PDF</p>
            </div>
          </button>
        </div>

        <div class="action-section">
          <h3>Publication Templates</h3>
          <div class="template-buttons">
            <button class="template-btn" @click="createFromTemplate('mobile')">
              <span class="template-icon">📱</span>
              <span>Mobile Knowledge Base</span>
            </button>
            <button class="template-btn" @click="createFromTemplate('pdf')">
              <span class="template-icon">📄</span>
              <span>PDF Document</span>
            </button>
            <button class="template-btn" @click="createFromTemplate('web')">
              <span class="template-icon">🌐</span>
              <span>Web Publication</span>
            </button>
          </div>
        </div>
      </div>

      <!-- Recent Publications -->
      <div class="dashboard-section">
        <h2>Recent Publications</h2>
        <div class="publications-list">
          <div v-if="recentPublications.length === 0" class="empty-state">
            <p>No publications yet. Create your first publication!</p>
          </div>
          <div v-else>
            <div 
              v-for="publication in recentPublications" 
              :key="publication.id"
              class="publication-item"
              @click="viewPublication(publication)"
            >
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
            <div 
              v-for="publication in publications" 
              :key="publication.id"
              class="publication-card"
              @click="viewPublication(publication)"
            >
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
                  <button 
                    v-if="publication.status === 'published'" 
                    @click.stop="downloadPublication(publication)" 
                    class="card-action-btn primary"
                  >
                    Download
                  </button>
                  <button 
                    v-else-if="publication.status === 'draft'" 
                    @click.stop="publishNow(publication)" 
                    class="card-action-btn primary"
                  >
                    Publish
                  </button>
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
      <div class="loading-spinner">Loading publications...</div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PublishDashboard',
  
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
      recentPublications: []
    }
  },

  async created() {
    await this.loadDashboardData()
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
        console.error('Failed to load publish dashboard:', error)
      } finally {
        this.loading = false
      }
    },

    async loadPublications() {
      try {
        // Create mock data for prototype - replace with real API call
        const mockPublications = [
          {
            id: 1,
            title: 'Census Bureau Mobile Knowledge Base',
            type: 'Mobile KB',
            status: 'published',
            description: 'Comprehensive mobile knowledge base for field operations',
            pages_count: 42,
            topics_count: 28,
            file_size: 2048000,
            created_at: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
            updated_at: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString()
          },
          {
            id: 2,
            title: 'Data Collection Procedures Manual',
            type: 'PDF',
            status: 'draft',
            description: 'Detailed procedures for data collection teams',
            pages_count: 18,
            topics_count: 12,
            file_size: 1536000,
            created_at: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
            updated_at: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString()
          },
          {
            id: 3,
            title: 'Survey Quality Guidelines',
            type: 'Web Publication',
            status: 'published',
            description: 'Guidelines for maintaining survey quality standards',
            pages_count: 8,
            topics_count: 6,
            file_size: 512000,
            created_at: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
            updated_at: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString()
          }
        ]

        // Try to fetch real data, fall back to mock
        try {
          const res = await fetch('/api/publications/')
          if (res.ok) {
            const realPublications = await res.json()
            this.publications = realPublications.length > 0 ? realPublications : mockPublications
          } else {
            this.publications = mockPublications
          }
        } catch {
          this.publications = mockPublications
        }

        // Get recent publications (last 5, sorted by updated_at)
        this.recentPublications = [...this.publications]
          .sort((a, b) => new Date(b.updated_at) - new Date(a.updated_at))
          .slice(0, 5)
        
      } catch (error) {
        console.error('Failed to load publications:', error)
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
      this.$router.push(`/publications/${publication.id}/edit`)
    },

    publishNow(publication) {
      // Implement publish functionality
      console.log('Publishing:', publication.title)
    },

    downloadPublication(publication) {
      // Implement download functionality
      console.log('Downloading:', publication.title)
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
.publish-dashboard {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.dashboard-header {
  margin-bottom: 2rem;
  text-align: center;
}

.dashboard-header h1 {
  color: #005a9c;
  margin-bottom: 0.5rem;
  font-size: 2.5rem;
  font-weight: 300;
}

.welcome-text {
  color: #6c757d;
  font-size: 1.1rem;
  margin: 0;
}

/* Metrics Grid */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 3rem;
}

.metric-card {
  background: white;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.metric-icon {
  font-size: 2.5rem;
  min-width: 60px;
  text-align: center;
}

.metric-content h3 {
  margin: 0 0 0.25rem 0;
  color: #495057;
  font-size: 0.875rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.metric-number {
  font-size: 2rem;
  font-weight: 700;
  color: #005a9c;
  line-height: 1;
  margin-bottom: 0.25rem;
}

.metric-detail {
  color: #6c757d;
  font-size: 0.875rem;
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

/* Dashboard Sections */
.dashboard-section {
  background: white;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.dashboard-section h2 {
  margin: 0 0 1.5rem 0;
  color: #495057;
  font-size: 1.25rem;
  font-weight: 600;
  border-bottom: 2px solid #f8f9fa;
  padding-bottom: 0.5rem;
}

/* Quick Actions */
.quick-actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.action-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: #f8fafc;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: left;
}

.action-card:hover {
  background: #005a9c;
  border-color: #005a9c;
  color: white;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 90, 156, 0.2);
}

.action-icon {
  font-size: 1.5rem;
  opacity: 0.8;
}

.action-content h3 {
  margin: 0 0 0.25rem 0;
  font-size: 1rem;
  font-weight: 600;
}

.action-content p {
  margin: 0;
  font-size: 0.85rem;
  opacity: 0.8;
}

/* Template Section */
.action-section {
  border-top: 1px solid #f8f9fa;
  padding-top: 1.5rem;
}

.action-section h3 {
  margin: 0 0 1rem 0;
  color: #495057;
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
  border: 1px solid #e9ecef;
  border-radius: 4px;
  background: white;
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: left;
  font-size: 0.85rem;
}

.template-btn:hover {
  border-color: #005a9c;
  background: #f8f9fa;
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
  border: 1px solid #f8f9fa;
  border-radius: 6px;
  margin-bottom: 0.75rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.publication-item:hover {
  border-color: #005a9c;
  background: #f8f9fa;
}

.publication-item:last-child {
  margin-bottom: 0;
}

.publication-icon {
  font-size: 1.5rem;
  min-width: 30px;
}

.publication-content {
  flex: 1;
}

.publication-title {
  font-weight: 600;
  color: #495057;
  margin-bottom: 0.25rem;
}

.publication-description {
  color: #6c757d;
  font-size: 0.875rem;
  margin-bottom: 0.25rem;
}

.publication-meta {
  color: #adb5bd;
  font-size: 0.75rem;
}

.publication-status {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.7rem;
  font-weight: 500;
  text-transform: uppercase;
}

.publication-status.draft {
  background: #fff3cd;
  color: #856404;
}

.publication-status.published {
  background: #d4edda;
  color: #155724;
}

.publication-status.processing {
  background: #cce5ff;
  color: #004085;
}

/* Publication Cards */
.publications-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
}

.publication-card {
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.2s ease;
  background: white;
}

.publication-card:hover {
  border-color: #005a9c;
  box-shadow: 0 4px 12px rgba(0,90,156,0.15);
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
  flex: 1;
}

.card-title h3 {
  margin: 0;
  color: #495057;
  font-size: 1rem;
  font-weight: 600;
}

.card-badge {
  background: #e9ecef;
  color: #495057;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
}

.card-status {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.7rem;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.card-status.draft {
  background: #fff3cd;
  color: #856404;
}

.card-status.published {
  background: #d4edda;
  color: #155724;
}

.card-status.processing {
  background: #cce5ff;
  color: #004085;
}

.card-content {
  margin-bottom: 1rem;
}

.card-description {
  color: #6c757d;
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
  color: #6c757d;
}

.metric-label {
  font-weight: 500;
  color: #495057;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-date {
  color: #adb5bd;
  font-size: 0.75rem;
}

.card-actions {
  display: flex;
  gap: 0.5rem;
}

.card-action-btn {
  padding: 0.25rem 0.75rem;
  border: 1px solid #e9ecef;
  border-radius: 4px;
  background: white;
  color: #495057;
  cursor: pointer;
  font-size: 0.75rem;
  transition: all 0.2s ease;
}

.card-action-btn:hover {
  border-color: #005a9c;
  background: #f8f9fa;
}

.card-action-btn.primary {
  background: #005a9c;
  color: white;
  border-color: #005a9c;
}

.card-action-btn.primary:hover {
  background: #004080;
}

/* Empty States */
.empty-state {
  text-align: center;
  padding: 2rem;
  color: #6c757d;
}

.empty-state p {
  margin: 0;
}

.link-btn {
  background: none;
  border: none;
  color: #005a9c;
  text-decoration: underline;
  cursor: pointer;
  padding: 0;
  font-size: inherit;
}

.link-btn:hover {
  color: #004080;
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
  color: #005a9c;
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
