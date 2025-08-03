<template>
  <NotificationTicker
    :notifications="allNotifications"
    contextType="document-builder"
    @mark-read="markNotificationRead"
  />
  <div class="document-builder">
    <Breadcrumbs />
    <div class="builder-header">
      <h1>📝 Document Builder</h1>
      <p class="subtitle">Your central workspace for creating and managing documentation</p>
    </div>

    <!-- Main Builder Interface -->
    <div class="builder-layout">
      <!-- Left Sidebar - Collections -->
      <div class="builder-sidebar">
        <div class="sidebar-section">
          <div class="section-header">
            <h3>📁 Collections</h3>
            <button class="btn-icon" @click="showCreateCollection = true" title="Create New Collection">
              ➕
            </button>
          </div>
          
          <div class="collections-list">
            <div 
              v-for="collection in collections" 
              :key="collection.id"
              :class="['collection-item', { active: selectedCollection?.id === collection.id }]"
              @click="selectCollection(collection)"
            >
              <div class="collection-icon">📁</div>
              <div class="collection-info">
                <div class="collection-name">{{ collection.name }}</div>
                <div class="collection-meta">
                  {{ collection.topics_count || 0 }} topics
                  <span v-if="collection.projectName" class="collection-project">
                    • {{ collection.projectName }}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- Create New Collection Button -->
          <button class="btn-secondary full-width" @click="showCreateCollection = true">
            ➕ New Collection
          </button>
        </div>
      </div>

      <!-- Main Content Area -->
      <div class="builder-main">
        <!-- No Collection Selected State -->
        <div v-if="!selectedCollection" class="empty-state">
          <div class="empty-icon">📝</div>
          <h3>Welcome to Document Builder</h3>
          <p>Select a collection from the sidebar to start building your document, or create a new collection to begin.</p>
        </div>

        <!-- Collection Selected -->
        <div v-else class="collection-workspace">
          <!-- Collection Header -->
          <div class="workspace-header">
            <div class="collection-title">
              <h2>{{ selectedCollection.name }}</h2>
              <div class="collection-badges">
                <span class="collection-status">{{ formatStatus(selectedCollection.status) }}</span>
                <span v-if="selectedCollection.projectName" class="project-badge">
                  📁 {{ selectedCollection.projectName }}
                </span>
              </div>
            </div>
            <div class="workspace-actions">
              <button class="btn-primary" @click="addNewTopic">➕ Add Topic</button>
              <button class="btn-outline" @click="organizeCollection">🔧 Organize</button>
              <button class="btn-success" @click="publishCollection">📤 Publish</button>
            </div>
          </div>

          <!-- Collection Topics -->
          <div class="topics-section">
            <h3>📝 Topics ({{ collectionTopics.length }})</h3>
            
            <div v-if="collectionTopics.length === 0" class="topics-empty">
              <p>No topics in this collection yet.</p>
              <button class="btn-primary" @click="addNewTopic">➕ Create First Topic</button>
            </div>

            <div v-else class="topics-grid">
              <div 
                v-for="topic in collectionTopics" 
                :key="topic.id"
                class="topic-card"
                @click="editTopic(topic)"
              >
                <div class="topic-header">
                  <h4>{{ topic.title }}</h4>
                  <span :class="['topic-status', `status-${topic.status}`]">
                    {{ formatStatus(topic.status) }}
                  </span>
                </div>
                <div class="topic-summary">{{ topic.summary || 'No summary available' }}</div>
                <div class="topic-meta">
                  <span class="topic-updated">{{ formatRelativeTime(topic.updated_at) }}</span>
                  <div class="topic-actions">
                    <button class="btn-icon" @click.stop="editTopic(topic)" title="Edit Topic">✏️</button>
                    <button class="btn-icon" @click.stop="removeTopic(topic)" title="Remove from Collection">🗑️</button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Available Topics -->
          <div class="available-topics-section">
            <h3>📚 Available Topics</h3>
            <div class="topics-filter">
              <input 
                v-model="topicsFilter" 
                placeholder="Search topics..." 
                class="filter-input"
              />
            </div>
            
            <div class="available-topics-grid">
              <div 
                v-for="topic in filteredAvailableTopics" 
                :key="topic.id"
                class="available-topic-card"
                @click="addTopicToCollection(topic)"
              >
                <div class="topic-header">
                  <h4>{{ topic.title }}</h4>
                  <span :class="['topic-status', `status-${topic.status}`]">
                    {{ formatStatus(topic.status) }}
                  </span>
                </div>
                <div class="topic-summary">{{ topic.summary || 'No summary available' }}</div>
                <button class="btn-add" @click.stop="addTopicToCollection(topic)">➕ Add</button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Sidebar - Resources -->
      <div class="builder-resources">
        <!-- Links Repository -->
        <div class="resource-section">
          <div class="section-header">
            <h3>🔗 Links</h3>
            <button class="btn-icon" @click="showLinksModal = true" title="Manage Links">
              ⚙️
            </button>
          </div>
          
          <div class="links-list">
            <div 
              v-for="link in recentLinks" 
              :key="link.id"
              class="link-item"
              @click="copyLinkReference(link)"
              :title="link.url"
            >
              <div class="link-icon">🔗</div>
              <div class="link-info">
                <div class="link-title">{{ link.title }}</div>
                <div class="link-code">{{ link.reference_code }}</div>
              </div>
            </div>
          </div>
          
          <button class="btn-secondary full-width" @click="showLinksModal = true">
            🔗 View All Links
          </button>
        </div>

        <!-- Images Repository -->
        <div class="resource-section">
          <div class="section-header">
            <h3>🖼️ Images</h3>
            <button class="btn-icon" @click="showImagesModal = true" title="Browse Images">
              👁️
            </button>
          </div>
          
          <div class="images-grid">
            <div 
              v-for="image in recentImages" 
              :key="image.id"
              class="image-item"
              @click="copyImagePath(image)"
              :title="image.filename"
            >
              <img 
                :src="image.public_url" 
                :alt="image.filename"
                class="image-thumbnail"
                @error="handleImageError"
              />
            </div>
          </div>
          
          <button class="btn-secondary full-width" @click="showImagesModal = true">
            🖼️ Browse All Images
          </button>
        </div>
      </div>
    </div>

    <!-- Create Collection Modal -->
    <div v-if="showCreateCollection" class="modal-overlay" @click="showCreateCollection = false">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h3>Create New Collection</h3>
          <button class="btn-close" @click="showCreateCollection = false">✕</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="createCollection">
            <div class="form-group">
              <label>Collection Name</label>
              <input 
                v-model="newCollection.name" 
                placeholder="Enter collection name" 
                required 
                ref="collectionNameInput"
              />
            </div>
            <div class="form-group">
              <label>Description</label>
              <textarea 
                v-model="newCollection.description" 
                placeholder="Optional description"
                rows="3"
              ></textarea>
            </div>
            <div class="form-group">
              <label>Project</label>
              <select v-model="newCollection.projectId">
                <option value="">Select a project (optional)</option>
                <option v-for="project in allProjects" :key="project.id" :value="project.id">
                  {{ project.name }}
                </option>
              </select>
            </div>
            <div class="form-group">
              <label>Status</label>
              <select v-model="newCollection.status">
                <option value="active">Active</option>
                <option value="draft">Draft</option>
                <option value="archived">Archived</option>
              </select>
            </div>
            <div class="form-actions">
              <button type="button" class="btn-secondary" @click="showCreateCollection = false">
                Cancel
              </button>
              <button type="submit" class="btn-primary">Create Collection</button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Links Modal -->
    <div v-if="showLinksModal" class="modal-overlay" @click="showLinksModal = false">
      <div class="modal large" @click.stop>
        <div class="modal-header">
          <h3>🔗 Links Repository</h3>
          <button class="btn-close" @click="showLinksModal = false">✕</button>
        </div>
        <div class="modal-body">
          <div class="links-manager">
            <div class="links-controls">
              <input 
                v-model="linksSearch" 
                placeholder="Search links..." 
                class="search-input"
              />
              <button class="btn-primary" @click="createNewLink">➕ New Link</button>
            </div>
            
            <div class="links-table">
              <div 
                v-for="link in filteredLinks" 
                :key="link.id"
                class="link-row"
              >
                <div class="link-main">
                  <div class="link-title">{{ link.title }}</div>
                  <div class="link-url">{{ link.url }}</div>
                </div>
                <div class="link-details">
                  <span class="link-code">{{ link.reference_code }}</span>
                  <span class="link-type">{{ link.link_type }}</span>
                </div>
                <div class="link-actions">
                  <button class="btn-icon" @click="copyLinkReference(link)" title="Copy Reference">📋</button>
                  <button class="btn-icon" @click="editLink(link)" title="Edit">✏️</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Images Modal -->
    <div v-if="showImagesModal" class="modal-overlay" @click="showImagesModal = false">
      <div class="modal large" @click.stop>
        <div class="modal-header">
          <h3>🖼️ Images Repository</h3>
          <button class="btn-close" @click="showImagesModal = false">✕</button>
        </div>
        <div class="modal-body">
          <div class="images-manager">
            <div class="images-controls">
              <input 
                v-model="imagesSearch" 
                placeholder="Search images..." 
                class="search-input"
              />
            </div>
            
            <div class="images-gallery">
              <div 
                v-for="image in filteredImages" 
                :key="image.id"
                class="image-card"
                @click="copyImagePath(image)"
              >
                <img 
                  :src="image.public_url" 
                  :alt="image.filename"
                  class="image-preview"
                  @error="handleImageError"
                />
                <div class="image-info">
                  <div class="image-name">{{ image.filename }}</div>
                  <div class="image-meta">{{ image.width }}x{{ image.height }}</div>
                </div>
                <button class="btn-copy" @click.stop="copyImagePath(image)">📋 Copy Path</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Success/Error Messages -->
    <div v-if="message" :class="['message', messageType]">
      {{ message }}
    </div>
  </div>
