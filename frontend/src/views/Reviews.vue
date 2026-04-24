<template>
  <div class="reviews">
    
    <h2>Review Dashboard <HelpIcon feature="reviews.request" /></h2>
    
    <p class="guidance-text">
      Review and approve topics, collections, and imported content before publication. Use this dashboard to manage the content approval workflow.
    </p>

    <!-- Review Statistics -->
    <div class="stats-grid" v-if="stats">
      <div class="stat-card">
        <h3>Topics</h3>
        <div class="stat-row">
          <span class="stat-label">Pending Review:</span>
          <span class="stat-value pending">{{ stats.topics?.pending_review || 0 }}</span>
        </div>
        <div class="stat-row">
          <span class="stat-label">Drafts:</span>
          <span class="stat-value draft">{{ stats.topics?.draft || 0 }}</span>
        </div>
        <div class="stat-row">
          <span class="stat-label">Published:</span>
          <span class="stat-value published">{{ stats.topics?.published || 0 }}</span>
        </div>
      </div>
      
      <div class="stat-card">
        <h3>Imports</h3>
        <div class="stat-row">
          <span class="stat-label">Pending:</span>
          <span class="stat-value pending">{{ stats.imports?.pending || 0 }}</span>
        </div>
        <div class="stat-row">
          <span class="stat-label">Approved:</span>
          <span class="stat-value sme">{{ stats.imports?.sme_approved || 0 }}</span>
        </div>
        <div class="stat-row">
          <span class="stat-label">Final Approved:</span>
          <span class="stat-value published">{{ stats.imports?.final_approved || 0 }}</span>
        </div>
      </div>
    </div>

    <!-- Review Tabs -->
    <div class="review-tabs">
      <button 
        @click="activeTab = 'topics'" 
        :class="{ active: activeTab === 'topics' }"
        class="tab-btn"
      >
        Topics Pending Review ({{ pendingTopics.length }})
      </button>
      <button 
        @click="activeTab = 'collections'" 
        :class="{ active: activeTab === 'collections' }"
        class="tab-btn"
      >
        Collections ({{ pendingCollections.length }})
      </button>
      <button 
        @click="activeTab = 'imports'" 
        :class="{ active: activeTab === 'imports' }"
        class="tab-btn"
      >
        Import Reviews ({{ pendingImports.length }})
      </button>
    </div>

    <!-- Loading and Error States -->
    <div v-if="loading" class="loading">Loading review items...</div>
    <div v-else-if="error" class="error">{{ error }}</div>

    <!-- Topics Tab -->
    <div v-if="activeTab === 'topics'" class="review-content">
      <div v-if="pendingTopics.length === 0" class="empty">
        No topics pending review.
      </div>
      <div v-else class="review-grid">
        <div v-for="topic in pendingTopics" :key="topic.id" class="review-item">
          <div class="item-header">
            <h4>{{ topic.title }}</h4>
            <span class="status-badge" :class="topic.status">{{ formatStatus(topic.status) }}</span>
          </div>
          <p class="item-preview">{{ topic.content?.substring(0, 150) }}...</p>
          <div class="item-meta">
            <span>Updated: {{ formatDate(topic.updated_at) }}</span>
          </div>
          <div class="item-actions">
            <button @click="reviewTopic(topic, 'approve')" class="btn-approve">
              ✓ Approve
            </button>
            <button @click="reviewTopic(topic, 'reject')" class="btn-reject">
              ✗ Reject
            </button>
            <router-link :to="{ name: 'EditTopic', params: { id: topic.id } }" class="btn-edit">
              Edit
            </router-link>
          </div>
        </div>
      </div>
    </div>

    <!-- Collections Tab -->
    <div v-if="activeTab === 'collections'" class="review-content">
      <div v-if="pendingCollections.length === 0" class="empty">
        No collections pending review.
      </div>
      <div v-else class="review-grid">
        <div v-for="collection in pendingCollections" :key="collection.id" class="review-item">
          <div class="item-header">
            <h4>{{ collection.name }}</h4>
            <span class="status-badge collection">Collection</span>
          </div>
          <p class="item-preview">{{ collection.description || 'No description' }}</p>
          <div class="item-meta">
            <span>Created: {{ formatDate(collection.created_at) }}</span>
            <span>Topics: {{ collection.topics?.length || 0 }}</span>
          </div>
          <div class="item-actions">
            <router-link :to="{ name: 'Collections' }" class="btn-edit">
              View Collection
            </router-link>
          </div>
        </div>
      </div>
    </div>

    <!-- Imports Tab -->
    <div v-if="activeTab === 'imports'" class="review-content">
      <div v-if="pendingImports.length === 0" class="empty">
        No imports pending review.
      </div>
      <div v-else class="review-grid">
        <div v-for="importItem in pendingImports" :key="importItem.id" class="review-item">
          <div class="item-header">
            <h4>{{ importItem.filename }}</h4>
            <span class="status-badge" :class="importItem.review_step">{{ importItem.review_step }}</span>
          </div>
          <p class="item-preview">{{ importItem.items?.length || 0 }} topics imported</p>
          <div class="item-meta">
            <span>Imported: {{ formatDate(importItem.created_at) }}</span>
            <span>Type: {{ importItem.type }}</span>
          </div>
          <div class="item-actions">
            <button 
              @click="reviewImport(importItem, 'sme_approve')" 
              class="btn-approve"
              v-if="importItem.review_step === 'pending'"
            >
              Approve
            </button>
            <button 
              @click="reviewImport(importItem, 'final_approve')" 
              class="btn-approve"
              v-if="importItem.review_step === 'sme_approved'"
            >
              Final Approve
            </button>
            <button @click="reviewImport(importItem, 'reject')" class="btn-reject">
              Reject
            </button>
            <router-link :to="{ name: 'ImportReviewView', params: { id: importItem.id } }" class="btn-edit">
              Review Details
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { toast } from '@/composables/useToast'
import HelpIcon from '@/components/HelpIcon.vue'
import { apiGet, apiPost } from '@/api/base'

