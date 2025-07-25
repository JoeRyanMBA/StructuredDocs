<template>
  <div class="edit-topic-view">
    <Breadcrumbs />

    <!-- Confirmation Banner -->
    <div v-if="confirmation" class="confirmation">
      {{ confirmation }}
    </div>

    <!-- New Topic Mode -->
    <div v-if="!hasId && !loading" class="new-mode">
      <h3>📄 Creating a New Topic</h3>
      <TopicEditor
        :topicId="null"
        :initialContent="''"
        :initialFrontmatter="''"
        @update:topicId="onTopicCreated"
      />
    </div>

    <!-- Loading / Error States -->
    <div v-else-if="loading" class="loading">Loading topic…</div>
    <div v-else-if="error" class="error">{{ error }}</div>

    <!-- Edit Existing Topic -->
    <div v-else>
      <TopicEditor
        :topicId="topicId"
        :initialContent="topic.content"
        :initialFrontmatter="topic.frontmatter"
        @save="onTopicSaved"
      />
    </div>
  </div>
</template>

<script>
import Breadcrumbs from '@/components/Breadcrumbs.vue'
import TopicEditor from '@/components/TopicEditor.vue'

export default {
  name: 'EditTopicView',
  components: { Breadcrumbs, TopicEditor },

  data() {
    return {
      topicId: this.$route.params.id
        ? parseInt(this.$route.params.id)
        : null,
      topic: { content: '', frontmatter: '' },
      loading: true,
      error: null,
      confirmation: null
    }
  },

  computed: {
    hasId() {
      return this.topicId !== null
    }
  },

  created() {
    if (!this.hasId) {
      this.loading = false
      return
    }

    fetch(`/api/topics/${this.topicId}`)
      .then(res => {
        if (!res.ok) throw new Error(`Topic not found (status ${res.status})`)
        return res.json()
      })
      .then(data => {
        this.topic.content = data.content || ''
        this.topic.frontmatter = data.frontmatter || ''
      })
      .catch(err => {
        console.error(err)
        this.error = 'Failed to load topic'
      })
      .finally(() => {
        this.loading = false
      })
  },

  methods: {
    // Called when TopicEditor emits a new ID (POST)
    onTopicCreated(newId) {
      this.topicId = newId
      this.showConfirmation(`✅ Topic ${newId} created successfully`)
      this.$router.replace({ name: 'EditTopic', params: { id: newId } })
    },

    // Called when TopicEditor emits save after PUT
    onTopicSaved(data) {
      this.showConfirmation(`✅ Topic ${this.topicId} updated successfully`)
      console.log('Saved response:', data)
    },

    // Shared confirmation logic
    showConfirmation(message) {
      this.confirmation = message
      setTimeout(() => {
        this.confirmation = null
      }, 4000)
    }
  }
}
</script>

<style scoped>
.edit-topic-view {
  padding: 2rem;
}

.loading {
  font-size: 1rem;
  color: #666;
}

.error {
  color: #c00;
  font-weight: bold;
  margin: 1rem 0;
}

/* Confirmation banner */
.confirmation {
  background: #e0f7e9;
  border-left: 4px solid #2e8b57;
  padding: 1rem;
  margin-bottom: 1rem;
  color: #2e8b57;
  font-weight: bold;
}

/* Optional: style for new-mode header */
.new-mode h3 {
  margin-bottom: 1rem;
}

@media (max-width: 768px) {
  .edit-topic-view {
    padding: 1rem;
  }
}
</style>