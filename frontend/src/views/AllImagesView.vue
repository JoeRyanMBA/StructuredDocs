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
        <button @click="loadImages" class="btn btn-secondary btn-sm" type="button">
          <i class="bi bi-search" aria-hidden="true"></i>
          <span>Search</span>
        </button>
      </div>
      <div class="view-controls">
        <button 
          type="button"
          :class="['btn','btn-sm', viewMode === 'grid' ? 'btn-primary' : 'btn-secondary']"
          :aria-pressed="viewMode === 'grid'"
          @click="viewMode = 'grid'"
        >
          <i class="bi bi-grid-3x3-gap" aria-hidden="true"></i>
          Grid
        </button>
        <button 
          type="button"
          :class="['btn','btn-sm', viewMode === 'list' ? 'btn-primary' : 'btn-secondary']"
          :aria-pressed="viewMode === 'list'"
          @click="viewMode = 'list'"
        >
          <i class="bi bi-list" aria-hidden="true"></i>
          List
        </button>
        <button @click="refreshImages" class="btn btn-primary btn-sm" type="button">
          <i class="bi bi-arrow-clockwise" aria-hidden="true"></i>
          <span>Refresh</span>
        </button>
      </div>
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
  <button @click="clearSearch" v-if="searchQuery" class="btn btn-secondary btn-sm"><i class="bi bi-x"></i> Clear Search</button>
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

      <!-- Missing Images Notice -->
      <div v-if="missingImagesCount > 0" class="info-banner">
        <i class="bi bi-info-circle"></i>
        <span>{{ missingImagesCount }} image{{ missingImagesCount !== 1 ? 's' : '' }} not displaying (files missing). Try re-importing the document.</span>
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
              :src="getImageUrl(image)" 
              :alt="image.filename"
              class="image-preview"
              @load="handleImageLoad"
              @error="handleImageError($event, image)"
              loading="lazy"
            />
            <div class="image-overlay">
              <button class="btn-overlay btn-icon" @click.stop="viewImageDetails(image)" title="View Details">
                <i class="bi bi-zoom-in"></i>
              </button>
              <button class="btn-overlay btn-icon" @click.stop="copyImagePath(image)" title="Copy URL">
                <i class="bi bi-clipboard"></i>
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
          <div class="col-topics">Topics</div>
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
              :src="getImageUrl(image)" 
              :alt="image.filename"
              class="list-thumbnail"
              @load="handleImageLoad"
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
          <div class="col-topics" @click.stop>
            <UsageBadge
              :count="(imageUsage[image.public_url]?.topics || []).length"
              label="topic"
              :items="imageUsage[image.public_url]?.topics || []"
            />
          </div>
          <div class="col-actions">
            <button class="btn-icon" @click.stop="viewImageDetails(image)" title="View Details"><i class="bi bi-zoom-in"></i></button>
            <button class="btn-icon" @click.stop="copyImagePath(image)" title="Copy URL"><i class="bi bi-clipboard"></i></button>
          </div>
        </div>
      </div>
    </div>

    <!-- Image Details Modal -->
  <div v-if="showDetailsModal" class="modal-overlay" @click.self="closeDetailsModal">
      <div class="modal large" @click.stop>
        <div class="modal-header-row modal-header">
          <h3>Image Details</h3>
          <button class="plain-close btn-close" @click="closeDetailsModal">✕</button>
        </div>
        <div class="modal-body" v-if="selectedImage">
          <div class="image-details">
            <div class="detail-image">
              <img 
                :src="getImageUrl(selectedImage)" 
                :alt="selectedImage.filename"
                class="detail-preview"
                @load="handleImageLoad"
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
                  <button @click="copyImagePath(selectedImage)" class="btn btn-secondary btn-sm"><i class="bi bi-clipboard"></i> Copy</button>
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
              <div class="detail-group">
                <label>Used In:</label>
                <div v-if="imageTopics(selectedImage).length > 0" class="topic-usage-list">
                  <span class="usage-count-badge">{{ imageTopics(selectedImage).length }} topic{{ imageTopics(selectedImage).length === 1 ? '' : 's' }}</span>
                  <ul class="topic-usage-links">
                    <li v-for="topic in imageTopics(selectedImage)" :key="topic.id">
                      <router-link :to="{ name: 'EditTopic', params: { id: topic.id } }" @click="closeDetailsModal">
                        {{ topic.name }}
                      </router-link>
                    </li>
                  </ul>
                </div>
                <span v-else class="usage-none">Not used in any topics</span>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="copyImagePath(selectedImage)" class="btn btn-primary">
            <i class="bi bi-clipboard"></i> Copy Image Path
          </button>
          <button @click="closeDetailsModal" class="btn btn-secondary">Close</button>
        </div>
      </div>
    </div>

  <!-- Toasts handled globally via ToastContainer -->
  </div>
