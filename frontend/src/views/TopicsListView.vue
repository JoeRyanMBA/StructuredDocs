<template>
  <div class="topics-list">
    
    
    <div class="dashboard-header">
      <h1>All Topics <HelpIcon feature="topics.list" /></h1>
      <p class="subtitle">Browse, review, and manage topics</p>
    </div>
    <div v-if="loading" class="loading">Loading…</div>
    <div v-else-if="error" class="error">{{ error }}</div>

    <div v-else class="topics-content">
      <!-- Filters -->
      <div class="filters-section">
        <div class="filter-row">
          <div class="filter-group">
            <label>Search:</label>
            <input
              v-model="searchQuery"
              type="text"
              class="filter-input"
              placeholder="Search topics..."
              @input="applyFilters"
            />
          </div>
          <div class="filter-group">
            <label>Status:</label>
            <select v-model="statusFilter" @change="applyFilters" class="filter-input">
              <option value="">All Statuses</option>
              <option value="draft">Draft</option>
              <option value="pending_review">Pending Review</option>
              <option value="approved">Approved</option>
              <option value="revisions_requested">Revisions Requested</option>
              <option value="published">Published</option>
              <option value="rejected">Rejected</option>
              <option value="archived">Archived</option>
            </select>
          </div>
          <div class="filter-group">
            <label>Collection:</label>
            <select v-model="collectionFilter" @change="applyFilters" class="filter-input">
              <option value="">All Collections</option>
              <option v-for="collection in uniqueCollections" :key="collection" :value="collection">{{ collection }}</option>
            </select>
          </div>
          <div class="filter-group">
            <div class="button-group">
              <button @click="applyFilters" class="btn btn-primary btn-sm">
                <i class="bi bi-search"></i> Search
              </button>
              <button @click="clearFilters" class="btn btn-secondary btn-sm"><i class="bi bi-x"></i> Clear Filters</button>
            </div>
          </div>
        </div>
      </div>

      <p class="table-instruction">Select a topic to edit.</p>

      <div class="topics-table-container">
        <table class="topics-table">
      <thead>
        <tr>
          <th class="select-col">
            <input
              type="checkbox"
              :checked="allSelectedOnPage"
              @change="toggleSelectAll($event.target.checked)"
              aria-label="Select all topics on this page"
            />
          </th>
          <th>ID</th>
          <th>Title</th>
          <th>Status</th>
          <th>Collections</th>
          <th>Projects</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="t in filteredTopics" :key="t.id">
          <td class="select-col">
            <input
              type="checkbox"
              :value="t.id"
              v-model="selectedTopicIds"
              @click.stop="handleRowCheckboxClick(t.id, $event)"
              aria-label="Select topic"
            />
          </td>
          <td>{{ t.id }}</td>
          <td>{{ t.title }}</td>
          <td>
            <span :class="`badge badge--${t.status}`">
              {{ formatStatus(t.status) }}
            </span>
          </td>
          <td class="usage-cell" @click.stop>
            <UsageBadge
              :count="(topicUsage[String(t.id)]?.collections || []).length"
              label="collection"
              :items="topicUsage[String(t.id)]?.collections || []"
            />
          </td>
          <td class="usage-cell" @click.stop>
            <UsageBadge
              :count="(topicUsage[String(t.id)]?.projects || []).length"
              label="project"
              :items="topicUsage[String(t.id)]?.projects || []"
            />
          </td>
          <td class="actions-cell">
            <div class="action-buttons">
              <router-link
                :to="{ name: 'EditTopic', params: { id: t.id } }"
                class="btn-icon btn-secondary"
                title="Edit topic"
                aria-label="Edit topic"
              >
                <i class="bi bi-pencil-square"></i>
              </router-link>

              <button
                v-if="t.status === 'draft'"
                @click="submitForReview(t.id)"
                class="btn-icon btn-send-review"
                title="Submit for review"
                aria-label="Submit for review"
              >
                <i class="bi bi-send"></i>
              </button>

              <button
                v-if="t.status === 'draft'"
                @click="openSequentialReview(t)"
                class="btn-icon btn-seq-review"
                title="Sequential review setup"
                aria-label="Sequential review setup"
              >
                <i class="bi bi-arrow-right-circle"></i>
              </button>

            </div>
          </td>
        </tr>
      </tbody>
    </table>
      </div>
      
      <!-- Bulk actions toolbar -->
      <div class="bulk-actions" v-if="selectedTopicIds.length > 0">
        <span class="selection-count">{{ selectedTopicIds.length }} selected</span>
        <button class="btn btn-sm btn-danger" @click="confirmBulkDelete" :disabled="deleting || !isAdmin">
          <i class="bi bi-trash"></i> Delete Selected
        </button>
        <button
          v-if="selectedTopicIds.length >= 2"
          class="btn btn-sm btn-primary"
          @click="showBulkReviewModal = true"
          :disabled="deleting"
        >
          <i class="bi bi-send"></i> Request Bulk Review
        </button>
        <div class="bulk-actions-spacer"></div>
        <button class="btn btn-sm btn-secondary" @click="selectAllResults" :disabled="deleting">
          Select all results ({{ filteredTopics.length }})
        </button>
        <button class="btn btn-sm" @click="clearSelection" :disabled="deleting">
          Clear selection
        </button>
      </div>
    </div>

    <BulkRequestReviewModal
      :topics="selectedTopicsForBulk"
      :is-visible="showBulkReviewModal"
      :current-user="currentUserObj"
      @close="showBulkReviewModal = false"
      @bulk-review-requested="onBulkReviewRequested"
    />

    <div v-if="showReviewModal" class="modal-overlay" @click.self="closeReviewModal">
      <div class="modal-content review-modal-content" role="dialog" aria-modal="true" aria-label="Submit topic for review">
        <div class="modal-header-row review-modal-header">
          <h3 class="modal-heading">Submit for Review</h3>
          <button type="button" class="plain-close" @click="closeReviewModal" aria-label="Close">&times;</button>
        </div>

        <div class="modal-body review-modal-body">
          <p class="review-topic-title">{{ selectedTopic?.title }}</p>

          <div class="form-group">
            <label>Project (optional)</label>
            <select v-model="reviewData.project_id" class="filter-input" @change="onProjectChange">
              <option value="">No project selected</option>
              <option v-for="project in availableProjects" :key="project.id" :value="project.id">
                {{ project.name }}
              </option>
            </select>
          </div>

          <div class="form-group">
            <label>Select one or more reviewers</label>
            <div v-if="safeProjectStakeholders.length" class="reviewers-list">
              <label v-for="stakeholder in safeProjectStakeholders" :key="stakeholder.id" class="reviewer-option">
                <input type="checkbox" :value="stakeholder.id" v-model="reviewData.assigned_stakeholder_ids" />
                <span>{{ stakeholder.name }} <small v-if="stakeholder.role">({{ stakeholder.role }})</small></span>
              </label>
            </div>
            <div v-else class="empty-help">No reviewers available. Please configure stakeholders with review access.</div>
          </div>

          <div class="form-group">
            <label>Due Date</label>
            <input v-model="reviewData.due_date" type="date" class="filter-input" />
          </div>

          <div class="form-group">
            <label>Notes to reviewer(s) (optional)</label>
            <textarea v-model="reviewData.submitter_notes" rows="3" class="filter-input" placeholder="What should reviewers focus on?"></textarea>
          </div>

          <div class="form-check form-switch" style="margin-top: .25rem;">
            <input class="form-check-input" id="sequentialToggle" type="checkbox" v-model="reviewData.isSequential" />
            <label class="form-check-label" for="sequentialToggle">Use sequential review order (expert first)</label>
          </div>
        </div>

        <div class="modal-footer review-modal-actions">
          <button type="button" class="btn btn-secondary" @click="closeReviewModal">Cancel</button>
          <button
            type="button"
            class="btn btn-primary"
            @click="confirmSubmitForReview"
            :disabled="!selectedTopic || reviewData.assigned_stakeholder_ids.length === 0"
          >
            Request Review
          </button>
        </div>
      </div>
    </div>

    <!-- Sequential Review Modal - Using Vue reactivity instead of Bootstrap modal events -->
    <SequentialReviewModal
      v-if="showSequentialModal"
      :topic="selectedTopicForSequence"
      :availableReviewers="availableReviewers"
      :availableProjects="availableProjects"
      @sequence-created="onSequenceCreated"
      @close="closeSequentialModal"
    />
  </div>