</template>

<script>
import { getCollections, saveCollections } from '@/api/collections.js'
import { getTopics, createTopic } from '@/api/topics.js'
import NotificationTicker from '@/components/NotificationTicker.vue'
import Breadcrumbs from '@/components/Breadcrumbs.vue'

export default {
  name: 'DocumentBuilder',
  components: {
    NotificationTicker,
    Breadcrumbs
  },
  props: {
    notifications: {
      type: Array,
      default: () => []
    },
    globalNotifications: {
      type: Array,
      default: () => []
    },
    builderNotifications: {
      type: Array,
      default: () => []
    },
    markNotificationRead: {
      type: Function,
      required: false,
      default: () => () => {}
    }
  },
  data() {
    return {
      // Collections
      collections: [],
      selectedCollection: null,
      showCreateCollection: false,
      newCollection: {
        name: '',
        description: '',
        status: 'active',
        projectId: null
      },
      
      // Projects
      allProjects: [],
      
      // Topics
      allTopics: [],
      topicsFilter: '',
      
      // Links
      allLinks: [],
      recentLinks: [],
      showLinksModal: false,
      linksSearch: '',
      
      // Images
      allImages: [],
      recentImages: [],
      showImagesModal: false,
      imagesSearch: '',
      
      // UI State
      loading: true,
      message: '',
      messageType: 'success'
    }
  },
  
  computed: {
    allNotifications() {
      const all = [
        ...(this.globalNotifications || []),
        ...(this.builderNotifications || []),
        ...(this.notifications || [])
      ]
      const seen = new Set()
      return all.filter(n => {
        if (!n || !n.id) return true
        if (seen.has(n.id)) return false
        seen.add(n.id)
        return true
      })
    },
    
    collectionTopics() {
      if (!this.selectedCollection || !this.selectedCollection.topics) {
        return []
      }
      
      // Get full topic objects from collection topic IDs
      const topicIds = this.selectedCollection.topics.map(t => t.id)
      return this.allTopics.filter(topic => topicIds.includes(topic.id))
    },
    
    availableTopics() {
      if (!this.selectedCollection) return this.allTopics
      
      // Topics not in the current collection
      const collectionTopicIds = new Set((this.selectedCollection.topics || []).map(t => t.id))
      return this.allTopics.filter(topic => !collectionTopicIds.has(topic.id))
    },
    
    filteredAvailableTopics() {
      if (!this.topicsFilter) return this.availableTopics.slice(0, 10) // Limit for performance
      
      const filter = this.topicsFilter.toLowerCase()
      return this.availableTopics.filter(topic => 
        topic.title.toLowerCase().includes(filter) ||
        (topic.summary && topic.summary.toLowerCase().includes(filter))
      ).slice(0, 10)
    },
    
    filteredLinks() {
      if (!this.linksSearch) return this.allLinks
      
      const search = this.linksSearch.toLowerCase()
      return this.allLinks.filter(link => 
        link.title.toLowerCase().includes(search) ||
        link.reference_code?.toLowerCase().includes(search) ||
        link.url.toLowerCase().includes(search)
      )
    },
    
    filteredImages() {
      if (!this.imagesSearch) return this.allImages
      
      const search = this.imagesSearch.toLowerCase()
      return this.allImages.filter(image => 
        image.filename.toLowerCase().includes(search)
      )
    }
  },
  
  async created() {
    await this.loadData()
  },
  
  methods: {
    async loadData() {
      this.loading = true
      try {
        await Promise.all([
          this.loadCollections(),
          this.loadProjects(),
          this.loadTopics(),
          this.loadLinks(),
          this.loadImages()
        ])
      } catch (error) {
        console.error('Failed to load data:', error)
        this.showMessage('Failed to load data', 'error')
      } finally {
        this.loading = false
      }
    },
    
    async loadCollections() {
      try {
        this.collections = await getCollections()
      } catch (error) {
        console.error('Failed to load collections:', error)
        // Use mock data for development
        this.collections = [
          {
            id: 1,
            name: 'User Documentation',
            status: 'active',
            topics_count: 5,
            topics: []
          },
          {
            id: 2,
            name: 'API Reference',
            status: 'active',
            topics_count: 8,
            topics: []
          }
        ]
      }
    },
    
    async loadProjects() {
      try {
        const response = await fetch('/api/projects/')
        if (response.ok) {
          this.allProjects = await response.json()
        }
      } catch (error) {
        console.error('Failed to load projects:', error)
        // Mock data for development
        this.allProjects = [
          {
            id: 1,
            name: 'Census Data Portal Redesign',
            description: 'Modernizing the main census data access portal',
            status: 'active'
          },
          {
            id: 2,
            name: 'Economic Survey Documentation',
            description: 'Creating comprehensive documentation for the economic survey',
            status: 'planning'
          },
          {
            id: 3,
            name: 'Mobile App API Documentation',
            description: 'Complete API documentation for the mobile application',
            status: 'completed'
          }
        ]
      }
    },
    
    async loadTopics() {
      try {
        this.allTopics = await getTopics()
      } catch (error) {
        console.error('Failed to load topics:', error)
        // Mock data for development
        this.allTopics = [
          {
            id: 1,
            title: 'Getting Started',
            status: 'published',
            summary: 'Introduction to the system',
            updated_at: '2025-08-01T10:00:00Z'
          },
          {
            id: 2,
            title: 'User Interface Guide',
            status: 'draft',
            summary: 'Complete UI walkthrough',
            updated_at: '2025-08-02T14:30:00Z'
          }
        ]
      }
    },
    
    async loadLinks() {
      try {
        const response = await fetch('/api/links?include_usage=true')
        if (response.ok) {
          const data = await response.json()
          this.allLinks = data.links || []
          this.recentLinks = this.allLinks.slice(0, 5) // Show 5 most recent
        }
      } catch (error) {
        console.error('Failed to load links:', error)
        // Mock data
        this.allLinks = [
          {
            id: 1,
            title: 'Form AB-123',
            reference_code: 'AB-123',
            url: 'https://forms.example.com/ab-123',
            link_type: 'form'
          }
        ]
        this.recentLinks = this.allLinks.slice(0, 5)
      }
    },
    
    async loadImages() {
      try {
        // Load images from various import documents
        const response = await fetch('/api/import/history')
        if (response.ok) {
          const imports = await response.json()
          let allImages = []
          
          // Load images from each import
          for (const importDoc of imports.slice(0, 5)) { // Limit for performance
            try {
              const imagesResponse = await fetch(`/api/import/staging/${importDoc.id}/images`)
              if (imagesResponse.ok) {
                const imagesData = await imagesResponse.json()
                allImages = allImages.concat(imagesData.images || [])
              }
            } catch (e) {
              console.warn(`Failed to load images for import ${importDoc.id}:`, e)
            }
          }
          
          this.allImages = allImages
          this.recentImages = allImages.slice(0, 6) // Show 6 most recent
        }
      } catch (error) {
        console.error('Failed to load images:', error)
        this.allImages = []
        this.recentImages = []
      }
    },
    
    selectCollection(collection) {
      this.selectedCollection = collection
      this.topicsFilter = '' // Reset filter when switching collections
    },
    
    async createCollection() {
      try {
        // Add project information to the collection data
        const collectionData = {
          ...this.newCollection
        }
        
        // Add project name if a project is selected
        if (this.newCollection.projectId) {
          const selectedProject = this.allProjects.find(p => p.id === parseInt(this.newCollection.projectId))
          if (selectedProject) {
            collectionData.projectName = selectedProject.name
          }
        }
        
        const response = await fetch('/api/collections', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(collectionData)
        })
        
        if (response.ok) {
          const collection = await response.json()
          
          // Add project information to the collection for display
          if (collectionData.projectName) {
            collection.projectName = collectionData.projectName
            collection.projectId = this.newCollection.projectId
          }
          
          this.collections.push(collection)
          this.selectedCollection = collection
          this.showCreateCollection = false
          this.resetNewCollection()
          this.showMessage('Collection created successfully!')
        } else {
          throw new Error('Failed to create collection')
        }
      } catch (error) {
        console.error('Failed to create collection:', error)
        this.showMessage('Failed to create collection', 'error')
      }
    },
    
    resetNewCollection() {
      this.newCollection = {
        name: '',
        description: '',
        status: 'active',
        projectId: null
      }
    },

    generateFrontmatter(title) {
      const user = JSON.parse(localStorage.getItem('user') || '{}')
      const now = new Date().toLocaleString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        timeZoneName: 'short'
      })
      
      return `---
title: "${title}"
author: "${user.name || user.username || 'Unknown User'}"
created: "${now}"
modified: "${now}"
status: "draft"
---`
    },
    
    async addNewTopic() {
      try {
        const title = 'New Topic'
        const frontmatter = this.generateFrontmatter(title)
        
        const topicData = {
          title: title,
          content: `# ${title}\n\nStart writing your content here...`,
          frontmatter: frontmatter,
          status: 'draft'
        }
        
        const newTopic = await createTopic(topicData)
        this.allTopics.push(newTopic)
        
        // Add to current collection
        if (this.selectedCollection) {
          this.addTopicToCollection(newTopic)
        }
        
        // Navigate to edit the new topic
        this.$router.push(`/topics/${newTopic.id}/edit`)
      } catch (error) {
        console.error('Failed to create topic:', error)
        this.showMessage('Failed to create topic', 'error')
      }
    },
    
    addTopicToCollection(topic) {
      if (!this.selectedCollection) return
      
      // Add topic to collection topics array
      if (!this.selectedCollection.topics) {
        this.selectedCollection.topics = []
      }
      
      // Check if already added
      const exists = this.selectedCollection.topics.some(t => t.id === topic.id)
      if (exists) {
        this.showMessage('Topic already in collection', 'error')
        return
      }
      
      this.selectedCollection.topics.push({ id: topic.id, title: topic.title })
      this.saveCollectionChanges()
      this.showMessage(`"${topic.title}" added to collection`)
    },
    
    removeTopic(topic) {
      if (!this.selectedCollection) return
      
      this.selectedCollection.topics = this.selectedCollection.topics.filter(t => t.id !== topic.id)
      this.saveCollectionChanges()
      this.showMessage(`"${topic.title}" removed from collection`)
    },
    
    async saveCollectionChanges() {
      try {
        await saveCollections(this.collections)
      } catch (error) {
        console.error('Failed to save collection changes:', error)
        this.showMessage('Failed to save changes', 'error')
      }
    },
    
    editTopic(topic) {
      this.$router.push(`/topics/${topic.id}/edit`)
    },
    
    organizeCollection() {
      if (!this.selectedCollection) return
      this.$router.push(`/organize/${this.selectedCollection.id}`)
    },
    
    async publishCollection() {
      if (!this.selectedCollection) return
      
      try {
        const response = await fetch(`/api/collections/${this.selectedCollection.id}/publish`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' }
        })
        
        if (response.ok) {
          const result = await response.json()
          this.showMessage('Collection published successfully!')
          if (result.redirect_url) {
            this.$router.push(result.redirect_url)
          }
        } else {
          throw new Error('Failed to publish collection')
        }
      } catch (error) {
        console.error('Failed to publish collection:', error)
        this.showMessage('Failed to publish collection', 'error')
      }
    },
    
    copyLinkReference(link) {
      const reference = link.reference_code || link.title
      navigator.clipboard.writeText(reference).then(() => {
        this.showMessage(`Copied "${reference}" to clipboard`)
      }).catch(() => {
        this.showMessage('Failed to copy to clipboard', 'error')
      })
    },
    
    copyImagePath(image) {
      const path = image.public_url || `/images/imports/${image.document_id}/${image.filename}`
      navigator.clipboard.writeText(path).then(() => {
        this.showMessage(`Copied image path to clipboard`)
      }).catch(() => {
        this.showMessage('Failed to copy to clipboard', 'error')
      })
    },
    
    createNewLink() {
      // Navigate to link creation or open inline form
      this.showMessage('Link creation feature coming soon')
    },
    
    editLink(link) {
      // Navigate to link editing
      this.showMessage('Link editing feature coming soon')
    },
    
    handleImageError(event) {
      event.target.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIHZpZXdCb3g9IjAgMCA0MCA0MCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHJlY3Qgd2lkdGg9IjQwIiBoZWlnaHQ9IjQwIiBmaWxsPSIjRjNGNEY2Ii8+CjxwYXRoIGQ9Ik0yMCAyNUwyNSAyMEgxNUwyMCAyNVoiIGZpbGw9IiM5Q0EzQUYiLz4KPC9zdmc+Cg=='
    },
    
    showMessage(text, type = 'success') {
      this.message = text
      this.messageType = type
      setTimeout(() => {
        this.message = ''
      }, 3000)
    },
    
    formatStatus(status) {
      const statusMap = {
        'active': 'Active',
        'draft': 'Draft',
        'published': 'Published',
        'archived': 'Archived'
      }
      return statusMap[status] || status
    },
    
    formatRelativeTime(timestamp) {
      if (!timestamp) return 'Unknown'
      
      const now = new Date()
      const time = new Date(timestamp)
      const diffMs = now - time
      const diffMins = Math.floor(diffMs / 60000)
      const diffHours = Math.floor(diffMs / 3600000)
      const diffDays = Math.floor(diffMs / 86400000)

      if (diffMins < 1) return 'Just now'
      if (diffMins < 60) return `${diffMins}m ago`
      if (diffHours < 24) return `${diffHours}h ago`
      if (diffDays < 7) return `${diffDays}d ago`
      
      return time.toLocaleDateString()
    }
  }
}
</script>

