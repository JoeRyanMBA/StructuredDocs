<template>
  <div class="topics-list">
    <h2>All Topics - Simple Version</h2>
    <p>This is a simplified test version of the Topics page.</p>
    
    <div class="test-section">
      <h3>Test Data:</h3>
      <div v-if="loading" class="loading-overlay">
        <div class="loading-spinner"></div>
      </div>
      <div v-else>
        <div v-for="topic in topics" :key="topic.id" class="topic-item">
          <h4>{{ topic.title }}</h4>
          <p>Status: {{ topic.status }}</p>
          <button @click="testButton(topic.id)" class="btn btn-primary">
            Test Button
          </button>
        </div>
      </div>
    </div>
    
    <div class="debug-info">
      <h3>Debug Info:</h3>
      <p>Component mounted: {{ mounted }}</p>
      <p>Props received: {{ JSON.stringify($props) }}</p>
      <p>Error: {{ error }}</p>
    </div>
  </div>
</template>

<script>
import { toast } from '@/composables/useToast'
export default {
  name: 'TopicsListViewSimple',
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
      loading: false,
      mounted: false,
      error: null,
      topics: [
        { id: 1, title: 'Test Topic 1', status: 'draft' },
        { id: 2, title: 'Test Topic 2', status: 'pending_review' },
        { id: 3, title: 'Test Topic 3', status: 'approved' }
      ]
    }
  },
  
  mounted() {
    this.mounted = true
    console.log('TopicsListViewSimple mounted successfully!')
    console.log('Props:', this.$props)
  },
  
  methods: {
    testButton(id) {
      toast.info(`Button clicked for topic ${id}!`)
      console.log(`Button clicked for topic ${id}`)
    },
    
  }
}
</script>

<style scoped>
.topics-list {
  padding: 2rem;
  background-color: var(--bg-light-gray);
}

h2, h3 {
  color: var(--text-dark-gray);
}

.topic-item {
  border: 1px solid var(--border-light-gray);
  padding: 1.5rem;
  margin: 1rem 0;
  border-radius: var(--border-radius-lg);
  background-color: var(--bg-white);
  box-shadow: var(--box-shadow-sm);
}

.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: var(--border-radius-md);
  cursor: pointer;
  font-weight: 600;
}

.btn-primary {
  background-color: var(--primary-deep-teal);
  color: var(--bg-white);
}

.btn-primary:hover {
  background-color: var(--primary-dark-blue);
}

.debug-info {
  background: var(--bg-light-mist-gray);
  padding: 1.5rem;
  margin-top: 2rem;
  border-radius: var(--border-radius-lg);
  border: 1px solid var(--border-light-gray);
}
</style>
