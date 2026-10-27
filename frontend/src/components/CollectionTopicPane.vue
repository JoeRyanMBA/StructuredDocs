<template>
  <main class="collection-reader" aria-label="Collection topic">
    <div class="reader-toolbar">
      <div class="reader-tabs" role="group" aria-label="Topic mode">
        <button type="button" :aria-pressed="!editing" :disabled="!topic || loading" @click="requestPreview">
          <i class="bi bi-eye" aria-hidden="true"></i> Preview
        </button>
        <button type="button" :aria-pressed="editing" :disabled="!topic || loading || !usageLoaded" @click="editing = true">
          <i class="bi bi-pencil" aria-hidden="true"></i> Edit
        </button>
      </div>
      <span v-if="saving" role="status">Saving topic...</span>
    </div>
    <div v-if="metadataError" class="reader-notice" role="alert">
      {{ metadataError }}
      <button type="button" @click="loadContext">Retry</button>
    </div>
    <div v-if="topic && sharedCollections.length > 1" class="reader-notice shared-topic-warning" role="status">
      <i class="bi bi-link-45deg" aria-hidden="true"></i>
      Used in {{ sharedCollections.length }} collections. Changes affect all of them.
      <details>
        <summary>Collections</summary>
        <ul><li v-for="collection in sharedCollections" :key="collection.id">{{ collection.name }}</li></ul>
      </details>
      <span v-if="editing">Use tagged snippets for collection-specific content.</span>
    </div>
    <details v-if="!editing" class="audience-settings">
      <summary>Audience tags <span v-if="selectedTagIds.length">({{ selectedTagIds.length }})</span></summary>
      <div class="audience-options">
        <label v-for="tag in tags" :key="tag.id">
          <input v-model="selectedTagIds" type="checkbox" :value="Number(tag.id)" /> {{ tag.name }}
        </label>
        <span v-if="!tags.length">No audience tags.</span>
      </div>
    </details>
    <div v-if="loading" class="reader-state" role="status">Loading topic...</div>
    <div v-else-if="error" class="reader-state" role="alert">
      {{ error }} <button type="button" @click="loadTopic(topic)">Retry</button>
    </div>
    <template v-else-if="topic">
      <TopicEditor
        v-if="editing"
        :key="topic.id"
        ref="editor"
        embedded
        :topic-id="topic.id"
        :initial-title="topic.title"
        :initial-content="topic.content"
        :initial-frontmatter="topic.frontmatter || ''"
        @save="onSaved"
        @close="requestPreview"
      />
      <article v-else class="collection-html-preview">
        <h1>{{ previewTitle }}</h1>
        <div v-if="rendering" role="status">Rendering preview...</div>
        <div v-else-if="previewError" role="alert">{{ previewError }} <button type="button" @click="renderPreview">Retry</button></div>
        <div v-else class="collection-html-content" v-html="previewHtml"></div>
      </article>
    </template>
    <div v-else class="reader-state">No topic selected.</div>

    <div v-if="pendingAction" class="modal-overlay" @keydown.esc="pendingAction = null">
      <div class="modal-content unsaved-topic-dialog" role="dialog" aria-modal="true" aria-labelledby="unsaved-topic-title">
        <div class="modal-header">
          <h2 id="unsaved-topic-title">Unsaved Topic Changes</h2>
          <button type="button" class="plain-close" aria-label="Close unsaved changes dialog" :disabled="saving" @click="pendingAction = null"><i class="bi bi-x-lg" aria-hidden="true"></i></button>
        </div>
        <p>{{ topic?.title }}</p>
        <div class="modal-footer">
          <button type="button" class="secondary-btn" :disabled="saving" @click="pendingAction = null">Cancel</button>
          <button type="button" class="secondary-btn" :disabled="saving" @click="finishPending">Discard</button>
          <button type="button" class="primary-btn" :disabled="saving" @click="savePending">Save</button>
        </div>
      </div>
    </div>
  </main>
</template>

<script>
import DOMPurify from 'dompurify'
import TopicEditor from '@/components/TopicEditor.vue'
import { getTopic, getTopicUsage, getAudienceTags } from '@/api/topics'
import { getCollectionVariablePreview } from '@/api/collections'
import { getSnippet } from '@/api/snippets'
import { renderCollectionTopic, substituteCollectionVariables } from '@/utils/collectionPreview'