</template>

<script>
import SequentialReviewModal from '@/components/SequentialReviewModal.vue'
import BulkRequestReviewModal from '@/components/BulkRequestReviewModal.vue'
import UsageBadge from '@/components/UsageBadge.vue'
import { toast } from '@/composables/useToast'
import { apiGet, apiPost } from '@/api/base'
import HelpIcon from '@/components/HelpIcon.vue'

export default {
  name: 'TopicListView',
  components: { SequentialReviewModal, BulkRequestReviewModal, UsageBadge, HelpIcon },
  props: {
    globalNotifications: {
      type: Array,
      default: () => []
    },
    markNotificationRead: {
      type: Function,
      default: () => {}
    }
  },

  data() {
    return {
      topics: [],
      topicUsage: {},
      filteredTopics: [],
      searchQuery: '',
      statusFilter: '',
      collectionFilter: '',
      loading: true,
      error: null,
      showReviewModal: false,
      showSequentialModal: false,
      selectedTopic: null,
      selectedTopicForSequence: null,
      availableReviewers: [],
      availableProjects: [],
      projectStakeholders: [],
      reviewData: {
        project_id: '',
        assigned_stakeholder_ids: [],  // Changed to array for multiple selection
        isSequential: false,  // New property for sequential review option
        due_date: (() => {
          const d = new Date();
          d.setDate(d.getDate() + 7);
          return d.toISOString().split('T')[0];
        })(),
        submitter_notes: ''
  },
  // Bulk selection state
  selectedTopicIds: [],
  showBulkReviewModal: false,
  deleting: false,
  lastSelectedIndex: null,
      // Removed local toast state
    }
  },

  computed: {
    // Determine if current user is admin for permissioned actions
    isAdmin() {
      try {
        const userStr = localStorage.getItem('user')
        if (!userStr) return false
        const user = JSON.parse(userStr)
        return user && user.role === 'admin'
      } catch (_) {
        return false
      }
    },
    currentUserObj() {
      try {
        return JSON.parse(localStorage.getItem('user') || '{}')
      } catch (_) {
        return {}
      }
    },
    selectedTopicsForBulk() {
      const idSet = new Set(this.selectedTopicIds)
      return this.topics.filter(t => idSet.has(t.id))
    },
    // Safe stakeholders for template rendering
    safeProjectStakeholders() {
      const projectStakeholders = (this.projectStakeholders || []).filter(s => s && s.id && s.name && s.can_review !== false)
      
      // If project has specific stakeholders with review permissions, use them
      if (projectStakeholders.length > 0) {
        return projectStakeholders
      }
      
      // Otherwise, fall back to general reviewers if project is selected but has no stakeholders
      if ((this.reviewData.project_id || !projectStakeholders.length) && this.availableReviewers.length > 0) {
        return (this.availableReviewers || []).filter(s => s && s.id && s.name)
      }

      return []
    },
    allSelectedOnPage() {
      if (!this.filteredTopics || this.filteredTopics.length === 0) return false
      const idsOnPage = this.filteredTopics.map(t => t.id)
      return idsOnPage.every(id => this.selectedTopicIds.includes(id))
    },
    uniqueCollections() {
      const names = this.topics
        .map(t => t.collection_name)
        .filter(name => name != null && name !== '')
      return [...new Set(names)].sort()
    }
  },

  created() {
    // Force reset modal states to prevent blocking overlay
    this.showReviewModal = false
    this.selectedTopicForSequence = null
    
    // Initialize data loading
    this.fetchTopics()
    this.fetchProjects()
    this.fetchReviewers()
  },

  methods: {
    async fetchTopics() {
      this.loading = true
      this.error = null

      try {
        const [data, usageData] = await Promise.all([
          apiGet('/api/topics/'),
          apiGet('/api/topics/usage-summary').catch(() => null)
        ])
        this.topics = Array.isArray(data) ? data : (data.topics || [])
        if (usageData) this.topicUsage = usageData
        this.applyFilters()
      } catch (err) {
        console.error('API fetch failed, using sample data:', err)
        // Provide mock data when backend is unavailable
        this.topics = [
          {
            id: 1,
            title: 'Sample Topic 1',
            status: 'draft',
            summary: 'This is a sample topic for testing',
            collection_name: 'Test Collection'
          },
          {
            id: 2,
            title: 'Sample Topic 2',
            status: 'pending_review',
            summary: 'Another sample topic',
            collection_name: 'Test Collection'
          },
          {
            id: 3,
            title: 'Sample Topic 3',
            status: 'approved',
            summary: 'Final sample topic',
            collection_name: 'Sample Collection'
          }
        ]
        this.applyFilters()
        this.error = 'Using sample data - backend unavailable'
  } finally {
        this.loading = false
      }
    },

    formatStatus(status) {
      // Convert status like "pending_review" to "Pending review"
      return status
        .split('_')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ')
    },

    applyFilters() {
      let filtered = [...this.topics]
      
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
      
      this.filteredTopics = filtered
    },
    
    clearFilters() {
      this.searchQuery = ''
      this.statusFilter = ''
      this.collectionFilter = ''
      this.applyFilters()
  // Clear selection when filters are reset
  this.selectedTopicIds = []
  this.lastSelectedIndex = null
    },

    // Bulk selection helpers
    selectAllResults() {
      this.selectedTopicIds = this.filteredTopics.map(t => t.id)
    },
    clearSelection() {
      this.selectedTopicIds = []
      this.lastSelectedIndex = null
    },
    onBulkReviewRequested() {
      this.showBulkReviewModal = false
      this.clearSelection()
      this.loadTopics()
    },
    toggleSelectAll(checked) {
      if (checked) {
        const idsOnPage = this.filteredTopics.map(t => t.id)
        // Merge unique ids
        const set = new Set([...this.selectedTopicIds, ...idsOnPage])
        this.selectedTopicIds = Array.from(set)
      } else {
        // Remove ids that are on the current page
        const idsOnPage = new Set(this.filteredTopics.map(t => t.id))
        this.selectedTopicIds = this.selectedTopicIds.filter(id => !idsOnPage.has(id))
      }
    },

    handleRowCheckboxClick(topicId, event) {
      const currentIndex = this.filteredTopics.findIndex(t => t.id === topicId)
      if (currentIndex === -1) return
      if (event.shiftKey && this.lastSelectedIndex !== null) {
        const start = Math.min(this.lastSelectedIndex, currentIndex)
        const end = Math.max(this.lastSelectedIndex, currentIndex)
        const idsInRange = this.filteredTopics.slice(start, end + 1).map(t => t.id)
        if (event.target.checked) {
          // Add all ids in range
          const set = new Set([...this.selectedTopicIds, ...idsInRange])
          this.selectedTopicIds = Array.from(set)
        } else {
          // Remove all ids in range
          const removeSet = new Set(idsInRange)
          this.selectedTopicIds = this.selectedTopicIds.filter(id => !removeSet.has(id))
        }
      }
      this.lastSelectedIndex = currentIndex
    },

    async confirmBulkDelete() {
      if (!this.selectedTopicIds.length) return
      const count = this.selectedTopicIds.length
      const confirmed = confirm(
        `Delete ${count} selected topic${count > 1 ? 's' : ''}?\n\nThis action cannot be undone.`
      )
      if (!confirmed) return

      await this.bulkDelete()
    },

    async bulkDelete() {
      this.deleting = true
      try {
        const token = localStorage.getItem('access_token')
        // Sanitize & normalize selected IDs (remove null/undefined/NaN, coerce to integers)
        const cleanedIds = Array.from(new Set(
          (this.selectedTopicIds || [])
            .filter(id => id !== null && id !== undefined && id !== '')
            .map(id => Number(id))
            .filter(id => Number.isInteger(id) && id > 0)
        ))

        if (!cleanedIds.length) {
          toast.error('No valid topic IDs to delete.')
          this.deleting = false
          return
        }

        if (cleanedIds.length !== this.selectedTopicIds.length) {
          console.warn('Some invalid topic IDs were removed from the bulk delete payload.', {
            original: this.selectedTopicIds,
            cleaned: cleanedIds
          })
        }
        // Prefer POST alias first (most proxies are fine with POST)
        let res = await fetch('/api/topics/bulk/delete', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            ...(token ? { 'Authorization': `Bearer ${token}` } : {})
          },
          body: JSON.stringify({ ids: cleanedIds })
        })

        // Fallback to DELETE in case POST alias is unavailable in older deployments
        if (res.status === 404 || res.status === 405) {
          res = await fetch('/api/topics/bulk', {
            method: 'DELETE',
            headers: {
              'Content-Type': 'application/json',
              ...(token ? { 'Authorization': `Bearer ${token}` } : {})
            },
            body: JSON.stringify({ ids: cleanedIds })
          })
        }

        if (!res.ok) {
          let message = `Bulk delete failed (${res.status})`
          if (res.status === 401) {
            message = 'Your session has expired. Please log in again.'
          } else if (res.status === 403) {
            message = 'Admin role required for bulk deletion.'
          }
          try {
            const err = await res.json()
            if (err && err.error) message = err.error
          } catch (_) {
            // ignore parse error
          }
          throw new Error(message)
        }

  const result = await res.json()
        const deleted = result.deleted || 0
        const notFound = (result.not_found || []).length

        // Refresh topics and clear selection
  await this.fetchTopics()
        this.selectedTopicIds = []

  const extra = notFound ? ` (${notFound} not found)` : ''
  toast.success(`Deleted ${deleted} topic${deleted !== 1 ? 's' : ''}${extra}.`)
      } catch (err) {
  console.error('Bulk delete error:', err)
  toast.error(err.message || 'Bulk delete failed')
      } finally {
        this.deleting = false
      }
    },

    async fetchReviewers() {
      try {
        const reviewers = await apiGet('/api/reviews/reviewers')
        this.availableReviewers = Array.isArray(reviewers) ? reviewers : []
      } catch (err) {
        console.error('Failed to fetch reviewers:', err)
        // Set fallback reviewers if API fails
        this.availableReviewers = [
          { id: 1, name: 'Default Reviewer', email: 'reviewer@census.gov' }
        ]
      }
    },

    async fetchProjects() {
      try {
        this.availableProjects = await apiGet('/api/projects/')
      } catch (err) {
        console.error('Failed to fetch projects:', err)
        this.availableProjects = []
      }
    },

    async fetchProjectStakeholders(projectId) {
      try {
        console.log('Fetching stakeholders for project:', projectId)
        const stakeholders = await apiGet(`/api/projects/${projectId}/stakeholders`)
        // Filter out any invalid stakeholder objects
        this.projectStakeholders = (stakeholders || []).filter(s => s && s.id && s.name)
        console.log('Loaded stakeholders:', this.projectStakeholders)
      } catch (err) {
        console.error('Failed to fetch project stakeholders:', err)
        this.projectStakeholders = []
      }
    },

    async onProjectChange() {
      console.log('Project changed to:', this.reviewData.project_id)
      if (this.reviewData.project_id) {
        await this.fetchProjectStakeholders(this.reviewData.project_id)
        // Reset stakeholder selection when project changes
        this.reviewData.assigned_stakeholder_ids = []
      } else {
        this.projectStakeholders = []
        this.reviewData.assigned_stakeholder_ids = []
      }
      console.log('Project stakeholders after change:', this.projectStakeholders)
    },

    async submitForReview(id) {
      console.log('🔥 submitForReview called with ID:', id)
  toast.info(`Submit for review clicked (Topic #${id})`)
      
      // Find the topic and open the modal
      const topic = this.topics.find(t => t.id === id)
      if (!topic) {
  toast.error('Topic not found')
        return
      }

      this.selectedTopic = topic
      this.showReviewModal = true
      
      // Reset form data with default due date (7 days from now)
      const defaultDueDate = new Date()
      defaultDueDate.setDate(defaultDueDate.getDate() + 7)
      
      this.reviewData = {
        project_id: '',
        assigned_stakeholder_ids: [],
        due_date: defaultDueDate.toISOString().split('T')[0],
        submitter_notes: ''
      }
      
      // Clear project stakeholders
      this.projectStakeholders = []
    },

    closeReviewModal() {
      this.showReviewModal = false
      this.selectedTopic = null
      this.selectedTopicForSequence = null  // Also clear sequential review state
      // Reset form data
      this.reviewData = {
        project_id: '',
        assigned_stakeholder_ids: [],
        isSequential: false,
        due_date: '',
        submitter_notes: ''
      }
      this.projectStakeholders = []
    },

    async confirmSubmitForReview() {
      try {
        console.log('Starting review submission...')
        console.log('Selected topic:', this.selectedTopic)
        console.log('Review data:', this.reviewData)
        const currentUser = JSON.parse(localStorage.getItem('user') || '{}')
        const requesterPayload = {
          requested_by: Number(currentUser.id) || null,
          requester_email: currentUser.email || '',
          requester_name: currentUser.name || ''
        }
        
        if (!this.selectedTopic || this.reviewData.assigned_stakeholder_ids.length === 0) {
          console.error('Validation failed:', {
            selectedTopic: !!this.selectedTopic,
            stakeholder_ids: this.reviewData.assigned_stakeholder_ids
          })
          toast.error('Select at least one reviewer before submitting.')
          return
        }

        // Check if sequential review was requested
        if (this.reviewData.isSequential && this.reviewData.assigned_stakeholder_ids.length > 1) {
          console.log('Creating sequential review...')
          
          // Create sequential review
          const sequencePayload = {
            topic_id: this.selectedTopic.id,
            created_by: 1, // TODO: Get current user ID from auth context
            name: `Review Sequence for ${this.selectedTopic.title}`,
            description: 'Expert-first sequential review workflow',
            initial_message: this.reviewData.submitter_notes || `Please review "${this.selectedTopic.title}" for technical accuracy and clarity.`,
            priority: 'medium',
            reviewers: this.reviewData.assigned_stakeholder_ids.map((stakeholderId, index) => ({
              reviewer_id: stakeholderId,
              step_name: index === 0 ? 'Expert Review' : `Review Step ${index + 1}`,
              instructions: index === 0 ? 'Focus on technical accuracy and completeness' : 'Focus on clarity and readability after technical improvements'
            })),
            auto_advance_on_approve: true,
            pause_on_changes: true,
            auto_start: true
          }

          console.log('Sending sequential review request:', sequencePayload)

          const result = await apiPost('/api/sequences/', sequencePayload)
          if (!result) throw new Error('Sequential review request failed')
          console.log('Sequential review created:', result)
          console.log('Sequential review created:', result)
          
          // Store topic title before closing modal
          const topicTitle = this.selectedTopic.title
          
          // Close modal and refresh topics
          this.closeReviewModal()
          await this.fetchTopics()
          
          toast.success(`"${topicTitle}" submitted for sequential review. First reviewer notified.`)
          
        } else {
          // Regular parallel review process
          console.log('Creating regular review requests for stakeholders:', this.reviewData.assigned_stakeholder_ids)

          // Create multiple review requests - one for each selected reviewer
          const reviewPromises = this.reviewData.assigned_stakeholder_ids.map(async (stakeholderId) => {
            const reviewPayload = {
              topic_id: this.selectedTopic.id,
              reviewer_id: stakeholderId,
              ...requesterPayload,
              priority: 'medium',
              due_date: this.reviewData.due_date,
              message: this.reviewData.submitter_notes || `Review requested for: ${this.selectedTopic.title}`
            }

            console.log('Sending review request:', reviewPayload)

            const result = await apiPost('/api/reviews/request', reviewPayload)
            console.log('Review request response:', result)
            return result
          })

          // Wait for all review requests to complete
          console.log('Waiting for all review requests to complete...')
          const results = await Promise.all(reviewPromises)
          console.log('All review requests completed:', results)
          
          // Store topic title before closing modal (which sets selectedTopic to null)
          const topicTitle = this.selectedTopic.title
          const reviewerCount = this.reviewData.assigned_stakeholder_ids.length
          
          // Close modal and refresh topics
          this.closeReviewModal()
          await this.fetchTopics()
          
          toast.success(`"${topicTitle}" submitted for review to ${reviewerCount} reviewer(s).`)
        }

      } catch (err) {
        console.error('Submit for review failed:', err)
  toast.error(err.message || 'Failed to submit topic for review. Please try again.')
      }
    },

    openSequentialReview(topic) {
      console.log('🔥 openSequentialReview called with topic:', topic)
      
      // Use Vue reactivity instead of Bootstrap modal to avoid overlay issues
      this.selectedTopicForSequence = topic
      this.showSequentialModal = true
    },

    closeSequentialModal() {
      this.showSequentialModal = false
      this.selectedTopicForSequence = null
    },

    fallbackSequentialReview(topic) {
      const confirmed = confirm(
        `Set up Sequential Review for "${topic.title}"?\n\n` +
        `This will create a multi-stage review process where:\n` +
        `1. Expert reviewer reviews first\n` +
        `2. Other reviewers see the improved version\n\n` +
        `Click OK to proceed or Cancel to abort.`
      )
      
      if (confirmed) {
        this.createSequentialReview(topic)
      }
    },

    async createSequentialReview(topic) {
      try {
        console.log('Creating sequential review for topic:', topic.id)
        
        // Simple implementation - just submit for regular review for now
        // TODO: Implement full sequential review logic
        await this.submitForReview(topic.id)
        
  toast.success(`Sequential review started for "${topic.title}" (simplified).`)
      } catch (error) {
        console.error('Error creating sequential review:', error)
  toast.error('Error creating sequential review - please try again')
      }
    },

    onSequenceCreated(sequence) {
      console.log('Sequence created:', sequence)
      
      // Refresh topics to update status
      this.fetchTopics()
      
      // Show success message
  toast.success(`Sequential review created for "${sequence.topic_title}". First reviewer notified.`)
    }
  }
}
</script>

