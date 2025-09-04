<template>
  <div class="edit-topic-view">
    <!-- Confirmation Banner -->
    <div v-if="confirmation" class="confirmation">
      {{ confirmation }}
    </div>

    <!-- New Topic Mode -->
    <div v-if="!hasId && !loading" class="new-mode">
      <h2 class="page-title">📄 Create a New Topic</h2>
      <TopicEditor
        :topicId="null"
        :initialTitle="''"
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
        :initialTitle="topic.title"
        :initialContent="topic.content"
        :initialFrontmatter="topic.frontmatter"
        @save="onTopicSaved"
      />
    </div>
  </div>
</template>

<script>
import TopicEditor from '@/components/TopicEditor.vue'

export default {
  name: 'EditTopicView',
  components: { TopicEditor },

  data() {
    return {
      topicId: this.$route.params.id
        ? parseInt(this.$route.params.id)
        : null,
      topic: { title: '', content: '', frontmatter: '' },
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
        this.topic.title = data.title || ''
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
      // Don't show confirmation banner since TopicEditor now shows its own local message
      // this.showConfirmation(`✅ Topic ${this.topicId} updated successfully`)
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
  padding: 0 2rem 2rem;
}

.loading {
  font-size: 1rem;
  color: var(--text-secondary-cool-gray);
}

.error {
  color: var(--error-coral-red);
  font-weight: bold;
  margin: 1rem 0;
}

/* Confirmation banner */
.confirmation {
  background: var(--extended-cool-mint);
  border-left: 4px solid var(--success-mint-green);
  padding: 1rem;
  margin-bottom: 1rem;
  color: var(--primary-deep-teal);
  font-weight: bold;
}

/* New topic header aligns with global titles */
.page-title { margin: 0 0 1rem 0; color: var(--primary-deep-teal); font-weight: 500; }

@media (max-width: 768px) {
  .edit-topic-view {
    padding: 1rem;
  }
}
</style>