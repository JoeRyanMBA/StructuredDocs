<template>
  <div class="all-images">
    <div class="page-header">
      <h1>🖼️ All Images</h1>
      <p class="subtitle">
        Browse and manage all images available for use in your content. Click on any image to copy its path for use in topics and documents.
      </p>
    </div>

    <div class="page-actions">
      <div class="search-controls">
        <input 
          v-model="searchQuery" 
          type="text" 
          class="search-input"
          placeholder="Search images by filename..." 
          @keyup.enter="loadImages"
        />
  <button @click="loadImages" class="btn btn-secondary btn-sm">
          🔍 Search
        </button>
      </div>
      <div class="view-controls">
        <button 
          :class="['btn', 'btn-secondary', viewMode === 'grid' ? 'active' : '']"
          @click="viewMode = 'grid'"
        >
          📱 Grid
        </button>
        <button 
          :class="['btn', 'btn-secondary', viewMode === 'list' ? 'active' : '']"
          @click="viewMode = 'list'"
        >
          📋 List
        </button>
      </div>
      <button @click="refreshImages" class="btn btn-primary">
        🔄 Refresh
      </button>
    </div>

    <div v-if="loading" class="loading">
      <div class="loading-spinner"></div>
      <p>Loading images...</p>
    </div>

    <div v-else-if="error" class="error-message">
      <p>{{ error }}</p>
      <button @click="loadImages" class="btn btn-secondary">Try Again</button>
    </div>

    <div v-else-if="filteredImages.length === 0" class="empty-state">
      <div class="empty-icon">📷</div>
      <h3>No Images Found</h3>
      <p>{{ searchQuery ? 'No images match your search criteria.' : 'No images are currently available.' }}</p>
  <button @click="clearSearch" v-if="searchQuery" class="btn btn-secondary btn-sm">Clear Search</button>
    </div>

    <div v-else class="images-content">
      <!-- Summary Stats -->
      <div class="stats-bar">
        <div class="stat-item">
          <span class="stat-number">{{ filteredImages.length }}</span>
          <span class="stat-label">{{ filteredImages.length === 1 ? 'Image' : 'Images' }}</span>
        </div>
        <div class="stat-item" v-if="totalSize > 0">
          <span class="stat-number">{{ formatFileSize(totalSize) }}</span>
          <span class="stat-label">Total Size</span>
        </div>
        <div class="stat-item" v-if="searchQuery">
          <span class="stat-number">{{ allImages.length }}</span>
          <span class="stat-label">Total Available</span>
        </div>
      </div>

      <!-- Grid View -->
      <div v-if="viewMode === 'grid'" class="images-grid">
        <div 
          v-for="image in filteredImages" 
          :key="image.id"
          class="image-card"
          @click="selectImage(image)"
          :class="{ 'selected': selectedImage?.id === image.id }"
        >
          <div class="image-container">
            <img 
              :src="image.public_url" 
              :alt="image.filename"
              class="image-preview"
              @error="handleImageError($event, image)"
              loading="lazy"
            />
            <div class="image-overlay">
              <button class="btn-overlay" @click.stop="copyImagePath(image)" title="Copy Path">
                📋
              </button>
              <button class="btn-overlay" @click.stop="viewImageDetails(image)" title="View Details">
                👁️
              </button>
            </div>
          </div>
          <div class="image-info">
            <div class="image-name" :title="image.filename">{{ image.filename }}</div>
            <div class="image-meta">
              <span v-if="image.size" class="file-size">{{ formatFileSize(image.size) }}</span>
              <span v-if="image.width && image.height" class="dimensions">{{ image.width }}×{{ image.height }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- List View -->
      <div v-if="viewMode === 'list'" class="images-list">
        <div class="list-header">
          <div class="col-filename">Filename</div>
          <div class="col-size">Size</div>
          <div class="col-dimensions">Dimensions</div>
          <div class="col-date">Date Added</div>
          <div class="col-actions">Actions</div>
        </div>
        <div 
          v-for="image in filteredImages" 
          :key="image.id"
          class="list-row"
          @click="selectImage(image)"
          :class="{ 'selected': selectedImage?.id === image.id }"
        >
          <div class="col-filename">
            <img 
              :src="image.public_url" 
              :alt="image.filename"
              class="list-thumbnail"
              @error="handleImageError($event, image)"
              loading="lazy"
            />
            <span class="filename" :title="image.filename">{{ image.filename }}</span>
          </div>
          <div class="col-size">{{ image.size ? formatFileSize(image.size) : 'N/A' }}</div>
          <div class="col-dimensions">
            {{ image.width && image.height ? `${image.width}×${image.height}` : 'N/A' }}
          </div>
          <div class="col-date">{{ formatDate(image.created_at) }}</div>
          <div class="col-actions">
            <button class="btn-icon" @click.stop="copyImagePath(image)" title="Copy Path">📋</button>
            <button class="btn-icon" @click.stop="viewImageDetails(image)" title="View Details">👁️</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Image Details Modal -->
    <div v-if="showDetailsModal" class="modal-overlay" @click="closeDetailsModal">
      <div class="modal large" @click.stop>
            /* Modal Styles - use global .modal-overlay and .modal styles */
        <div class="modal-header">
          <h3>Image Details</h3>
          <button class="btn-close" @click="closeDetailsModal">✕</button>
        </div>
        <div class="modal-body" v-if="selectedImage">
          <div class="image-details">
            <div class="detail-image">
              <img 
                :src="selectedImage.public_url" 
                :alt="selectedImage.filename"
                class="detail-preview"
                @error="handleImageError($event, selectedImage)"
              />
            </div>
            <div class="detail-info">
              <div class="detail-group">
                <label>Filename:</label>
                <span>{{ selectedImage.filename }}</span>
              </div>
              <div class="detail-group">
                <label>File Path:</label>
                <div class="path-display">
                  <code>{{ selectedImage.public_url }}</code>
                  <button @click="copyImagePath(selectedImage)" class="btn-copy">📋 Copy</button>
                </div>
              </div>
              <div class="detail-group" v-if="selectedImage.size">
                <label>File Size:</label>
                <span>{{ formatFileSize(selectedImage.size) }}</span>
              </div>
              <div class="detail-group" v-if="selectedImage.width && selectedImage.height">
                <label>Dimensions:</label>
                <span>{{ selectedImage.width }} × {{ selectedImage.height }} pixels</span>
              </div>
              <div class="detail-group" v-if="selectedImage.created_at">
                <label>Date Added:</label>
                <span>{{ formatDate(selectedImage.created_at) }}</span>
              </div>
              <div class="detail-group" v-if="selectedImage.alt_text">
                <label>Alt Text:</label>
                <span>{{ selectedImage.alt_text }}</span>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="copyImagePath(selectedImage)" class="btn btn-primary">
            📋 Copy Image Path
          </button>
          <button @click="closeDetailsModal" class="btn btn-secondary">Close</button>
        </div>
      </div>
    </div>

    <!-- Success/Error Messages -->
    <div v-if="message" :class="['message-toast', messageType]">
      {{ message }}
    </div>
  </div>
</template>

<script>

export default {
  name: 'AllImagesView',
  data() {
    return {
      allImages: [],
      filteredImages: [],
      loading: false,
      error: null,
      searchQuery: '',
      viewMode: 'grid', // 'grid' or 'list'
      selectedImage: null,
      showDetailsModal: false,
      message: '',
      messageType: 'success' // 'success' or 'error'
    }
  },
  computed: {
    totalSize() {
      return this.filteredImages.reduce((total, image) => {
        return total + (image.size || 0)
      }, 0)
    }
  },
  async created() {
    await this.loadImages()
  },
  methods: {
    async loadImages() {
      this.loading = true
      this.error = null
      
      try {
        // Load from static images API
        const staticResponse = await fetch('/api/images')
        let staticImages = []
        if (staticResponse.ok) {
          const staticData = await staticResponse.json()
          staticImages = staticData || []
        }

        // Load from import documents
        const importResponse = await fetch('/api/import/history')
        let importImages = []
        if (importResponse.ok) {
          const imports = await importResponse.json()
          
          // Load images from each import
          for (const importDoc of imports.slice(0, 10)) { // Limit for performance
            try {
              const imagesResponse = await fetch(`/api/import/staging/${importDoc.id}/images`)
              if (imagesResponse.ok) {
                const imagesData = await imagesResponse.json()
                const docImages = (imagesData.images || []).map(img => ({
                  ...img,
                  source: 'import',
                  document_id: importDoc.id,
                  public_url: img.public_url || `/api/import/staging/${importDoc.id}/images/${img.filename}`
                }))
                importImages = importImages.concat(docImages)
              }
            } catch (e) {
              console.warn(`Failed to load images for import ${importDoc.id}:`, e)
            }
          }
        }

        // Combine all images
        this.allImages = [
          ...staticImages.map(img => ({ ...img, source: 'static' })),
          ...importImages
        ]

        this.applyFilters()

      } catch (error) {
        console.error('Failed to load images:', error)
        // Provide mock data for testing when backend is unavailable
        this.allImages = [
          {
            id: 1,
            filename: 'sample-chart.png',
            source: 'static',
            public_url: '/images/sample-chart.png',
            file_size: 45600,
            alt_text: 'Sample chart showing data visualization'
          },
          {
            id: 2,
            filename: 'workflow-diagram.svg',
            source: 'static', 
            public_url: '/images/workflow-diagram.svg',
            file_size: 12300,
            alt_text: 'Process workflow diagram'
          },
          {
            id: 3,
            filename: 'logo-placeholder.jpg',
            source: 'import',
            document_id: 1,
            public_url: '/images/logo-placeholder.jpg',
            file_size: 89200,
            alt_text: 'Company logo placeholder'
          }
        ]
        this.applyFilters()
        this.error = 'Using sample data - backend unavailable.'
      } finally {
        this.loading = false
      }
    },

    applyFilters() {
      let filtered = [...this.allImages]

      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase()
        filtered = filtered.filter(image => 
          image.filename.toLowerCase().includes(query) ||
          (image.alt_text && image.alt_text.toLowerCase().includes(query))
        )
      }

      // Sort by filename
      filtered.sort((a, b) => a.filename.localeCompare(b.filename))

      this.filteredImages = filtered
    },

    async refreshImages() {
      await this.loadImages()
      this.showMessage('Images refreshed successfully!')
    },

    clearSearch() {
      this.searchQuery = ''
      this.applyFilters()
    },

    selectImage(image) {
      this.selectedImage = image
    },

    viewImageDetails(image) {
      this.selectedImage = image
      this.showDetailsModal = true
    },

    closeDetailsModal() {
      this.showDetailsModal = false
    },

    copyImagePath(image) {
      const path = image.public_url || image.file_path || `/images/${image.filename}`
      navigator.clipboard.writeText(path).then(() => {
        this.showMessage(`Copied image path to clipboard: ${path}`)
      }).catch(() => {
        this.showMessage('Failed to copy to clipboard', 'error')
      })
    },

    handleImageError(event, image) {
      console.warn(`Failed to load image: ${image.filename}`)
      event.target.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZjBmMGYwIi8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxNCIgZmlsbD0iIzk5OSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPkltYWdlIE5vdCBGb3VuZDwvdGV4dD48L3N2Zz4='
    },

    formatFileSize(bytes) {
      if (!bytes) return 'N/A'
      if (bytes === 0) return '0 B'
      const k = 1024
      const sizes = ['B', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
    },

    formatDate(dateString) {
      if (!dateString) return 'N/A'
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    },

    showMessage(text, type = 'success') {
      this.message = text
      this.messageType = type
      setTimeout(() => {
        this.message = ''
      }, 3000)
    }
  },

  watch: {
    searchQuery() {
      this.applyFilters()
    }
  }
}
</script>

<style scoped>
.all-images {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 2rem;
}

.page-header h1 {
  margin: 0 0 1rem 0;
  color: #333;
}

.guidance-text {
  color: #666;
  font-size: 1.1rem;
  line-height: 1.5;
  margin: 0;
}

.page-actions {
  display: flex;
  gap: 1rem;
  align-items: center;
  margin-bottom: 2rem;
  flex-wrap: wrap;
}

.search-controls {
  display: flex;
  gap: 0.5rem;
  flex: 1;
  min-width: 300px;
}

.search-input {
  flex: 1;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 1rem;
}

.view-controls {
  display: flex;
  gap: 0.5rem;
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.2s ease;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-primary {
  background: #2196f3;
  color: white;
}

.btn-primary:hover {
  background: #1976d2;
}

.btn-secondary {
  background: #f5f5f5;
  color: #333;
  border: 1px solid #ddd;
}

.btn-secondary:hover {
  background: #ebebeb;
}

.btn-secondary.active {
  background: #2196f3;
  color: white;
  border-color: #2196f3;
}

.loading {
  text-align: center;
  padding: 4rem 2rem;
  color: #666;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #2196f3;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-message {
  text-align: center;
  padding: 3rem 2rem;
  color: #d32f2f;
}

.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  color: #666;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.stats-bar {
  display: flex;
  gap: 2rem;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
  margin-bottom: 2rem;
}

.stat-item {
  text-align: center;
}

.stat-number {
  display: block;
  font-size: 1.5rem;
  font-weight: bold;
  color: #2196f3;
}

.stat-label {
  display: block;
  font-size: 0.875rem;
  color: #666;
  margin-top: 0.25rem;
}

/* Grid View */
.images-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1.5rem;
}

