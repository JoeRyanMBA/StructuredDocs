<template>
  <div class="edit-topic-view">
    <!-- Confirmation Banner -->
    <div v-if="confirmation" class="confirmation">
      {{ confirmation }}
    </div>

    <!-- Review Feedback Panel -->
    <div v-if="reviewId && reviewFeedback.length" class="review-panel">
      <div class="review-panel-header" @click="panelOpen = !panelOpen">
        <span>
          <i class="bi bi-chat-square-text me-2"></i>
          <strong>Reviewer Feedback</strong>
          <span class="feedback-count-badge">{{ reviewFeedback.length }}</span>
          <span class="reviewer-name-hint" v-if="reviewerName"> — {{ reviewerName }}</span>
        </span>
        <span class="panel-toggle">{{ panelOpen ? '▲ Hide' : '▼ Show' }}</span>
      </div>
      <div v-if="panelOpen" class="review-panel-body">
        <div
          v-for="(item, index) in reviewFeedback"
          :key="item.id"
          class="fb-item"
          :class="'prio-' + item.priority"
        >
          <div class="fb-item-header">
            <span class="fb-num">#{{ index + 1 }}</span>
            <span class="fb-type">{{ formatFeedbackType(item.feedback_type) }}</span>
            <span v-if="item.section_title" class="fb-section">{{ item.section_title }}</span>
            <span class="ms-auto d-flex gap-1">
              <span class="prio-pill prio-{{ item.priority }}">{{ item.priority }}</span>
            </span>
          </div>
          <div v-if="item.original_text || item.suggested_text" class="fb-comparison">
            <div v-if="item.original_text" class="fb-original">
              <div class="fb-label">Original</div>
              <div class="fb-text">{{ item.original_text }}</div>
            </div>
            <div v-if="item.suggested_text" class="fb-suggested">
              <div class="fb-label">Suggested</div>
              <div class="fb-text">{{ item.suggested_text }}</div>
            </div>
          </div>
          <div v-if="item.comment" class="fb-comment"><strong>Comment:</strong> {{ item.comment }}</div>
          <div v-if="item.rationale" class="fb-comment"><strong>Rationale:</strong> {{ item.rationale }}</div>
        </div>
      </div>
    </div>

    <!-- New Topic Mode -->
    <div v-if="!hasId && !loading" class="new-mode">
      <h2 class="page-title">📄 Create a New Topic <HelpIcon feature="topics.edit" /></h2>
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
import HelpIcon from '@/components/HelpIcon.vue'
import { apiGet } from '@/api/base'

