<template>
  <div class="publication-view">
    
    <div v-if="loading" class="loading">Loading publication...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else-if="pub">
      <h2>{{ pub.title }}</h2>
      
      <p class="guidance-text">
        This is the detailed view of a published collection. You can navigate through the content tree below and use the actions to download or export this publication.
      </p>
      
      <p v-if="pub.description" class="description">{{ pub.description }}</p>

      <!-- top‐level tree -->
      <PublicationNodeView
        :nodes="tree"
      />

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

      <div class="actions">
        <button @click="downloadPDF">Download PDF</button>
        <button @click="exportMobileKB" class="mobile-kb-btn">📱 Export Mobile Knowledge Base</button>
        <button @click="previewMobileKB" class="preview-btn">👁️ Preview Mobile KB</button>
      </div>
    </div>
    <div v-else class="empty">
      Publication not found.
    </div>
  </div>
</template>

<script>
import PublicationNodeView from '@/components/PublicationNodeView.vue'

export default {
  name: 'PublicationView',
  components: { PublicationNodeView },
  props: {
    id: { type: [String, Number], required: true }
  },
  data() {
    return {
      pub: null,
      tree: [],
      loading: true,
      error: null,
      allTags: [],
      selectedTagIds: []
    }
  },
  async created() {
    try {
      const [pubRes, tagsRes] = await Promise.all([
        fetch(`/api/publications/${this.id}`),
        fetch('/api/tags/')
      ])
      if (!pubRes.ok) throw new Error(`Failed to fetch publication: ${pubRes.status}`)
      const json = await pubRes.json()
      this.pub  = { title: json.title, description: json.description }
      this.tree = json.tree
      if (tagsRes.ok) {
        const tagsData = await tagsRes.json()
        this.allTags = Array.isArray(tagsData) ? tagsData : (tagsData.tags || [])
      }
    } catch (error) {
      console.error('Error loading publication:', error)
      this.error = 'Failed to load publication'
    } finally {
      this.loading = false
    }
  },
  methods: {
    _tagParams() {
      return this.selectedTagIds.map(id => `tag_ids=${id}`).join('&')
    },
    downloadPDF() {
      const params = this._tagParams()
      const pdfUrl = `/api/publications/${this.id}/export/pdf${params ? '?' + params : ''}`
      const link = document.createElement('a')
      link.href = pdfUrl
      link.download = `${this.pub?.title || 'publication'}.pdf`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    },
    exportMobileKB() {
      const params = this._tagParams()
      window.open(`/api/publications/${this.id}/export/mobile-kb${params ? '?' + params : ''}`, '_blank')
    },
    previewMobileKB() {
      const params = this._tagParams()
      const previewUrl = `/api/publications/${this.id}/preview/mobile-kb${params ? '?' + params : ''}`
      const previewWindow = window.open(previewUrl, '_blank', 'width=375,height=812,scrollbars=yes,resizable=yes')
      if (previewWindow) {
        previewWindow.focus()
      }
    }
  }
}
</script>

<style scoped>
.publication-view { 
  margin:0 auto;
}

.guidance-text {
  background: var(--bg-light-mist-gray);
  border-left: 4px solid var(--primary-deep-teal);
  border-radius: .75rem;
  padding: 1rem;
  margin-bottom: 1.5rem;
  color: var(--text-primary-charcoal);
  font-size: 0.95rem;
  line-height: 1.5;
}

.loading,
.error {
  margin-top: 1rem;
  font-size: 0.9rem;
}

.error {
  color: var(--error-coral-red);
}

.description {
  color: var(--text-secondary-cool-gray);
  font-style: italic;
  margin-bottom: 1.5rem;
  line-height: 1.5;
}

.empty {
  color: var(--text-secondary-cool-gray);
  font-style: italic;
  text-align: center;
  margin-top: 2rem;
}

.actions { 
  margin-top: 1rem; 
  display: flex; 
  gap: 1rem; 
  flex-wrap: wrap; 
}

.audience-bar {
  background: #f0f4ff;
  border: 1px solid #c5d3f0;
  border-radius: 8px;
  padding: 0.75rem 1rem;
  margin-top: 1.5rem;
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

.actions button {
  padding: 0.75rem 1.25rem; 
  border: none; 
  background: var(--primary-deep-teal); 
  color: white; 
  border-radius: 4px;
  cursor: pointer; 
  transition: background-color 0.2s ease;
  font-size: 0.9rem;
}

.actions button:hover {
  background: var(--primary-medium-teal);
}

.publish-button {
  background: var(--success-mint-green) !important;
}

.publish-button:hover {
  background: var(--success-dark-mint) !important;
}

.preview-btn {
  background: var(--text-secondary-cool-gray) !important;
}

.preview-btn:hover {
  background: var(--text-primary-charcoal) !important;
}

@media (max-width: 768px) {
  .actions {
    flex-direction: column;
  }
  .actions button {
    width: 100%;
    margin-bottom: 0.5rem;
  }
}
</style>