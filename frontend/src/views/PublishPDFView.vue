<template>
  <div class="publish-pdf">
    <Breadcrumbs />
    <h2>Publish PDF Documents</h2>
    
    <p class="guidance-text">
            Generate high-quality PDF documents with professional formatting, table of contents, and print-ready layouts.
      Perfect for formal documentation, training materials, and distribution.</p>
    

    <div class="features-grid">
      <div class="feature-card">
        <div class="feature-icon">📄</div>
        <h3>Professional Layout</h3>
        <p>Clean, formatted documents ready for business use</p>
      </div>
      <div class="feature-card">
        <div class="feature-icon">🖨️</div>
        <h3>Print Ready</h3>
        <p>Optimized for high-quality printing and physical distribution</p>
      </div>
      <div class="feature-card">
        <div class="feature-icon">📧</div>
        <h3>Easy Sharing</h3>
        <p>Perfect for email attachments and document management</p>
      </div>
      <div class="feature-card">
        <div class="feature-icon">📚</div>
        <h3>Table of Contents</h3>
        <p>Automatic navigation with bookmarks and page numbers</p>
      </div>
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
              📄 Download PDF
            </button>
          </div>
        </div>
      </div>
    </div>

    <div class="help-section">
      <h3>PDF Export Features</h3>
      <ul class="feature-list">
        <li><strong>Hierarchical Structure:</strong> Topics are organized with proper headings and sub-headings</li>
        <li><strong>Automatic Table of Contents:</strong> Generated based on your topic structure</li>
        <li><strong>Professional Formatting:</strong> Clean typography and consistent styling</li>
        <li><strong>Page Numbers:</strong> Automatic page numbering and headers</li>
        <li><strong>Print Optimization:</strong> Properly formatted for standard paper sizes</li>
        <li><strong>Hyperlinks:</strong> Internal navigation links within the document</li>
      </ul>
    </div>
  </div>
</template>

<script>
import Breadcrumbs from '@/components/Breadcrumbs.vue'

export default {
  name: 'PublishPDFView',
  components: { Breadcrumbs },
  data() {
    return {
      publications: [],
      loading: true,
      error: null
    }
  },
  async created() {
    await this.loadPublications()
  },
  methods: {
    async loadPublications() {
      try {
        const res = await fetch('/api/publications')
        if (!res.ok) {
          throw new Error(`Failed to fetch publications: ${res.statusText}`)
        }
        this.publications = await res.json()
      } catch (err) {
        console.error('Failed to fetch publications:', err)
        this.error = 'Failed to load publications'
      } finally {
        this.loading = false
      }
    },
    downloadPDF(pub) {
      // Create a direct download link for PDF
      const pdfUrl = `/api/publications/${pub.id}/export/pdf`
      
      // Create temporary link element to trigger download
      const link = document.createElement('a')
      link.href = pdfUrl
      link.download = `${pub.title || 'publication'}.pdf`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
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
.publish-pdf {
 margin: 0 auto;
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

.description {
  color: #666;
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
  border: 1px solid #e1e5e9;
  border-radius: 8px;
  padding: 1.5rem;
  text-align: center;
  transition: box-shadow 0.2s ease;
}

.feature-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.feature-icon {
  font-size: 2rem;
  margin-bottom: 1rem;
}

.feature-card h3 {
  margin: 0 0 0.5rem 0;
  color: #333;
  font-size: 1.1rem;
}

.feature-card p {
  margin: 0;
  color: #666;
  font-size: 0.9rem;
  line-height: 1.4;
}

.publications-section {
  margin: 3rem 0;
}

.publications-section h3 {
  margin-bottom: 1.5rem;
  color: #333;
}

.loading,
.error,
.empty {
  text-align: center;
  padding: 2rem;
  color: #666;
  font-style: italic;
}

.error {
  color: #c00;
}

.publications-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.publication-card {
  background: white;
  border: 1px solid #e1e5e9;
  border-radius: 8px;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.publication-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-color: #007acc;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.card-header h4 {
  margin: 0;
  color: #333;
  font-size: 1.1rem;
}

.publication-date {
  font-size: 0.8rem;
  color: #999;
  white-space: nowrap;
}

.publication-description {
  color: #666;
  font-size: 0.9rem;
  line-height: 1.4;
  margin-bottom: 1rem;
}

.card-actions {
  display: flex;
  gap: 0.5rem;
}

.export-btn {
  background: #005a9c;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background-color 0.2s ease;
}

.export-btn:hover {
  background: #004080;
}

.help-section {
  margin-top: 3rem;
  background: #f8f9fa;
  padding: 2rem;
  border-radius: 8px;
}

.help-section h3 {
  margin-top: 0;
  color: #333;
}

.feature-list {
  margin: 1rem 0;
  padding-left: 1.5rem;
}

.feature-list li {
  margin-bottom: 0.75rem;
  line-height: 1.5;
  color: #555;
}

.feature-list strong {
  color: #333;
}

@media (max-width: 768px) {
  .features-grid {
    grid-template-columns: 1fr;
  }
  
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
