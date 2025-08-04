<template>
  <div class="publish-mobile-kb">
    <Breadcrumbs />
    <h2>Publish Mobile Knowledge Base</h2>
    <p class="description">
      Create mobile-first knowledge bases optimized for field staff on iPhones and iPads.
      These are lightweight, offline-ready HTML files that work without internet connectivity.
    </p>

    <div class="features-grid">
      <div class="feature-card">
        <div class="feature-icon">📱</div>
        <h3>Mobile-First Design</h3>
        <p>Optimized for touch interfaces and small screens</p>
      </div>
      <div class="feature-card">
        <div class="feature-icon">⚡</div>
        <h3>Lightweight</h3>
        <p>Fast loading with minimal data usage</p>
      </div>
      <div class="feature-card">
        <div class="feature-icon">🔌</div>
        <h3>Offline Ready</h3>
        <p>Works without internet connection</p>
      </div>
      <div class="feature-card">
        <div class="feature-icon">🌙</div>
        <h3>Dark Mode</h3>
        <p>Automatic dark mode support</p>
      </div>
    </div>

    <div class="publications-section">
      <h3>Select Publication to Export</h3>
      <div v-if="loading" class="loading">Loading publications...</div>
      <div v-else-if="error" class="error">{{ error }}</div>
      <div v-else-if="publications.length === 0" class="empty">
        No publications available. Create a publication first.
      </div>
      <div v-else class="publications-grid">
        <div 
          v-for="pub in publications" 
          :key="pub.id" 
          class="publication-card"
          @click="selectPublication(pub)"
        >
          <div class="card-header">
            <h4>{{ pub.title }}</h4>
            <span class="publication-date">{{ formatDate(pub.created_at) }}</span>
          </div>
          <p class="publication-description">{{ pub.description || 'No description' }}</p>
          <div class="card-actions">
            <button @click.stop="previewMobileKB(pub.id)" class="btn-preview">
              👁️ Preview
            </button>
            <button @click.stop="exportMobileKB(pub.id)" class="btn-export">
              📥 Download
            </button>
          </div>
        </div>
      </div>
    </div>

    <div class="help-section">
      <h3>📚 Usage Instructions</h3>
      <div class="instructions">
        <div class="instruction-step">
          <span class="step-number">1</span>
          <div class="step-content">
            <strong>Export Knowledge Base</strong>
            <p>Click "Download" to get a single HTML file containing your entire knowledge base.</p>
          </div>
        </div>
        <div class="instruction-step">
          <span class="step-number">2</span>
          <div class="step-content">
            <strong>Deploy to Field Staff</strong>
            <p>Share the HTML file via email, cloud storage, or mobile device management systems.</p>
          </div>
        </div>
        <div class="instruction-step">
          <span class="step-number">3</span>
          <div class="step-content">
            <strong>Access Offline</strong>
            <p>Staff can open the file in any mobile browser and bookmark it for offline access.</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Breadcrumbs from '@/components/Breadcrumbs.vue'

