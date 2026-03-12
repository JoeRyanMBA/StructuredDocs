<template>
  <div class="import-view">
    <div class="page-header">
      <h1>Import Content</h1>
  <p class="subtitle" style="margin-bottom: 1rem;">Use this tool to import content from outside this app. You can import Markdown (.md) documents (preferred) or Word (.docx) documents.</p>
    </div>

    <!-- Import Type Selection -->
    <div class="import-type-selection">
      <h3>Import Type</h3>
      <p class="section-help">Choose how to structure your import.</p>
      <div class="card-options" role="group" aria-label="Import type">
        <label class="card-option" :class="{ selected: importType === 'topic' }" tabindex="0">
          <input type="radio" class="visually-hidden" v-model="importType" value="topic" :disabled="isUploading" />
          <div class="card-content">
            <div class="card-icon" aria-hidden="true">📝</div>
            <div class="card-text">
              <div class="card-title">Import Topic</div>
              <div class="card-desc">Import a single file as one topic. Review and edit before saving.</div>
            </div>
          </div>
        </label>

        <label class="card-option" :class="{ selected: importType === 'collection' }" tabindex="0">
          <input type="radio" class="visually-hidden" v-model="importType" value="collection" :disabled="isUploading" />
          <div class="card-content">
            <div class="card-icon" aria-hidden="true">🗂️</div>
            <div class="card-text">
              <div class="card-title">Collection</div>
              <div class="card-desc">Import a document as a collection with headings becoming topics.</div>
            </div>
          </div>
        </label>

        <label class="card-option" :class="{ selected: importType === 'bulk-collection' }" tabindex="0">
          <input type="radio" class="visually-hidden" v-model="importType" value="bulk-collection" :disabled="isUploading" />
          <div class="card-content">
            <div class="card-icon" aria-hidden="true">📚</div>
            <div class="card-text">
              <div class="card-title">Create Collection</div>
              <div class="card-desc">Select multiple files — each file becomes one topic in a new collection.</div>
            </div>
          </div>
        </label>
      </div>
    </div>

    <!-- Collection Details (shown for both 'collection' and 'bulk-collection') -->
    <div v-if="importType === 'collection' || importType === 'bulk-collection'" class="collection-details">
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
        <p v-if="bulkProgress">
          Uploading file {{ bulkProgress.current }} of {{ bulkProgress.total }}…
        </p>
        <p v-else>Parsing document and extracting content. Please wait...</p>
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
        :multiple="importType === 'bulk-collection'"
      />

      <!-- Single-file preview -->
      <div v-if="selectedFile && importType !== 'bulk-collection'" class="file-preview">
        <div class="file-info">
          <div class="file-icon">📄</div>
          <div class="file-details">
            <div class="file-name">{{ selectedFile.name }}</div>
            <div class="file-size">{{ formatFileSize(selectedFile.size) }}</div>
          </div>
        </div>
      </div>

      <!-- Multi-file preview -->
      <div v-if="selectedFiles.length > 0 && importType === 'bulk-collection'" class="file-preview">
        <div class="file-count-badge">{{ selectedFiles.length }} file{{ selectedFiles.length !== 1 ? 's' : '' }} selected</div>
        <div v-for="(f, idx) in selectedFiles" :key="idx" class="file-info">
          <div class="file-icon">📄</div>
          <div class="file-details">
            <div class="file-name">{{ f.name }}</div>
            <div class="file-size">{{ formatFileSize(f.size) }}</div>
          </div>
        </div>
      </div>

      <div v-if="error" class="error">{{ error }}</div>

      <!-- Import Button -->
      <div class="import-actions">
        <button 
          v-if="hasSelectedFiles" 
          @click="startImport" 
          :disabled="isUploading || !canStartImport"
          class="import-btn"
        >
          <span v-if="isUploading">⏳ Processing...</span>
          <span v-else>📥 Start Import</span>
        </button>
        <button 
          v-if="hasSelectedFiles && !isUploading" 
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
      importType: 'topic',
      collectionName: '',
      collectionFormNumber: '',
      collectionDescription: '',
      selectedFile: null,
      selectedFiles: [],
      bulkProgress: null,
      projects: [],
      selectedProjectId: '',
      loadingProjects: true
    }
  },

  computed: {
    acceptedTypes() {
      return this.source === 'word' ? '.docx' : '.md,.markdown'
    },

    hasSelectedFiles() {
      return this.importType === 'bulk-collection'
        ? this.selectedFiles.length > 0
        : !!this.selectedFile
    },

    canStartImport() {
      const needsCollection = this.importType === 'collection' || this.importType === 'bulk-collection'
      const collectionValid = this.collectionName.trim() &&
                              this.collectionFormNumber.trim() &&
                              this.selectedProjectId

      if (this.importType === 'bulk-collection') {
        return this.selectedFiles.length > 0 && collectionValid
      }
      if (needsCollection) {
        return !!this.selectedFile && collectionValid
      }
      return !!this.selectedFile
    }
  },

  watch: {
    importType() {
      // Clear file selections when switching import modes
      this.selectedFile = null
      this.selectedFiles = []
      if (this.$refs.fileInput) {
        this.$refs.fileInput.value = null
      }
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

    updateHierarchyDefault() {
      // No-op kept for backward compatibility; hierarchy is now determined by import type
    },

    onFileSelected(event) {
      this.error = null
      if (this.importType === 'bulk-collection') {
        this.selectedFiles = Array.from(event.target.files)
        if (this.selectedFiles.length > 0) {
          this.preparingImport = true
          setTimeout(() => { this.preparingImport = false }, 800)
        }
      } else {
        const file = event.target.files[0]
        if (!file) {
          this.selectedFile = null
          this.preparingImport = false
          return
        }
        this.selectedFile = file
        this.preparingImport = true
        setTimeout(() => {
          this.preparingImport = false
        }, 800)
      }
    },

    clearFile() {
      this.selectedFile = null
      this.selectedFiles = []
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

      if (this.importType === 'bulk-collection') {
        await this.startBulkImport()
        return
      }

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

        if (this.importType === 'collection') {
          // Redirect to the collection organize page
          const collectionId = result.collection_id || result.id
          if (collectionId) {
            this.$router.push({
              name: 'Organize',
              params: { id: collectionId }
            })
          } else {
            throw new Error('Collection creation failed - no collection ID returned')
          }
        } else {
          // 'topic' → go to import review page
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
    },

    async startBulkImport() {
      if (this.selectedFiles.length === 0) {
        this.error = 'Please select at least one file'
        return
      }
      if (!this.collectionName.trim()) {
        this.error = 'Collection name is required'
        return
      }
      if (!this.collectionFormNumber.trim()) {
        this.error = 'Collection ID (Form Number) is required'
        return
      }
      if (!this.selectedProjectId) {
        this.error = 'Project selection is required'
        return
      }

      this.error = null
      this.isUploading = true
      let collectionId = null
      let completedCount = 0

      try {
        for (let i = 0; i < this.selectedFiles.length; i++) {
          this.bulkProgress = { current: i + 1, total: this.selectedFiles.length }

          const form = new FormData()
          form.append('file', this.selectedFiles[i])
          form.append('source', this.source)
          form.append('import_type', 'bulk-collection')

          if (collectionId) {
            form.append('existing_collection_id', String(collectionId))
          } else {
            form.append('collection_name', this.collectionName)
            form.append('collection_form_number', this.collectionFormNumber)
            form.append('collection_description', this.collectionDescription)
            form.append('project_id', String(this.selectedProjectId))
          }

          const res = await fetch('/api/import/upload', {
            method: 'POST',
            body: form
          })

          const text = await res.text()
          let result = null
          const ct = res.headers.get('content-type') || ''
          if (ct.includes('application/json')) {
            result = JSON.parse(text)
          }

          if (!res.ok) {
            const msg = result?.error || text || `HTTP ${res.status}`
            throw new Error(`"${this.selectedFiles[i].name}": ${msg}`)
          }

          collectionId = result.collection_id
          completedCount++
        }

        if (collectionId) {
          this.$router.push({ name: 'Organize', params: { id: collectionId } })
        }

      } catch (err) {
        console.error('Bulk import failed:', err)
        this.error = `Import failed: ${err.message}`
        if (completedCount > 0) {
          this.error += ` (${completedCount} of ${this.selectedFiles.length} files imported successfully)`
        }
      } finally {
        this.isUploading = false
        this.bulkProgress = null
        if (!this.error) {
          this.selectedFiles = []
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
  background: var(--bg-white);
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
  background: var(--bg-white);
}

.import-type-selection h3 {
  margin: 0 0 1rem 0;
  color: var(--text-primary-charcoal);
  font-size: 1.1rem;
}

/* Card-like option controls */
.section-help {
  margin: 0 0 0.75rem 0;
  color: var(--text-secondary-cool-gray);
  font-size: 0.95rem;
}

.card-options {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 1rem;
  max-width: 680px;
}

.card-option {
  display: block;
  border: 2px solid var(--extended-lavender-gray);
  border-radius: 8px;
  background: #fff;
  cursor: pointer;
  transition: all 0.2s ease;
  margin: 0;
  outline: none;
}

.card-option:hover {
  border-color: var(--primary-deep-teal);
  background: #f8fcff;
}

.card-option.selected {
  border-color: var(--primary-deep-teal);
  background: #f8fcff;
  box-shadow: 0 0 0 3px rgba(0, 122, 204, 0.12);
}

.card-content {
  display: flex;
  gap: 0.75rem;
  padding: 1rem;
  align-items: flex-start;
}

.card-icon { font-size: 1.25rem; line-height: 1; }

.card-text { flex: 1; min-width: 0; }
.card-title { font-weight: 600; margin: 0 0 0.25rem 0; color: var(--text-primary-charcoal); }
.card-desc { margin: 0; color: var(--text-secondary-cool-gray); font-size: 0.9rem; line-height: 1.4; }

.visually-hidden {
  position: absolute !important;
  height: 1px; width: 1px;
  overflow: hidden; clip: rect(1px, 1px, 1px, 1px);
  white-space: nowrap; border: 0; padding: 0; margin: -1px;
}

.advanced-options {
  margin-bottom: 2rem;
  padding: 1.5rem;
  border: 1px solid var(--extended-lavender-gray);
  border-radius: 8px;
  background: white;
}

.advanced-options h3 {
  margin: 0 0 1.5rem 0;
  color: var(--text-primary-charcoal);
  font-size: 1.1rem;
}

.checkbox-label {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  cursor: pointer;
  font-weight: normal;
  margin-bottom: 0;
}

.checkbox-label input[type="checkbox"] {
  margin: 0;
  width: auto;
  flex-shrink: 0;
  margin-top: 0.2rem;
}

.checkbox-text {
  flex: 1;
  line-height: 1.4;
}

.checkbox-text strong {
  color: var(--text-primary-charcoal);
}

.recommended-badge {
  display: inline-block;
  background: #e7f3ff;
  color: #0066cc;
  font-size: 0.75rem;
  font-weight: 500;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  margin-left: 0.5rem;
  border: 1px solid #b3d9ff;
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
  background: var(--bg-white);
  border: 1px solid var(--extended-lavender-gray);
  border-radius: 6px;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-top: 0.5rem;
}

.file-count-badge {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-primary-charcoal);
  margin-bottom: 0.5rem;
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