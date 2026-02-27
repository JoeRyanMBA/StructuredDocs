<template>
  <div class="author-dashboard">
    
    <!-- Compact Toolbar -->
    <CompactToolbar :show-metrics="true">
      <template #metrics>
        <div class="metric-card" @click="navigateTo('/topics')">
          <div class="metric-icon">📝</div>
          <div class="metric-content">
            <h3>My Topics</h3>
            <div class="metric-number">{{ stats.myTopics || 0 }}</div>
            <div class="metric-detail">{{ stats.drafts || 0 }} Drafts</div>
          </div>
        </div>

        <div class="metric-card">
          <div class="metric-icon">✅</div>
          <div class="metric-content">
            <h3>Published</h3>
            <div class="metric-number">{{ stats.published || 0 }}</div>
            <div class="metric-detail">Live topics</div>
          </div>
        </div>

        <div class="metric-card">
          <div class="metric-icon">🔄</div>
          <div class="metric-content">
            <h3>In Review</h3>
            <div class="metric-number">{{ stats.inReview || 0 }}</div>
            <div class="metric-detail">Pending feedback</div>
          </div>
        </div>

        <div class="metric-card">
          <div class="metric-icon">📊</div>
          <div class="metric-content">
            <h3>This Week</h3>
            <div class="metric-number">{{ stats.createdThisWeek || 0 }}</div>
            <div class="metric-detail">Topics created</div>
          </div>
        </div>
      </template>
    </CompactToolbar>
    
    <div class="dashboard-header">
      <h1>Author Dashboard</h1>
      <p class="subtitle">Create and manage your content</p>
    </div>

    <!-- Quick Actions Section (Start Page style) -->
    <div class="quick-actions-section">
      <h2>Quick Actions</h2>
      <p class="section-description">Tools for writing and organizing your work</p>
      <div class="quick-actions-grid">
          <button class="quick-action-card" @click="navigateTo('/topics/new')">
            <div class="action-icon"><IconPlus size="28" /></div>
            <div class="action-content">
              <h3>Create New Topic</h3>
              <p>Start writing new content</p>
            </div>
          </button>
          <button class="quick-action-card" @click="navigateTo('/topics')">
            <div class="action-icon">📚</div>
            <div class="action-content">
              <h3>Browse My Topics</h3>
              <p>Review and edit your work</p>
            </div>
          </button>
          <button class="quick-action-card" @click="navigateTo('/import')">
            <div class="action-icon">📥</div>
            <div class="action-content">
              <h3>Import Content</h3>
              <p>Add from external sources</p>
            </div>
          </button>
  </div>
  <div class="quick-actions-grid" style="margin-top: 1rem;">
          <button class="quick-action-card resource-card" @click="navigateTo('/all-images')">
            <div class="action-icon">🖼️</div>
            <div class="action-content">
              <h3>Browse Images</h3>
              <p>Find reusable images for content</p>
            </div>
          </button>
          <button class="quick-action-card resource-card" @click="navigateTo('/all-links')">
            <div class="action-icon">🔗</div>
            <div class="action-content">
              <h3>Browse Links</h3>
              <p>Find reusable links for content</p>
            </div>
          </button>
          
      </div>
    </div>

  <!-- Main Content (full width after removing Recent Work) -->
  <div class="dashboard-section">
        <h2>Writing Progress</h2>
        <div class="progress-overview">
          <div v-if="myTopics.length === 0" class="empty-state">
            <p>No topics found. <button @click="navigateTo('/topics/new')" class="link-btn">Create your first topic</button></p>
          </div>
          <div v-else>
            <!-- Filters -->
            <div class="filters-section">
              <div class="filter-row">
                <div class="filter-group">
                  <label>Search:</label>
                  <input
                    v-model="searchQuery"
                    type="text"
                    class="filter-input"
                    placeholder="Search your topics..."
                    @input="applyFilters"
                  />
                </div>
                <div class="filter-group">
                  <label>Status:</label>
                  <select v-model="statusFilter" @change="applyFilters" class="filter-input">
                    <option value="">All Statuses</option>
                    <option value="draft">Draft</option>
                    <option value="pending_review">Pending Review</option>
                    <option value="in_review">In Review</option>
                    <option value="published">Published</option>
                  </select>
                </div>
                <div class="filter-group">
                  <label>Collection:</label>
                  <select v-model="collectionFilter" @change="applyFilters" class="filter-input">
                    <option value="">All Collections</option>
                    <option v-for="collection in uniqueCollections" :key="collection" :value="collection">{{ collection || 'No Collection' }}</option>
                  </select>
                </div>
                <div class="filter-group">
                  <button @click="clearFilters" class="btn btn-secondary btn-sm"><i class="bi bi-x"></i> Clear Filters</button>
                </div>
              </div>
            </div>

            <div class="topics-table-container">
            <table class="topics-table">
              <thead>
                <tr>
                  <th class="sortable" @click="toggleSort('id')" :aria-sort="idSortStateAria">ID <span class="sort-indicator" :class="idSortState"></span></th>
                  <th>Title</th>
                  <th>Status</th>
                  <th>Collection</th>
                  <th>Collections</th>
                  <th>Projects</th>
                  <th>Words</th>
                  <th class="sortable" @click="toggleSort('updated')" :aria-sort="updatedSortStateAria">Updated <span class="sort-indicator" :class="updatedSortState"></span></th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr 
                  v-for="topic in filteredMyTopics" 
                  :key="topic.id"
                  class="topic-row"
                  @click="editTopic(topic)"
                >
                  <td class="id-cell" @click.stop="copyId(topic.id)" :title="copyTooltip(topic.id)">{{ topic.id }}</td>
                  <td class="topic-title-cell">
                    <div class="topic-title">{{ topic.title }}</div>
                    <div class="topic-summary">{{ topic.summary || 'No summary available' }}</div>
                  </td>
                  <td>
                    <span class="status-badge" :class="topic.status">{{ formatStatus(topic.status) }}</span>
                  </td>
                  <td class="collection-cell">{{ topic.collection_name || 'None' }}</td>
                  <td class="usage-cell" @click.stop>
                    <UsageBadge
                      :count="(topicUsage[String(topic.id)]?.collections || []).length"
                      label="collection"
                      :items="topicUsage[String(topic.id)]?.collections || []"
                    />
                  </td>
                  <td class="usage-cell" @click.stop>
                    <UsageBadge
                      :count="(topicUsage[String(topic.id)]?.projects || []).length"
                      label="project"
                      :items="topicUsage[String(topic.id)]?.projects || []"
                    />
                  </td>
                  <td class="word-count">{{ topic.word_count || 0 }}</td>
                  <td class="updated-cell">{{ formatRelativeTime(topic.updated_at) }}</td>
                  <td class="actions-cell">
                    <div class="action-buttons">
                      <router-link
                        :to="{ name: 'EditTopic', params: { id: topic.id } }"
                        class="btn-icon btn-secondary"
                        title="Edit topic"
                        aria-label="Edit topic"
                        @click.stop
                      >
                        <i class="bi bi-pencil-square"></i>
                      </router-link>

                      <button
                        v-if="topic.status === 'draft'"
                        @click.stop="submitForReview(topic.id)"
                        class="btn-icon btn-send-review"
                        title="Submit for review"
                        aria-label="Submit for review"
                        type="button"
                      >
                        <i class="bi bi-send"></i>
                      </button>

                      <button
                        v-if="topic.status === 'draft'"
                        @click.stop="openSequentialReview(topic)"
                        class="btn-icon btn-seq-review"
                        title="Sequential review setup"
                        aria-label="Sequential review setup"
                        type="button"
                      >
                        <i class="bi bi-arrow-right-circle"></i>
                      </button>

                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
            </div>
          </div>
        </div>
      </div>

    <div v-if="showReviewModal" class="modal-overlay" @click.self="closeReviewModal">
      <div class="modal-content review-modal-content" role="dialog" aria-modal="true" aria-label="Request review">
        <div class="modal-header-row review-modal-header">
          <h3 class="modal-heading">Submit for Review</h3>
          <button type="button" class="plain-close" @click="closeReviewModal" aria-label="Close">&times;</button>
        </div>
        <div class="modal-body review-modal-body">
          <p class="review-topic-title">{{ selectedTopicForReview?.title }}</p>

          <div class="review-form-group">
            <label>Select one or more reviewers</label>
            <div v-if="availableReviewers.length" class="reviewers-list">
              <label v-for="reviewer in availableReviewers" :key="reviewer.id" class="reviewer-option">
                <input type="checkbox" :value="reviewer.id" v-model="selectedReviewerIds" />
                <span>{{ reviewer.name }} <small>({{ reviewer.role || 'reviewer' }})</small></span>
              </label>
            </div>
            <div v-else class="empty-help">No reviewers available. Please configure reviewers first.</div>
          </div>

          <div class="review-form-group">
            <label>Due Date</label>
            <input v-model="reviewDueDate" type="date" class="filter-input" />
          </div>

          <div class="review-form-group">
            <label>Notes to reviewer(s) (optional)</label>
            <textarea v-model="reviewMessage" class="filter-input" rows="3" placeholder="What should reviewers focus on?"></textarea>
          </div>
        </div>
        <div class="modal-footer review-modal-actions">
          <button type="button" class="btn btn-secondary" @click="closeReviewModal" :disabled="submittingReview">Cancel</button>
          <button type="button" class="btn btn-primary" @click="confirmSubmitForReview" :disabled="submittingReview || selectedReviewerIds.length === 0">
            Request Review
          </button>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div
      v-if="loading"
      class="loading-overlay"
      role="status"
      aria-live="polite"
      aria-busy="true"
    >
      <div class="loading-container">
        <div class="loading-spinner" aria-hidden="true"></div>
        <div class="loading-text">Loading your content...</div>
      </div>
    </div>
  </div>