.image-card {
  background: white;
  border: 1px solid #ddd;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
}

.image-card:hover {
  border-color: #2196f3;
  box-shadow: 0 4px 12px rgba(33, 150, 243, 0.15);
}

.image-card.selected {
  border-color: #2196f3;
  box-shadow: 0 0 0 2px rgba(33, 150, 243, 0.2);
}

.image-container {
  position: relative;
  height: 200px;
  overflow: hidden;
}

.image-preview {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.2s ease;
}

.image-card:hover .image-preview {
  transform: scale(1.05);
}

.image-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.image-card:hover .image-overlay {
  opacity: 1;
}

.btn-overlay {
  background: rgba(255, 255, 255, 0.9);
  border: none;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  cursor: pointer;
  font-size: 1.2rem;
  transition: all 0.2s ease;
}

.btn-overlay:hover {
  background: white;
  transform: scale(1.1);
}

.image-info {
  padding: 1rem;
}

.image-name {
  font-weight: 500;
  margin-bottom: 0.5rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.image-meta {
  display: flex;
  gap: 1rem;
  font-size: 0.875rem;
  color: #666;
}

/* List View */
.images-list {
  background: white;
  border: 1px solid #ddd;
  border-radius: 8px;
  overflow: hidden;
}

.list-header {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr 120px;
  gap: 1rem;
  padding: 1rem;
  background: #f8f9fa;
  font-weight: 500;
  border-bottom: 1px solid #ddd;
}

.list-row {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr 120px;
  gap: 1rem;
  padding: 1rem;
  border-bottom: 1px solid #eee;
  cursor: pointer;
  transition: all 0.2s ease;
  align-items: center;
}

.list-row:hover {
  background: #f8f9fa;
}

.list-row.selected {
  background: #e3f2fd;
  border-color: #2196f3;
}

.col-filename {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.list-thumbnail {
  width: 40px;
  height: 40px;
  object-fit: cover;
  border-radius: 4px;
  border: 1px solid #ddd;
}

.filename {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.col-actions {
  display: flex;
  gap: 0.5rem;
}

/* Modal Styles - use global .modal-overlay and .modal; keep size overrides if needed */
.modal.large {
  min-width: 800px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #eee;
}

.modal-header h3 {
  margin: 0;
}

.btn-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #666;
}

.btn-close:hover {
  color: #333;
}

.modal-body {
  padding: 1.5rem;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding: 1.5rem;
  border-top: 1px solid #eee;
}

.image-details {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
}

.detail-image {
  text-align: center;
}

.detail-preview {
  max-width: 100%;
  max-height: 400px;
  border-radius: 8px;
  border: 1px solid #ddd;
}

.detail-info {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.detail-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.detail-group label {
  font-weight: 500;
  color: #333;
}

.path-display {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.path-display code {
  flex: 1;
  background: #f5f5f5;
  padding: 0.5rem;
  border-radius: 4px;
  font-size: 0.875rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.btn-copy {
  background: #2196f3;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 0.5rem 1rem;
  cursor: pointer;
  font-size: 0.875rem;
}

.btn-copy:hover {
  background: #1976d2;
}

/* Message Toast */
.message-toast {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  padding: 1rem 1.5rem;
  border-radius: 6px;
  color: white;
  font-weight: 500;
  z-index: 3000;
  animation: slideIn 0.3s ease;
}

.message-toast.success {
  background: #4caf50;
}

.message-toast.error {
  background: #f44336;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

/* Responsive Design */
@media (max-width: 768px) {
  .all-images {
    padding: 1rem;
  }

  .page-actions {
    flex-direction: column;
    align-items: stretch;
  }

  .search-controls {
    min-width: auto;
  }

  .images-grid {
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 1rem;
  }

  .list-header,
  .list-row {
    grid-template-columns: 2fr 1fr 100px;
    font-size: 0.875rem;
  }

  .col-size,
  .col-date {
    display: none;
  }

  .image-details {
    grid-template-columns: 1fr;
  }

  .modal.large {
    min-width: auto;
    margin: 1rem;
  }
}
</style>
