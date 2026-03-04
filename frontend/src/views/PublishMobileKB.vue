<template>
  <div class="publish-mobile-kb">
    <h2>Publish Mobile Knowledge Base</h2>
    <p class="description">
      Create mobile-first knowledge bases optimized for field staff on iPhones and iPads.
      These are lightweight, offline-ready HTML files that work without internet connectivity.
    </p>

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
      <span class="audience-hint">Only snippets tagged with the selected audiences will be included in the export.</span>
    </div>

    <div v-if="recentPublishedPublications.length" class="recent-section">
      <h3>Recent Publications</h3>
      <div class="recent-list">
        <div
          v-for="pub in recentPublishedPublications"
          :key="`recent-${pub.id}`"
          class="recent-item"
          @click="selectPublication(pub)"
        >
          <div class="recent-main">
            <div class="recent-title">{{ pub.title }}</div>
            <div class="recent-meta">Updated {{ formatDate(pub.updated_at || pub.created_at) }}</div>
          </div>
          <div class="recent-actions">
            <button @click.stop="previewMobileKB(pub.id)" class="btn-preview btn-compact">Preview</button>
            <button @click.stop="exportMobileKB(pub.id)" class="btn-export btn-compact">Export KB</button>
          </div>
        </div>
      </div>
      <button type="button" class="view-all-link" @click="scrollToAllPublications">View all published</button>
    </div>

    <div ref="allPublicationsSection" class="publications-section">
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

  </div>
</template>

<script>

export default {
  name: 'PublishMobileKB',
  computed: {
    recentPublishedPublications() {
      return (this.publications || [])
        .filter(pub => pub && pub.status === 'published')
        .slice(0, 5)
    }
  },
  data() {
    return {
      publications: [],
      allTags: [],
      selectedTagIds: [],
      loading: true,
      error: null
    }
  },
  async created() {
    await Promise.all([this.fetchPublications(), this.loadTags()])
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

    _tagParams() {
      return this.selectedTagIds.map(id => `tag_ids=${id}`).join('&')
    },
    
    selectPublication(pub) {
      // Navigate to publication view
      this.$router.push({ name: 'PublicationView', params: { id: pub.id } })
    },
    
    previewMobileKB(pubId) {
      const params = this._tagParams()
      const previewUrl = `/api/publications/${pubId}/preview/mobile-kb${params ? '?' + params : ''}`
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
      const params = this._tagParams()
      window.open(`/api/publications/${pubId}/export/mobile-kb${params ? '?' + params : ''}`, '_blank')
    },
    scrollToAllPublications() {
      this.$refs.allPublicationsSection?.scrollIntoView({ behavior: 'smooth', block: 'start' })
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

.publish-mobile-kb {
  margin: 0 auto;
  padding: 1.5rem 2rem;
  background-color: var(--bg-light-mist-gray);
}

.description {
  font-size: 1.1rem;
  color: var(--text-secondary-cool-gray);
  margin-bottom: 1.25rem;
  line-height: 1.6;
}

.recent-section {
  margin-bottom: 1.25rem;
}

.recent-section h3 {
  margin: 0 0 0.75rem;
  color: var(--text-primary-charcoal);
}

.view-all-link {
  margin-top: 0.5rem;
  background: none;
  border: none;
  padding: 0;
  color: var(--primary-deep-teal);
  text-decoration: underline;
  cursor: pointer;
  font-size: 0.9rem;
}

.view-all-link:hover {
  color: var(--primary-medium-teal);
}

.recent-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.recent-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  background: var(--bg-primary-white);
  border: 1px solid var(--border-color-gray);
  border-radius: 8px;
  padding: 0.75rem 1rem;
  cursor: pointer;
}

.recent-main {
  min-width: 0;
}

.recent-title {
  font-weight: 600;
  color: var(--text-primary-charcoal);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.recent-meta {
  font-size: 0.85rem;
  color: var(--text-secondary-cool-gray);
}

.recent-actions {
  display: flex;
  gap: 0.5rem;
  flex-shrink: 0;
}

.btn-compact {
  padding: 0.35rem 0.65rem;
  font-size: 0.8rem;
}

.publications-section {
  margin-bottom: 0;
}

.publications-section h3 {
  margin-bottom: 1rem;
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
  gap: 1rem;
}

.publication-card {
  background: var(--bg-primary-white);
  padding: 1.25rem;
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
  margin: 0 0 1rem 0;
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

/* Mobile optimizations */
@media (max-width: 768px) {
  .publish-mobile-kb {
    padding: 1rem;
  }
  
  .publications-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  .recent-item {
    flex-direction: column;
    align-items: flex-start;
  }

  .recent-actions {
    width: 100%;
  }

  .recent-actions .btn-compact {
    flex: 1;
  }
  
  .card-actions {
    flex-direction: column;
  }
  
}
</style>