</template>

<script>
import CompactToolbar from '../components/CompactToolbar.vue'
import IconPlus from '@/components/icons/IconPlus.vue'
import { toast } from '@/composables/useToast'
import UsageBadge from '@/components/UsageBadge.vue'

export default {
  name: 'AuthorDashboard',
  
  components: {
    CompactToolbar,
    IconPlus,
    UsageBadge
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
    markNotificationRead: {
      type: Function,
      required: true
    }
  },

  computed: {
    mergedNotifications() {
      const all = [...(this.globalNotifications || []), ...(this.notifications || [])]
      const seen = new Set()
      return all.filter(n => {
        if (!n || !n.id) return true
        if (seen.has(n.id)) return false
        seen.add(n.id)
        return true
      })
    },

    uniqueCollections() {
      const collections = [...new Set(this.myTopics.map(t => t.collection_name).filter(col => col))]
      return collections.sort()
    },

    idSortState() { return this.sortKey === 'id' ? this.sortDir : '' },
    updatedSortState() { return this.sortKey === 'updated' ? this.sortDir : '' },
    idSortStateAria() { return this.sortKey === 'id' ? (this.sortDir === 'asc' ? 'ascending' : 'descending') : 'none' },
  },
  
  data() {
    return {
      loading: true,
      stats: {
        myTopics: 0,
        drafts: 0,
        published: 0,
        inReview: 0,
        createdThisWeek: 0
      },
  myTopics: [],
  topicUsage: {},
  filteredMyTopics: [],
      searchQuery: '',
      statusFilter: '',
      collectionFilter: '',
      showReviewModal: false,
      submittingReview: false,
      selectedTopicForReview: null,
      availableReviewers: [],
      selectedReviewerIds: [],
      reviewPriority: 'medium',
      reviewDueDate: '',
      reviewMessage: '',
  recentTopics: [], /* deprecated after removing Recent Work */
  sortKey: 'updated',
  sortDir: 'desc', // 'asc' | 'desc'
      copiedId: null,
      copiedAt: 0
    }
  },

  async created() {
  await this.loadDashboardData()
  },

  methods: {
    async loadDashboardData() {
      this.loading = true
      try {
  await this.loadMyTopics()
  await this.loadStats()
      } catch (error) {
        console.error('Failed to load author dashboard:', error)
      } finally {
        this.loading = false
      }
    },

    async loadMyTopics() {
      try {
        const [res, usageRes] = await Promise.all([
          fetch('/api/topics/'),
          fetch('/api/topics/usage-summary')
        ])
        if (res.ok) {
          const allTopics = await res.json()
          this.myTopics = allTopics
          this.recentTopics = [...this.myTopics]
            .sort((a, b) => new Date(b.updated_at || b.created_at) - new Date(a.updated_at || a.created_at))
            .slice(0, 5)
          this.applyFilters()
        }
        if (usageRes.ok) {
          this.topicUsage = await usageRes.json()
        }
      } catch (error) {
        console.error('Failed to load topics:', error)
        this.myTopics = []
        this.recentTopics = []
      }
    },

    applyFilters() {
      let filtered = [...this.myTopics]
      
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase()
        filtered = filtered.filter(topic => 
          topic.title.toLowerCase().includes(query) ||
          (topic.summary && topic.summary.toLowerCase().includes(query)) ||
          (topic.collection_name && topic.collection_name.toLowerCase().includes(query))
        )
      }
      
      if (this.statusFilter) {
        filtered = filtered.filter(topic => topic.status === this.statusFilter)
      }
      
      if (this.collectionFilter) {
        filtered = filtered.filter(topic => topic.collection_name === this.collectionFilter)
      }
      
      // Apply sorting
      if (this.sortKey === 'updated') {
        filtered.sort((a, b) => {
          const aDate = new Date(a.updated_at || a.created_at || 0)
          const bDate = new Date(b.updated_at || b.created_at || 0)
          return this.sortDir === 'asc' ? aDate - bDate : bDate - aDate
        })
      } else if (this.sortKey === 'id') {
        filtered.sort((a, b) => {
          return this.sortDir === 'asc' ? a.id - b.id : b.id - a.id
        })
      }
      this.filteredMyTopics = filtered
    },
    toggleSort(key) {
      if(!['updated','id'].includes(key)) return
      if(this.sortKey===key){
        this.sortDir=this.sortDir==='asc'?'desc':'asc'
      } else {
        this.sortKey=key
        this.sortDir= key==='id' ? 'asc':'desc'
      }
      this.applyFilters()
    },

    updatedSortStateAria() {
      if (this.sortKey !== 'updated') return 'none'
      return this.sortDir === 'asc' ? 'ascending' : 'descending'
    },
    
    clearFilters() {
      this.searchQuery = ''
      this.statusFilter = ''
      this.collectionFilter = ''
      this.applyFilters()
    },

    async loadStats() {
      try {
        // Calculate stats from topics data
        const total = this.myTopics.length
        const drafts = this.myTopics.filter(t => t.status === 'draft').length
        const published = this.myTopics.filter(t => t.status === 'published').length
        const inReview = this.myTopics.filter(t => ['in_review', 'pending_review'].includes(t.status)).length
        
        // Calculate topics created this week
        const oneWeekAgo = new Date()
        oneWeekAgo.setDate(oneWeekAgo.getDate() - 7)
        const createdThisWeek = this.myTopics.filter(t => 
          t.created_at && new Date(t.created_at) > oneWeekAgo
        ).length

        this.stats = {
          myTopics: total,
          drafts,
          published,
          inReview,
          createdThisWeek
        }
      } catch (error) {
        console.error('Failed to calculate stats:', error)
      }
    },

    editTopic(topic) {
      this.$router.push(`/topics/${topic.id}/edit`)
    },

    viewPublished(topic) {
      this.$router.push(`/topics/${topic.id}`)
    },

    async submitForReview(id) {
      const topic = this.myTopics.find(t => t.id === id)
      if (!topic) {
        toast.error('Topic not found')
        return
      }

      this.selectedTopicForReview = topic
      this.selectedReviewerIds = []
      this.reviewPriority = 'medium'
      const defaultDueDate = new Date()
      defaultDueDate.setDate(defaultDueDate.getDate() + 7)
      this.reviewDueDate = defaultDueDate.toISOString().split('T')[0]
      this.reviewMessage = ''
      this.showReviewModal = true

      await this.loadReviewers()
    },

    closeReviewModal() {
      this.showReviewModal = false
      this.submittingReview = false
      this.selectedTopicForReview = null
      this.selectedReviewerIds = []
      this.reviewPriority = 'medium'
      this.reviewDueDate = ''
      this.reviewMessage = ''
    },

    async loadReviewers() {
      if (this.availableReviewers.length) return
      try {
        const res = await fetch('/api/reviews/reviewers')
        if (!res.ok) throw new Error(`Failed to fetch reviewers (${res.status})`)
        const reviewers = await res.json()
        this.availableReviewers = Array.isArray(reviewers) ? reviewers : []
      } catch (err) {
        console.error('Failed to load reviewers:', err)
        toast.error('Unable to load reviewers')
      }
    },

    async confirmSubmitForReview() {
      if (!this.selectedTopicForReview || this.selectedReviewerIds.length === 0) {
        toast.error('Please select at least one reviewer')
        return
      }

      this.submittingReview = true
      try {
        const currentUser = JSON.parse(localStorage.getItem('user') || '{}')
        const requesterPayload = {
          requested_by: Number(currentUser.id) || null,
          requester_email: currentUser.email || '',
          requester_name: currentUser.name || ''
        }

        const reviewPromises = this.selectedReviewerIds.map(async (reviewerId) => {
          const res = await fetch('/api/reviews/request', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              topic_id: this.selectedTopicForReview.id,
              reviewer_id: Number(reviewerId),
              ...requesterPayload,
              priority: this.reviewPriority,
              due_date: this.reviewDueDate || null,
              message: this.reviewMessage || `Review requested for: ${this.selectedTopicForReview.title}`
            })
          })

          const payload = await res.json().catch(() => null)
          if (!res.ok) throw new Error(payload?.error || 'Failed to submit for review')

          return payload
        })

        await Promise.all(reviewPromises)

        const topicTitle = this.selectedTopicForReview.title
        const reviewerCount = this.selectedReviewerIds.length
        await this.loadMyTopics()
        await this.loadStats()
        this.closeReviewModal()
        toast.success(`"${topicTitle}" submitted for review to ${reviewerCount} reviewer(s).`)
        this.$router.push({ name: 'ReviewsHome' })
      } catch (err) {
        console.error('Submit for review failed:', err)
        toast.error(err.message || 'Failed to submit for review')
      } finally {
        this.submittingReview = false
      }
    },

    openSequentialReview(topic) {
      // For now, route to reviews setup if available; fallback: call sendForReview
      if (this.$router && this.$router.resolve) {
        try {
          // If there is a dedicated route, navigate; otherwise, fallback
          const target = this.$router.resolve({ name: 'SequentialReviewSetup', params: { id: topic.id } })
          if (target && target.href) {
            this.$router.push(target)
            return
          }
        } catch (_) { /* ignore */ }
      }
      // Fallback simple path if no route exists
      this.sendForReview(topic)
    },

    async sendForReview(topic) {
      await this.submitForReview(topic.id)
    },

    async duplicateTopic(topic) {
      // Persist duplication to backend
      try {
        const res = await fetch(`/api/topics/${topic.id}/duplicate`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' }
        })
        if (!res.ok) throw new Error('Failed to duplicate topic')
        await this.loadMyTopics()
      } catch (err) {
        console.error('Error duplicating topic:', err)
      }
    },

    navigateTo(path) {
      this.$router.push(path)
    },

    formatStatus(status) {
      const statusMap = {
        'draft': 'Draft',
        'pending_review': 'Pending Review',
        'in_review': 'In Review',
        'published': 'Published',
        'archived': 'Archived'
      }
      return statusMap[status] || status
    },

    formatReviewStatus(status) {
      const statusMap = {
        'pending': 'Pending',
        'approved': 'Approved',
        'needs_changes': 'Needs Changes',
        'rejected': 'Rejected'
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
    },

    copyId(id){
      try { navigator.clipboard.writeText(String(id)); this.copiedId = id; this.copiedAt = Date.now(); setTimeout(()=>{ if(Date.now()-this.copiedAt>=1800) { this.copiedId=null } }, 2000); } catch(e){ console.error('Copy failed', e); }
    },
    copyTooltip(id){ return this.copiedId===id ? 'Copied!' : 'Click to copy ID'; },
  }
}
</script>

