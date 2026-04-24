<template>
  <div class="publish-pdf-view">
    <div class="page-header">
      <h1>Publish PDF <HelpIcon feature="publish.pdf" /></h1>
      <p class="subtitle">Generate and download PDF documents</p>
    </div>

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

    <div class="publications-section">
      <h3>Select Publication to Export as PDF</h3>
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
          @click="downloadPDF(pub)"
        >
          <div class="card-header">
            <h4>{{ pub.title }}</h4>
            <span class="publication-date">{{ formatDate(pub.created_at) }}</span>
          </div>
          <p class="publication-description">{{ pub.description || 'No description' }}</p>
          <div class="card-actions">
            <button @click.stop="downloadPDF(pub)" class="export-btn">
              📄 Export PDF
            </button>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script>
import { apiGet } from '@/api/base'
import { downloadPublicationPdf, getPublications } from '@/api/publications'
import HelpIcon from '@/components/HelpIcon.vue'

export default {
  name: 'PublishPDFView',
  components: { HelpIcon },
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
    await Promise.all([this.loadPublications(), this.loadTags()])
  },
  methods: {
    async loadPublications() {
      try {
        const data = await getPublications()
        this.publications = Array.isArray(data) ? data : (data.publications || [])
      } catch (err) {
        console.error('Failed to fetch publications:', err)
        this.error = 'Failed to load publications'
      } finally {
        this.loading = false
      }
    },
    async loadTags() {
      try {
        const data = await apiGet('/api/tags/')
        this.allTags = Array.isArray(data) ? data : (data.tags || [])
      } catch (e) {
        console.error('Failed to load tags', e)
      }
    },
    async downloadPDF(pub) {
      try {
        await downloadPublicationPdf(pub.id, `${pub.title || 'publication'}.pdf`, this.selectedTagIds)
      } catch (e) {
        console.error('PDF export failed:', e)
        this.error = e.message || 'Failed to export PDF'
      }
    },
    formatDate(dateString) {
      if (!dateString) return 'Unknown'
      try {
        return new Date(dateString).toLocaleDateString()
      } catch (e) {
        return 'Unknown'
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

.publish-pdf {
  margin: 0 auto;
  padding: 2rem;
  background-color: var(--bg-white);
}

.guidance-text {
  background: var(--bg-white);
  border-left: 4px solid var(--primary-deep-teal);
  border-radius: .75rem;
  padding: 1rem;
  margin-bottom: 1.5rem;
  color: var(--text-primary-charcoal);
  font-size: 0.95rem;
  line-height: 1.5;
}

.description {
  color: var(--text-secondary-cool-gray);
  margin-bottom: 2rem;
  line-height: 1.6;
}

.publications-section {
  margin: 1.5rem 0 0;
}

.publications-section h3 {
  margin-bottom: 1.5rem;
  color: var(--text-primary-charcoal);
}

.loading,
.error,
.empty {
  text-align: center;
  padding: 2rem;
  color: var(--text-secondary-cool-gray);
  font-style: italic;
}

.error {
  color: var(--error-coral-red);
}

.publications-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.publication-card {
  background: var(--bg-primary-white);
  border: 1px solid var(--border-color-gray);
  border-radius: 8px;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.publication-card:hover {
  box-shadow: var(--shadow-md);
  border-color: var(--primary-deep-teal);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.card-header h4 {
  margin: 0;
  color: var(--text-primary-charcoal);
  font-size: 1.1rem;
}

.publication-date {
  font-size: 0.8rem;
  color: var(--text-secondary-cool-gray);
  white-space: nowrap;
}

.publication-description {
  color: var(--text-secondary-cool-gray);
  font-size: 0.9rem;
  line-height: 1.4;
  margin-bottom: 1rem;
}

.card-actions {
  display: flex;
  gap: 0.5rem;
}

@media (max-width: 768px) {
  .publications-grid {
    grid-template-columns: 1fr;
  }
  
  .card-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .publication-date {
    margin-top: 0.5rem;
  }
}
</style>
