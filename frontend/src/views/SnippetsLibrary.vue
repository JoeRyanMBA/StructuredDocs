<template>
  <div class="snippets-library">
    <div class="page-header">
      <h1>📎 Snippets Library</h1>
      <p class="subtitle">Manage reusable audience-specific content blocks</p>
    </div>

    <div class="library-layout">
      <!-- List panel -->
      <aside class="snippet-list-panel">
        <div class="panel-toolbar">
          <input v-model="search" type="text" class="search-input" placeholder="Search snippets or #id…" />
          <button class="btn-new" @click="startNew">+ New Snippet</button>
        </div>
        <ul class="snippet-list">
          <li
            v-for="s in filtered"
            :key="s.id"
            class="snippet-list-item"
            :class="{ active: selected && selected.id === s.id }"
            @click="selectSnippet(s)"
          >
            <div class="snippet-name">
                {{ s.title }}
                <span class="snippet-id-pill">#{{ s.id }}</span>
                <span v-if="s.usage_count > 0" class="usage-badge" :title="`Used in ${s.usage_count} topic(s)`">{{ s.usage_count }}</span>
              </div>
            <div class="snippet-tag-row">
              <span v-for="tag in s.tags" :key="tag.id" class="tag-badge">{{ tag.name }}</span>
              <span v-if="!s.tags || s.tags.length === 0" class="no-tags">No audience tags</span>
            </div>
          </li>
          <li v-if="filtered.length === 0" class="empty-state">
            {{ search ? 'No snippets match your search.' : 'No snippets yet. Create one!' }}
          </li>
        </ul>
      </aside>

      <!-- Editor panel -->
      <section class="snippet-editor-panel">
        <div v-if="!selected && !creating" class="select-prompt">
          <p>Select a snippet from the list or create a new one.</p>
        </div>

        <form v-else @submit.prevent="save" class="editor-form">
          <div class="form-header">
            <h2>
              {{ creating ? 'New Snippet' : 'Edit Snippet' }}
              <span v-if="!creating && selected" class="object-id-badge" title="Snippet ID">#{{ selected.id }}</span>
            </h2>
            <div class="form-header-actions">
              <button v-if="!creating" type="button" class="btn-delete"
                :disabled="selected && selected.usage_count > 0"
                :title="selected && selected.usage_count > 0 ? 'Cannot delete: used in topics' : 'Delete snippet'"
                @click="confirmDelete">🗑 Delete</button>
            </div>
          </div>

          <div class="form-group">
            <label>Title <span class="required">*</span></label>
            <input v-model="form.title" type="text" class="form-input" placeholder="Short descriptive name" required />
          </div>

          <div class="form-group">
            <label>Audience Tags</label>
            <TagEditor
              v-if="!creating && selected"
              :entity-type="'snippet'"
              :entity-id="selected.id"
              @change="onTagsChanged"
            />
            <p v-else class="hint">Save the snippet first, then assign audience tags.</p>
          </div>

          <div class="form-group">
            <label>Content</label>
            <div class="editor-mode-toggle">
              <button type="button" :class="['mode-btn', editorMode === 'markdown' ? 'active' : '']" @click="editorMode = 'markdown'">📝 Markdown</button>
              <button type="button" :class="['mode-btn', editorMode === 'wysiwyg' ? 'active' : '']" @click="editorMode = 'wysiwyg'">📄 WYSIWYG</button>
              <button type="button" :class="['mode-btn', editorMode === 'preview' ? 'active' : '']" @click="editorMode = 'preview'">🔍 Preview</button>
            </div>
            <div v-if="editorMode === 'markdown'" class="markdown-editor-wrap">
              <div class="markdown-toolbar">
                <button type="button" class="md-btn" @click="insertMarkdown('link')" title="Insert link">🔗 Link</button>
                <button type="button" class="md-btn" @click="insertMarkdown('image')" title="Insert image">🖼️ Image</button>
              </div>
              <textarea v-model="form.content" ref="mdTextarea" class="markdown-textarea" rows="12" placeholder="Write content in Markdown…"></textarea>
            </div>
            <RichTextEditor v-else-if="editorMode === 'wysiwyg'" ref="richEditor" @update:model-value="onRichEditorUpdate">
              <template #toolbar-extra>
                <button type="button" @click="openLinkModal" class="toolbar-btn">🔗 Link</button>
                <button type="button" @click="openImageModal" class="toolbar-btn">🖼️ Image</button>
              </template>
            </RichTextEditor>
            <div v-else class="preview-content" v-html="renderedContent"></div>
          </div>

          <div class="form-actions">
            <button type="submit" class="btn-save" :disabled="saving">
              {{ saving ? 'Saving…' : (creating ? 'Create Snippet' : 'Save Changes') }}
            </button>
            <button type="button" class="btn-cancel" @click="cancel">Cancel</button>
            <span v-if="saveMsg" class="save-msg">{{ saveMsg }}</span>
          </div>

          <div v-if="!creating && usageTopics.length > 0" class="usage-section">
            <h4 class="usage-title">Used in {{ usageTopics.length }} topic{{ usageTopics.length > 1 ? 's' : '' }}</h4>
            <ul class="usage-list">
              <li v-for="t in usageTopics" :key="t.id" class="usage-item">
                <span v-if="t.project" class="usage-breadcrumb">{{ t.project }} › {{ t.collection }} › </span>
                <span v-else-if="t.collection" class="usage-breadcrumb">{{ t.collection }} › </span>
                <strong>{{ t.title }}</strong>
              </li>
            </ul>
          </div>
        </form>
      </section>
    </div>

    <!-- Delete confirmation -->
    <div v-if="showDeleteConfirm" class="modal-overlay" @click.self="showDeleteConfirm = false">
      <div class="confirm-modal">
        <h3>Delete Snippet?</h3>
        <p>This will remove <strong>{{ selected && selected.title }}</strong> and all its placeholder references in topic content will become empty.</p>
        <div class="confirm-actions">
          <button class="btn-delete" @click="doDelete">Yes, Delete</button>
          <button class="btn-cancel" @click="showDeleteConfirm = false">Cancel</button>
        </div>
      </div>
    </div>

    <!-- Link Modal -->
    <div v-if="showLinkModal" class="modal-overlay" @click.self="showLinkModal = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Insert Link</h3>
          <button @click="showLinkModal = false" class="close-btn">&times;</button>
        </div>
        <div class="modal-body">
          <div class="segmented-control" role="tablist" aria-label="Insert link mode" style="margin-bottom:.75rem">
            <button type="button" role="tab" :aria-selected="(linkInsertMode === 'manual').toString()" :tabindex="linkInsertMode === 'manual' ? 0 : -1" :class="['segmented-btn','btn','btn-sm', linkInsertMode === 'manual' ? 'btn-primary active' : 'btn-secondary']" @click="linkInsertMode = 'manual'">Manual</button>
            <button type="button" role="tab" :aria-selected="(linkInsertMode === 'existing').toString()" :tabindex="linkInsertMode === 'existing' ? 0 : -1" :class="['segmented-btn','btn','btn-sm', linkInsertMode === 'existing' ? 'btn-primary active' : 'btn-secondary']" @click="openExistingLinks">Existing</button>
          </div>
          <div v-if="linkInsertMode === 'manual'">
            <div class="form-group">
              <label>Link Text</label>
              <input v-model="linkText" type="text" class="form-input" placeholder="Display text">
            </div>
            <div class="form-group">
              <label>URL</label>
              <input v-model="linkUrl" type="url" class="form-input" placeholder="https://example.com">
            </div>
          </div>
          <div v-else>
            <div class="form-group">
              <label>Search Links</label>
              <input v-model="linkSearch" type="text" class="form-input" placeholder="Search by title, description, reference, or URL" @input="debouncedFetchLinks">
            </div>
            <div class="resource-list" v-if="availableLinks && availableLinks.length">
              <div v-for="link in availableLinks" :key="link.id" class="resource-item" :class="{ selected: selectedExistingLink && selectedExistingLink.id === link.id }" @click="selectExistingLink(link)">
                <div class="resource-title">{{ link.title }} <span v-if="link.reference_code" class="muted">({{ link.reference_code }})</span></div>
                <div class="resource-sub">{{ link.url }}</div>
              </div>
            </div>
            <div class="empty-state" v-else>No links found.</div>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="insertLink" class="btn btn-primary">Insert Link</button>
          <button @click="showLinkModal = false" class="btn btn-secondary">Cancel</button>
        </div>
      </div>
    </div>

    <!-- Image Modal -->
    <div v-if="showImageModal" class="modal-overlay" @click.self="showImageModal = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Insert Image</h3>
          <button @click="showImageModal = false" class="close-btn">&times;</button>
        </div>
        <div class="modal-body">
          <div class="segmented-control" role="tablist" aria-label="Insert image mode" style="margin-bottom:.75rem">
            <button type="button" role="tab" :aria-selected="(imageInsertMode === 'url').toString()" :tabindex="imageInsertMode === 'url' ? 0 : -1" :class="['segmented-btn','btn','btn-sm', imageInsertMode === 'url' ? 'btn-primary active' : 'btn-secondary']" @click="imageInsertMode = 'url'">By URL</button>
            <button type="button" role="tab" :aria-selected="(imageInsertMode === 'existing').toString()" :tabindex="imageInsertMode === 'existing' ? 0 : -1" :class="['segmented-btn','btn','btn-sm', imageInsertMode === 'existing' ? 'btn-primary active' : 'btn-secondary']" @click="openExistingImages">Browse</button>
            <button type="button" role="tab" :aria-selected="(imageInsertMode === 'upload').toString()" :tabindex="imageInsertMode === 'upload' ? 0 : -1" :class="['segmented-btn','btn','btn-sm', imageInsertMode === 'upload' ? 'btn-primary active' : 'btn-secondary']" @click="imageInsertMode = 'upload'">Upload</button>
          </div>
          <div v-if="imageInsertMode === 'url'">
            <div class="form-group">
              <label>Image URL</label>
              <input v-model="imageUrl" type="url" class="form-input" placeholder="https://example.com/image.jpg">
            </div>
            <div class="form-group">
              <label>Alt Text</label>
              <input v-model="imageAlt" type="text" class="form-input" placeholder="Description of image">
            </div>
          </div>
          <div v-else-if="imageInsertMode === 'existing'">
            <div class="form-group">
              <label>Search Images</label>
              <input v-model="imageSearch" type="text" class="form-input" placeholder="Filter by filename" @input="filterImages">
            </div>
            <div class="image-grid" v-if="filteredImages && filteredImages.length">
              <div v-for="img in filteredImages" :key="img.id" class="image-item" :class="{ selected: selectedExistingImage && selectedExistingImage.id === img.id }" @click="selectExistingImage(img)">
                <img :src="imageDisplayUrl(img)" :alt="img.alt_text || img.filename" @error="handleImageError">
                <div class="image-caption">{{ img.filename }}</div>
              </div>
            </div>
            <div class="empty-state" v-else>No images found.</div>
          </div>
          <div v-else>
            <div class="form-group">
              <label>Upload Image</label>
              <input type="file" accept="image/*" @change="onImageUploadSelect">
            </div>
            <div class="upload-status" v-if="imageUploadMessage">{{ imageUploadMessage }}</div>
            <div class="upload-actions">
              <button class="btn btn-primary" :disabled="imageUploadUploading || !imageUploadFile" @click="uploadImageFile">
                {{ imageUploadUploading ? 'Uploading...' : 'Upload & Use' }}
              </button>
            </div>
            <div class="form-group" v-if="imageUrl">
              <label>Resulting URL</label>
              <input v-model="imageUrl" type="url" class="form-input">
            </div>
            <div class="form-group">
              <label>Alt Text</label>
              <input v-model="imageAlt" type="text" class="form-input" placeholder="Description of image">
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="insertImage" class="btn btn-primary">Insert Image</button>
          <button @click="showImageModal = false" class="btn btn-secondary">Cancel</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { listSnippets, createSnippet, updateSnippet, deleteSnippet, getSnippetUsage } from '@/api/snippets.js'