<style scoped>
.author-dashboard {
  margin: 0 auto;
  padding: 2rem;
  background-color: var(--bg-light-mist-gray);
}

.dashboard-header {
  margin-bottom: 2rem;
  text-align: center;
}

.dashboard-header h1 {
  color: var(--primary-deep-teal);
  margin-bottom: 0.5rem;
  font-size: 2.5rem;
  font-weight: 300;
}

.welcome-text {
  color: var(--text-secondary-cool-gray);
  font-size: 1.1rem;
  margin: 0;
}

/* Metrics Grid */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 3rem;
}

/* Main Content Grid */
.content-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 2rem;
  margin-bottom: 2rem;
}

.content-grid .full-width {
  grid-column: 1 / -1;
}

.review-modal-content { width: min(560px, 92vw); max-width: 560px; }

.review-topic-title {
  margin: 0 0 0.9rem;
  font-weight: 600;
  color: #374151;
}

.review-form-group {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  margin-bottom: 0.85rem;
}

.review-form-group label {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-dark-gray);
}

.reviewers-list {
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  max-height: 180px;
  overflow: auto;
  padding: .5rem .6rem;
}

.reviewer-option {
  display: flex;
  align-items: center;
  gap: .5rem;
  margin-bottom: .35rem;
}

.empty-help {
  font-size: .85rem;
  color: #6b7280;
}


