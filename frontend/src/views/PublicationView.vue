<template>
  <div class="publication-view">
    <Breadcrumbs />
    
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
import Breadcrumbs from '@/components/Breadcrumbs.vue'
import PublicationNodeView from '@/components/PublicationNodeView.vue'

export default {
  name: 'PublicationView',
  components: { Breadcrumbs, PublicationNodeView },
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
  background: #f8f9fa;
  border-left: 4px solid #007acc;
  border-radius: .75rem;
  padding: 1rem;
  margin-bottom: 1.5rem;
  color: #495057;
  font-size: 0.95rem;
  line-height: 1.5;
}

.loading,
.error {
  margin-top: 1rem;
  font-size: 0.9rem;
}

.error {
  color: #c00;
}

.description {
  color: #666;
  font-style: italic;
  margin-bottom: 1.5rem;
  line-height: 1.5;
}

.empty {
  color: #999;
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
  background: #205493; 
  color: white; 
  border-radius: 4px;
  cursor: pointer; 
  transition: background-color 0.2s ease;
  font-size: 0.9rem;
}

.actions button:hover {
  background: #005E7B;
}

.mobile-kb-btn {
  background: #28a745 !important;
}

.mobile-kb-btn:hover {
  background: #218838 !important;
}

.preview-btn {
  background: #6c757d !important;
}

.preview-btn:hover {
  background: #5a6268 !important;
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