export default {
  name: 'EditTopicView',
  components: { TopicEditor, HelpIcon },

  data() {
    return {
      topicId: this.$route.params.id
        ? parseInt(this.$route.params.id)
        : null,
      reviewId: this.$route.query.reviewId
        ? parseInt(this.$route.query.reviewId)
        : null,
      topic: { title: '', content: '', frontmatter: '' },
      loading: true,
      error: null,
      confirmation: null,
      reviewFeedback: [],
      reviewerName: null,
      panelOpen: true
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

    const topicFetch = apiGet(`/api/topics/${this.topicId}`)
      .then(data => {
        this.topic.title = data.title || ''
        this.topic.content = data.content || ''
        this.topic.frontmatter = data.frontmatter || ''
      })
      .catch(err => {
        console.error(err)
        this.error = 'Failed to load topic'
      })

    const reviewFetch = this.reviewId
      ? apiGet(`/api/reviews/${this.reviewId}`)
          .then(data => {
            if (data) {
              this.reviewFeedback = data.feedback_items || []
              this.reviewerName = data.reviewer_name || null
            }
          })
          .catch(() => {})
      : Promise.resolve()

    Promise.all([topicFetch, reviewFetch]).finally(() => {
      this.loading = false
    })
  },

  methods: {
    formatFeedbackType(type) {
      const labels = {
        'general_comment': 'General Comment', 'text_edit': 'Text Edit',
        'text_addition': 'Addition', 'text_deletion': 'Deletion',
        'structural_change': 'Structural Change', 'technical_correction': 'Technical Correction',
        'style_suggestion': 'Style Suggestion'
      }
      return labels[type] || type
    },

    onTopicCreated(result) {
      const newId = result?.id ?? result
      this.topic = {
        title: result?.title || '',
        content: result?.content || '',
        frontmatter: result?.frontmatter || ''
      }
      this.topicId = newId
      this.showConfirmation(`✅ Topic ${newId} created successfully`)
      this.$router.replace({ name: 'EditTopic', params: { id: newId } })
    },

    onTopicSaved(data) {
      console.log('Saved response:', data)
    },

    showConfirmation(message) {
      this.confirmation = message
      setTimeout(() => { this.confirmation = null }, 4000)
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

.confirmation {
  background: var(--extended-cool-mint);
  border-left: 4px solid var(--success-mint-green);
  padding: 1rem;
  margin-bottom: 1rem;
  color: var(--primary-deep-teal);
  font-weight: bold;
}

.page-title { margin: 0 0 1rem 0; color: var(--primary-deep-teal); font-weight: 500; }

/* Review Feedback Panel */
.review-panel {
  border: 1px solid #ffc107;
  border-radius: 8px;
  margin-bottom: 1.5rem;
  overflow: hidden;
}

.review-panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  background: #fff8e1;
  cursor: pointer;
  user-select: none;
}

.review-panel-header:hover { background: #fff3cd; }

.feedback-count-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: #ffc107;
  color: #212529;
  font-size: 0.72rem;
  font-weight: 700;
  border-radius: 50%;
  width: 1.25rem;
  height: 1.25rem;
  margin-left: 0.4rem;
}

.reviewer-name-hint { color: #6c757d; font-weight: normal; font-size: 0.9rem; }
.panel-toggle { font-size: 0.8rem; color: #6c757d; }

.review-panel-body { background: #fff; }

.fb-item {
  padding: 0.85rem 1rem;
  border-bottom: 1px solid #f0f0f0;
  border-left: 4px solid #dee2e6;
}
.fb-item:last-child { border-bottom: none; }
.fb-item.prio-critical { border-left-color: #dc3545; }
.fb-item.prio-high     { border-left-color: #fd7e14; }
.fb-item.prio-medium   { border-left-color: #ffc107; }
.fb-item.prio-low      { border-left-color: #198754; }

.fb-item-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
  flex-wrap: wrap;
}
.fb-num  { font-weight: 700; color: #6c757d; font-size: 0.82rem; }
.fb-type { background: #e9ecef; color: #495057; font-size: 0.72rem; font-weight: 600; padding: 0.15rem 0.5rem; border-radius: 4px; }
.fb-section { font-size: 0.8rem; color: #0d6efd; }

.prio-pill {
  font-size: 0.68rem;
  font-weight: 700;
  text-transform: uppercase;
  padding: 0.1rem 0.4rem;
  border-radius: 3px;
  background: #e9ecef;
  color: #495057;
}

.fb-comparison {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}
@media (max-width: 600px) { .fb-comparison { grid-template-columns: 1fr; } }

.fb-original, .fb-suggested { border-radius: 4px; overflow: hidden; }
.fb-label {
  font-size: 0.68rem;
  font-weight: 700;
  text-transform: uppercase;
  padding: 0.15rem 0.5rem;
}
.fb-text { padding: 0.4rem 0.6rem; font-size: 0.84rem; white-space: pre-wrap; word-break: break-word; }
.fb-original .fb-label  { background: #f8d7da; color: #842029; }
.fb-original .fb-text   { background: #fff5f5; border: 1px solid #f5c2c7; }
.fb-suggested .fb-label { background: #d1e7dd; color: #0a3622; }
.fb-suggested .fb-text  { background: #f0fff4; border: 1px solid #badbcc; }

.fb-comment { font-size: 0.85rem; color: #343a40; margin-top: 0.3rem; }

@media (max-width: 768px) {
  .edit-topic-view { padding: 1rem; }
}
</style>
