<template>
  <div class="topic-editor">
    <!-- Page Heading (only for edit mode) -->
    <h2 v-if="topicId" class="page-heading">{{ pageTitle }}</h2>
    
    <!-- Guidance Text for New Topics -->
    <p v-if="!topicId" class="guidance-text">
      Enter the content for a new topic here. Use the Markdown cheatsheet at the bottom of this page to format the content.
    </p>
    
    <!-- Title Input (outside split-pane) -->
    <label class="title-label">
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
      <div class="pane preview-container">
        <label class="preview-label">Preview</label>
        <div class="preview-pane">
          <div class="preview" v-html="renderedMarkdown"></div>
        </div>
      </div>
    </div>

    <!-- Save Button -->
    <button @click="save" :disabled="isSaving">
      <span v-if="isSaving">Saving…</span>
      <span v-else>Save</span>
    </button>

    <!-- Markdown Cheatsheet -->
    <div class="markdown-cheatsheet">
      <h3>Markdown Quick Reference</h3>
      <div class="cheatsheet-grid">
        <div class="cheatsheet-section">
          <strong>Headers:</strong>
          <pre># H1
## H2
### H3</pre>
        </div>
        <div class="cheatsheet-section">
          <strong>Text Formatting:</strong>
          <pre>**bold text**
*italic text*
`code`</pre>
        </div>
        <div class="cheatsheet-section">
          <strong>Lists:</strong>
          <pre>- Item 1
- Item 2
1. Numbered item
2. Another item</pre>
        </div>
        <div class="cheatsheet-section">
          <strong>Links & Images:</strong>
          <pre>[link text](URL)
![alt text](image-URL)</pre>
        </div>
      </div>
    </div>
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
    initialTitle: {
      type: String,
      default: ''
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
      title: this.initialTitle,
      content: this.initialContent,
      frontmatter: this.initialFrontmatter,

      // ← move isSaving here so you can mutate it
      isSaving: false
    }
  },

  computed: {
    renderedMarkdown() {
      return marked(this.content || '')
    },

    pageTitle() {
      return this.topicId ? 'Edit Topic' : 'Create a New Topic'
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
          // For new topics, clear the form after successful save
          this.clearForm()
          this.$emit('update:topicId', data.id)
        } else {
          this.$emit('save', data)
        }
      } catch (err) {
        console.error('❌ Save error:', err)
      } finally {
        this.isSaving = false
      }
    },

    clearForm() {
      this.title = ''
      this.content = ''
      this.frontmatter = ''
    }
  }
}
</script>

<style scoped>
.topic-editor {
  padding: 1rem;
}

/* Page heading */
.page-heading {
  margin-top: 0;
  margin-bottom: 1.5rem;
  color: #1f2937;
  font-size: 1.5rem;
}

/* Guidance text for new topics */
.guidance-text {
  background: #f8f9fa;
  border-left: 4px solid #007acc;
  padding: 1rem;
  margin-bottom: 1.5rem;
  color: #495057;
  font-size: 0.95rem;
  line-height: 1.5;
}

/* Title input styling */
.title-label {
  display: block;
  margin-bottom: 1rem;
}

.title-label input {
  width: 100%;
  padding: 0.5rem;
  box-sizing: border-box;
  margin-top: 0.25rem;
}

/* Preview label styling */
.preview-label {
  display: block;
  margin-bottom: 0.25rem;
  font-weight: normal;
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

.input-pane textarea {
  width: 100%;
  padding: 0.5rem;
  box-sizing: border-box;
}

.preview-container {
  display: flex;
  flex-direction: column;
}

.preview-pane {
  background: #f9f9f9;
  border: 1px solid #ddd;
  overflow-y: auto;
  padding: 1rem;
  flex: 1;
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
  margin-bottom: 2rem;
}
button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Markdown Cheatsheet */
.markdown-cheatsheet {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 6px;
  padding: 1.5rem;
  margin-top: 1rem;
}

.markdown-cheatsheet h3 {
  margin-top: 0;
  margin-bottom: 1rem;
  color: #495057;
  font-size: 1.1rem;
}

.cheatsheet-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.cheatsheet-section {
  background: white;
  padding: 1rem;
  border-radius: 4px;
  border: 1px solid #dee2e6;
}

.cheatsheet-section strong {
  display: block;
  margin-bottom: 0.5rem;
  color: #495057;
}

.cheatsheet-section pre {
  background: #f8f9fa;
  padding: 0.5rem;
  border-radius: 3px;
  font-size: 0.85rem;
  margin: 0;
  border: 1px solid #e9ecef;
}
</style>