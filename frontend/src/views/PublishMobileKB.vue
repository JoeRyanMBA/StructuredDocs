<template>
  <div class="publish-mobile-kb">
    <h2>Publish Mobile Knowledge Base</h2>
    <p class="description">
      Create mobile-first knowledge bases optimized for field staff on iPhones and iPads.
      These are lightweight, offline-ready HTML files that work without internet connectivity.
    </p>

    <div class="features-list">
      <div class="feature-item">
        <span class="feature-icon">📱</span>
        <div class="feature-content">
          <strong>Mobile-First Design</strong> - Optimized for touch interfaces and small screens
        </div>
      </div>
      <div class="feature-item">
        <span class="feature-icon">⚡</span>
        <div class="feature-content">
          <strong>Lightweight</strong> - Fast loading with minimal data usage
        </div>
      </div>
      <div class="feature-item">
        <span class="feature-icon">🔌</span>
        <div class="feature-content">
          <strong>Offline Ready</strong> - Works without internet connection
        </div>
      </div>
      <div class="feature-item">
        <span class="feature-icon">🌙</span>
        <div class="feature-content">
          <strong>Dark Mode</strong> - Automatic dark mode support
        </div>
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

export default {
  name: 'PublishMobileKB',
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
      // Open preview in mobile-sized window using the preview endpoint
      const previewUrl = `/api/publications/${pubId}/preview/mobile-kb`
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
  padding: 2rem;
  background-color: var(--bg-light-mist-gray);
}

.description {
  font-size: 1.1rem;
  color: var(--text-secondary-cool-gray);
  margin-bottom: 2rem;
  line-height: 1.6;
}

.features-list {
  background: var(--bg-primary-white);
  border-radius: 8px;
  border: 1px solid var(--border-color-gray);
  margin-bottom: 3rem;
  overflow: hidden;
}

.feature-item {
  display: flex;
  align-items: center;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid var(--border-color-gray);
  gap: 1rem;
}

.feature-item:last-child {
  border-bottom: none;
}

.feature-icon {
  font-size: 1.5rem;
  flex-shrink: 0;
}

.feature-content {
  flex: 1;
  color: var(--text-secondary-cool-gray);
  line-height: 1.4;
}

.feature-content strong {
  color: var(--text-primary-charcoal);
}

.publications-section {
  margin-bottom: 3rem;
}

.publications-section h3 {
  margin-bottom: 1.5rem;
  color: var(--text-primary-charcoal);
}

.loading, .error, .empty {
  padding: 2rem;
  text-align: center;
  border-radius: 8px;
  background: var(--bg-light-mist-gray);
  color: var(--text-secondary-cool-gray);
}

.error {
  background: var(--extended-dusty-rose);
  color: var(--error-coral-red);
}

.publications-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.publication-card {
  background: var(--bg-primary-white);
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: var(--shadow-md);
  border: 1px solid var(--border-color-gray);
  cursor: pointer;
  transition: all 0.2s ease;
}

.publication-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

.publication-card h4 {
  margin: 0;
  color: var(--text-primary-charcoal);
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
  color: var(--text-secondary-cool-gray);
  background: var(--bg-light-mist-gray);
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  white-space: nowrap;
  margin-left: 1rem;
}

.publication-description {
  margin: 0 0 1.5rem 0;
  color: var(--text-secondary-cool-gray);
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
  background: var(--text-secondary-cool-gray);
  color: white;
}

.btn-preview:hover {
  background: var(--text-primary-charcoal);
}

.btn-export {
  background: var(--success-mint-green);
  color: white;
}

.btn-export:hover {
  background: var(--success-dark-mint);
}

.help-section {
  background: var(--bg-light-mist-gray);
  padding: 2rem;
  border-radius: 8px;
  border: 1px solid var(--border-color-gray);
}

.help-section h3 {
  margin: 0 0 1.5rem 0;
  color: var(--text-primary-charcoal);
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
  background: var(--primary-deep-teal);
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
  color: var(--text-primary-charcoal);
}

.step-content p {
  margin: 0;
  color: var(--text-secondary-cool-gray);
  line-height: 1.5;
}

/* Mobile optimizations */
@media (max-width: 768px) {
  .publish-mobile-kb {
    padding: 1rem;
  }
  
  /* Compact the features list on small screens */
  .features-list {
    margin-bottom: 1rem;
  }

  .feature-item {
    padding: 0.5rem 0.75rem;
    gap: 0.5rem;
  }

  .feature-icon {
    font-size: 1.2rem;
  }

  .feature-content {
    font-size: 0.95rem;
    line-height: 1.3;
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
