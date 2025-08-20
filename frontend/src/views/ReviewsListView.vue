<template>
  <div class="reviews-list-view">
    <Breadcrumbs />
    <div class="page-header">
      <h1>📝 Review Tasks</h1>
      <p>Review topics and provide feedback to authors</p>
    </div>
    
    <!-- Tabs for different review views -->
    <div class="review-tabs">
      <button 
        @click="activeTab = 'assigned'" 
        :class="{ active: activeTab === 'assigned' }"
        class="tab-btn"
      >
        My Reviews ({{ assignedReviews.length }})
      </button>
      <button 
        @click="activeTab = 'completed'" 
        :class="{ active: activeTab === 'completed' }"
        class="tab-btn"
      >
        Completed
      </button>
    </div>
    
    <!-- Assigned Reviews Tab -->
    <div v-if="activeTab === 'assigned'" class="tab-content">
      <div v-if="loading" class="loading">Loading reviews...</div>
      <div v-else-if="assignedReviews.length === 0" class="empty-state">
        <p>🎉 No pending reviews assigned to you!</p>
      </div>
      <div v-else class="reviews-grid">
        <ReviewCard 
          v-for="review in assignedReviews" 
          :key="review.id"
          :review="review"
          @review-updated="loadReviews"
        />
      </div>
    </div>
    
    <!-- Completed Reviews Tab -->
    <div v-if="activeTab === 'completed'" class="tab-content">
      <div v-if="loading" class="loading">Loading completed reviews...</div>
      <div v-else-if="completedReviews.length === 0" class="empty-state">
        <p>No completed reviews yet.</p>
      </div>
      <div v-else class="reviews-grid">
        <ReviewCard 
          v-for="review in completedReviews" 
          :key="review.id"
          :review="review"
          @review-updated="loadReviews"
        />
      </div>
    </div>
  </div>
</template>

<script>
import Breadcrumbs from '@/components/Breadcrumbs.vue'
import ReviewCard from '@/components/ReviewCard.vue'
import { getPendingReviews, getReviews } from '@/api/reviews.js'

export default {
  name: 'ReviewsListView',
  components: { 
    Breadcrumbs,
    ReviewCard
  },
  
  data() {
    return {
      activeTab: 'assigned',
      loading: false,
      assignedReviews: [],
      completedReviews: [],
      currentUser: JSON.parse(localStorage.getItem('user') || '{}')
    }
  },
  
  async created() {
    await this.loadReviews()
  },
  
  methods: {
    async loadReviews() {
      this.loading = true
      try {
        // For now, get current user as stakeholder ID 1 (hardcoded for demo)
        const currentUserId = this.currentUser.id || 1
        
        // Get all reviews and filter by current user
        const allReviews = await getReviews()
        
        // Assigned reviews (pending/in_progress for current user)
        this.assignedReviews = allReviews.filter(review => 
          review.reviewer_id === currentUserId && 
          ['pending', 'in_progress'].includes(review.status)
        )
        
        // Completed reviews by current user
        this.completedReviews = allReviews.filter(review => 
          review.reviewer_id === currentUserId && 
          review.status === 'completed'
        )
        
      } catch (error) {
        console.error('Failed to load reviews:', error)
        alert('Failed to load reviews')
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.reviews-list-view {
  padding: 1rem;
}

.page-header {
  margin-bottom: 2rem;
}

.page-header h1 {
  margin: 0 0 0.5rem 0;
  color: #1f2937;
}

.page-header p {
  margin: 0;
  color: #6b7280;
}

.review-tabs {
  display: flex;
  border-bottom: 2px solid #e5e7eb;
  margin-bottom: 1.5rem;
}

.tab-btn {
  padding: 0.75rem 1.5rem;
  border: none;
  background: none;
  color: #6b7280;
  cursor: pointer;
  font-weight: 500;
  border-bottom: 3px solid transparent;
  transition: all 0.2s;
}

.tab-btn:hover {
  color: #374151;
}

.tab-btn.active {
  color: #3b82f6;
  border-bottom-color: #3b82f6;
}

.tab-content {
  min-height: 400px;
}

.loading {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
  color: #6b7280;
  font-size: 1.1rem;
}

.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
  color: #6b7280;
  font-size: 1.1rem;
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
