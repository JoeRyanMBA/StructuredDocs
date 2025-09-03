<template>
  <div class="import-view">
    <div class="page-header">
      <h1>Import Content</h1>
  <p class="subtitle" style="margin-bottom: 1rem;">Use this tool to import content from outside this app. You can import Markdown (.md) documents (preferred) or Word (.docx) documents.</p>
    </div>

    <!-- Import Type Selection -->
    <div class="import-type-selection">
      <h3>Import Type</h3>
      <div class="radio-group">
        <label class="radio-option">
          <input type="radio" v-model="importType" value="topics" :disabled="isUploading">
          <span class="radio-label">
            <strong>Individual Topics</strong>
            <p>Import as separate topics that can be organized later</p>
          </span>
        </label>
        <label class="radio-option">
          <input type="radio" v-model="importType" value="collection" :disabled="isUploading">
          <span class="radio-label">
            <strong>Collection (Document)</strong>
            <p>Import as a single collection with hierarchical structure maintained</p>
          </span>
        </label>
      </div>
    </div>

    <!-- Collection Details (only shown when importing as collection) -->
    <div v-if="importType === 'collection'" class="collection-details">
      <h3>Collection Details</h3>
      <div class="form-group">
        <label for="projectSelect">Project *</label>
        <select 
          id="projectSelect"
          v-model="selectedProjectId" 
          required
          :disabled="isUploading"
          class="project-select"
        >
          <option value="">Select a project...</option>
          <option 
            v-for="project in projects" 
            :key="project.id" 
            :value="project.id"
          >
            {{ project.name }}
          </option>
        </select>
        <small class="form-help">Select the project this collection belongs to</small>
      </div>
      <div class="form-group">
        <label for="collectionName">Collection Name *</label>
        <input 
          id="collectionName"
          v-model="collectionName" 
          type="text" 
          placeholder="Enter collection name"
          required
          :disabled="isUploading"
        />
      </div>
      <div class="form-group">
        <label for="collectionFormNumber">Collection ID (Form Number) *</label>
        <input 
          id="collectionFormNumber"
          v-model="collectionFormNumber" 
          type="text" 
          placeholder="e.g., DOC-001, FORM-ABC"
          pattern="^[A-Za-z0-9\-_]+$"
          title="Only letters, numbers, hyphens, and underscores are allowed"
          required
          :disabled="isUploading"
        />
        <small class="form-help">Unique identifier for this collection</small>
      </div>
      <div class="form-group">
        <label for="collectionDescription">Description (Optional)</label>
        <textarea 
          id="collectionDescription"
          v-model="collectionDescription" 
          rows="3" 
          placeholder="Describe the content of this collection"
          :disabled="isUploading"
        ></textarea>
      </div>
    </div>

    <!-- Loading indicator -->
    <div v-if="preparingImport" class="loading-overlay">
      <div class="loading-content">
        <div class="spinner"></div>
        <h3>Preparing to import your document...</h3>
        <p>Reading file and preparing for upload. Please wait...</p>
      </div>
    </div>
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

      <div v-if="selectedFile" class="file-preview">
        <div class="file-info">
          <div class="file-icon">📄</div>
          <div class="file-details">
            <div class="file-name">{{ selectedFile.name }}</div>
            <div class="file-size">{{ formatFileSize(selectedFile.size) }}</div>
          </div>
        </div>
      </div>

      <div v-if="error" class="error">{{ error }}</div>

      <!-- Import Button -->
      <div class="import-actions">
        <button 
          v-if="selectedFile" 
          @click="startImport" 
          :disabled="isUploading || !canStartImport"
          class="import-btn"
        >
          <span v-if="isUploading">⏳ Processing...</span>
          <span v-else>📥 Start Import</span>
        </button>
        <button 
          v-if="selectedFile && !isUploading" 
          @click="clearFile" 
          class="clear-btn"
        >
          Clear
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ImportView',

  data() {
    return {
      source: 'markdown',
      error: null,
  isUploading: false,
  preparingImport: false,
      importType: 'topics',
      collectionName: '',
      collectionFormNumber: '',
      collectionDescription: '',
      selectedFile: null,
      projects: [],
      selectedProjectId: '',
      loadingProjects: true
    }
  },

  computed: {
    acceptedTypes() {
      return this.source === 'word' ? '.docx' : '.md,.markdown'
    },
    
    canStartImport() {
      if (!this.selectedFile) return false
      
      // For collection imports, require collection details and project selection
      if (this.importType === 'collection') {
        return this.collectionName.trim() && 
               this.collectionFormNumber.trim() && 
               this.selectedProjectId
      }
      
      return true
    }
  },

  mounted() {
    this.fetchProjects()
  },

  methods: {
    async fetchProjects() {
      this.loadingProjects = true
      try {
        const response = await fetch('/api/projects/')
        if (response.ok) {
          const data = await response.json()
          this.projects = data || []
        } else {
          console.error('Failed to fetch projects:', response.statusText)
        }
      } catch (error) {
        console.error('Error fetching projects:', error)
      } finally {
        this.loadingProjects = false
      }
    },

    onFileSelected(event) {
      this.error = null
      const file = event.target.files[0]
      if (!file) {
        this.selectedFile = null
        this.preparingImport = false
        return
      }
      this.selectedFile = file
      this.preparingImport = true
      // Simulate a short delay for UX (remove if not desired)
      setTimeout(() => {
        this.preparingImport = false
      }, 800)
    },

    clearFile() {
      this.selectedFile = null
      this.$refs.fileInput.value = null
      this.error = null
    },

    formatFileSize(bytes) {
      if (bytes === 0) return '0 Bytes'
      const k = 1024
      const sizes = ['Bytes', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
    },

    async startImport() {
      this.preparingImport = false
      if (!this.selectedFile) {
        this.error = 'Please select a file to import'
        return
      }

      this.error = null
      this.isUploading = true

      // Validate collection details if importing as collection
      if (this.importType === 'collection') {
        if (!this.collectionName.trim()) {
          this.error = 'Collection name is required'
          this.isUploading = false
          return
        }
        if (!this.collectionFormNumber.trim()) {
          this.error = 'Collection ID (Form Number) is required'
          this.isUploading = false
          return
        }
        if (!this.selectedProjectId) {
          this.error = 'Project selection is required'
          this.isUploading = false
          return
        }
      }

      const form = new FormData()
      form.append('file', this.selectedFile)
      form.append('source', this.source)
      form.append('import_type', this.importType)
      
      // Add collection details if importing as collection
      if (this.importType === 'collection') {
        form.append('collection_name', this.collectionName)
        form.append('collection_form_number', this.collectionFormNumber)
        form.append('collection_description', this.collectionDescription)
        form.append('project_id', this.selectedProjectId)
      }

      try {
        const res = await fetch('/api/import/upload', {
          method: 'POST',
          body: form
        })

        // Always read text first
        const text = await res.text()

        // Try parse JSON if appropriate
        let result = null
        const ct = res.headers.get('content-type') || ''
        if (ct.includes('application/json')) {
          result = JSON.parse(text)
        }

        // On error status, throw with message from payload or raw text
        if (!res.ok) {
          const msg = result?.error || text || `HTTP ${res.status}`
          throw new Error(msg)
        }

        console.log('Upload successful, result:', result) // Debug log

        // Handle different import types
        if (this.importType === 'collection') {
          // For collection imports, redirect to the collection organize page
          if (result.collection_id) {
            this.$router.push({
              name: 'Organize',
              params: { id: result.collection_id }
            })
          } else {
            throw new Error('Collection creation failed - no collection ID returned')
          }
        } else {
          // For topic imports, go to the import review page
          if (result.id) {
            this.$router.push({
              name: 'ImportReview',
              params: { id: result.id }
            })
          } else {
            throw new Error('Import failed - no import document ID returned')
          }
        }

      } catch (err) {
        console.error('Import failed:', err)
        this.error = `Import failed: ${err.message}`
      } finally {
        this.isUploading = false
        // Clear the file selection after successful import
        if (!this.error) {
          this.selectedFile = null
          this.$refs.fileInput.value = null
        }
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
  background: var(--bg-light-mist-gray);
  border-left: 4px solid var(--primary-deep-teal);
  border-radius: .75rem;
  padding: 1rem;
  margin-bottom: 1.5rem;
  color: var(--text-secondary-cool-gray);
  font-size: 0.95rem;
  line-height: 1.5;
}

.import-type-selection {
  margin-bottom: 2rem;
  padding: 1.5rem;
  border: 1px solid var(--extended-lavender-gray);
  border-radius: 8px;
  background: var(--bg-light-mist-gray);
}

.import-type-selection h3 {
  margin: 0 0 1rem 0;
  color: var(--text-primary-charcoal);
  font-size: 1.1rem;
}

.radio-group {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  /* Constrain overall width so options don't span the whole page */
  max-width: 680px;
}

.radio-option {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 1rem;
  border: 2px solid var(--extended-lavender-gray);
  border-radius: 6px;
  background: white;
  cursor: pointer;
  transition: all 0.2s ease;
  /* Fill the radio-group width but not the entire page */
  width: 100%;
  /* Keep all content visually inside the border */
  overflow: hidden;
  box-sizing: border-box;
  /* Avoid inheriting generic label margins */
  margin: 0;
}

.radio-option:hover {
  border-color: var(--primary-deep-teal);
  background: #f8fcff;
}

.radio-option input[type="radio"] {
  margin: 0.25rem 0 0 0;
  flex-shrink: 0;
}

.radio-option input[type="radio"]:checked + .radio-label {
  color: var(--primary-deep-teal);
}

.radio-option:has(input[type="radio"]:checked) {
  border-color: var(--primary-deep-teal);
  background: #f8fcff;
}

/* Keyboard focus state for accessibility */
.radio-option:focus-within {
  outline: none;
  border-color: var(--primary-deep-teal);
  box-shadow: 0 0 0 3px rgba(0, 122, 204, 0.15);
}

.radio-label {
  flex: 1;
  min-width: 0; /* Allow text to wrap properly */
  display: block; /* Keep content contained within the bordered area */
}

.radio-label strong {
  display: block;
  margin-bottom: 0.5rem;
  font-size: 1rem;
}

.radio-label p {
  margin: 0;
  font-size: 0.9rem;
  color: var(--text-secondary-cool-gray);
  line-height: 1.4;
  word-break: break-word;
}

.collection-details {
  margin-bottom: 2rem;
  padding: 1.5rem;
  border: 1px solid var(--extended-lavender-gray);
  border-radius: 8px;
  background: white;
}

.collection-details h3 {
  margin: 0 0 1.5rem 0;
  color: var(--text-primary-charcoal);
  font-size: 1.1rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group:last-child {
  margin-bottom: 0;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: var(--text-primary-charcoal);
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid var(--extended-lavender-gray);
  border-radius: 4px;
  font-size: 1rem;
  transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: 0;
  border-color: var(--primary-deep-teal);
  box-shadow: 0 0 0 0.2rem rgba(0, 122, 204, 0.25);
}

.form-help {
  display: block;
  margin-top: 0.25rem;
  font-size: 0.875rem;
  color: var(--text-secondary-cool-gray);
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
  color: var(--error-coral-red);
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
  color: var(--text-primary-charcoal);
}

.loading-content p {
  margin: 0;
  color: var(--text-secondary-cool-gray);
  font-size: 0.9rem;
}

/* Spinner animation */
.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid var(--bg-light-mist-gray);
  border-top: 4px solid var(--primary-deep-teal);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* File preview */
.file-preview {
  margin: 1rem 0;
  padding: 1rem;
  background: var(--bg-light-mist-gray);
  border: 1px solid var(--extended-lavender-gray);
  border-radius: 6px;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.file-icon {
  font-size: 1.5rem;
  color: var(--text-secondary-cool-gray);
}

.file-details {
  flex: 1;
}

.file-name {
  font-weight: 500;
  color: var(--text-primary-charcoal);
  margin-bottom: 0.25rem;
}

.file-size {
  font-size: 0.875rem;
  color: var(--text-secondary-cool-gray);
}

/* Import actions */
.import-actions {
  display: flex;
  gap: 1rem;
  margin-top: 1.5rem;
}

.import-btn {
  background: var(--primary-deep-teal);
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.import-btn:hover:not(:disabled) {
  background: var(--primary-medium-teal);
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 122, 204, 0.3);
}

.import-btn:disabled {
  background: var(--text-secondary-cool-gray);
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.clear-btn {
  background: var(--text-secondary-cool-gray);
  color: white;
  border: none;
  padding: 0.75rem 1rem;
  border-radius: 6px;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.clear-btn:hover {
  background: var(--text-primary-charcoal);
}
</style>