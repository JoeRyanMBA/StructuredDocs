<template>
  <div class="all-links">
    <div class="page-header">
      <h1>🔗 All Links</h1>
      <p class="guidance-text">
        Browse and manage all reusable links available for use in your content. Create links once and reuse them across multiple topics with reference codes like "AB-123" or "DOC-456".
      </p>
    </div>

    <div class="page-actions">
      <div class="search-and-filters">
        <input 
          v-model="searchQuery" 
          type="text" 
          class="search-input"
          placeholder="Search links by title, URL, or reference code..." 
          @keyup.enter="loadLinks"
        />
        <select v-model="filterType" class="filter-select" @change="applyFilters">
          <option value="">All Types</option>
          <option v-for="type in linkTypes" :key="type" :value="type">
            {{ formatLinkType(type) }}
          </option>
        </select>
        <select v-model="filterStatus" class="filter-select" @change="applyFilters">
          <option value="">All Status</option>
          <option value="active">Active</option>
          <option value="inactive">Inactive</option>
        </select>
      </div>
      <div class="action-buttons">
  <button @click="loadLinks" class="btn btn-secondary btn-sm">
          <i class="bi bi-search"></i> Search
        </button>
        <button @click="createNewLink" class="btn btn-primary">
          <span class="action-icon"><IconPlus size="28" /></span> Create Link
        </button>
        <button @click="refreshLinks" class="btn btn-secondary btn-sm">
          <i class="bi bi-arrow-clockwise"></i> Refresh
        </button>
      </div>
    </div>

    <div v-if="loading" class="loading">
      <div class="loading-spinner"></div>
      <p>Loading links...</p>
    </div>

    <div v-else-if="error" class="error-message">
      <p>{{ error }}</p>
      <button @click="loadLinks" class="btn btn-secondary">Try Again</button>
    </div>

    <div v-else-if="filteredLinks.length === 0" class="empty-state">
      <div class="empty-icon">🔗</div>
      <h3>No Links Found</h3>
      <p>{{ hasFilters ? 'No links match your search criteria.' : 'No links are currently available.' }}</p>
      <div class="empty-actions">
  <button @click="clearFilters" v-if="hasFilters" class="btn btn-secondary btn-sm"><i class="bi bi-x"></i> Clear Filters</button>
        <button @click="createNewLink" class="btn btn-primary">Create First Link</button>
      </div>
    </div>

    <div v-else class="links-content">
      <!-- Summary Stats -->
      <div class="stats-bar">
        <div class="stat-item">
          <span class="stat-number">{{ filteredLinks.length }}</span>
          <span class="stat-label">{{ filteredLinks.length === 1 ? 'Link' : 'Links' }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-number">{{ activeLinksCount }}</span>
          <span class="stat-label">Active</span>
        </div>
        <div class="stat-item" v-if="importedLinksCount > 0">
          <span class="stat-number">{{ importedLinksCount }}</span>
          <span class="stat-label">Imported</span>
        </div>
        <div class="stat-item" v-if="importedLinksCount > 0">
          <span class="stat-number">{{ regularLinksCount }}</span>
          <span class="stat-label">Regular</span>
        </div>
        <div class="stat-item" v-if="hasFilters">
          <span class="stat-number">{{ allLinks.length }}</span>
          <span class="stat-label">Total Available</span>
        </div>
        <div class="stat-item">
          <span class="stat-number" :class="{ 'stat-warning': unusedLinksCount > 0 }">{{ unusedLinksCount }}</span>
          <span class="stat-label">Unused</span>
        </div>
      </div>

      <!-- Links List -->
      <div class="links-list">
        <div class="list-header">
          <div class="col-id">ID</div>
          <div class="col-title">Title & URL</div>
          <div class="col-reference">Reference</div>
          <div class="col-type">Type</div>
          <div class="col-topics">Topics</div>
          <div class="col-status">Status</div>
          <div class="col-actions">Actions</div>
        </div>
        
        <div 
          v-for="link in filteredLinks" 
          :key="link.id"
          class="link-row"
          @click="selectLink(link)"
          :class="{ 'selected': selectedLink?.id === link.id }"
        >
          <div class="col-id">#{{ link.id }}</div>
          <div class="col-title">
            <div class="link-main">
              <div class="link-title" :title="link.title">{{ link.title }}</div>
              <div class="link-url" :title="link.url">{{ link.url }}</div>
              <div v-if="link.description" class="link-description" :title="link.description">
                {{ link.description }}
              </div>
            </div>
          </div>
          <div class="col-reference">
            <div class="reference-info">
              <span v-if="link.reference_code" class="reference-code">{{ link.reference_code }}</span>
              <span v-else class="no-reference">No reference</span>

            </div>
          </div>
          <div class="col-type">
            <span class="link-type" :class="'type-' + link.link_type">
              {{ formatLinkType(link.link_type) }}
            </span>
          </div>
          <div class="col-topics" @click.stop>
            <UsageBadge
              :count="link.usage_count || 0"
              label="topic"
              :items="link.used_in_topics_detail || []"
            />
          </div>
          <div class="col-status">
            <span :class="['status-badge', link.is_active ? 'status-active' : 'status-inactive']">
              {{ link.is_active ? 'Active' : 'Inactive' }}
            </span>
          </div>
          <div class="col-actions">
            <button class="btn-icon" @click.stop="copyLinkReference(link)" title="Copy Reference"><i class="bi bi-clipboard"></i></button>
            <button class="btn-icon" @click.stop="viewLinkDetails(link)" title="View Details"><i class="bi bi-zoom-in"></i></button>
            <button class="btn-icon" @click.stop="editLink(link)" title="Edit Link"><i class="bi bi-pencil-square"></i></button>
            <button class="btn-icon" @click.stop="openUrl(link)" title="Open URL" v-if="link.url"><i class="bi bi-box-arrow-up-right"></i></button>
          </div>
        </div>
      </div>
    </div>

    <!-- Link Details Modal -->
  <div v-if="showDetailsModal" class="modal-overlay" @click.self="closeDetailsModal">
      <div class="modal large" @click.stop>
        <div class="modal-header-row modal-header">
          <h3>Link Details</h3>
          <button class="plain-close btn-close" @click="closeDetailsModal">✕</button>
        </div>
        <div class="modal-body" v-if="selectedLink">
          <div class="link-details">
            <div class="detail-main">
              <div class="detail-group">
                <label>Title:</label>
                <span>{{ selectedLink.title }}</span>
              </div>
              <div class="detail-group">
                <label>URL:</label>
                <div class="url-display">
                  <a :href="selectedLink.url" target="_blank" rel="noopener noreferrer">{{ selectedLink.url }}</a>
                  <button @click="openUrl(selectedLink)" class="btn-icon" title="Open URL"><i class="bi bi-box-arrow-up-right"></i></button>
                </div>
              </div>
              <div class="detail-group" v-if="selectedLink.description">
                <label>Description:</label>
                <span>{{ selectedLink.description }}</span>
              </div>
              <div class="detail-group">
                <label>Reference Code:</label>
                <div class="reference-display">
                  <code v-if="selectedLink.reference_code">{{ selectedLink.reference_code }}</code>
                  <span v-else class="no-reference">No reference code</span>
                  <button v-if="selectedLink.reference_code" @click="copyLinkReference(selectedLink)" class="btn btn-secondary btn-sm"><i class="bi bi-clipboard"></i> Copy</button>
                </div>
              </div>
              <div class="detail-group">
                <label>Type:</label>
                <span class="link-type" :class="'type-' + selectedLink.link_type">
                  {{ formatLinkType(selectedLink.link_type) }}
                </span>
              </div>
              <div class="detail-group">
                <label>Status:</label>
                <span :class="['status-badge', selectedLink.is_active ? 'status-active' : 'status-inactive']">
                  {{ selectedLink.is_active ? 'Active' : 'Inactive' }}
                </span>
              </div>
              <div class="detail-group" v-if="selectedLink.usage_count !== undefined">
                <label>Usage:</label>
                <span>Used in {{ selectedLink.usage_count }} {{ selectedLink.usage_count === 1 ? 'topic' : 'topics' }}</span>
              </div>
              <div class="detail-group" v-if="selectedLink.created_at">
                <label>Created:</label>
                <span>{{ formatDate(selectedLink.created_at) }}</span>
              </div>
              <div class="detail-group" v-if="selectedLink.updated_at">
                <label>Last Updated:</label>
                <span>{{ formatDate(selectedLink.updated_at) }}</span>
              </div>
            </div>
            
            <div class="detail-usage" v-if="selectedLink.topics && selectedLink.topics.length > 0">
              <h4>Used in Topics:</h4>
              <div class="usage-list">
                <div v-for="topic in selectedLink.topics" :key="topic.id" class="usage-item">
                  <div class="topic-title">{{ topic.title }}</div>
                  <div v-if="topic.context" class="topic-context">{{ topic.context }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="copyLinkReference(selectedLink)" class="btn btn-secondary" v-if="selectedLink.reference_code">
            <i class="bi bi-clipboard"></i> Copy Reference
          </button>
          <button @click="openUrl(selectedLink)" class="btn btn-secondary" v-if="selectedLink.url">
            <i class="bi bi-box-arrow-up-right"></i> Open URL
          </button>
          <button @click="editLink(selectedLink)" class="btn btn-primary">
            <i class="bi bi-pencil-square"></i> Edit Link
          </button>
          <button @click="closeDetailsModal" class="btn btn-secondary">Close</button>
        </div>
      </div>
    </div>

    <!-- Create/Edit Link Modal -->
  <div v-if="showEditModal" class="modal-overlay" @click.self="closeEditModal">
      <div class="modal" @click.stop>
        <div class="modal-header-row modal-header">
          <h3>{{ editingLink ? 'Edit Link' : 'Create New Link' }}</h3>
          <button class="plain-close btn-close" @click="closeEditModal">✕</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="saveLink">
            <div class="form-group">
              <label>Title *</label>
              <input 
                v-model="linkForm.title" 
                type="text"
                class="form-input"
                placeholder="Enter link title"
                required 
              />
            </div>
            <div class="form-group">
              <label>URL *</label>
              <input 
                v-model="linkForm.url" 
                type="url"
                class="form-input"
                placeholder="https://example.com"
                required 
              />
            </div>
            <!-- Reference code is auto-assigned by the system; no manual entry -->
            <div class="form-group">
              <label>Description</label>
              <textarea 
                v-model="linkForm.description" 
                class="form-textarea"
                placeholder="Optional description of this link"
                rows="3"
              ></textarea>
            </div>
            <div class="form-group">
              <label>Type</label>
              <select v-model="linkForm.link_type" class="form-select">
                <option v-for="type in linkTypes" :key="type" :value="type">
                  {{ formatLinkType(type) }}
                </option>
              </select>
            </div>
            <div class="form-group">
              <label class="checkbox-label">
                <input 
                  v-model="linkForm.is_active" 
                  type="checkbox"
                  class="form-checkbox"
                />
                Active
              </label>
              <small class="form-help">Inactive links are hidden from most views</small>
            </div>
            <div class="form-group">
              <label class="checkbox-label">
                <input 
                  v-model="linkForm.is_internal" 
                  type="checkbox"
                  class="form-checkbox"
                />
                Internal Link
              </label>
              <small class="form-help">Check if this is an internal company/organization link</small>
            </div>
          </form>
          <div v-if="editingLink?.id" class="form-group" style="padding: 0 1.5rem 1rem;">
            <label>Tags</label>
            <TagEditor entity-type="link" :entity-id="editingLink.id" />
          </div>
        </div>
        <div class="modal-footer">
          <button @click="saveLink" class="btn btn-primary" :disabled="!linkForm.title || !linkForm.url">
            {{ editingLink ? 'Update Link' : 'Create Link' }}
          </button>
          <button @click="closeEditModal" class="btn btn-secondary">Cancel</button>
        </div>
      </div>
    </div>

  <!-- Toasts handled globally via ToastContainer -->
  </div>
</template>

<script>
import { toast } from '@/composables/useToast'
import unsavedChangesGuard from '@/mixins/unsavedChangesGuard.js'
import { apiRequest } from '../api/base.js'
import UsageBadge from '@/components/UsageBadge.vue'
import TagEditor from '@/components/TagEditor.vue'

export default {
  name: 'AllLinksView',
  components: { UsageBadge, TagEditor },
  mixins: [unsavedChangesGuard],
  data() {
    return {
      allLinks: [],
      filteredLinks: [],
      loading: false,
      error: null,
      searchQuery: '',
      filterType: '',
      filterStatus: '',
      selectedLink: null,
      showDetailsModal: false,
      showEditModal: false,
      editingLink: null,
  linkForm: {
        title: '',
        url: '',
        description: '',
        link_type: 'other',
        is_active: true,
        is_internal: false
      },
  lastSavedLinkSnapshot: '',
      linkTypes: ['form', 'document', 'website', 'policy', 'procedure', 'regulation', 'other'],
  message: '',
  messageType: 'success' // legacy
    }
  },
  computed: {
    hasFilters() {
      return !!(this.searchQuery || this.filterType || this.filterStatus)
    },
    
    activeLinksCount() {
      return this.filteredLinks.filter(link => link.is_active).length
    },
    
    importedLinksCount() {
      return this.filteredLinks.filter(link => link.source === 'import').length
    },
    
    regularLinksCount() {
      return this.filteredLinks.filter(link => link.source !== 'import').length
    },
    
    unusedLinksCount() {
      return this.filteredLinks.filter(link => !link.usage_count || link.usage_count === 0).length
    }
  },
  async created() {
    await this.loadLinks()
  },
  methods: {
    async loadLinks() {
      this.loading = true
      this.error = null
      
      try {
        const data = await apiRequest('/api/links/?include_usage=true')
        this.allLinks = data.links || []
        this.applyFilters()
      } catch (error) {
        console.error('Failed to load links:', error)
        this.allLinks = []
        this.applyFilters()
      } finally {
        this.loading = false
      }
    },

    applyFilters() {
      let filtered = [...this.allLinks]

      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase()
        filtered = filtered.filter(link => 
          link.title.toLowerCase().includes(query) ||
          link.url.toLowerCase().includes(query) ||
          (link.reference_code && link.reference_code.toLowerCase().includes(query)) ||
          (link.description && link.description.toLowerCase().includes(query))
        )
      }

      if (this.filterType) {
        filtered = filtered.filter(link => link.link_type === this.filterType)
      }

      if (this.filterStatus) {
        const isActive = this.filterStatus === 'active'
        filtered = filtered.filter(link => link.is_active === isActive)
      }

      // Sort by title
      filtered.sort((a, b) => a.title.localeCompare(b.title))

      this.filteredLinks = filtered
    },

    async refreshLinks() {
      await this.loadLinks()
      toast.success('Links refreshed successfully!')
    },

    clearFilters() {
      this.searchQuery = ''
      this.filterType = ''
      this.filterStatus = ''
      this.applyFilters()
    },

    selectLink(link) {
      this.selectedLink = link
    },

    viewLinkDetails(link) {
      this.selectedLink = link
      this.showDetailsModal = true
    },

    closeDetailsModal() {
      this.showDetailsModal = false
    },

  createNewLink() {
      this.editingLink = null
      this.linkForm = {
        title: '',
        url: '',
        description: '',
        link_type: 'other',
        is_active: true,
        is_internal: false
      }
      this.showEditModal = true
      this.$nextTick(()=>{ this.lastSavedLinkSnapshot = JSON.stringify(this.linkForm) })
    },

  editLink(link) {
      this.editingLink = link
      this.linkForm = {
        title: link.title || '',
        url: link.url || '',
        description: link.description || '',
        link_type: link.link_type || 'other',
        is_active: link.is_active !== false,
        is_internal: link.is_internal || false
      }
      this.showEditModal = true
      this.$nextTick(()=>{ this.lastSavedLinkSnapshot = JSON.stringify(this.linkForm) })
    },

    closeEditModal() {
      this.showEditModal = false
      this.editingLink = null
      this.lastSavedLinkSnapshot = ''
    },

  async saveLink() {
      try {
        const method = this.editingLink ? 'PUT' : 'POST'
        const url = this.editingLink ? `/api/links/${this.editingLink.id}` : '/api/links/'
        
        // Build payload; exclude reference_code on create so server can auto-generate
        const payload = { ...this.linkForm }
        if (!this.editingLink) {
          delete payload.reference_code
        }

        const response = await fetch(url, {
          method,
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(payload)
        })

        if (response.ok) {
          toast.success(this.editingLink ? 'Link updated successfully!' : 'Link created successfully!')
          this.lastSavedLinkSnapshot = JSON.stringify(this.linkForm)
          this.closeEditModal()
          await this.loadLinks()
        } else {
          const errorData = await response.json()
          throw new Error(errorData.error || 'Failed to save link')
        }
      } catch (error) {
        console.error('Failed to save link:', error)
        toast.error(error.message || 'Failed to save link')
      }
    },

    copyLinkReference(link) {
      const reference = link.reference_code || link.title
      navigator.clipboard.writeText(reference).then(() => {
        toast.success(`Copied "${reference}" to clipboard`)
      }).catch(() => {
        toast.error('Failed to copy to clipboard')
      })
    },

    openUrl(link) {
      if (link.url) {
        window.open(link.url, '_blank', 'noopener,noreferrer')
      }
    },

    formatLinkType(type) {
      const typeMap = {
        form: 'Form',
        document: 'Document',
        website: 'Website',
        policy: 'Policy',
        procedure: 'Procedure',
        regulation: 'Regulation',
        other: 'Other'
      }
      return typeMap[type] || type
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

    showMessage(text, type = 'success') { /* legacy no-op for backward compat */
      if (type === 'error') toast.error(text); else toast.success(text)
    },
    isDirty() {
      if (!this.showEditModal) return false
      try { return JSON.stringify(this.linkForm) !== this.lastSavedLinkSnapshot } catch(e){ return false }
    }
  },

  watch: {
    searchQuery() {
      this.applyFilters()
    },
    filterType() {
      this.applyFilters()
    },
    filterStatus() {
      this.applyFilters()
    }
  }
}
</script>
<style>
.all-links {
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
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.search-and-filters {
  display: flex;
  gap: 1rem;
  flex: 1;
  align-items: center;
  flex-wrap: wrap;
}

.search-input {
  flex: 1;
  min-width: 300px;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 1rem;
}

.filter-select {
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 1rem;
  background: white;
}

.action-buttons {
  display: flex;
  gap: 1rem;
}

/* Buttons: rely on global button system in assets/style.css */

/* Use global button system from assets/style.css for consistency */

.loading {
  text-align: center;
  padding: 4rem 2rem;
  color: #666;
}

/* Use global loading styles */

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

.empty-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-top: 2rem;
}

.stats-bar {
  display: flex;
  gap: 2rem;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
  margin-bottom: 2rem;
  flex-wrap: wrap;
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

.stat-number.stat-warning {
  color: #b45309;
}

.stat-label {
  display: block;
  font-size: 0.875rem;
  color: #666;
  margin-top: 0.25rem;
}

/* Links List */
.links-list {
  background: white;
  border: 1px solid #ddd;
  border-radius: 8px;
  overflow: visible;
}

.list-header {
  display: grid;
  grid-template-columns: 55px 2fr 150px 120px 120px 100px 150px;
  gap: 1rem;
  padding: 1rem;
  background: #f8f9fa;
  font-weight: 500;
  border-bottom: 1px solid #ddd;
}

.link-row {
  display: grid;
  grid-template-columns: 55px 2fr 150px 120px 120px 100px 150px;
  gap: 1rem;
  padding: 1rem;
  border-bottom: 1px solid #eee;
  cursor: pointer;
  transition: all 0.2s ease;
  align-items: start;
}

.col-id {
  font-size: 0.8rem;
  color: #5a6a8a;
  text-align: center;
  white-space: nowrap;
  padding-top: 0.1rem;
}

.link-row:hover {
  background: #f8f9fa;
}

.link-row.selected {
  background: var(--primary-light-blue);
  border-color: var(--primary-medium-teal);
}

.col-title {
  min-width: 0;
}

.link-main {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  min-width: 0;
}

.link-title {
  font-weight: 500;
  color: #333;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.link-url {
  font-size: 0.875rem;
  color: #666;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.link-description {
  font-size: 0.875rem;
  color: #777;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-top: 0.25rem;
}

.reference-code {
  background: var(--primary-light-blue);
  color: var(--primary-dark-blue);
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-family: monospace;
  font-size: 0.875rem;
  font-weight: 500;
}

.no-reference {
  color: #999;
  font-style: italic;
  font-size: 0.875rem;
}

.reference-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}


.link-type {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.875rem;
  font-weight: 500;
}

.type-form { background: #e8f5e8; color: #2e7d32; }
.type-document { background: #fff3e0; color: #f57c00; }
.type-website { background: #e3f2fd; color: #1976d2; }
.type-policy { background: #fce4ec; color: #c2185b; }
.type-procedure { background: #f3e5f5; color: #7b1fa2; }
.type-regulation { background: #ffebee; color: #d32f2f; }
.type-other { background: #f5f5f5; color: #616161; }

.usage-count {
  color: #666;
  font-size: 0.875rem;
}

.usage-unknown {
  color: #999;
  font-style: italic;
}

.status-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.875rem;
  font-weight: 500;
}

.status-active {
  background: #e8f5e8;
  color: #2e7d32;
}

.status-inactive {
  background: #ffebee;
  color: #d32f2f;
}

.col-actions {
  display: flex;
  gap: 0.5rem;
}

/* Modal Styles - using global .modal-overlay and .modal utilities */

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

.link-details {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
}

.detail-main {
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

.url-display {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.url-display a {
  flex: 1;
  color: var(--primary-medium-teal);
  text-decoration: none;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.url-display a:hover {
  text-decoration: underline;
}

.reference-display {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.reference-display code {
  flex: 1;
  background: #f5f5f5;
  padding: 0.5rem;
  border-radius: 4px;
  font-size: 0.875rem;
}

.btn-copy {
  background: var(--primary-medium-teal);
  color: white;
  border: none;
  border-radius: 4px;
  padding: 0.5rem 1rem;
  cursor: pointer;
  font-size: 0.875rem;
}

.btn-copy:hover {
  background: var(--primary-light-teal);
}

.detail-usage h4 {
  margin: 0 0 1rem 0;
  color: #333;
}

.usage-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.usage-item {
  padding: 0.75rem;
  background: #f8f9fa;
  border-radius: 6px;
  border-left: 3px solid var(--primary-medium-teal);
}

.topic-title {
  font-weight: 500;
  color: #333;
}

.topic-context {
  font-size: 0.875rem;
  color: #666;
  margin-top: 0.25rem;
}

/* Form Styles */
.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #333;
}

.form-input,
.form-textarea,
.form-select {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 1rem;
  transition: border-color 0.2s ease;
}

.form-input:focus,
.form-textarea:focus,
.form-select:focus {
  outline: none;
  border-color: #2196f3;
  box-shadow: 0 0 0 2px rgba(33, 150, 243, 0.1);
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
}

.checkbox-label {
  display: flex !important;
  align-items: center;
  gap: 0.5rem;
  font-weight: normal !important;
  margin-bottom: 0 !important;
}

.form-checkbox {
  width: auto !important;
  margin: 0 !important;
}

.form-help {
  display: block;
  margin-top: 0.25rem;
  font-size: 0.875rem;
  color: #666;
}

/* Removed legacy .message-toast styles; using global ToastContainer */

/* Responsive Design */
@media (max-width: 1200px) {
  .list-header,
  .link-row {
    grid-template-columns: 55px 2fr 130px 110px 80px 130px;
  }

  .col-reference {
    display: none;
  }
}

@media (max-width: 768px) {
  .all-links {
    padding: 1rem;
  }

  .page-actions {
    flex-direction: column;
    align-items: stretch;
  }

  .search-and-filters {
    flex-direction: column;
  }

  .search-input {
    min-width: auto;
  }

  .list-header,
  .link-row {
    grid-template-columns: 1fr 80px 120px;
    font-size: 0.875rem;
  }

  .col-reference,
  .col-type,
  .col-status {
    display: none;
  }

  .link-details {
    grid-template-columns: 1fr;
  }

  .modal.large {
    min-width: auto;
    margin: 1rem;
  }

  .stats-bar {
    justify-content: center;
  }
}
</style>
