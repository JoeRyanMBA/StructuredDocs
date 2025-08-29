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
      error: null
    }
  },
  async created() {
    try {
      // now this.id is defined
      const res  = await fetch(`/api/publications/${this.id}`)
      if (!res.ok) {
        throw new Error(`Failed to fetch publication: ${res.status}`)
      }
      const json = await res.json()
      this.pub  = { title: json.title, description: json.description }
      this.tree = json.tree
    } catch (error) {
      console.error('Error loading publication:', error)
      this.error = 'Failed to load publication'
    } finally {
      this.loading = false
    }
  },
  methods: {
    downloadPDF() {
      // Create a direct download link for PDF
      const pdfUrl = `/api/publications/${this.id}/export/pdf`
      
      // Create temporary link element to trigger download
      const link = document.createElement('a')
      link.href = pdfUrl
      link.download = `${this.pub?.title || 'publication'}.pdf`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    },
    exportMobileKB() {
      // Download the mobile knowledge base HTML file
      window.open(`/api/publications/${this.id}/export/mobile-kb`, '_blank')
    },
    previewMobileKB() {
      // Open preview in a new window/tab using the preview endpoint
      const previewUrl = `/api/publications/${this.id}/preview/mobile-kb`
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
  margin-top: 2rem; 
  display: flex; 
  gap: 1rem; 
  flex-wrap: wrap; 
}

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