import { marked } from 'marked'
import { htmlToMarkdown } from '@/utils/htmlToMarkdown'
import TagEditor from '@/components/TagEditor.vue'
import RichTextEditor from '@/components/RichTextEditor.vue'

export default {
  name: 'SnippetsLibrary',
  components: { TagEditor, RichTextEditor },
  data() {
    return {
      snippets: [],
      search: '',
      selected: null,
      creating: false,
      form: { title: '', content: '' },
      saving: false,
      saveMsg: '',
      showDeleteConfirm: false,
      editorMode: 'markdown',
      usageTopics: [],
      // Link modal
      showLinkModal: false,
      linkInsertMode: 'manual',
      linkText: '',
      linkUrl: '',
      linkSearch: '',
      availableLinks: [],
      selectedExistingLink: null,
      _linkDebounceTimer: null,
      // Image modal
      showImageModal: false,
      imageInsertMode: 'url',
      imageUrl: '',
      imageAlt: '',
      imageSearch: '',
      availableImages: [],
      filteredImages: [],
      selectedExistingImage: null,
      imageUploadFile: null,
      imageUploadUploading: false,
      imageUploadMessage: '',
    }
  },
  computed: {
    filtered() {
      const q = this.search.toLowerCase().trim()
      if (!q) return this.snippets
      // Support search by ID with # prefix (e.g. "#42") or plain number
      const idMatch = q.match(/^#?(\d+)$/)
      if (idMatch) return this.snippets.filter(s => s.id === parseInt(idMatch[1]))
      return this.snippets.filter(s => s.title.toLowerCase().includes(q))
    },
    renderedContent() {
      if (!this.form.content) return ''
      try { return marked(this.form.content) } catch { return this.form.content }
    },
  },
  async mounted() {
    await this.loadSnippets()
  },
  watch: {
    editorMode(newMode) {
      if (newMode === 'wysiwyg') {
        this.$nextTick(() => {
          const html = this.renderedContent
          this.$refs.richEditor?.setContent(html)
        })
      }
    },
  },
  methods: {
    async loadSnippets() {
      try {
        this.snippets = await listSnippets()
      } catch (e) {
        console.error('Failed to load snippets', e)
      }
    },
    selectSnippet(s) {
      this.creating = false
      this.selected = s
      this.form = { title: s.title, content: s.content || '' }
      this.editorMode = 'markdown'
      this.usageTopics = []
      this.loadUsage(s.id)
    },
    startNew() {
      this.creating = true
      this.selected = null
      this.form = { title: '', content: '' }
      this.editorMode = 'markdown'
      this.usageTopics = []
    },
    cancel() {
      this.creating = false
      this.selected = null
      this.form = { title: '', content: '' }
      this.editorMode = 'markdown'
      this.usageTopics = []
    },
    async loadUsage(snippetId) {
      try {
        this.usageTopics = await getSnippetUsage(snippetId)
      } catch (e) {
        console.error('Failed to load snippet usage', e)
      }
    },
    onRichEditorUpdate(html) {
      const md = htmlToMarkdown(html)
      if (md !== this.form.content) {
        this.form.content = md
      }
    },
    async save() {
      if (!this.form.title.trim()) return
      this.saving = true
      this.saveMsg = ''
      try {
        if (this.creating) {
          const created = await createSnippet({ title: this.form.title, content: this.form.content })
          this.snippets.unshift(created)
          this.creating = false
          this.selected = created
          this.loadUsage(created.id)
        } else {
          const updated = await updateSnippet(this.selected.id, { title: this.form.title, content: this.form.content })
          const idx = this.snippets.findIndex(s => s.id === this.selected.id)
          if (idx !== -1) this.snippets.splice(idx, 1, updated)
          this.selected = updated
        }
        this.saveMsg = '✓ Saved'
        setTimeout(() => { this.saveMsg = '' }, 2000)
      } catch (e) {
        this.saveMsg = 'Error saving'
        console.error(e)
      } finally {
        this.saving = false
      }
    },
    confirmDelete() {
      this.showDeleteConfirm = true
    },
    async doDelete() {
      try {
        await deleteSnippet(this.selected.id)
        this.snippets = this.snippets.filter(s => s.id !== this.selected.id)
        this.selected = null
        this.creating = false
      } catch (e) {
        console.error('Delete failed', e)
      } finally {
        this.showDeleteConfirm = false
      }
    },
    onTagsChanged(tags) {
      if (this.selected) {
        this.selected = { ...this.selected, tags }
        const idx = this.snippets.findIndex(s => s.id === this.selected.id)
        if (idx !== -1) this.snippets.splice(idx, 1, this.selected)
      }
    },
    insertMarkdown(type) {
      const ta = this.$refs.mdTextarea
      if (!ta) return
      const start = ta.selectionStart
      const end = ta.selectionEnd
      const selected = this.form.content.substring(start, end)
      const insertion = type === 'link'
        ? (selected ? `[${selected}](url)` : '[link text](url)')
        : (selected ? `![${selected}](url)` : '![alt text](url)')
      this.form.content = this.form.content.substring(0, start) + insertion + this.form.content.substring(end)
      this.$nextTick(() => {
        ta.focus()
        const urlStart = start + insertion.indexOf('url')
        ta.setSelectionRange(urlStart, urlStart + 3)
      })
    },
    // --- Link modal ---
    openLinkModal() {
      this.$refs.richEditor?.saveSelection()
      this.linkInsertMode = 'manual'
      this.linkText = ''
      this.linkUrl = ''
      this.linkSearch = ''
      this.availableLinks = []
      this.selectedExistingLink = null
      this.showLinkModal = true
    },
    async openExistingLinks() {
      this.linkInsertMode = 'existing'
      await this.fetchLinks()
    },
    async fetchLinks() {
      try {
        const qs = this.linkSearch ? `?search=${encodeURIComponent(this.linkSearch)}&include_usage=true` : '?include_usage=true'
        const res = await fetch(`/api/links/${qs}`)
        if (res.ok) {
          const data = await res.json()
          this.availableLinks = data.links || []
        }
      } catch (e) { console.error('Failed to fetch links', e) }
    },
    debouncedFetchLinks() {
      clearTimeout(this._linkDebounceTimer)
      this._linkDebounceTimer = setTimeout(() => this.fetchLinks(), 300)
    },
    selectExistingLink(link) {
      this.selectedExistingLink = link
      this.linkText = link.title || link.reference_code || 'Link'
      this.linkUrl = link.url
    },
    insertLink() {
      if (!this.linkUrl) return
      const editor = this.$refs.richEditor?.getEditorEl()
      if (editor) {
        const restored = this.$refs.richEditor?.restoreSelection()
        const anchor = document.createElement('a')
        anchor.href = this.linkUrl
        anchor.textContent = this.linkText || this.linkUrl
        anchor.target = '_blank'
        anchor.rel = 'noopener noreferrer'
        if (restored) {
          const sel = window.getSelection()
          if (sel && sel.rangeCount > 0) {
            const range = sel.getRangeAt(0)
            range.deleteContents()
            range.insertNode(anchor)
            range.setStartAfter(anchor)
            range.collapse(true)
            sel.removeAllRanges()
            sel.addRange(range)
          } else {
            editor.appendChild(anchor)
          }
        } else {
          editor.appendChild(anchor)
        }
        this.$refs.richEditor?.emitUpdate()
      }
      this.showLinkModal = false
      this.linkText = ''
      this.linkUrl = ''
      this.selectedExistingLink = null
    },
    // --- Image modal ---
    openImageModal() {
      this.$refs.richEditor?.saveSelection()
      this.imageInsertMode = 'url'
      this.imageUrl = ''
      this.imageAlt = ''
      this.imageSearch = ''
      this.availableImages = []
      this.filteredImages = []
      this.selectedExistingImage = null
      this.imageUploadFile = null
      this.imageUploadMessage = ''
      this.showImageModal = true
    },
    async openExistingImages() {
      this.imageInsertMode = 'existing'
      await this.fetchImages()
      this.filterImages()
    },
    async fetchImages() {
      try {
        const res = await fetch('/api/images')
        if (res.ok) {
          this.availableImages = await res.json()
          this.filteredImages = [...this.availableImages]
        }
      } catch (e) { console.error('Failed to fetch images', e) }
    },
    filterImages() {
      const q = (this.imageSearch || '').toLowerCase()
      this.filteredImages = q
        ? this.availableImages.filter(img => (img.filename || '').toLowerCase().includes(q))
        : [...this.availableImages]
    },
    selectExistingImage(img) {
      this.selectedExistingImage = img
      this.imageUrl = img.public_url || img.file_path || ''
      this.imageAlt = img.alt_text || img.filename || ''
    },
    imageDisplayUrl(img) {
      return img.public_url || img.file_path || ''
    },
    handleImageError(event) {
      event.target.style.opacity = '0.3'
    },
    onImageUploadSelect(event) {
      this.imageUploadFile = event.target.files[0] || null
      this.imageUploadMessage = this.imageUploadFile ? `Selected: ${this.imageUploadFile.name}` : ''
    },
    async uploadImageFile() {
      if (!this.imageUploadFile) return
      this.imageUploadUploading = true
      this.imageUploadMessage = 'Uploading...'
      try {
        const formData = new FormData()
        formData.append('image', this.imageUploadFile)
        const res = await fetch('/api/images/upload', { method: 'POST', body: formData })
        if (!res.ok) throw new Error(`Upload failed: ${res.status}`)
        const uploaded = await res.json()
        this.imageUrl = uploaded.public_url || uploaded.file_path || ''
        this.imageAlt = uploaded.alt_text || uploaded.filename || ''
        this.imageUploadMessage = '✅ Upload successful'
      } catch (e) {
        this.imageUploadMessage = `❌ ${e.message}`
      } finally {
        this.imageUploadUploading = false
      }
    },
    insertImage() {
      if (!this.imageUrl) return
      const editor = this.$refs.richEditor?.getEditorEl()
      if (editor) {
        this.$refs.richEditor?.restoreSelection()
        const alt = this.imageAlt || 'Image'
        document.execCommand('insertHTML', false, `<img src="${this.imageUrl}" alt="${alt}" />`)
        this.$refs.richEditor?.emitUpdate()
      }
      this.showImageModal = false
      this.imageUrl = ''
      this.imageAlt = ''
      this.selectedExistingImage = null
      this.imageInsertMode = 'url'
      this.imageUploadFile = null
      this.imageUploadMessage = ''
    },
  },
}
</script>

<style scoped>
.snippets-library { padding: 1.5rem; max-width: 1100px; }
.page-header { margin-bottom: 1.5rem; }
.page-header h1 { margin: 0 0 0.25rem; font-size: 1.5rem; }
.subtitle { color: #6c757d; margin: 0; font-size: 0.95rem; }

.library-layout {
  display: flex;
  gap: 1.5rem;
  align-items: flex-start;
}

.snippet-list-panel {
  width: 280px;
  flex-shrink: 0;
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  overflow: hidden;
}
.panel-toolbar {
  padding: 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  border-bottom: 1px solid #dee2e6;
}
.search-input {
  width: 100%;
  padding: 0.4rem 0.65rem;
  border: 1px solid #ced4da;
  border-radius: 6px;
  font-size: 0.85rem;
  box-sizing: border-box;
}
.btn-new {
  background: #205493;
  color: #fff;
  border: none;
  border-radius: 6px;
  padding: 0.4rem 0.75rem;
  font-size: 0.85rem;
  cursor: pointer;
  text-align: center;
}
.btn-new:hover { background: #1a4376; }

.snippet-list { list-style: none; margin: 0; padding: 0.25rem 0; max-height: 60vh; overflow-y: auto; }
.snippet-list-item {
  padding: 0.6rem 0.75rem;
  cursor: pointer;
  border-left: 3px solid transparent;
  transition: background 0.15s;
}
.snippet-list-item:hover { background: #e9ecef; }
.snippet-list-item.active { background: #e8eef7; border-left-color: #205493; }
.snippet-name {
  font-size: 0.88rem; font-weight: 500; color: #212529;
  display: flex; align-items: center; gap: 0.4rem;
}
.usage-badge {
  background: #205493; color: #fff;
  border-radius: 10px; padding: 0.05rem 0.45rem;
  font-size: 0.7rem; font-weight: 600; line-height: 1.4;
}
.snippet-tag-row { margin-top: 0.2rem; display: flex; flex-wrap: wrap; gap: 0.2rem; }
.tag-badge {
  background: #e3f2fd; color: #1565c0; border: 1px solid #bbdefb;
  border-radius: 10px; padding: 0.05rem 0.4rem; font-size: 0.72rem;
}
.no-tags { color: #adb5bd; font-size: 0.72rem; font-style: italic; }
.empty-state { padding: 1rem; color: #6c757d; font-size: 0.85rem; text-align: center; }

.snippet-editor-panel {
  flex: 1;
  background: #fff;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  padding: 1.25rem;
  min-height: 400px;
}
.select-prompt { color: #6c757d; text-align: center; padding: 3rem 1rem; }

.editor-form { display: flex; flex-direction: column; gap: 1rem; }
.form-header { display: flex; align-items: center; justify-content: space-between; }
.form-header h2 { margin: 0; font-size: 1.1rem; }

.form-group { display: flex; flex-direction: column; gap: 0.35rem; }
.form-group label { font-size: 0.85rem; font-weight: 600; color: #495057; }
.form-input {
  padding: 0.5rem 0.75rem;
  border: 1px solid #ced4da;
  border-radius: 6px;
  font-size: 0.9rem;
}
.form-input:focus { outline: none; border-color: #205493; }
.hint { color: #6c757d; font-size: 0.82rem; margin: 0; }
.required { color: #dc3545; }

.form-actions { display: flex; align-items: center; gap: 0.75rem; flex-wrap: wrap; }

/* Give RichTextEditor a fixed height in snippet forms */
.form-group :deep(.rte-wysiwyg-editor) {
  height: auto;
  min-height: 0;
}
.form-group :deep(.wysiwyg-content) {
  min-height: 200px;
  height: auto;
  border-radius: 0 0 6px 6px;
  font-size: 0.9rem;
}

.editor-mode-toggle {
  display: flex;
  gap: 0.35rem;
  margin-bottom: 0.5rem;
}
.mode-btn {
  background: none;
  border: 1px solid #ced4da;
  border-radius: 5px;
  padding: 0.25rem 0.65rem;
  font-size: 0.82rem;
  cursor: pointer;
  color: #495057;
}
.mode-btn:hover { background: #e9ecef; }
.mode-btn.active { background: #205493; color: #fff; border-color: #205493; }
.markdown-editor-wrap { display: flex; flex-direction: column; }
.markdown-toolbar {
  display: flex;
  gap: 0.3rem;
  padding: 0.3rem 0.4rem;
  background: #f8f9fa;
  border: 1px solid #ced4da;
  border-bottom: none;
  border-radius: 6px 6px 0 0;
}
.md-btn {
  background: #fff;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  padding: 0.2rem 0.55rem;
  font-size: 0.8rem;
  cursor: pointer;
  color: #495057;
}
.md-btn:hover { background: #e9ecef; border-color: #adb5bd; }
.markdown-textarea {
  width: 100%;
  padding: 0.6rem 0.75rem;
  border: 1px solid #ced4da;
  border-radius: 0 0 6px 6px;
  font-family: monospace;
  font-size: 0.88rem;
  resize: vertical;
  box-sizing: border-box;
}
.markdown-textarea:focus { outline: none; border-color: #205493; }
.preview-content {
  border: 1px solid #dee2e6;
  border-radius: 6px;
  padding: 0.75rem 1rem;
  min-height: 200px;
  font-size: 0.9rem;
  line-height: 1.6;
}
.btn-save {
  background: #205493; color: #fff; border: none;
  border-radius: 6px; padding: 0.5rem 1.25rem; font-size: 0.9rem; cursor: pointer;
}
.btn-save:hover:not(:disabled) { background: #1a4376; }
.btn-save:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-cancel {
  background: none; border: 1px solid #ced4da;
  border-radius: 6px; padding: 0.5rem 1rem; font-size: 0.9rem; cursor: pointer; color: #495057;
}
.btn-cancel:hover { background: #f8f9fa; }
.btn-delete {
  background: #dc3545; color: #fff; border: none;
  border-radius: 6px; padding: 0.4rem 0.75rem; font-size: 0.85rem; cursor: pointer;
}
.btn-delete:hover:not(:disabled) { background: #b02a37; }
.btn-delete:disabled { opacity: 0.45; cursor: not-allowed; }
.save-msg { color: #198754; font-size: 0.85rem; }
.form-header-actions { display: flex; gap: 0.5rem; }

.usage-section {
  border-top: 1px solid #dee2e6;
  padding-top: 0.75rem;
  margin-top: 0.5rem;
}
.usage-title { margin: 0 0 0.4rem; font-size: 0.85rem; color: #495057; font-weight: 600; }
.usage-list { margin: 0; padding: 0; list-style: none; display: flex; flex-direction: column; gap: 0.25rem; }
.usage-item { font-size: 0.85rem; color: #212529; }
.usage-breadcrumb { color: #6c757d; font-size: 0.8rem; }

.upload-status { font-size: 0.85rem; margin: 0.35rem 0; color: #495057; }
.upload-actions { margin: 0.5rem 0; }


.modal-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.4);
  display: flex; align-items: center; justify-content: center; z-index: 2000;
}
.confirm-modal {
  background: #fff; border-radius: 8px; padding: 1.5rem;
  max-width: 400px; width: 90%;
  box-shadow: 0 8px 32px rgba(0,0,0,0.15);
}
.confirm-modal h3 { margin: 0 0 0.5rem; }
.confirm-modal p { margin: 0 0 1rem; font-size: 0.9rem; color: #495057; }
.confirm-actions { display: flex; gap: 0.75rem; }

.object-id-badge {
  display: inline-block;
  font-size: 0.75rem;
  font-weight: 500;
  color: #5a6a8a;
  background: #e8eef7;
  border: 1px solid #c5d3f0;
  border-radius: 10px;
  padding: 0.1rem 0.5rem;
  margin-left: 0.5rem;
  vertical-align: middle;
  letter-spacing: 0.01em;
}
.snippet-id-pill {
  display: inline-block;
  font-size: 0.7rem;
  color: #8a9bb5;
  background: #f0f4ff;
  border: 1px solid #d0d9f0;
  border-radius: 8px;
  padding: 0.05rem 0.35rem;
  margin-left: 0.25rem;
  vertical-align: middle;
}
</style>