<style scoped>
.topics-table .actions-cell { text-align: center; }
.action-buttons { display: inline-flex; gap: 0.5rem; align-items: center; justify-content: center; }
.review-modal-content { width: min(700px, 94vw); max-width: 700px; }
.review-topic-title { font-weight: 600; color: #374151; margin-bottom: .85rem; }
.reviewers-list { border: 1px solid #e5e7eb; border-radius: 6px; max-height: 180px; overflow: auto; padding: .5rem .6rem; }
.reviewer-option { display: flex; align-items: center; gap: .5rem; margin-bottom: .35rem; }
.empty-help { font-size: .85rem; color: #6b7280; }
/* Match User Management icon buttons */
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
/* Colored variants defined globally in assets/style.css */
.topics-list {
  padding: 2rem;
  background-color: var(--bg-light-gray);
}

.guidance-text {
  background: var(--info-light-blue);
  border-left: 4px solid var(--primary-deep-teal);
  border-radius: var(--border-radius-lg);
  padding: 1rem 1.5rem;
  margin-bottom: 1.5rem;
  color: var(--text-dark-gray);
  font-size: 0.95rem;
  line-height: 1.5;
}

/* Filters */
.filters-section {
  margin-bottom: 2rem;
  background: var(--bg-white);
  padding: 1.5rem;
  border-radius: var(--border-radius-lg);
  border: 1px solid var(--border-light-gray);
  box-shadow: var(--box-shadow-sm);
}

.filter-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
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
  font-size: 0.9rem;
}

.filter-input {
  padding: 0.75rem;
  border: 1px solid var(--border-light-gray);
  border-radius: var(--border-radius-md);
  font-size: 0.9rem;
  background: var(--bg-white);
}

.filter-input:focus {
  outline: none;
  border-color: var(--primary-deep-teal);
  box-shadow: 0 0 0 2px rgba(32, 84, 147, 0.1);
}

.button-group {
  display: flex;
  gap: 0.5rem;
  align-items: center !important; /* Force center alignment, override parent flex-end */
}

.table-instruction {
  color: var(--text-medium-gray);
  font-size: 0.9rem;
  margin: 1rem 0 0.5rem 0;
  font-style: italic;
}

.loading, .error {
  text-align: center;
  padding: 2rem;
  font-size: 1.1rem;
  background-color: var(--bg-white);
  border-radius: var(--border-radius-lg);
}

.error {
  color: var(--error-coral-red);
}

.topics-table-container {
  background: var(--bg-white);
  border-radius: var(--border-radius-lg);
  box-shadow: var(--box-shadow-sm);
  overflow: hidden;
}

.topics-table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  text-align: left;
  padding: 1rem;
  border-bottom: 1px solid var(--border-light-gray);
}

th {
  background-color: var(--bg-light-mist-gray);
}

.select-col {
  width: 48px;
  text-align: center;
}

th:nth-child(4),
td:nth-child(4) {
  white-space: nowrap;
  min-width: 120px;
}

.badge {
  padding: 0.25rem 0.75rem;
  border-radius: var(--border-radius-pill);
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: capitalize;
}

.badge--draft { background: var(--secondary-light-gray); color: var(--secondary-dark-gray); }
.badge--published { background: var(--success-light-green); color: var(--success-dark-green); }
.badge--pending_review { background: var(--warning-light-yellow); color: var(--warning-dark-yellow); }
.badge--approved { background: var(--success-light-green); color: var(--success-dark-green); }
.badge--revisions_requested { background: var(--warning-light-yellow); color: var(--warning-dark-yellow); }
.badge--rejected { background: var(--error-light-red); color: var(--error-dark-red); }
.badge--archived { background: var(--secondary-light-gray); color: var(--secondary-dark-gray); }

.actions-cell {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: var(--border-radius-md);
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

.btn-primary { background-color: var(--primary-deep-teal); color: var(--bg-white); }
.btn-primary:hover:not(:disabled) { background-color: var(--primary-dark-blue); }
/* Use global .btn-secondary styles from assets/style.css for consistent contrast */
.btn-success { background-color: var(--success-dark-green); color: var(--bg-white); }
.btn-success:hover { background-color: #14532d; }
.btn-warning { background-color: var(--warning-dark-yellow); color: var(--bg-white); }
.btn-warning:hover { background-color: #78350f; }
.btn-danger { background-color: var(--error-coral-red); color: var(--bg-white); }
.btn-danger:hover { background-color: var(--error-dark-red); }
.btn-info { background-color: var(--info-dark-blue); color: var(--bg-white); }
.btn-info:hover { background-color: #1e40af; }

.btn-sm {
  padding: 0.375rem 0.75rem;
  font-size: 0.8rem;
}

.bulk-actions {
  display: flex;
  gap: 0.75rem;
  align-items: center;
  padding: 0.75rem 1rem;
  margin-top: 0.75rem;
  background: var(--bg-white);
  border: 1px solid var(--border-light-gray);
  border-radius: var(--border-radius-md);
}

.bulk-actions .btn {
  margin: 0 !important;
  align-self: center;
}

.selection-count {
  color: var(--text-medium-gray);
  font-size: 0.9rem;
}

.bulk-actions-spacer {
  flex: 1;
}
</style>