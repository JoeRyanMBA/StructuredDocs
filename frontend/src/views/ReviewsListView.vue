<template>
  <div class="reviews-list-view">
    
    <div class="page-header">
      <h1>📝 Review Tasks</h1>
      <p>Track reviews you need to complete and reviews you have sent.</p>
    </div>
    
    <!-- Tabs for different review views -->
    <div class="review-tabs">
      <button 
        @click="activeTab = 'assigned'" 
        :class="{ active: activeTab === 'assigned' }"
        :aria-pressed="activeTab === 'assigned'"
        class="tab-btn"
      >
        Needs My Review ({{ assignedReviews.length }})
      </button>
      <button
        @click="activeTab = 'sent'"
        :class="{ active: activeTab === 'sent' }"
        :aria-pressed="activeTab === 'sent'"
        class="tab-btn"
      >
        Sent for Review ({{ sentReviews.length }})
      </button>
      <button 
        @click="activeTab = 'completed'" 
        :class="{ active: activeTab === 'completed' }"
        :aria-pressed="activeTab === 'completed'"
        class="tab-btn"
      >
        Completed ({{ completedReviews.length }})
      </button>
    </div>
    
    <div v-if="!loading && !error && !stakeholderLinked" class="identity-notice" role="status">
      No stakeholder matches your account email. A matching stakeholder is created when you send a review.
      An administrator can also create one so reviews can be assigned to you.
    </div>
    <div class="tab-content">
      <div v-if="loading" class="loading">Loading reviews...</div>
      <div v-else-if="error" class="empty-state" role="alert">{{ error }}</div>
      <div v-else-if="visibleReviews.length === 0" class="empty-state">
        <p>{{ emptyMessage }}</p>
      </div>
      <div v-else class="reviews-grid">
        <ReviewCard 
          v-for="review in visibleReviews"
          :key="review.id"
          :review="review"
          :can-review="activeTab === 'assigned'"
          @review-updated="loadReviews"
        />
      </div>
    </div>
  </div>
</template>

<script>
import ReviewCard from '@/components/ReviewCard.vue'
import { getReviewTasks } from '@/api/reviews.js'
import { toast } from '@/composables/useToast'

export default {
  name: 'ReviewsListView',
  components: { 
    ReviewCard
  },
  
  data() {
    return {
      activeTab: 'assigned',
      loading: false,
      error: '',
      stakeholderLinked: false,
      assignedReviews: [],
      sentReviews: [],
      completedReviews: [],
    }
  },

  computed: {
    visibleReviews() {
      return {
        assigned: this.assignedReviews,
        sent: this.sentReviews,
        completed: this.completedReviews,
      }[this.activeTab]
    },
    emptyMessage() {
      return {
        assigned: 'No pending reviews assigned to you.',
        sent: 'No outstanding or declined reviews sent by you.',
        completed: 'No completed reviews sent or received by you.',
      }[this.activeTab]
    },
  },
  
  async created() {
    await this.loadReviews()
  },
  
  methods: {
    async loadReviews() {
      this.loading = true
      this.error = ''
      try {
        const tasks = await getReviewTasks()
        if (!Array.isArray(tasks?.assigned) || !Array.isArray(tasks?.sent) ||
            !Array.isArray(tasks?.completed) || typeof tasks?.stakeholder_linked !== 'boolean') {
          throw new Error('Invalid review tasks response')
        }
        this.assignedReviews = tasks.assigned
        this.sentReviews = tasks.sent
        this.completedReviews = tasks.completed
        this.stakeholderLinked = tasks.stakeholder_linked
      } catch (error) {
        console.error('Failed to load reviews:', error)
        this.error = error.message || 'Failed to load reviews.'
        toast.error(this.error)
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.reviews-list-view {
  padding: 2rem;
  background-color: var(--bg-light-mist-gray);
}

.page-header {
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--border-light-gray);
}

.page-header h1 {
  margin: 0 0 0.5rem 0;
  color: var(--primary-deep-teal);
  font-size: 2.25rem;
  font-weight: 300;
}

.page-header p {
  margin: 0;
  color: var(--text-secondary-cool-gray);
  font-size: 1.1rem;
}

.review-tabs {
  display: flex;
  flex-wrap: wrap;
  border-bottom: 2px solid var(--border-light-gray);
  margin-bottom: 1.5rem;
}

.tab-btn {
  padding: 0.75rem 1.5rem;
  border: none;
  background: none;
  color: var(--text-medium-gray);
  cursor: pointer;
  font-weight: 500;
  font-size: 1rem;
  border-bottom: 3px solid transparent;
  transition: all 0.2s;
}

.tab-btn:hover {
  color: var(--text-dark-gray);
}

.tab-btn.active {
  color: var(--primary-deep-teal);
  border-bottom-color: var(--primary-deep-teal);
  font-weight: 600;
}

.tab-content {
  min-height: 400px;
}

.identity-notice {
  padding: 1rem;
  margin-bottom: 1rem;
  background: var(--warning-light-yellow);
  color: var(--warning-dark-yellow);
}

.loading,
.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
  color: var(--text-medium-gray);
  font-size: 1.1rem;
  background-color: var(--bg-white);
  border-radius: var(--border-radius-lg);
  box-shadow: var(--box-shadow-sm);
}

.reviews-grid {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

@media (min-width: 768px) {
  .reviews-list-view {
    padding: 2rem;
  }
}
</style>