/* Dashboard Sections */
/* Use global .dashboard-section from style.css */



/* Quick Actions */
.quick-actions-grid {
  --quick-action-min-width: 240px;
  --quick-action-gap: 1rem;
  margin-bottom: 2rem;
}

.action-card.resource-card {
  background: #fff8e1;
  border-color: #ffcc02;
}

.action-card.resource-card:hover {
  background: #ff9800;
  border-color: #ff9800;
  color: white;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(255, 152, 0, 0.2);
}

/* Topics List */
.topics-list {
  max-height: 400px;
  overflow-y: auto;
}

.topic-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  border: 1px solid #f8f9fa;
  border-radius: 6px;
  margin-bottom: 0.75rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.topic-item:hover {
  border-color: #205493;
  background: #f8f9fa;
}

.topic-item:last-child {
  margin-bottom: 0;
}

.topic-icon {
  font-size: 1.5rem;
  min-width: 30px;
}

.topic-content {
  flex: 1;
}

.topic-title {
  font-weight: 600;
  color: #495057;
  margin-bottom: 0.25rem;
}

.topic-description {
  color: #6c757d;
  font-size: 0.875rem;
  margin-bottom: 0.25rem;
}

.topic-meta {
  color: #adb5bd;
  font-size: 0.75rem;
}