<style scoped>
.document-builder {
  padding: 1rem;
  max-width: 1400px;
  margin: 0 auto;
}

.builder-header {
  text-align: center;
  margin-bottom: 2rem;
}

.builder-header h1 {
  color: #005a9c;
  margin-bottom: 0.5rem;
  font-size: 2.5rem;
  font-weight: 300;
}

.subtitle {
  color: #6c757d;
  font-size: 1.1rem;
}

.builder-layout {
  display: grid;
  grid-template-columns: 300px 1fr 280px;
  gap: 2rem;
  min-height: 80vh;
}

/* Left Sidebar - Collections */
.builder-sidebar {
  background: white;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 1.5rem;
  height: fit-content;
}

.sidebar-section {
  margin-bottom: 2rem;
}

.section-header {
  display: flex;
  justify-content: between;
  align-items: center;
  margin-bottom: 1rem;
}

.section-header h3 {
  margin: 0;
  color: #112e51;
  font-size: 1.1rem;
  font-weight: 600;
}

.collections-list {
  margin-bottom: 1rem;
}

.collection-item {
  display: flex;
  align-items: center;
  padding: 0.75rem;
  border: 1px solid #e9ecef;
  border-radius: 6px;
  margin-bottom: 0.5rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.collection-item:hover {
  border-color: #005a9c;
  background: #f8f9fa;
}

.collection-item.active {
  border-color: #005a9c;
  background: #e7f3ff;
}

.collection-icon {
  font-size: 1.2rem;
  margin-right: 0.75rem;
}

.collection-info {
  flex: 1;
}

.collection-name {
  font-weight: 600;
  color: #112e51;
  margin-bottom: 0.25rem;
}

.collection-meta {
  font-size: 0.8rem;
  color: #6c757d;
}

.collection-project {
  color: #005a9c;
  font-weight: 500;
}

/* Main Content */
.builder-main {
  background: white;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 2rem;
}

.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  color: #6c757d;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.workspace-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e9ecef;
}