export default {
  name: 'PublishMobileKB',
  components: { Breadcrumbs },
  data() {
    return {
      publications: [],
      loading: true,
      error: null
    }
  },
  async created() {
    await this.fetchPublications()
  },
  methods: {
    async fetchPublications() {
      this.loading = true
      this.error = null
      
      try {
        const res = await fetch('/api/publications')
        if (!res.ok) throw new Error(`Status ${res.status}`)
        
        const data = await res.json()
        // Ensure publications are sorted by most recent first
        this.publications = data.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
      } catch (err) {
        console.error('Failed to fetch publications:', err)
        this.error = 'Failed to load publications'
      } finally {
        this.loading = false
      }
    },
    
    selectPublication(pub) {
      // Navigate to publication view
      this.$router.push({ name: 'PublicationView', params: { id: pub.id } })
    },
    
    previewMobileKB(pubId) {
      // Open preview in mobile-sized window
      const previewUrl = `/api/publications/${pubId}/export/mobile-kb`
      const previewWindow = window.open(
        previewUrl, 
        '_blank', 
        'width=375,height=812,scrollbars=yes,resizable=yes,toolbar=no,menubar=no'
      )
      if (previewWindow) {
        previewWindow.focus()
      }
    },
    
    exportMobileKB(pubId) {
      // Download the mobile knowledge base HTML file
      window.open(`/api/publications/${pubId}/export/mobile-kb`, '_blank')
    },
    
    formatDate(dateString) {
      // Parse the date and ensure it's treated as UTC, then convert to local time
      const date = new Date(dateString + (dateString.includes('Z') ? '' : 'Z'))
      const now = new Date()
      const diffTime = Math.abs(now - date)
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
      
      // Format time in local timezone
      const timeString = date.toLocaleTimeString(undefined, { 
        hour: 'numeric', 
        minute: '2-digit',
        hour12: true
      })
      
      if (diffDays === 1) {
        return `Today ${timeString}`
      } else if (diffDays === 2) {
        return `Yesterday ${timeString}`
      } else if (diffDays <= 7) {
        return `${diffDays - 1} days ago ${timeString}`
      } else {
        // Format date in local timezone
        const formattedDate = date.toLocaleDateString(undefined, { 
          year: 'numeric', 
          month: 'short', 
          day: 'numeric' 
        })
        return `${formattedDate} ${timeString}`
      }
    }
  }
}
</script>

<style scoped>
.publish-mobile-kb {
  margin: 0 auto;
}

.description {
  font-size: 1.1rem;
  color: #6c757d;
  margin-bottom: 2rem;
  line-height: 1.6;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 3rem;
}

.feature-card {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  text-align: center;
  border: 1px solid #e9ecef;
}

.feature-icon {
  font-size: 2rem;
  margin-bottom: 1rem;
}

.feature-card h3 {
  margin: 0 0 0.5rem 0;
  color: #212529;
  font-size: 1.1rem;
}

.feature-card p {
  margin: 0;
  color: #6c757d;
  font-size: 0.9rem;
}

.publications-section {
  margin-bottom: 3rem;
}

.publications-section h3 {
  margin-bottom: 1.5rem;
  color: #212529;
}

.loading, .error, .empty {
  padding: 2rem;
  text-align: center;
  border-radius: 8px;
  background: #f8f9fa;
  color: #6c757d;
}

.error {
  background: #f8d7da;
  color: #721c24;
}

.publications-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.publication-card {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  border: 1px solid #e9ecef;
  cursor: pointer;
  transition: all 0.2s ease;
}

.publication-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0,0,0,0.15);
}

.publication-card h4 {
  margin: 0;
  color: #212529;
  font-size: 1.2rem;
  flex: 1;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: start;
  margin-bottom: 0.75rem;
}

.publication-date {
  font-size: 0.8rem;
  color: #6c757d;
  background: #f8f9fa;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  white-space: nowrap;
  margin-left: 1rem;
}

.publication-description {
  margin: 0 0 1.5rem 0;
  color: #6c757d;
  line-height: 1.5;
}

.card-actions {
  display: flex;
  gap: 0.75rem;
}

.btn-preview, .btn-export {
  flex: 1;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s ease;
}

.btn-preview {
  background: #6c757d;
  color: white;
}

.btn-preview:hover {
  background: #5a6268;
}

.btn-export {
  background: #28a745;
  color: white;
}

.btn-export:hover {
  background: #218838;
}

.help-section {
  background: #f8f9fa;
  padding: 2rem;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.help-section h3 {
  margin: 0 0 1.5rem 0;
  color: #212529;
}

.instructions {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.instruction-step {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
}

.step-number {
  background: #005a9c;
  color: white;
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  flex-shrink: 0;
}

.step-content {
  flex: 1;
}

.step-content strong {
  display: block;
  margin-bottom: 0.25rem;
  color: #212529;
}

.step-content p {
  margin: 0;
  color: #6c757d;
  line-height: 1.5;
}

/* Mobile optimizations */
@media (max-width: 768px) {
  .publish-mobile-kb {
    padding: 1rem;
  }
  
  .features-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  
  .publications-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  
  .card-actions {
    flex-direction: column;
  }
  
  .instruction-step {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }
  
  .help-section {
    padding: 1.5rem;
  }
}
</style>
