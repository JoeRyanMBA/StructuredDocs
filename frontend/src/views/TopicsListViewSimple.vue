<template>
  <div class="topics-list">
    <h2>All Topics - Simple Version</h2>
    <p>This is a simplified test version of the Topics page.</p>
    
    <div class="test-section">
      <h3>Test Data:</h3>
      <div v-if="loading">Loading...</div>
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
      alert(`Button clicked for topic ${id}!`)
      console.log(`Button clicked for topic ${id}`)
    }
  }
}
</script>

<style scoped>
.topics-list {
  padding: 20px;
}

.topic-item {
  border: 1px solid #ddd;
  padding: 15px;
  margin: 10px 0;
  border-radius: 5px;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn-primary {
  background-color: #007bff;
  color: white;
}

.debug-info {
  background: #f8f9fa;
  padding: 15px;
  margin-top: 20px;
  border-radius: 5px;
}
</style>