.collection-title {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.collection-title h2 {
  margin: 0;
  color: #112e51;
}

.collection-badges {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.collection-status {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  background: #d1fae5;
  color: #065f46;
}

.project-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  background: #e7f3ff;
  color: #005a9c;
}

.workspace-actions {
  display: flex;
  gap: 0.5rem;
}

.topics-section {
  margin-bottom: 3rem;
}

.topics-section h3 {
  color: #112e51;
  margin-bottom: 1rem;
}

.topics-empty {
  text-align: center;
  padding: 2rem;
  border: 2px dashed #e9ecef;
  border-radius: 8px;
  color: #6c757d;
}

.topics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1rem;
}

.topic-card {
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 1rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.topic-card:hover {
  border-color: #005a9c;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.topic-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.5rem;
}

.topic-header h4 {
  margin: 0;
  color: #112e51;
  font-size: 1rem;
}

.topic-status {
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
}

.status-draft {
  background: #fef3c7;
  color: #92400e;
}

.status-published {
  background: #d1fae5;
  color: #065f46;
}

.topic-summary {
  color: #6c757d;
  font-size: 0.9rem;
  margin-bottom: 0.75rem;
  line-height: 1.4;
}

.topic-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.topic-updated {
  font-size: 0.8rem;
  color: #9ca3af;
}

.topic-actions {
  display: flex;
  gap: 0.25rem;
}

.available-topics-section {
  border-top: 1px solid #e9ecef;
  padding-top: 2rem;
}

.available-topics-section h3 {
  color: #112e51;
  margin-bottom: 1rem;
}

.topics-filter {
  margin-bottom: 1rem;
}

.filter-input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #e9ecef;
  border-radius: 6px;
  font-size: 0.9rem;
}

