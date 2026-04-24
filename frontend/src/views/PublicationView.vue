<template>
  <div class="publication-view">

    <div v-if="loading" class="loading">Loading publication…</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else-if="pub" class="pub-wrapper">

      <!-- Header -->
      <div class="pub-header">
        <h2>{{ pub.title }}</h2>
        <p v-if="pub.description" class="description">{{ pub.description }}</p>
      </div>

      <!-- Two-panel layout -->
      <div class="pub-body">

        <!-- Left: navigable tree -->
        <aside class="pub-sidebar">
          <div class="sidebar-heading">Topics</div>
          <div class="sidebar-scroll">
            <PublicationNodeView
              :nodes="tree"
              :selected-id="selectedNode && selectedNode.id"
              @select="selectNode"
            />
            <div v-if="!tree.length" class="no-content-hint">No topics in this publication.</div>
          </div>
        </aside>

        <!-- Right: content panel -->
        <main class="pub-content">
          <div v-if="selectedNode" class="content-inner">
            <h3 class="content-title">{{ selectedNode.title }}</h3>
            <!-- eslint-disable-next-line vue/no-v-html -->
            <div class="content-body" v-html="renderedContent"></div>
          </div>
          <div v-else class="content-empty">
            Select a topic from the list to preview its content.
          </div>
        </main>
      </div>

      <!-- Audience tag selector -->
      <div class="audience-bar">
        <label class="audience-label">🎯 Audience Tags:</label>
        <div class="tag-checkboxes">
          <label v-for="tag in allTags" :key="tag.id" class="tag-check">
            <input type="checkbox" :value="tag.id" v-model="selectedTagIds" />
            {{ tag.name }}
          </label>
          <span v-if="allTags.length === 0" class="no-tags-hint">No tags defined yet.</span>
        </div>
        <span class="audience-hint">Only snippets tagged with the selected audiences will be included in the export.</span>
      </div>

      <div class="actions">
        <button @click="downloadPDF">Download PDF</button>
        <button @click="exportMobileKB" class="mobile-kb-btn">📱 Export Mobile Knowledge Base</button>
        <button @click="previewMobileKB" class="preview-btn"><i class="bi bi-zoom-in" aria-hidden="true"></i> Preview Mobile KB</button>
      </div>

    </div>
    <div v-else class="empty">Publication not found.</div>
  </div>
</template>

<script>
import { marked } from 'marked'
import { apiGet } from '@/api/base'
import { downloadMobileKnowledgeBase, downloadPublicationPdf, getPublication, previewMobileKnowledgeBase } from '@/api/publications'
import PublicationNodeView from '@/components/PublicationNodeView.vue'

export default {
  name: 'PublicationView',
  components: { PublicationNodeView },
  props: {
    id: { type: [String, Number], required: true }
  },
  data() {
    return {
      pub:            null,
      tree:           [],
      selectedNode:   null,
      loading:        true,
      error:          null,
      allTags:        [],
      selectedTagIds: []
    }
  },
  computed: {
    renderedContent() {
      if (!this.selectedNode?.content) return ''
      // Strip Pandoc image-size attributes before parsing
      const md = this.selectedNode.content.replace(/(\!\[[^\]]*\]\([^)]+\))\{[^}]*\}/g, '$1')
      return marked.parse(md)
    }
  },
  async created() {
    try {
      const [json, tagsData] = await Promise.all([
        getPublication(this.id),
        apiGet('/api/tags/')
      ])
      this.pub  = { title: json.title, description: json.description }
      this.tree = json.tree
      // Auto-select the first topic so the panel is never empty
      if (this.tree.length) this._autoSelectFirst(this.tree)
      this.allTags = Array.isArray(tagsData) ? tagsData : (tagsData.tags || [])
    } catch (err) {
      console.error('Error loading publication:', err)
      this.error = 'Failed to load publication'
    } finally {
      this.loading = false
    }
  },
  methods: {
    _autoSelectFirst(nodes) {
      if (!nodes || !nodes.length) return
      this.selectedNode = nodes[0]
    },
    selectNode(node) {
      this.selectedNode = node
    },
    _tagParams() {
      return this.selectedTagIds.map(id => `tag_ids=${id}`).join('&')
    },
    async downloadPDF() {
      try {
        await downloadPublicationPdf(this.id, `${this.pub?.title || 'publication'}.pdf`, this.selectedTagIds)
      } catch (e) {
        console.error('PDF export failed:', e)
        this.error = e.message || 'Failed to export PDF'
      }
    },
    async exportMobileKB() {
      try {
        await downloadMobileKnowledgeBase(this.id, `${this.pub?.title || 'publication'}_mobile_kb.html`, this.selectedTagIds)
      } catch (e) {
        console.error('Mobile KB export failed:', e)
        this.error = e.message || 'Failed to export mobile knowledge base'
      }
    },
    async previewMobileKB() {
      try {
        await previewMobileKnowledgeBase(this.id, this.selectedTagIds)
      } catch (e) {
        console.error('Mobile KB preview failed:', e)
        this.error = e.message || 'Failed to preview mobile knowledge base'
      }
    }
  }
}
</script>