.topic-status {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.7rem;
  font-weight: 500;
  text-transform: uppercase;
  display: inline-block;
}

.topic-status.draft {
  background: #fff3cd;
  color: #856404;
}

.topic-status.published {
  background: #d4edda;
  color: #155724;
}

.topic-status.in_review {
  background: #cce5ff;
  color: #004085;
}

/* Topics Table */
.topics-table-container {
  overflow-x: auto;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.topics-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 1000px;
}

.topics-table th,
.topics-table td {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid #e0e0e0;
}

.topics-table th {
  background-color: #f5f5f5;
  font-weight: 600;
  color: #333;
  font-size: 0.875rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.topics-table tbody tr {
  transition: background-color 0.2s ease;
  cursor: pointer;
}

.topics-table tbody tr:hover {
  background-color: #f8f9fa;
}

.topic-title-cell {
  max-width: 300px;
}

.topic-title {
  font-weight: 600;
  color: #333;
  margin: 0 0 0.25rem 0;
  font-size: 0.95rem;
}

.topic-summary {
  font-size: 0.85rem;
  color: #666;
  line-height: 1.4;
  margin: 0;
}

.status-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
  display: inline-block;
}

.status-badge.draft {
  background-color: #fff3e0;
  color: #f57c00;
}

.status-badge.published {
  background-color: #e8f5e8;
  color: #2e7d32;
}