.available-topics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1rem;
}

.available-topic-card {
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 1rem;
  position: relative;
  transition: all 0.2s ease;
}

.available-topic-card:hover {
  border-color: #005a9c;
  background: #f8f9fa;
}

.btn-add {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  background: #005a9c;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 0.25rem 0.5rem;
  font-size: 0.8rem;
  cursor: pointer;
}

/* Right Sidebar - Resources */
.builder-resources {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.resource-section {
  background: white;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 1rem;
}

.links-list {
  margin-bottom: 1rem;
}

.link-item {
  display: flex;
  align-items: center;
  padding: 0.5rem;
  border: 1px solid #e9ecef;
  border-radius: 4px;
  margin-bottom: 0.5rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.link-item:hover {
  background: #f8f9fa;
  border-color: #005a9c;
}

.link-icon {
  font-size: 1rem;
  margin-right: 0.5rem;
}

.link-info {
  flex: 1;
}

.link-title {
  font-weight: 600;
  font-size: 0.9rem;
  color: #112e51;
}

.link-code {
  font-size: 0.8rem;
  color: #6c757d;
}

.images-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.image-item {
  aspect-ratio: 1;
  border: 1px solid #e9ecef;
  border-radius: 4px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.2s ease;
}

.image-item:hover {
  border-color: #005a9c;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.image-thumbnail {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* Buttons */
.btn-primary {
  background: #005a9c;
  color: white;
  border: none;
  padding: 0.75rem 1rem;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s ease;
}

.btn-primary:hover {
  background: #004080;
}

.btn-secondary {
  background: #6c757d;
  color: white;
  border: none;
  padding: 0.75rem 1rem;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s ease;
}

.btn-secondary:hover {
  background: #5a6268;
}

.btn-outline {
  background: transparent;
  color: #005a9c;
  border: 1px solid #005a9c;
  padding: 0.75rem 1rem;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-outline:hover {
  background: #005a9c;
  color: white;
}

.btn-success {
  background: #28a745;
  color: white;
  border: none;
  padding: 0.75rem 1rem;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s ease;
}

.btn-success:hover {
  background: #218838;
}

.btn-icon {
  background: transparent;
  border: none;
  font-size: 1rem;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 4px;
  transition: background 0.2s ease;
}

.btn-icon:hover {
  background: #f8f9fa;
}

.btn-close {
  background: transparent;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  padding: 0.25rem;
  color: #6c757d;
}

.full-width {
  width: 100%;
}

/* Modals */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: white;
  border-radius: 8px;
  min-width: 500px;
  max-width: 90vw;
  max-height: 90vh;
  overflow: auto;
}

.modal.large {
  min-width: 800px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e9ecef;
}

.modal-header h3 {
  margin: 0;
  color: #112e51;
}

.modal-body {
  padding: 1.5rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #112e51;
}

.form-group input,
.form-group textarea,
.form-group select {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #e9ecef;
  border-radius: 6px;
  font-size: 0.9rem;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  margin-top: 1.5rem;
}

/* Links Manager */
.links-controls {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.search-input {
  flex: 1;
  padding: 0.75rem;
  border: 1px solid #e9ecef;
  border-radius: 6px;
  font-size: 0.9rem;
}

.link-row {
  display: flex;
  align-items: center;
  padding: 1rem;
  border: 1px solid #e9ecef;
  border-radius: 6px;
  margin-bottom: 0.5rem;
}

.link-main {
  flex: 1;
}

.link-main .link-title {
  font-weight: 600;
  color: #112e51;
  margin-bottom: 0.25rem;
}

.link-main .link-url {
  color: #6c757d;
  font-size: 0.9rem;
}

.link-details {
  display: flex;
  gap: 1rem;
  margin-right: 1rem;
}

.link-details .link-code {
  background: #e7f3ff;
  color: #005a9c;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 600;
}

.link-details .link-type {
  background: #f8f9fa;
  color: #6c757d;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
}

.link-actions {
  display: flex;
  gap: 0.25rem;
}

/* Images Manager */
.images-controls {
  margin-bottom: 1.5rem;
}

.images-gallery {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 1rem;
}

.image-card {
  border: 1px solid #e9ecef;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.2s ease;
}

.image-card:hover {
  border-color: #005a9c;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.image-preview {
  width: 100%;
  height: 120px;
  object-fit: cover;
}

.image-info {
  padding: 0.75rem;
}

.image-name {
  font-weight: 600;
  font-size: 0.9rem;
  color: #112e51;
  margin-bottom: 0.25rem;
  word-break: break-word;
}

.image-meta {
  font-size: 0.8rem;
  color: #6c757d;
}

.btn-copy {
  width: 100%;
  background: #005a9c;
  color: white;
  border: none;
  padding: 0.5rem;
  font-size: 0.8rem;
  cursor: pointer;
}

/* Messages */
.message {
  position: fixed;
  top: 2rem;
  right: 2rem;
  padding: 1rem 1.5rem;
  border-radius: 6px;
  font-weight: 600;
  z-index: 1100;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.message.success {
  background: #d1fae5;
  color: #065f46;
  border: 1px solid #a7f3d0;
}

.message.error {
  background: #fee2e2;
  color: #dc2626;
  border: 1px solid #fca5a5;
}

/* Responsive Design */
@media (max-width: 1200px) {
  .builder-layout {
    grid-template-columns: 250px 1fr 250px;
  }
}

@media (max-width: 1000px) {
  .builder-layout {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  
  .builder-sidebar,
  .builder-resources {
    order: 2;
  }
  
  .builder-main {
    order: 1;
  }
  
  .workspace-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .workspace-actions {
    width: 100%;
    justify-content: space-between;
  }
  
  .topics-grid {
    grid-template-columns: 1fr;
  }
  
  .available-topics-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .document-builder {
    padding: 0.5rem;
  }
  
  .builder-header h1 {
    font-size: 2rem;
  }
  
  .modal {
    min-width: auto;
    width: 95vw;
  }
  
  .images-gallery {
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  }
}
</style>
