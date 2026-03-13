<template>
  <div class="topic-view">
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading topic…</p>
    </div>

    <div v-else-if="error" class="error-banner">{{ error }}</div>

    <template v-else-if="topic">
      <div class="topic-header">
        <h1 class="topic-title">{{ topic.title }} <HelpIcon feature="topics.view" /></h1>
        <div class="topic-meta">
          <span v-if="topic.status" class="status-badge" :class="topic.status">{{ topic.status }}</span>
          <router-link
            :to="{ name: 'EditTopic', params: { id: topicId } }"
            class="btn-edit"
          >✏️ Edit</router-link>
        </div>
      </div>

      <div
        ref="contentEl"
        class="topic-body"
        v-html="renderedContent"
      ></div>
    </template>
  </div>
</template>

<script>
import { marked } from 'marked'

function slugify(text) {
  return String(text)
    .replace(/[*_`[\]]/g, '')        // strip markdown syntax chars
    .toLowerCase()
    .trim()
    .replace(/[^\w\s-]/g, '')        // remove non-word chars
    .replace(/[\s_]+/g, '-')         // spaces → hyphens
    .replace(/^-+|-+$/g, '')         // trim leading/trailing hyphens
}

function buildRenderer() {
  const renderer = new marked.Renderer()

  renderer.heading = function (token) {
    const slug = slugify(token.text)
    const inner = marked.parseInline(token.text)
    return (
      `<h${token.depth} id="${slug}" class="anchor-heading">` +
      `<a class="anchor-link" href="#${slug}" aria-label="Link to this section">#</a>` +
      inner +
      `</h${token.depth}>\n`
    )
  }

  renderer.image = function (...args) {
    let href = '', title = '', text = ''
    if (args.length === 1 && args[0] && typeof args[0] === 'object') {
      href = args[0].href || ''
      title = args[0].title || ''
      text = args[0].text || ''
    } else {
      href = args[0] || ''
      title = args[1] || ''
      text = args[2] || ''
    }
    const esc = v => String(v ?? '').replace(/&/g, '&amp;').replace(/"/g, '&quot;')
    let out = `<img src="${esc(href)}" alt="${esc(text)}"`
    if (title) out += ` title="${esc(title)}"`
    out += '>'
    return out
  }

  return renderer
}

import HelpIcon from '@/components/HelpIcon.vue'

export default {
  name: 'TopicView',
  components: { HelpIcon },

  props: {
    topicId: { type: Number, required: true }
  },

  data() {
    return {
      topic: null,
      loading: false,
      error: null
    }
  },

  computed: {
    renderedContent() {
      if (!this.topic?.content) return ''
      const content = this.topic.content.replace(
        /(\!\[[^\]]*\]\([^)]+\))\{[^}]*\}/g,
        '$1'
      )
      return marked.parse(content, {
        breaks: false,
        gfm: true,
        renderer: buildRenderer()
      })
    }
  },

  async mounted() {
    await this.fetchTopic()
    this.scrollToHash()
  },

  watch: {
    '$route.hash'(hash) {
      if (hash) this.scrollToAnchor(hash.slice(1))
    }
  },

  methods: {
    async fetchTopic() {
      this.loading = true
      this.error = null
      try {
        const res = await fetch(`/api/topics/${this.topicId}`)
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        this.topic = await res.json()
      } catch (e) {
        this.error = `Could not load topic: ${e.message}`
      } finally {
        this.loading = false
      }
    },

    scrollToHash() {
      const hash = this.$route.hash
      if (!hash) return
      // Wait for v-html to render before scrolling
      this.$nextTick(() => this.scrollToAnchor(hash.slice(1)))
    },

    scrollToAnchor(id) {
      const el = document.getElementById(id)
      if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }
  }
}
</script>

<style scoped>
.topic-view {
  max-width: 860px;
  margin: 0 auto;
  padding: 1.5rem 2rem;
}

/* Header */
.topic-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--extended-lavender-gray, #e0e0e0);
}

.topic-title {
  margin: 0;
  font-size: 1.75rem;
  color: var(--text-primary-charcoal, #2d2d2d);
}

.topic-meta {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-shrink: 0;
}

.btn-edit {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.375rem 0.875rem;
  background: var(--brand-primary, #4a6cf7);
  color: #fff;
  border-radius: 4px;
  text-decoration: none;
  font-size: 0.875rem;
  white-space: nowrap;
}
.btn-edit:hover {
  opacity: 0.88;
}

.status-badge {
  padding: 0.2rem 0.6rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: capitalize;
  background: #e8eaf6;
  color: #3949ab;
}
.status-badge.approved  { background: #e8f5e9; color: #2e7d32; }
.status-badge.draft     { background: #fff8e1; color: #f57f17; }

/* Body content */
.topic-body {
  line-height: 1.75;
  color: var(--text-primary-charcoal, #2d2d2d);
}

/* Anchor headings */
:deep(.anchor-heading) {
  position: relative;
  scroll-margin-top: 5rem; /* offset for fixed header */
}

:deep(.anchor-link) {
  position: absolute;
  left: -1.4rem;
  color: var(--text-secondary-cool-gray, #888);
  text-decoration: none;
  font-weight: 400;
  opacity: 0;
  transition: opacity 0.15s;
  font-size: 0.9em;
}

:deep(.anchor-heading:hover .anchor-link) {
  opacity: 1;
}

/* Loading / error */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 3rem;
  color: var(--text-secondary-cool-gray, #888);
  gap: 0.75rem;
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #e0e0e0;
  border-top-color: var(--brand-primary, #4a6cf7);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

.error-banner {
  padding: 1rem;
  background: #fff3f3;
  border: 1px solid #ffcdd2;
  border-radius: 6px;
  color: #c62828;
}
</style>