export default {
  name: 'Reviews',
  components: { HelpIcon },
  data() {
    return {
      activeTab: 'topics',
      loading: false,
      error: null,
      stats: null,
      pendingTopics: [],
      pendingCollections: [],
      pendingImports: []
    }
  },
  async created() {
    await this.loadReviewData()
  },
  methods: {
    async loadReviewData() {
      this.loading = true
      try {
        // Load all review data
        const [stats, topics, collections, imports] = await Promise.all([
          apiGet('/api/reviews/stats'),
          apiGet('/api/reviews/topics/pending'),
          apiGet('/api/reviews/collections/pending'),
          apiGet('/api/reviews/imports/pending')
        ])

        this.stats = stats
        this.pendingTopics = topics
        this.pendingCollections = collections
        this.pendingImports = imports

      } catch (err) {
        console.error('Failed to load review data:', err)
        this.error = 'Failed to load review data'
      } finally {
        this.loading = false
      }
    },

    formatStatus(status) {
      // Convert status like "pending_review" to "Pending Review"
      return status
        .split('_')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ')
    },

    async reviewTopic(topic, action) {
      try {
        const endpoint = action === 'approve' ? 'approve' : 'reject'
        const reviewer = prompt(`${action === 'approve' ? 'Approve' : 'Reject'} topic "${topic.title}"?\n\nEnter your name:`)
        
        if (!reviewer) return
        
        let comments = ''
        if (action === 'reject') {
          comments = prompt('Reason for rejection:') || ''
        }

        await apiPost(`/api/reviews/topic/${topic.id}/${endpoint}`, { reviewer, comments })

  // Reload data
  await this.loadReviewData()
  toast.success(`Topic ${action}d successfully`)

      } catch (err) {
  console.error(`Failed to ${action} topic:`, err)
  toast.error(`Failed to ${action} topic`)
      }
    },
    async reviewImport(importItem, action) {
      try {
        const reviewer = prompt(`${action.replace('_', ' ')} import "${importItem.filename}"?\n\nEnter your name:`)
        
        if (!reviewer) return
        
        const comments = prompt('Comments (optional):') || ''

        await apiPost(`/api/reviews/import/${importItem.id}/review`, { action, reviewer, comments })

  // Reload data
  await this.loadReviewData()
  toast.success(`Import ${action.replace('_', ' ')}d successfully`)

      } catch (err) {
  console.error(`Failed to ${action} import:`, err)
  toast.error(`Failed to ${action} import`)
      }
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
.reviews {
  padding: 2rem;
  background-color: var(--bg-light-gray);
}

h2 {
  color: var(--text-dark-gray);
  margin-bottom: 1rem;
}

.guidance-text {
  background: var(--info-light-blue);
  border-left: 4px solid var(--primary-deep-teal);
  border-radius: var(--border-radius-lg);
  padding: 1rem 1.5rem;
  margin-bottom: 2rem;
  color: var(--text-dark-gray);
  font-size: 0.95rem;
  line-height: 1.5;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: var(--bg-white);
  border: 1px solid var(--border-light-gray);
  border-radius: var(--border-radius-lg);
  padding: 1.5rem;
  box-shadow: var(--box-shadow-sm);
}

.stat-card h3 {
  margin: 0 0 1rem 0;
  color: var(--text-dark-gray);
  font-size: 1.1rem;
  border-bottom: 1px solid var(--border-light-gray);
  padding-bottom: 0.75rem;
}

.stat-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.stat-label {
  color: var(--text-medium-gray);
  font-size: 0.9rem;
}

.stat-value {
  font-weight: bold;
  padding: 0.25rem 0.5rem;
  border-radius: var(--border-radius-sm);
  font-size: 0.9rem;
}

.stat-value.pending {
  background: var(--warning-light-yellow);
  color: var(--warning-dark-yellow);
}

.stat-value.draft {
  background: var(--info-light-blue);
  color: var(--info-dark-blue);
}

.stat-value.published {
  background: var(--success-light-green);
  color: var(--success-dark-green);
}

.stat-value.sme {
  background: var(--secondary-light-gray);
  color: var(--secondary-dark-gray);
}

.review-tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 2rem;
  border-bottom: 1px solid var(--border-light-gray);
}

.tab-btn {
  padding: 0.75rem 1.5rem;
  border: none;
  background: transparent;
  color: var(--text-medium-gray);
  cursor: pointer;
  border-bottom: 3px solid transparent;
  transition: all 0.2s ease;
  font-size: 1rem;
  font-weight: 500;
}

.tab-btn:hover {
  color: var(--primary-deep-teal);
}

.tab-btn.active {
  color: var(--primary-deep-teal);
  border-bottom-color: var(--primary-deep-teal);
  font-weight: 600;
}

.loading,
.error,
.empty {
  text-align: center;
  padding: 3rem;
  color: var(--text-medium-gray);
  font-style: italic;
  background-color: var(--bg-white);
  border-radius: var(--border-radius-lg);
}

.error {
  color: var(--error-coral-red);
  background-color: var(--error-light-red);
  border: 1px solid var(--error-coral-red);
}

.review-content {
  margin-top: 1rem;
}

.review-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
}

.review-item {
  background: var(--bg-white);
  border: 1px solid var(--border-light-gray);
  border-radius: var(--border-radius-lg);
  padding: 1.5rem;
  transition: box-shadow 0.2s ease, transform 0.2s ease;
  display: flex;
  flex-direction: column;
}

.review-item:hover {
  box-shadow: var(--box-shadow-md);
  transform: translateY(-3px);
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.item-header h4 {
  margin: 0;
  color: var(--text-dark-gray);
  font-size: 1.1rem;
  line-height: 1.3;
  font-weight: 600;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: var(--border-radius-sm);
  font-size: 0.8rem;
  font-weight: 500;
  white-space: nowrap;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.status-badge.draft {
  background: var(--info-light-blue);
  color: var(--info-dark-blue);
}

.status-badge.pending_review,
.status-badge.pending {
  background: var(--warning-light-yellow);
  color: var(--warning-dark-yellow);
}

.status-badge.sme_approved {
  background: var(--secondary-light-gray);
  color: var(--secondary-dark-gray);
}

.status-badge.collection {
  background: var(--primary-light-blue);
  color: var(--primary-dark-blue);
}

.item-preview {
  color: var(--text-medium-gray);
  font-size: 0.9rem;
  line-height: 1.4;
  margin-bottom: 1rem;
  flex-grow: 1;
}

.item-meta {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
  font-size: 0.8rem;
  color: var(--text-light-gray);
}

.item-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  margin-top: auto;
  padding-top: 1rem;
  border-top: 1px solid var(--border-light-gray);
}

.btn-approve,
.btn-reject,
.btn-edit {
  padding: 0.5rem 1rem;
  border: 1px solid transparent;
  border-radius: var(--border-radius-md);
  cursor: pointer;
  font-size: 0.9rem;
  text-decoration: none;
  display: inline-block;
  text-align: center;
  transition: all 0.2s ease;
  font-weight: 600;
}

.btn-approve {
  background: var(--success-dark-green);
  color: var(--bg-white);
}

.btn-approve:hover {
  background: #14532d; /* Darker green */
}

.btn-reject {
  background: var(--error-coral-red);
  color: var(--bg-white);
}

.btn-reject:hover {
  background: var(--error-dark-red);
}

.btn-edit {
  background: transparent;
  color: var(--primary-deep-teal);
  border-color: var(--primary-deep-teal);
}

.btn-edit:hover {
  background: var(--primary-light-blue);
  color: var(--primary-dark-blue);
}

@media (max-width: 768px) {
  .reviews {
    padding: 1rem;
  }
  .stats-grid,
  .review-grid {
    grid-template-columns: 1fr;
  }
  
  .review-tabs {
    flex-direction: column;
    align-items: stretch;
  }

  .tab-btn {
    text-align: left;
    border-bottom: 2px solid var(--border-light-gray);
  }

  .tab-btn.active {
    border-bottom-color: var(--primary-deep-teal);
  }
  
  .item-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .status-badge {
    margin-top: 0.5rem;
  }
  
  .item-meta {
    flex-direction: column;
    gap: 0.25rem;
  }
}
</style>