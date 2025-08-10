<template>
  <div class="reviews">
    <Breadcrumbs />
    <h2>Review Dashboard</h2>
    
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
            <span class="status-badge" :class="topic.status">{{ topic.status }}</span>
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
import Breadcrumbs from '@/components/Breadcrumbs.vue'

export default {
  name: 'Reviews',
  components: { Breadcrumbs },
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
        const [statsRes, topicsRes, collectionsRes, importsRes] = await Promise.all([
          fetch('/api/reviews/stats'),
          fetch('/api/reviews/topics/pending'),
          fetch('/api/reviews/collections/pending'),
          fetch('/api/reviews/imports/pending')
        ])

        this.stats = await statsRes.json()
        this.pendingTopics = await topicsRes.json()
        this.pendingCollections = await collectionsRes.json()
        this.pendingImports = await importsRes.json()

      } catch (err) {
        console.error('Failed to load review data:', err)
        this.error = 'Failed to load review data'
      } finally {
        this.loading = false
      }
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

        const res = await fetch(`/api/reviews/topic/${topic.id}/${endpoint}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ reviewer, comments })
        })

        if (!res.ok) throw new Error(`Failed to ${action} topic`)

        // Reload data
        await this.loadReviewData()
        
        alert(`Topic ${action}d successfully`)

      } catch (err) {
        console.error(`Failed to ${action} topic:`, err)
        alert(`Failed to ${action} topic`)
      }
    },
    async reviewImport(importItem, action) {
      try {
        const reviewer = prompt(`${action.replace('_', ' ')} import "${importItem.filename}"?\n\nEnter your name:`)
        
        if (!reviewer) return
        
        const comments = prompt('Comments (optional):') || ''

        const res = await fetch(`/api/reviews/import/${importItem.id}/review`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ action, reviewer, comments })
        })

        if (!res.ok) throw new Error(`Failed to ${action} import`)

        // Reload data
        await this.loadReviewData()
        
        alert(`Import ${action.replace('_', ' ')}d successfully`)

      } catch (err) {
        console.error(`Failed to ${action} import:`, err)
        alert(`Failed to ${action} import`)
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
  padding-top: 0px; /* Top padding to account for fixed header */
  padding-left: 2rem;
  padding-right: 2rem;
  padding-bottom: 2rem;
}

.guidance-text {
  background: #f8f9fa;
  border-left: 4px solid #007acc;
  border-radius: .75rem;
  padding: 1rem;
  margin-bottom: 2rem;
  color: #495057;
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
  background: white;
  border: 1px solid #e1e5e9;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.stat-card h3 {
  margin: 0 0 1rem 0;
  color: #333;
  font-size: 1.1rem;
}

.stat-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.stat-label {
  color: #666;
  font-size: 0.9rem;
}

.stat-value {
  font-weight: bold;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.9rem;
}

.stat-value.pending {
  background: #fff3cd;
  color: #856404;
}

.stat-value.draft {
  background: #d1ecf1;
  color: #0c5460;
}

.stat-value.published {
  background: #d4edda;
  color: #155724;
}

.stat-value.sme {
  background: #e2e3e5;
  color: #383d41;
}

.review-tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 2rem;
  border-bottom: 1px solid #e1e5e9;
}

.tab-btn {
  padding: 0.75rem 1.5rem;
  border: none;
  background: transparent;
  color: #666;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: all 0.2s ease;
  font-size: 0.9rem;
}

.tab-btn:hover {
  color: #007acc;
}

.tab-btn.active {
  color: #007acc;
  border-bottom-color: #007acc;
  font-weight: 500;
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

.review-content {
  margin-top: 1rem;
}

.review-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
}

.review-item {
  background: white;
  border: 1px solid #e1e5e9;
  border-radius: 8px;
  padding: 1.5rem;
  transition: box-shadow 0.2s ease;
}

.review-item:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.item-header h4 {
  margin: 0;
  color: #333;
  font-size: 1.1rem;
  line-height: 1.3;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 500;
  white-space: nowrap;
}

.status-badge.draft {
  background: #d1ecf1;
  color: #0c5460;
}

.status-badge.pending_review {
  background: #fff3cd;
  color: #856404;
}

.status-badge.pending {
  background: #fff3cd;
  color: #856404;
}

.status-badge.sme_approved {
  background: #e2e3e5;
  color: #383d41;
}

.status-badge.collection {
  background: #e7f3ff;
  color: #004085;
}

.item-preview {
  color: #666;
  font-size: 0.9rem;
  line-height: 1.4;
  margin-bottom: 1rem;
}

.item-meta {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
  font-size: 0.8rem;
  color: #999;
}

.item-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.btn-approve,
.btn-reject,
.btn-edit {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  text-decoration: none;
  display: inline-block;
  text-align: center;
  transition: background-color 0.2s ease;
}

.btn-approve {
  background: #28a745;
  color: white;
}

.btn-approve:hover {
  background: #218838;
}

.btn-reject {
  background: #dc3545;
  color: white;
}

.btn-reject:hover {
  background: #c82333;
}

.btn-edit {
  background: #007acc;
  color: white;
}

.btn-edit:hover {
  background: #0056b3;
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .review-grid {
    grid-template-columns: 1fr;
  }
  
  .review-tabs {
    flex-direction: column;
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