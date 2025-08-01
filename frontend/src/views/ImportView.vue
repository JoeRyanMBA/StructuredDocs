<template>
  <div class="import-view">
    <Breadcrumbs />
    <h2>Import Topics</h2>
    
    <p class="guidance-text">
      Use this tool to import content from outside this app. You can import Markdown (.md) documents (preferred) or Word (.docx) documents.
    </p>

    <!-- Loading indicator -->
    <div v-if="isUploading" class="loading-overlay">
      <div class="loading-content">
        <div class="spinner"></div>
        <h3>Processing Import...</h3>
        <p>Parsing document and extracting content. Please wait...</p>
      </div>
    </div>

    <!-- Upload form (disabled during upload) -->
    <div class="upload-form" :class="{ disabled: isUploading }">
      <label>
        Format
        <select v-model="source" :disabled="isUploading">
          <option value="markdown">Markdown</option>
          <option value="word">Word (.docx)</option>
        </select>
      </label>

      <input
        ref="fileInput"
        type="file"
        @change="onFileSelected"
        :accept="acceptedTypes"
        :disabled="isUploading"
      />

      <div v-if="error" class="error">{{ error }}</div>
    </div>
  </div>
</template>

<script>
import Breadcrumbs from '@/components/Breadcrumbs.vue'

export default {
  name: 'ImportView',
  components: { Breadcrumbs },

  data() {
    return {
      source: 'markdown',
      error: null,
      isUploading: false
    }
  },

  computed: {
    acceptedTypes() {
      return this.source === 'word' ? '.docx' : '.md,.markdown'
    }
  },

  methods: {
    async onFileSelected(event) {
      this.error = null
      this.isUploading = true
      
      const file = event.target.files[0]
      if (!file) {
        this.isUploading = false
        return
      }

      const form = new FormData()
      form.append('file', file)
      form.append('source', this.source)

      try {
        const res = await fetch('/api/import/upload', {
          method: 'POST',
          body: form
        })

        // Always read text first
        const text = await res.text()

        // Try parse JSON if appropriate
        let importDoc = null
        const ct = res.headers.get('content-type') || ''
        if (ct.includes('application/json')) {
          importDoc = JSON.parse(text)
        }

        // On error status, throw with message from payload or raw text
        if (!res.ok) {
          const msg = importDoc?.error || text || `HTTP ${res.status}`
          throw new Error(msg)
        }

        // Ensure we got an ID
        if (!importDoc || typeof importDoc.id !== 'number') {
          throw new Error('Invalid response from import endpoint')
        }

        console.log('Upload successful, import doc:', importDoc) // Debug log

        // Navigate to review, passing ID as param
        this.$router.push({
          name: 'ImportReview',
          params: { id: importDoc.id }
        })

      } catch (err) {
        console.error('Import failed:', err)
        this.error = `Import failed: ${err.message}`
      } finally {
        this.isUploading = false
        // Clear the file input so the same file can be re‐selected
        this.$refs.fileInput.value = null
      }
    }
  }
}
</script>

<style scoped>
.import-view {
  padding-top: 0px; /* Top padding to account for fixed header */
  padding-left: 2rem;
  padding-right: 2rem;
  padding-bottom: 2rem;
  position: relative;
}

.guidance-text {
  background: #f8f9fa;
  border-left: 4px solid #007acc;
  padding: 1rem;
  margin-bottom: 1.5rem;
  color: #495057;
  font-size: 0.95rem;
  line-height: 1.5;
}

.upload-form {
  transition: opacity 0.3s ease;
}

.upload-form.disabled {
  opacity: 0.5;
  pointer-events: none;
}

label {
  display: block;
  margin-bottom: 1rem;
}

input[type="file"] {
  display: block;
  margin-bottom: 1rem;
}

.error {
  color: #c00;
  font-weight: bold;
  margin-top: 1rem;
}

/* Loading overlay */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.95);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.loading-content {
  text-align: center;
  padding: 2rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  max-width: 400px;
}

.loading-content h3 {
  margin: 1rem 0 0.5rem 0;
  color: #333;
}

.loading-content p {
  margin: 0;
  color: #666;
  font-size: 0.9rem;
}

/* Spinner animation */
.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #007acc;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>