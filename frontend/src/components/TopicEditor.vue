<template>
  <div class="topic-editor">
    <!-- Title Input -->
    <label>
      Title
      <input
        v-model="title"
        type="text"
        placeholder="Enter topic title"
      />
    </label>

    <!-- Split‐pane: Editor on left, Preview on right -->
    <div class="split-pane">
      <!-- Left: Content + Frontmatter -->
      <div class="pane input-pane">
        <label>
          Content
          <textarea
            v-model="content"
            rows="10"
            placeholder="Enter topic content (Markdown)"
          ></textarea>
        </label>

        <label>
          Frontmatter
          <textarea
            v-model="frontmatter"
            rows="4"
            placeholder="Enter YAML frontmatter"
          ></textarea>
        </label>
      </div>

      <!-- Right: Live Preview -->
      <div class="pane preview-pane">
        <div class="preview" v-html="renderedMarkdown"></div>
      </div>
    </div>

    <!-- Save Button -->
    <button @click="save" :disabled="isSaving">
      <span v-if="isSaving">Saving…</span>
      <span v-else>Save</span>
    </button>
  </div>
</template>

<script>
import { marked } from 'marked'

export default {
  name: 'TopicEditor',

  props: {
    topicId: {
      type: [String, Number],
      default: null
    },
    initialContent: {
      type: String,
      default: ''
    },
    initialFrontmatter: {
      type: String,
      default: ''
    }
  },

  data() {
    return {
      title: '',
      content: this.initialContent,
      frontmatter: this.initialFrontmatter,

      // ← move isSaving here so you can mutate it
      isSaving: false
    }
  },

  computed: {
    renderedMarkdown() {
      return marked(this.content || '')
    }
  },

  methods: {
    async save() {
      this.isSaving = true

      const payload = {
        title: this.title,
        content: this.content,
        frontmatter: this.frontmatter
      }
      const url = this.topicId
        ? `/api/topics/${this.topicId}`
        : '/api/topics'
      const method = this.topicId ? 'PUT' : 'POST'

      try {
        const res = await fetch(url, {
          method,
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        })
        const data = await res.json()
        console.log('✅ Saved:', data)

        if (!this.topicId) {
          this.$emit('update:topicId', data.id)
        } else {
          this.$emit('save', data)
        }
      } catch (err) {
        console.error('❌ Save error:', err)
      } finally {
        this.isSaving = false
      }
    }
  }
}
</script>

<style scoped>
.topic-editor {
  padding: 1rem;
}

/* Split‐pane layout */
.split-pane {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}

.pane {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.input-pane textarea,
.input-pane input {
  width: 100%;
  padding: 0.5rem;
  box-sizing: border-box;
}

.preview-pane {
  background: #f9f9f9;
  border: 1px solid #ddd;
  overflow-y: auto;
  padding: 1rem;
}

/* Rendered Markdown styles (optional) */
.preview h1,
.preview h2,
.preview h3 {
  margin-top: 1.5rem;
  margin-bottom: 0.5rem;
}
.preview p {
  line-height: 1.6;
  margin-bottom: 1rem;
}

/* Save button */
button {
  padding: 0.75rem 1.5rem;
  background: #005a9c;
  color: white;
  border: none;
  cursor: pointer;
  border-radius: 4px;
}
button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>