</template>

<script>
import { toast } from '@/composables/useToast'
import { getImageUrl as getResolvedImageUrl, getRetryImageSrc } from '@/services/imageUrl'
import UsageBadge from '@/components/UsageBadge.vue'

export default {
  name: 'AllImagesView',
  components: { UsageBadge },
  data() {
    return {
      allImages: [],
      imageUsage: {},
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
    },
    missingImagesCount() {
      return this.allImages.filter(img => {
        if (img.source === 'import') {
          return img.file_exists !== true
        }
        return img.file_exists === false
      }).length
    },
    apiBase() {
      try {
        const { API_BASE } = require('../api/base.js')
        return API_BASE || ''
      } catch (e) {
        let raw = (import.meta.env.VITE_API_BASE_URL || '').trim()
        return raw ? raw.replace(/\/+$/, '') : ''
      }
    },
    apiBaseHost() {
      try {
        if (!this.apiBase) return ''

        if (this.apiBase.startsWith('http')) {
          const url = new URL(this.apiBase)
          if (url.pathname.endsWith('/api')) {
            url.pathname = url.pathname.slice(0, -4) || '/'
          }
          const normalizedPath = url.pathname.replace(/\/+$/, '')
          return normalizedPath ? `${url.origin}${normalizedPath}` : url.origin
        }

        return this.apiBase.replace(/\/api\/?$/, '') || ''
      } catch (_e) {
        return ''
      }
    }
  },
  async created() {
    await this.loadImages()
  },
  methods: {
    imageTopics(image) {
      return this.imageUsage[image?.public_url]?.topics || []
    },
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
          let imports = await importResponse.json()
          if (Array.isArray(imports)) {
            // Sort newest first by created_at if present
            imports.sort((a, b) => new Date(b.created_at || 0) - new Date(a.created_at || 0))
          } else {
            imports = []
          }
          const sliceSize = 25 // raised from 10 to reduce chance of excluding recent import
          let importDocsProcessed = 0
          let importDocsFailed = 0
          for (const importDoc of imports.slice(0, sliceSize)) {
            try {
              const imagesResponse = await fetch(`/api/import/staging/${importDoc.id}/images`)
              if (imagesResponse.ok) {
                const imagesData = await imagesResponse.json()
                const docImagesRaw = imagesData.images || []
                const docImages = docImagesRaw.map(img => {
                  // Normalize size property for UI expectations
                  const size = img.size || img.file_size || null
                  return {
                    ...img,
                    size, // ensure size field exists
                    file_size: size,
                    source: 'import',
                    document_id: importDoc.id,
                    public_url: img.public_url || `/images/imports/${importDoc.id}/${img.filename}`
                  }
                })
                importImages = importImages.concat(docImages)
                importDocsProcessed++
              } else {
                importDocsFailed++
                console.warn(`[AllImagesView] Images request failed for import ${importDoc.id}: status ${imagesResponse.status}`)
              }
            } catch (e) {
              importDocsFailed++
              console.warn(`[AllImagesView] Exception loading images for import ${importDoc.id}:`, e)
            }
          }
          console.info(`[AllImagesView] Processed ${importDocsProcessed} import docs, ${importDocsFailed} failed, collected ${importImages.length} images (slice limit ${sliceSize}).`)
        } else {
          console.warn('[AllImagesView] /api/import/history request failed, skipping import images.')
        }

        // Combine all images
        this.allImages = [
          ...staticImages.map(img => ({
            ...img,
            source: 'static',
            size: img.size || img.file_size || null,
            file_size: img.size || img.file_size || null
          })),
            ...importImages
        ]

        const usageRes = await fetch('/api/images/usage-summary')
        if (usageRes.ok) this.imageUsage = await usageRes.json()

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
            size: 45600,
            file_size: 45600,
            alt_text: 'Sample chart showing data visualization'
          },
          {
            id: 2,
            filename: 'workflow-diagram.svg',
            source: 'static', 
            public_url: '/images/workflow-diagram.svg',
            size: 12300,
            file_size: 12300,
            alt_text: 'Process workflow diagram'
          },
          {
            id: 3,
            filename: 'logo-placeholder.jpg',
            source: 'import',
            document_id: 1,
            public_url: '/images/logo-placeholder.jpg',
            size: 89200,
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

      // Filter out images that definitely don't exist on disk
      filtered = filtered.filter(image => {
        // Import images should only be shown when file existence is explicitly true
        if (image.source === 'import' && image.file_exists !== true) {
          console.debug(`Filtering out missing image: ${image.filename}`)
          return false
        }

        // For non-import sources, honor explicit false
        if (image.file_exists === false) {
          console.debug(`Filtering out missing image: ${image.filename}`)
          return false
        }

        // Include images where file_exists is true, undefined, or null (unknown status)
        return true
      })

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
      toast.success('Images refreshed successfully!')
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

    getImageUrl(image) {
      return getResolvedImageUrl(image, {
        apiBase: this.apiBase,
        apiBaseHost: this.apiBaseHost
      })
    },

    copyImagePath(image) {
      const path = image.public_url || image.file_path || `/images/${image.filename}`
      navigator.clipboard.writeText(path).then(() => {
        toast.success(`Copied image path to clipboard: ${path}`)
      }).catch(() => {
        toast.error('Failed to copy to clipboard')
      })
    },

    handleImageLoad(event) {
      if (event?.target?.dataset) {
        delete event.target.dataset.retryAttempted
      }
    },

    handleImageError(event, image) {
      const element = event?.target
      if (element && image) {
        const currentSrc = element.getAttribute('src') || ''
        const retryResult = getRetryImageSrc(
          currentSrc,
          image,
          element?.dataset?.retryAttempted === '1',
          {
            apiBase: this.apiBase,
            apiBaseHost: this.apiBaseHost
          }
        )

        if (retryResult?.src) {
          if (retryResult.shouldMarkRetried && element?.dataset) {
            element.dataset.retryAttempted = '1'
          }
          setTimeout(() => {
            element.src = retryResult.src
          }, 120)
          return
        }
      }

      console.warn(`Failed to load image after retry: ${image.filename}`)
      if (element) {
        element.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZjBmMGYwIi8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxNCIgZmlsbD0iIzk5OSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPkltYWdlIE5vdCBGb3VuZDwvdGV4dD48L3N2Zz4='
      }
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

    showMessage(text, type = 'success') { /* legacy no-op */
      if (type === 'error') toast.error(text); else toast.success(text)
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

/* Use global button styles from assets/style.css */

.loading {
  text-align: center;
  padding: 4rem 2rem;
  color: #666;
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
  color: var(--primary-medium-teal);
}

.stat-label {
  display: block;
  font-size: 0.875rem;
  color: #666;
  margin-top: 0.25rem;
}

.info-banner {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: #e3f2fd;
  border-left: 4px solid #2196f3;
  border-radius: 4px;
  margin-bottom: 1.5rem;
  color: #1976d2;
  font-size: 0.95rem;
}

.info-banner i {
  flex-shrink: 0;
  font-size: 1.2rem;
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
  border-color: var(--primary-medium-teal);
  box-shadow: 0 4px 12px rgba(0, 140, 158, 0.15);
}

.image-card.selected {
  border-color: var(--primary-medium-teal);
  box-shadow: 0 0 0 2px rgba(0, 140, 158, 0.2);
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
  background: rgba(255, 255, 255, 0.92);
  border: none;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  cursor: pointer;
  font-size: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  color: var(--primary-deep-teal, #1a6b6b);
  box-shadow: 0 1px 4px rgba(0,0,0,0.15);
}

.btn-overlay:hover {
  background: white;
  transform: scale(1.1);
  box-shadow: 0 2px 8px rgba(0,0,0,0.2);
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

.usage-count-badge {
  display: inline-block;
  background: var(--extended-sky-blue, #d0eaf9);
  color: var(--primary-deep-teal, #1a6b6b);
  border-radius: 999px;
  padding: 0.15rem 0.6rem;
  font-size: 0.8rem;
  font-weight: 600;
  margin-bottom: 0.4rem;
}

.topic-usage-links {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.topic-usage-links li a {
  color: var(--primary-deep-teal, #1a6b6b);
  text-decoration: none;
  font-size: 0.875rem;
}

.topic-usage-links li a:hover {
  text-decoration: underline;
}

.usage-none {
  font-size: 0.875rem;
  color: #888;
  font-style: italic;
}

/* Removed legacy .message-toast styles; using global ToastContainer */

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