.status-badge.in_review {
  background-color: #e3f2fd;
  color: #1976d2;
}

.status-badge.pending_review {
  background-color: #e3f2fd;
  color: #1976d2;
}

.collection-cell {
  color: #666;
  font-size: 0.9rem;
}

.word-count {
  font-weight: 500;
  color: #333;
  font-size: 0.9rem;
}

.updated-cell {
  color: #666;
  font-size: 0.85rem;
}

.actions-cell {
  min-width: 200px;
}

/* Filters */
.filters-section {
  margin-bottom: 1.5rem;
  background: var(--bg-white);
  padding: 1rem;
  border-radius: var(--border-radius-lg);
  border: 1px solid var(--border-light-gray);
  box-shadow: var(--box-shadow-sm);
}

.filter-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1rem;
  align-items: center;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.filter-group label {
  font-weight: 600;
  color: var(--text-dark-gray);
  font-size: 0.85rem;
}

.filter-input {
  padding: 0.4rem;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 0.85rem;
  background: white;
}

.filter-input:focus {
  outline: none;
  border-color: #205493;
  box-shadow: 0 0 0 2px rgba(32, 84, 147, 0.2);
}

.action-buttons {
  display: flex;
  gap: 0.5rem;
  align-items: center;
  flex-wrap: wrap;
}