<style scoped>
.publication-view {
  margin: 0 auto;
}

.pub-header {
  margin-bottom: 1.25rem;
}

.pub-header h2 {
  margin: 0 0 0.25rem;
}

.description {
  color: var(--text-secondary-cool-gray);
  font-style: italic;
  margin: 0;
  line-height: 1.5;
}

/* Two-panel layout */
.pub-body {
  display: flex;
  gap: 0;
  border: 1px solid var(--extended-lavender-gray, #e2e8f0);
  border-radius: 8px;
  overflow: hidden;
  min-height: 420px;
  margin-bottom: 1.5rem;
}

.pub-sidebar {
  flex: 0 0 280px;
  width: 280px;
  border-right: 1px solid var(--extended-lavender-gray, #e2e8f0);
  background: var(--bg-light-mist-gray, #f8f9fb);
  display: flex;
  flex-direction: column;
}

.sidebar-heading {
  padding: 0.65rem 0.75rem;
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--text-secondary-cool-gray, #718096);
  border-bottom: 1px solid var(--extended-lavender-gray, #e2e8f0);
  flex-shrink: 0;
}

.sidebar-scroll {
  flex: 1;
  overflow-y: auto;
  padding: 0.5rem 0.25rem;
}

.no-content-hint {
  padding: 1rem;
  color: var(--text-secondary-cool-gray, #718096);
  font-size: 0.85rem;
  font-style: italic;
  text-align: center;
}

/* Content panel */
.pub-content {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  background: #fff;
}

.content-inner {
  flex: 1;
  padding: 1.5rem 2rem;
  overflow-y: auto;
}

.content-title {
  margin: 0 0 1rem;
  font-size: 1.35rem;
  color: var(--text-primary-charcoal, #2d3748);
  border-bottom: 2px solid var(--primary-deep-teal, #005b6e);
  padding-bottom: 0.5rem;
}

.content-body {
  font-size: 0.95rem;
  line-height: 1.7;
  color: var(--text-primary-charcoal, #2d3748);
}

.content-body :deep(h1),
.content-body :deep(h2),
.content-body :deep(h3),
.content-body :deep(h4) {
  margin: 1.25rem 0 0.5rem;
  color: var(--text-primary-charcoal, #2d3748);
}

.content-body :deep(p) {
  margin: 0 0 0.85rem;
}

.content-body :deep(ul),
.content-body :deep(ol) {
  padding-left: 1.5rem;
  margin-bottom: 0.85rem;
}

.content-body :deep(img) {
  max-width: 100%;
  height: auto;
  border-radius: 4px;
}

.content-body :deep(pre) {
  background: #f5f7fa;
  border-radius: 4px;
  padding: 0.75rem 1rem;
  overflow-x: auto;
}

.content-body :deep(code) {
  background: #f5f7fa;
  padding: 0.1em 0.35em;
  border-radius: 3px;
  font-size: 0.88em;
}

.content-empty {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary-cool-gray, #718096);
  font-style: italic;
  font-size: 0.9rem;
  padding: 2rem;
}

/* Audience bar & actions (unchanged) */
.audience-bar {
  background: #f0f4ff;
  border: 1px solid #c5d3f0;
  border-radius: 8px;
  padding: 0.75rem 1rem;
  margin-bottom: 1rem;
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  gap: 0.5rem;
}
.audience-label { font-weight: 600; font-size: 0.88rem; color: #205493; white-space: nowrap; padding-top: 2px; }
.tag-checkboxes { display: flex; flex-wrap: wrap; gap: 0.5rem; flex: 1; }
.tag-check {
  display: flex; align-items: center; gap: 0.3rem;
  font-size: 0.85rem; cursor: pointer; white-space: nowrap;
  background: #fff; border: 1px solid #c5d3f0; border-radius: 12px;
  padding: 0.2rem 0.6rem;
}
.tag-check input { cursor: pointer; }
.no-tags-hint  { color: #6c757d; font-size: 0.82rem; font-style: italic; }
.audience-hint { width: 100%; color: #6c757d; font-size: 0.78rem; margin-top: 0.25rem; }

.actions {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.actions button {
  padding: 0.75rem 1.25rem;
  border: none;
  background: var(--primary-deep-teal);
  color: white;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s ease;
  font-size: 0.9rem;
}

.actions button:hover { background: var(--primary-medium-teal); }
.preview-btn { background: var(--text-secondary-cool-gray) !important; }
.preview-btn:hover { background: var(--text-primary-charcoal) !important; }

.loading, .error { margin-top: 1rem; font-size: 0.9rem; }
.error { color: var(--error-coral-red); }
.empty { color: var(--text-secondary-cool-gray); font-style: italic; text-align: center; margin-top: 2rem; }

/* Responsive: stack panels on narrow screens */
@media (max-width: 768px) {
  .pub-body { flex-direction: column; min-height: unset; }
  .pub-sidebar { flex: none; width: 100%; border-right: none; border-bottom: 1px solid var(--extended-lavender-gray, #e2e8f0); }
  .sidebar-scroll { max-height: 250px; }
  .content-inner { padding: 1rem; }
  .actions { flex-direction: column; }
  .actions button { width: 100%; }
}
</style>