export default {
  name: 'CollectionTopicPane',
  components: { TopicEditor },
  props: { collectionId: { type: [String, Number], required: true } },
  emits: ['selected', 'saved', 'audience-change'],
  data() {
    return {
      topic: null, editing: false, loading: false, error: '', saving: false,
      previewHtml: '', previewError: '', rendering: false, metadataError: '',
      usage: {}, usageLoaded: false, tags: [], selectedTagIds: [], mapping: {},
      pendingAction: null, requestId: 0, renderId: 0,
    }
  },
  computed: {
    sharedCollections() { return this.usage[String(this.topic?.id)]?.collections || [] },
    previewTitle() { return substituteCollectionVariables(this.topic?.title, this.mapping) },
    storageKey() { return `collection-audience-${this.collectionId}` },
  },
  watch: {
    selectedTagIds: {
      deep: true,
      handler(value) {
        try { localStorage.setItem(this.storageKey, JSON.stringify(value)) } catch {}
        this.$emit('audience-change', value)
        this.renderPreview()
      },
    },
  },
  mounted() {
    try {
      const stored = JSON.parse(localStorage.getItem(this.storageKey) || '[]')
      if (Array.isArray(stored)) this.selectedTagIds = stored.map(Number).filter(Number.isFinite)
    } catch {}
    this.loadContext()
  },
  beforeUnmount() { this.requestId++; this.renderId++ },
  methods: {
    async loadContext() {
      this.metadataError = ''
      try {
        const [usage, tags, variables] = await Promise.all([
          getTopicUsage(), getAudienceTags(), getCollectionVariablePreview(this.collectionId),
        ])
        this.usage = usage
        this.usageLoaded = true
        this.tags = Array.isArray(tags) ? tags : (tags.tags || [])
        this.mapping = variables.mapping || {}
        await this.renderPreview()
      } catch {
        this.metadataError = 'Collection variables, audience tags, or shared-topic usage could not be loaded. Preview may be incomplete.'
      }
    },
    hasUnsavedChanges() {
      const editor = this.$refs.editor
      if (editor?.editorMode === 'wysiwyg') editor.updateContentFromWysiwyg()
      return !!editor?.isDirty
    },
    openTopic(topic) {
      if (String(topic?.id) === String(this.topic?.id)) return
      const action = () => this.loadTopic(topic)
      if (this.hasUnsavedChanges()) this.pendingAction = action
      else action()
    },
    requestPreview() {
      if (!this.editing) return
      const action = () => { this.editing = false; this.renderPreview() }
      if (this.hasUnsavedChanges()) this.pendingAction = action
      else action()
    },
    finishPending() {
      const action = this.pendingAction
      this.pendingAction = null
      action?.()
    },
    async savePending() {
      this.saving = true
      await this.$refs.editor.saveTopic()
      this.saving = false
      if (!this.hasUnsavedChanges()) this.finishPending()
    },
    async loadTopic(topic) {
      const requestId = ++this.requestId
      this.renderId++
      this.topic = topic
      this.editing = false
      this.loading = !!topic
      this.error = ''
      if (!topic) return
      try {
        const data = await getTopic(topic.id)
        if (requestId !== this.requestId) return
        this.topic = data
        this.$emit('selected', data)
        await this.renderPreview()
      } catch (error) {
        if (requestId === this.requestId) this.error = error.message || 'Could not load topic.'
      } finally {
        if (requestId === this.requestId) this.loading = false
      }
    },
    async renderPreview() {
      if (!this.topic) return
      const renderId = ++this.renderId
      this.rendering = true
      this.previewError = ''
      try {
        const html = await renderCollectionTopic(this.topic.content, {
          document, getSnippet, tagIds: this.selectedTagIds, mapping: this.mapping,
          sanitize: html => DOMPurify.sanitize(html),
        })
        if (renderId === this.renderId) this.previewHtml = html
      } catch (error) {
        if (renderId === this.renderId) this.previewError = error.message || 'Could not render preview.'
      } finally {
        if (renderId === this.renderId) this.rendering = false
      }
    },
    async onSaved(result) {
      const editor = this.$refs.editor
      this.topic = { ...this.topic, title: editor.title, content: editor.content, frontmatter: editor.frontmatter, ...result }
      this.$emit('saved', this.topic)
      await this.$nextTick()
      if (!this.pendingAction) {
        this.editing = false
        await this.renderPreview()
      }
    },
  },
}
</script>

<style scoped>
.collection-reader { min-width: 0; border-left: 1px solid var(--extended-lavender-gray); padding-left: 1.5rem; }
.reader-toolbar { display: flex; align-items: center; justify-content: space-between; gap: 1rem; margin-bottom: 1rem; }
.reader-tabs { display: flex; gap: 0; }
.reader-tabs button { border: 1px solid var(--extended-lavender-gray); padding: .5rem 1rem; background: white; color: var(--primary-deep-teal); }
.reader-tabs button[aria-pressed="true"] { background: var(--primary-deep-teal); color: white; }
.reader-tabs button:disabled { opacity: .5; }
.reader-notice { padding: .75rem; background: #fff8db; border-left: 3px solid #a97600; margin-bottom: 1rem; overflow-wrap: anywhere; }
.reader-state { padding: 2rem 0; }
.audience-settings { padding: .75rem 0; border-bottom: 1px solid var(--extended-lavender-gray); margin-bottom: 1.5rem; }
.audience-options { display: flex; flex-wrap: wrap; gap: .75rem 1.25rem; margin-top: .75rem; }
.audience-options label { display: flex; align-items: center; gap: .4rem; }
.audience-options input[type="checkbox"] { width: 1rem; height: 1rem; flex: 0 0 1rem; margin: 0; padding: 0; }
.collection-html-preview { max-width: 76ch; margin: 0 auto; line-height: 1.65; overflow-wrap: anywhere; }
.collection-html-preview h1 { font-size: 1.75rem; line-height: 1.25; margin-bottom: 1.5rem; }
.collection-html-content :deep(img) { max-width: 100%; height: auto; }
.collection-html-content :deep(table) { display: block; max-width: 100%; overflow-x: auto; border-collapse: collapse; }
.collection-html-content :deep(td), .collection-html-content :deep(th) { border: 1px solid #d6dadd; padding: .5rem; }
.collection-html-content :deep(pre) { overflow-x: auto; padding: 1rem; background: #f4f5f5; }
.unsaved-topic-dialog { width: min(30rem, calc(100vw - 2rem)); padding: 1.25rem; border-radius: 6px; }
.unsaved-topic-dialog h2 { font-size: 1.25rem; }
@media (max-width: 800px) { .collection-reader { border-left: 0; padding: 1rem 0 0; border-top: 1px solid var(--extended-lavender-gray); } }
</style>