/* Button Styles */
.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  transition: background-color 0.2s;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn i {
  flex-shrink: 0;
  width: 1em;
}

.btn-primary {
  background-color: #205493;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #005E7B;
}

/* Use global .btn-secondary styles from assets/style.css */

.btn-success {
  background-color: #009964;
  color: white;
}

.btn-success:hover {
  background-color: #006548;
}

.btn-outline {
  background-color: transparent;
  color: #6c757d;
  border: 1px solid #6c757d;
}

.btn-outline:hover {
  background-color: #6c757d;
  color: white;
}

.btn-sm {
  padding: 0.375rem 0.75rem;
  font-size: 0.8rem;
}

/* Icon button styles aligned with All Topics */
.action-buttons { display: inline-flex; gap: 0.5rem; align-items: center; justify-content: center; }
.btn-icon {
  width: 32px;
  height: 32px;
  padding: 0;
  border-radius: 4px;
  border: 1px solid transparent;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  transition: all 0.2s ease;
  text-decoration: none;
}
.btn-icon:hover:not(:disabled) { transform: translateY(-1px); box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
.btn-icon:disabled { opacity: 0.5; cursor: not-allowed; }
/* Colored icon variants are defined globally in assets/style.css */

/* Empty States */
.empty-state {
  text-align: center;
  padding: 2rem;
  color: #6c757d;
}

.empty-state p {
  margin: 0;
}

.link-btn {
  background: none;
  border: none;
  color: #205493;
  text-decoration: underline;
  cursor: pointer;
  padding: 0;
  font-size: inherit;
}

.link-btn:hover {
  color: #005E7B;
}

/* Loading */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.loading-spinner {
  color: #205493;
  font-size: 1.1rem;
}

/* Responsive Design */
/* two column layout for desktop */
.two-col { grid-template-columns: 1fr 1fr; }

@media (max-width: 768px) {
  .author-dashboard {
    padding: 1rem;
  }
  .metrics-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  .content-grid {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }
  
  .topics-table-container {
    margin: 0 -1rem;
    border-radius: 0;
  }
  
  .topics-table {
    min-width: 800px;
  }
  
  .topics-table th,
  .topics-table td {
    padding: 0.75rem 0.5rem;
    font-size: 0.875rem;
  }
  
  .action-buttons {
    flex-direction: column;
    gap: 0.25rem;
    align-items: stretch;
  }
  
  .action-buttons .btn {
    width: 100%;
    justify-content: center;
  }
  
  .template-buttons {
    grid-template-columns: 1fr;
  }
  
  .dashboard-header h1 {
    font-size: 2rem;
  }
}

.id-cell { width:72px; font-family:monospace; cursor:pointer; user-select:text; }
.id-cell:hover { background: var(--table-row-hover-bg,#f5f7fa); }
.id-cell:active { background: var(--table-row-active-bg,#e8eef5); }
.sort-indicator.asc::after{content:'▲'; margin-left:4px; font-size:0.7em;}
.sort-indicator.desc::after{content:'▼'; margin-left:4px; font-size:0.7em;}
</style>
