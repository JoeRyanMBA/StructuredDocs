
<template>
  <div class="topic-editor">
    <template v-if="readOnly">
      <h2 class="page-heading">{{ title }}</h2>
      <hr />
      <div v-html="abbreviatedHtml" class="topic-preview-content"></div>
    </template>
    <template v-else>
      <!-- Topic Editor UI -->
      <div class="editor-container">
        <div class="editor-header">
          <h2 class="page-heading">{{ pageTitle }}</h2>
          
          <!-- Save Status -->
          <div v-if="saveSuccess" class="save-status success">
            ✅ {{ saveSuccess }}
          </div>
          
          <!-- Title Field -->
          <div class="form-group">
            <label for="title">Title</label>
            <input 
              id="title"
              v-model="title" 
              type="text" 
              class="form-input title-input"
              placeholder="Enter topic title..."
              required
            />
            <div class="variable-insert" v-if="variableSlugs.length">
              <label class="var-insert-label">Variables</label>
              <input v-model="variableSearch" class="var-search" placeholder="Search…" @input="filterVariables" />
              <select v-model="selectedVariableSlug" @change="handleInsertVariable" class="var-insert-select" :title="selectedVariableSlug ? tokenPreview(selectedVariableSlug) : 'Select variable to insert'">
                <option value="">-- choose --</option>
                <optgroup v-if="recentVariables.length" label="Recent">
                  <option v-for="slug in recentVariables" :key="'r-'+slug" :value="slug">{{ slug }}</option>
                </optgroup>
                <optgroup label="All">
                  <option v-for="slug in filteredVariables" :key="slug" :value="slug">{{ slug }}</option>
                </optgroup>
              </select>
              <button type="button" class="btn btn-sm btn-secondary" @click="openVariablesAdmin" title="Manage variables in new tab">
                Manage
              </button>
            </div>
          </div>
        </div>

        <!-- Editor Mode Toggle -->
    <div class="editor-mode-toggle" role="tablist" aria-label="Select editor mode">
          <button
            type="button"
            role="tab"
            :aria-selected="(editorMode === 'markdown').toString()"
            :tabindex="editorMode === 'markdown' ? 0 : -1"
            :class="['mode-toggle-btn','btn','btn-sm', editorMode === 'markdown' ? 'btn-primary active' : 'btn-secondary']"
      @click="editorMode = 'markdown'"
      title="Edit in raw Markdown"
          >
            📝 <span class="label-text">Markdown</span>
          </button>
          <button
            type="button"
            role="tab"
            :aria-selected="(editorMode === 'wysiwyg').toString()"
            :tabindex="editorMode === 'wysiwyg' ? 0 : -1"
            :class="['mode-toggle-btn','btn','btn-sm', editorMode === 'wysiwyg' ? 'btn-primary active' : 'btn-secondary']"
      @click="editorMode = 'wysiwyg'"
      title="Visual editor"
          >
            📄 <span class="label-text">WYSIWYG</span>
          </button>
          <button
            type="button"
            role="tab"
            :aria-selected="(editorMode === 'preview').toString()"
            :tabindex="editorMode === 'preview' ? 0 : -1"
            :class="['mode-toggle-btn','btn','btn-sm', editorMode === 'preview' ? 'btn-primary active' : 'btn-secondary']"
      @click="editorMode = 'preview'"
      title="Preview rendered content"
          >
            <i class="bi bi-eye" aria-hidden="true"></i> <span class="label-text">Preview</span>
          </button>
        </div>

        <!-- Content Editor -->
        <div class="editor-content">
          <!-- Markdown Mode -->
          <div v-if="editorMode === 'markdown'" class="markdown-editor">
            <div class="toolbar">
              <button @click="insertMarkdown('**', '**')" class="toolbar-btn">𝐁 Bold</button>
              <button @click="insertMarkdown('*', '*')" class="toolbar-btn">𝐼 Italic</button>
              <button @click="insertMarkdown('`', '`')" class="toolbar-btn">⟨⟩ Code</button>
              <button @click="insertMarkdown('## ', '')" class="toolbar-btn">𝐇𝟐 Header</button>
              <button @click="insertMarkdown('### ', '')" class="toolbar-btn">𝐇𝟑 Header</button>
              <button @click="insertMarkdown('- ', '')" class="toolbar-btn">• List</button>
              <button @click="insertMarkdown('1. ', '')" class="toolbar-btn">1. List</button>
              <button @click="openLinkModal" class="toolbar-btn">🔗 Link</button>
              <button @click="openImageModal" class="toolbar-btn">🖼️ Image</button>
            </div>
            <textarea 
              ref="markdownEditor"
              v-model="content" 
              class="markdown-textarea"
              placeholder="Write your content in Markdown..."
              rows="20"
            ></textarea>
          </div>

          <!-- WYSIWYG Mode -->
          <div v-if="editorMode === 'wysiwyg'" class="wysiwyg-editor">
            <div class="toolbar">
              <button @click="execCommand('bold')" class="toolbar-btn">𝐁 Bold</button>
              <button @click="execCommand('italic')" class="toolbar-btn">𝐼 Italic</button>
              <button @click="execCommand('formatBlock', 'code')" class="toolbar-btn">⟨⟩ Code</button>
              <button @click="execCommand('formatBlock', 'h2')" class="toolbar-btn">𝐇𝟐 Header</button>
              <button @click="execCommand('formatBlock', 'h3')" class="toolbar-btn">𝐇𝟑 Header</button>
              <button @click="execCommand('insertUnorderedList')" class="toolbar-btn">• List</button>
              <button @click="execCommand('insertOrderedList')" class="toolbar-btn">1. List</button>
              <button @click="openLinkModal" class="toolbar-btn">🔗 Link</button>
              <button @click="openImageModal" class="toolbar-btn">🖼️ Image</button>
            </div>
            <div 
              ref="wysiwygEditor"
              @input="onWysiwygInput"
              @paste="handleWysiwygPaste"
              contenteditable="true" 
              class="wysiwyg-content"
            ></div>
          </div>

          <!-- Preview Mode -->
          <div v-if="editorMode === 'preview'" class="preview-mode">
            <div class="preview-content" v-html="renderedMarkdown"></div>
          </div>
        </div>

        <!-- Actions -->
        <div class="editor-actions">
          <button
            type="button"
            @click="saveTopic"
            :disabled="isSaving || !title.trim()"
            class="btn btn-primary"
          >
            {{ isSaving ? 'Saving...' : (topicId ? 'Update Topic' : 'Create Topic') }}
          </button>

          <button
            type="button"
            @click="$router.go(-1)"
            class="btn btn-secondary"
          >
            Cancel
          </button>
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
            <div class="tabs">
              <div class="segmented-control" role="tablist" aria-label="Insert link mode">
                <button
                  type="button"
                  role="tab"
                  :aria-selected="(linkInsertMode === 'manual').toString()"
                  :tabindex="linkInsertMode === 'manual' ? 0 : -1"
                  :class="['segmented-btn','btn','btn-sm', linkInsertMode === 'manual' ? 'btn-primary active' : 'btn-secondary']"
                  @click="linkInsertMode = 'manual'"
                  title="Enter link text and URL manually"
                >Manual</button>
                <button
                  type="button"
                  role="tab"
                  :aria-selected="(linkInsertMode === 'existing').toString()"
                  :tabindex="linkInsertMode === 'existing' ? 0 : -1"
                  :class="['segmented-btn','btn','btn-sm', linkInsertMode === 'existing' ? 'btn-primary active' : 'btn-secondary']"
                  @click="openExistingLinks"
                  title="Choose from existing saved links"
                >Existing</button>
                <button
                  type="button"
                  role="tab"
                  :aria-selected="(linkInsertMode === 'upload').toString()"
                  :tabindex="linkInsertMode === 'upload' ? 0 : -1"
                  :class="['segmented-btn','btn','btn-sm', linkInsertMode === 'upload' ? 'btn-primary active' : 'btn-secondary']"
                  @click="linkInsertMode = 'upload'"
                  title="Upload an image and link to it"
                >Upload Image</button>
              </div>
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
            <div v-else-if="linkInsertMode === 'existing'">
              <div class="form-group">
                <label>Search Links</label>
                <input v-model="linkSearch" type="text" class="form-input" placeholder="Search by title, description, reference, or URL" @input="debouncedFetchLinks">
              </div>
              <div class="resource-list" v-if="availableLinks && availableLinks.length">
                <div 
                  v-for="link in availableLinks" 
                  :key="link.id" 
                  class="resource-item"
                  :class="{ selected: selectedExistingLink && selectedExistingLink.id === link.id }"
                  @click="selectExistingLink(link)"
                >
                  <div class="resource-title">{{ link.title }} <span v-if="link.reference_code" class="muted">({{ link.reference_code }})</span></div>
                  <div class="resource-sub">{{ link.url }}</div>
                </div>
              </div>
              <div class="empty-state" v-else>No links found.</div>
            </div>
            <div v-else>
              <div class="form-group">
                <label>Upload Image (becomes link URL)</label>
                <input type="file" accept="image/*" @change="onLinkUploadSelect" />
              </div>
              <div class="upload-status" v-if="linkUploadMessage">{{ linkUploadMessage }}</div>
              <div class="upload-actions">
                <button class="btn btn-primary" :disabled="linkUploadUploading || !linkUploadFile" @click="uploadLinkImage">
                  {{ linkUploadUploading ? 'Uploading...' : 'Upload & Use as Link' }}
                </button>
              </div>
              <div class="form-group" v-if="linkUrl">
                <label>Resulting URL</label>
                <input v-model="linkUrl" type="url" class="form-input">
              </div>
              <div class="form-group" v-if="linkText === '' && linkUrl">
                <label>Link Text</label>
                <input v-model="linkText" type="text" class="form-input" placeholder="Display text">
              </div>
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
            <div class="tabs">
              <div class="segmented-control" role="tablist" aria-label="Insert image mode">
                <button
                  type="button"
                  role="tab"
                  :aria-selected="(imageInsertMode === 'url').toString()"
                  :tabindex="imageInsertMode === 'url' ? 0 : -1"
                  :class="['segmented-btn','btn','btn-sm', imageInsertMode === 'url' ? 'btn-primary active' : 'btn-secondary']"
                  @click="imageInsertMode = 'url'"
                  title="Provide a direct image URL"
                >By URL</button>
                <button
                  type="button"
                  role="tab"
                  :aria-selected="(imageInsertMode === 'existing').toString()"
                  :tabindex="imageInsertMode === 'existing' ? 0 : -1"
                  :class="['segmented-btn','btn','btn-sm', imageInsertMode === 'existing' ? 'btn-primary active' : 'btn-secondary']"
                  @click="openExistingImages"
                  title="Browse previously uploaded images"
                >Browse</button>
                <button
                  type="button"
                  role="tab"
                  :aria-selected="(imageInsertMode === 'upload').toString()"
                  :tabindex="imageInsertMode === 'upload' ? 0 : -1"
                  :class="['segmented-btn','btn','btn-sm', imageInsertMode === 'upload' ? 'btn-primary active' : 'btn-secondary']"
                  @click="imageInsertMode = 'upload'"
                  title="Upload an image from your computer"
                >Upload</button>
              </div>
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
                <div class="image-grid" v-if="availableImages && availableImages.length">
                  <div 
                    v-for="img in filteredImages" 
                    :key="img.id" 
                    class="image-item" 
                    :class="{ selected: selectedExistingImage && selectedExistingImage.id === img.id }"
                    @click="selectExistingImage(img)"
                  >
                    <img :src="imageDisplayUrl(img)" :alt="img.alt_text || img.filename" @error="handleImageError($event, img)">
                    <div class="image-caption">{{ img.filename }}</div>
                    <div class="image-source-badge">{{ formatImageSource(img.source) }}</div>
                  </div>
                </div>
              <div class="empty-state" v-else>No images found.</div>
            </div>
            <div v-else>
              <div class="form-group">
                <label>Upload Image</label>
                <input type="file" accept="image/*" @change="onImageUploadSelect" />
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
            <div class="form-group">
              <label>Caption (optional)</label>
              <input v-model="imageCaption" type="text" class="form-input" placeholder="Image caption shown below the image">
            </div>
          </div>
          <div class="modal-footer">
            <button @click="insertImage" class="btn btn-primary">Insert Image</button>
            <button @click="showImageModal = false" class="btn btn-secondary">Cancel</button>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script>
import { marked } from 'marked'
import { getImageUrl as getResolvedImageUrl, getRetryImageSrc } from '@/services/imageUrl'
import { API_BASE } from '@/api/base'

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
    },
    readOnly: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      title: this.initialTitle,
      content: this.initialContent,
      frontmatter: this.initialFrontmatter,
      isSaving: false,
      saveSuccess: null,
      showMarkdownCheatsheet: false,
      showImageModal: false,
      showLinkModal: false,
      showTableModal: false,
      editorMode: 'wysiwyg',
      wysiwygUpdateTimeout: null,
      tableRows: 3,
      tableCols: 3,
  imageInsertMode: 'url',
  imageUploadFile: null,
  imageUploadUploading: false,
  imageUploadMessage: '',
  imageUploadPreview: '',
      imageUrl: '',
      imageAlt: '',
      imageCaption: '',
      availableImages: [],
  filteredImages: [],
  imageSearch: '',
      linkInsertMode: 'manual',
  linkUploadFile: null,
  linkUploadUploading: false,
  linkUploadMessage: '',
      linkText: '',
      linkTitle: '',
      linkUrl: '',
  availableLinks: [],
  linkSearch: '',
  _debounceTimer: null,
  variableSlugs: [],
  filteredVariables: [],
  recentVariables: [],
  variableSearch: '',
  selectedVariableSlug: '',
  selectedExistingImage: null,
  selectedExistingLink: null,
  savedWysiwygRange: null
    }
  },
  computed: {
    apiBase() {
      return API_BASE || ''
    },
    apiBaseHost() {
      try {
        if (!this.apiBase) return ''

        if (this.apiBase.startsWith('http')) {
          const url = new URL(this.apiBase)
          if (url.pathname.endsWith('/api')) {
            url.pathname = url.pathname.slice(0, -4) || '/'
          }
          const normalizedPath = url.pathname.replace(/\/+$/, '')
          return normalizedPath ? `${url.origin}${normalizedPath}` : url.origin
        }

        return this.apiBase.replace(/\/api\/?$/, '') || ''
      } catch (_e) {
        return ''
      }
    },
    markdownPreview() {
      if (!this.content) return ''
      // Use marked library if available, otherwise return plain text
      if (typeof marked !== 'undefined') {
        return marked(this.content)
      }
      return this.content.replace(/\n/g, '<br>')
    },
    renderedMarkdown() {
      const content = this.content || ''

      // Custom renderer to handle broken images
      const renderer = new marked.Renderer()

      const escapeAttr = (value) => String(value ?? '')
        .replace(/&/g, '&amp;')
        .replace(/"/g, '&quot;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')

      // Override image rendering to add error handling
      renderer.image = function(...args) {
        let href = ''
        let title = ''
        let text = ''

        // marked v16 passes a single token object; older versions pass (href, title, text)
        if (args.length === 1 && args[0] && typeof args[0] === 'object') {
          const token = args[0]
          href = token.href || ''
          title = token.title || ''
          text = token.text || ''
        } else {
          href = args[0] || ''
          title = args[1] || ''
          text = args[2] || ''
        }

        const safeHref = escapeAttr(href)
        const safeTitle = escapeAttr(title)
        const safeText = escapeAttr(text)

        let out = '<img src="' + safeHref + '" alt="' + safeText + '"'
        if (title) {
          out += ' title="' + safeTitle + '"'
        }

        // Add error handling for broken images
        out += ' onerror="this.style.border=\'2px dashed #ff6b6b\'; this.style.padding=\'10px\'; this.alt=\'❌ Image not found: ' + (safeText || safeHref) + '\'; this.title=\'Click the 🖼️ button to upload this image\'"'
        out += ' onload="this.style.border=\'none\'; this.style.padding=\'0\'"'
        out += '>'

        return out
      }

      let rendered = marked.parse(content, {
        breaks: true,
        gfm: true,
        renderer
      })
      
      // Post-process to add helpful messages for problematic image patterns
      if (content.includes('media/')) {
        rendered += '<div class="image-warning" style="background: #fff3cd; border: 1px solid #ffeaa7; padding: 10px; margin: 10px 0; border-radius: 4px;"><strong>⚠️ Image Display Issue:</strong> This topic contains images with "media/" paths that won\'t display in the editor. Use the 🖼️ button to upload images properly.</div>'
      }
      
      if (content.includes('.emf')) {
        rendered += '<div class="image-warning" style="background: #f8d7da; border: 1px solid #f5c6cb; padding: 10px; margin: 10px 0; border-radius: 4px;"><strong>🚫 Unsupported Format:</strong> This topic contains .emf images which are not web-compatible. Please convert to .png and re-upload using the 🖼️ button.</div>'
      }
      
      if (content.match(/\{width=|{height=/)) {
        rendered += '<div class="image-warning" style="background: #d1ecf1; border: 1px solid #bee5eb; padding: 10px; margin: 10px 0; border-radius: 4px;"><strong>📝 Formatting Note:</strong> This topic contains Pandoc-style attributes that aren\'t displayed in the editor. For size control, use HTML: &lt;img src="/images/file.png" width="500"&gt;</div>'
      }
      
      return rendered
    },
    pageTitle() {
      return this.topicId ? 'Edit Topic' : 'Create a New Topic'
    },
    abbreviatedHtml() {
      const text = this.content || ''
      const shortText = text.length > 200 ? text.substring(0, 200) : text
      return marked(shortText)
    },
    /* True if any field differs from last saved snapshot */
    isDirty() {
      if (this.readOnly || this.isSaving) return false
      if (!this.lastSaved) return false
      return (
        this.title !== this.lastSaved.title ||
        this.content !== this.lastSaved.content ||
        this.frontmatter !== this.lastSaved.frontmatter
      )
    }
  },
  watch: {
    editorMode(newMode) {
      if (newMode === 'wysiwyg') {
        this.$nextTick(() => {
          if (this.$refs.wysiwygEditor) {
            this.$refs.wysiwygEditor.innerHTML = this.renderedMarkdown
          }
        })
      }
    },
    // Remove content->HTML sync in wysiwyg to avoid caret jumping.
    initialContent(newValue) {
      this.content = newValue
    },
    initialTitle(newValue) {
      this.title = newValue
    },
    initialFrontmatter(newValue) {
      this.frontmatter = newValue
    }
  },
  mounted() {
    // Establish initial snapshot after mount
    this.setSnapshot()
    // Warn on tab/window close if there are unsaved edits
    window.addEventListener('beforeunload', this.beforeUnloadHandler)
  this.loadVariables()
  this.loadRecentVariables()
    // Initialize WYSIWYG editor content without creating a reactive loop that resets caret
    if(this.editorMode === 'wysiwyg' && this.$refs.wysiwygEditor){
      this.$refs.wysiwygEditor.innerHTML = this.renderedMarkdown
    }
  },
  unmounted() {
    window.removeEventListener('beforeunload', this.beforeUnloadHandler)
  },
  beforeRouteLeave(to, from, next) {
    if (this.readOnly || !this.isDirty) return next()
    const answer = window.confirm('You have unsaved changes. Leave this page without saving?')
    if (answer) {
      return next()
    }
    next(false)
  },
  methods: {
    openLinkModal() {
      if (this.editorMode === 'wysiwyg') {
        this.captureWysiwygSelection()
      }
      this.showLinkModal = true
    },
    openImageModal() {
      if (this.editorMode === 'wysiwyg') {
        this.captureWysiwygSelection()
      }
      this.showImageModal = true
    },
    captureWysiwygSelection() {
      const editor = this.$refs.wysiwygEditor
      if (!editor) {
        this.savedWysiwygRange = null
        return
      }
      const selection = window.getSelection()
      if (selection && selection.rangeCount > 0) {
        const range = selection.getRangeAt(0)
        if (editor.contains(range.startContainer)) {
          this.savedWysiwygRange = range.cloneRange()
          return
        }
      }
      this.savedWysiwygRange = null
    },
    restoreWysiwygSelection() {
      const editor = this.$refs.wysiwygEditor
      if (!editor || !this.savedWysiwygRange) return false
      editor.focus()
      const selection = window.getSelection()
      if (!selection) return false
      selection.removeAllRanges()
      selection.addRange(this.savedWysiwygRange)
      return true
    },
    async loadVariables(){
      try {
        const res = await fetch('/api/variables')
        if(res.ok){
          const arr = await res.json()
          if(Array.isArray(arr)) {
            this.variableSlugs = arr.map(v=>v.slug).sort()
            this.filteredVariables = this.variableSlugs.slice()
          }
        }
      } catch(e){ /* silent */ }
    },
    filterVariables(){
      const q = this.variableSearch.trim().toLowerCase()
      if(!q){ this.filteredVariables = this.variableSlugs.slice(); return }
      this.filteredVariables = this.variableSlugs.filter(s=>s.toLowerCase().includes(q))
    },
    tokenPreview(slug){
      return `Inserts {{${slug}}}`
    },
    loadRecentVariables(){
      try {
        const raw = localStorage.getItem('recentVariableSlugs')
        if(raw){
          const arr = JSON.parse(raw)
          if(Array.isArray(arr)) this.recentVariables = arr.filter(s=>typeof s==='string')
        }
      } catch(_e){ /* ignore */ }
    },
    pushRecent(slug){
      if(!slug) return
      const set = [slug, ...this.recentVariables.filter(s=>s!==slug)]
      this.recentVariables = set.slice(0,8)
      try { localStorage.setItem('recentVariableSlugs', JSON.stringify(this.recentVariables)) } catch(_e){ }
    },
    handleInsertVariable(){
      if(!this.selectedVariableSlug) return
      const slug = this.selectedVariableSlug
      const token = `{{${slug}}}`
      if(this.editorMode === 'markdown'){
        const ta = this.$refs.markdownEditor
        if(ta && ta.selectionStart != null){
          const start = ta.selectionStart
          const end = ta.selectionEnd
          const before = this.content.slice(0,start)
          const after = this.content.slice(end)
          this.content = before + token + after
          this.$nextTick(()=>{
            ta.focus()
            const pos = start + token.length
            ta.selectionStart = ta.selectionEnd = pos
          })
        } else {
          this.content += token
        }
      } else if(this.editorMode === 'wysiwyg') {
        const el = this.$refs.wysiwygEditor
        if(el){
          const sel = window.getSelection()
          if(sel && sel.rangeCount){
            const range = sel.getRangeAt(0)
            range.deleteContents()
            range.insertNode(document.createTextNode(token))
            range.collapse(false)
            sel.removeAllRanges(); sel.addRange(range)
          } else {
            el.appendChild(document.createTextNode(token))
          }
        }
        this.onWysiwygInput()
      }
  // Track recent before clearing selection
  this.pushRecent(slug)
  this.selectedVariableSlug = ''
    },
    openVariablesAdmin(){
      if(!this.$router) return
      const query = {}
      if(this.topicId) query.topicId = String(this.topicId)
      this.$router.push({ name: 'AdminVariables', query })
    },
    setSnapshot() {
      this.lastSaved = {
        title: this.title,
        content: this.content,
        frontmatter: this.frontmatter
      }
    },
    beforeUnloadHandler(e) {
      if (this.isDirty) {
        e.preventDefault()
        e.returnValue = '' // Required for Chrome to show prompt
      }
    },
    // Existing Links/Image helpers
    debounce(fn, delay = 300) {
      return (...args) => {
        clearTimeout(this._debounceTimer)
        this._debounceTimer = setTimeout(() => fn(...args), delay)
      }
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
      this.debounce(this.fetchLinks, 300)()
    },
    selectExistingLink(link) {
      this.selectedExistingLink = link
      this.linkText = link.title || link.reference_code || 'Link'
      this.linkUrl = link.url
    },
    async openExistingImages() {
      this.imageInsertMode = 'existing'
      await this.fetchImages()
      this.filterImages()
    },
    async fetchImages() {
      try {
        console.log('📥 Fetching images from /api/images')
        const res = await fetch('/api/images')
        if (res.ok) {
          this.availableImages = await res.json()
          this.filteredImages = this.availableImages
          console.log(`✅ Fetched ${this.availableImages.length} images`)
        } else {
          console.error('❌ Failed to fetch images:', res.status)
        }
      } catch (e) { 
        console.error('❌ Failed to fetch images', e) 
      }
    },
    filterImages() {
      const q = (this.imageSearch || '').toLowerCase()
      this.filteredImages = (this.availableImages || []).filter(img => !q || (img.filename || '').toLowerCase().includes(q))
    },
    imageDisplayUrl(img) {
      const resolved = getResolvedImageUrl(img, {
        apiBase: this.apiBase,
        apiBaseHost: this.apiBaseHost
      })
      console.debug(`🖼️ imageDisplayUrl for ${img.filename || 'unknown'}:`, { img, resolved })
      return resolved
    },
    formatImageSource(source) {
      const value = (source || 'local').toLowerCase()
      if (value === 'spaces') return 'Spaces'
      if (value === 'import') return 'Imported'
      return 'Local'
    },
    handleImageError(event, img){
      const element = event?.target
      if (element && img) {
        const currentSrc = element.getAttribute('src') || ''
        const retryResult = getRetryImageSrc(
          currentSrc,
          img,
          element?.dataset?.retryAttempted === '1',
          {
            apiBase: this.apiBase,
            apiBaseHost: this.apiBaseHost
          }
        )

        if (retryResult?.src) {
          if (retryResult.shouldMarkRetried && element?.dataset) {
            element.dataset.retryAttempted = '1'
          }
          setTimeout(() => {
            element.src = retryResult.src
          }, 120)
          return
        }
      }

      const placeholderSvg = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjQiIGhlaWdodD0iNjQiIHZpZXdCb3g9IjAgMCA2NCA2NCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHJlY3Qgd2lkdGg9IjY0IiBoZWlnaHQ9IjY0IiByeD0iMTIiIGZpbGw9IiNGNUY2RjgiIHN0cm9rZT0iI0Q1RDZENSIgc3Ryb2tlLXdpZHRoPSIyIi8+Cjwvc3ZnPgo='
      event.target.src = placeholderSvg
      event.target.style.opacity = '0.5'
      event.target.title = '❌ Image not found'
    },
    selectExistingImage(img) {
      this.selectedExistingImage = img
      this.imageUrl = this.imageDisplayUrl(img)
      this.imageAlt = img.alt_text || img.filename
    },

    onImageUploadSelect(event) {
      const file = event.target.files && event.target.files[0]
      this.imageUploadFile = file || null
      this.imageUploadMessage = file ? `Selected ${file.name}` : ''
    },

    async uploadImageFile() {
      if (!this.imageUploadFile) return
      this.imageUploadUploading = true
      this.imageUploadMessage = 'Uploading...'
      try {
        const formData = new FormData()
        formData.append('image', this.imageUploadFile)
        console.log('📤 Uploading image:', this.imageUploadFile.name)
        const res = await fetch('/api/images/upload', {
          method: 'POST',
          body: formData
        })
        if (!res.ok) throw new Error(`Upload failed: ${res.status}`)
        const uploadData = await res.json()
        console.log('✅ Upload response:', uploadData)
        
        // Refresh the image list to get the new image with proper metadata
        // This ensures we get the complete record from the backend API
        console.log('🔄 Fetching updated image list...')
        await this.fetchImages()
        this.filterImages()
        
        // Find the newly uploaded image by filename (most reliable)
        const uploadedFilename = uploadData.filename
        const newImage = this.availableImages.find(img => img.filename === uploadedFilename)
        console.log('🔍 Found new image:', newImage)
        
        if (newImage) {
          // Use the image from the fetched list (has proper public_url)
          this.imageUrl = newImage.public_url || newImage.file_path || uploadData.public_url
          this.imageAlt = newImage.alt_text || newImage.filename
          this.selectedExistingImage = newImage
          this.imageUploadMessage = '✅ Upload successful. Inserting...'
          console.log('🎯 Set image URL to:', this.imageUrl)
          
          // Auto-insert immediately after successful upload and selection
          this.$nextTick(() => {
            this.restoreWysiwygSelection()
            console.log('🔨 Auto-inserting image...')
            this.insertImage()
          })
        } else {
          // Fallback: use the upload response directly
          this.imageUrl = uploadData.public_url || uploadData.file_path
          this.imageAlt = uploadData.alt_text || uploadData.filename
          this.imageUploadMessage = '✅ Upload successful. Ready to insert.'
          console.log('⚠️ Image not in fetched list, using upload response:', this.imageUrl)
          this.imageInsertMode = 'existing'
        }
      } catch (e) {
        console.error('❌ Upload failed', e)
        this.imageUploadMessage = `❌ Upload failed: ${e.message}`
      } finally {
        this.imageUploadUploading = false
      }
    },

    onLinkUploadSelect(event) {
      const file = event.target.files && event.target.files[0]
      this.linkUploadFile = file || null
      this.linkUploadMessage = file ? `Selected ${file.name}` : ''
    },

    async uploadLinkImage() {
      if (!this.linkUploadFile) return
      this.linkUploadUploading = true
      this.linkUploadMessage = 'Uploading...'
      try {
        const formData = new FormData()
        formData.append('image', this.linkUploadFile)
        const res = await fetch('/api/images/upload', {
          method: 'POST',
          body: formData
        })
        if (!res.ok) throw new Error(`Upload failed: ${res.status}`)
        const data = await res.json()
        // Use uploaded image URL as link target
        this.linkUrl = data.public_url || data.file_path
        if (!this.linkText) {
          this.linkText = data.alt_text || data.filename || 'Image'
        }
        this.linkUploadMessage = '✅ Upload successful. Inserting link...'
        
        // Auto-insert the link immediately after upload
        this.$nextTick(() => {
          this.restoreWysiwygSelection()
          this.insertLink()
        })
      } catch (e) {
        console.error('Upload failed', e)
        this.linkUploadMessage = `❌ Upload failed: ${e.message}`
      } finally {
        this.linkUploadUploading = false
      }
    },
    async saveTopic() {
      if (!this.title.trim()) return
      
      this.isSaving = true
      this.saveSuccess = null
      
      try {
        const payload = {
          title: this.title,
          content: this.content,
          frontmatter: this.frontmatter
        }
        
        let response
        if (this.topicId) {
          // Update existing topic
          response = await fetch(`/api/topics/${this.topicId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
          })
        } else {
          // Create new topic
          response = await fetch('/api/topics/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
          })
        }
        
        if (!response.ok) {
          throw new Error(`Save failed: ${response.status}`)
        }
        
        const result = await response.json()
        
        if (!this.topicId && result.id) {
          // New topic created, emit the ID
          this.$emit('update:topicId', result.id)
        } else {
          // Existing topic updated
          this.$emit('save', result)
        }
        
        this.saveSuccess = this.topicId ? 'Topic updated successfully!' : 'Topic created successfully!'
  // Update snapshot immediately so navigation (manual or automated) won't prompt
  this.setSnapshot()
        
        // Redirect to Review Dashboard after successful save
        setTimeout(() => { 
          this.saveSuccess = null
          if (this.topicId) {
            // For updates, navigate to Review Dashboard
            this.$router.push('/dashboard')
          } else {
            // For new topics, stay on the edit page with the new ID
            // The parent component will handle this via the update:topicId emit
          }
        }, 1500) // Reduced timeout for better UX
        
      } catch (error) {
        console.error('Save error:', error)
        try {
          const { toast } = await import('@/composables/useToast')
          toast.error('Failed to save topic. Please try again.')
        } catch (_e) {
          /* no-op if import fails at runtime */
        }
      } finally {
        this.isSaving = false
      }
    },

    insertMarkdown(before, after) {
      const textarea = this.$refs.markdownEditor
      if (!textarea) return
      
      const start = textarea.selectionStart
      const end = textarea.selectionEnd
      const selectedText = textarea.value.substring(start, end)
      const replacement = before + selectedText + after
      
      textarea.value = textarea.value.substring(0, start) + replacement + textarea.value.substring(end)
      this.content = textarea.value
      
      // Reset cursor position
      const newCursorPos = start + before.length + selectedText.length + after.length
      this.$nextTick(() => {
        textarea.focus()
        textarea.setSelectionRange(newCursorPos, newCursorPos)
      })
    },

    execCommand(command, value = null) {
      if (this.editorMode === 'wysiwyg') {
        document.execCommand(command, false, value)
        this.updateContentFromWysiwyg()
      }
    },

    onWysiwygInput() {
      if (this.wysiwygUpdateTimeout) {
        clearTimeout(this.wysiwygUpdateTimeout)
      }
      this.wysiwygUpdateTimeout = setTimeout(() => {
        this.updateContentFromWysiwyg()
      }, 300)
    },

    insertLink() {
      if (!this.linkText || !this.linkUrl) return
      
      const linkMarkdown = `[${this.linkText}](${this.linkUrl})`
      
      if (this.editorMode === 'markdown') {
        this.insertMarkdown(linkMarkdown, '')
      } else if (this.editorMode === 'wysiwyg') {
        this.restoreWysiwygSelection()
        const editor = this.$refs.wysiwygEditor
        if (editor) {
          const selection = window.getSelection()
          let insertedAtCaret = false

          if (selection && selection.rangeCount > 0) {
            const range = selection.getRangeAt(0)
            if (editor.contains(range.startContainer)) {
              const anchor = document.createElement('a')
              anchor.href = this.linkUrl
              anchor.textContent = this.linkText
              anchor.target = '_blank'
              anchor.rel = 'noopener noreferrer'

              range.deleteContents()
              range.insertNode(anchor)
              range.setStartAfter(anchor)
              range.collapse(true)
              selection.removeAllRanges()
              selection.addRange(range)
              insertedAtCaret = true
            }
          }

          if (!insertedAtCaret) {
            const anchor = document.createElement('a')
            anchor.href = this.linkUrl
            anchor.textContent = this.linkText
            anchor.target = '_blank'
            anchor.rel = 'noopener noreferrer'
            editor.appendChild(anchor)
            editor.appendChild(document.createTextNode(' '))
          }

          this.updateContentFromWysiwyg()
        }
      }
      
      // Reset modal
      this.linkText = ''
      this.linkUrl = ''
      this.selectedExistingLink = null
      this.savedWysiwygRange = null
      this.showLinkModal = false
    },

    insertImage() {
      if (!this.imageUrl) return
      const alt = this.imageAlt || 'Image'
      const caption = (this.imageCaption || '').trim()
      const imageMarkdown = caption
        ? `![${alt}](${this.imageUrl})\n${caption}`
        : `![${alt}](${this.imageUrl})`
      
      if (this.editorMode === 'markdown') {
        this.insertMarkdown(imageMarkdown, '')
      } else if (this.editorMode === 'wysiwyg') {
        this.restoreWysiwygSelection()
        const escapedCaption = caption
          .replace(/&/g, '&amp;')
          .replace(/</g, '&lt;')
          .replace(/>/g, '&gt;')
          .replace(/"/g, '&quot;')
        const imgHtml = caption
          ? `<img src="${this.imageUrl}" alt="${alt}" /><p>${escapedCaption}</p>`
          : `<img src="${this.imageUrl}" alt="${alt}" />`
        document.execCommand('insertHTML', false, imgHtml)
        this.updateContentFromWysiwyg()
      }
      
      // Reset modal
      this.imageUrl = ''
      this.imageAlt = ''
      this.imageCaption = ''
      this.selectedExistingImage = null
      this.savedWysiwygRange = null
      this.imageInsertMode = 'url'
      this.showImageModal = false
    },

    updateContentFromWysiwyg() {
      if (this.$refs.wysiwygEditor) {
        const html = this.$refs.wysiwygEditor.innerHTML
        const md = this.htmlToMarkdown(html)
        if (md !== this.content) {
          this.content = md
        }
      }
    },

    htmlToMarkdown(html) {
      const parser = new DOMParser()
      const doc = parser.parseFromString(html || '', 'text/html')

      const renderChildren = (node) => {
        let out = ''
        node.childNodes.forEach(child => {
          out += renderNode(child)
        })
        return out
      }

      const renderList = (listNode, isOrdered) => {
        let index = 1
        const lines = []
        listNode.childNodes.forEach(child => {
          if (!(child instanceof HTMLElement) || child.tagName.toLowerCase() !== 'li') return
          const item = renderChildren(child).replace(/\n+/g, ' ').trim()
          if (!item) return
          const marker = isOrdered ? `${index}. ` : '- '
          lines.push(`${marker}${item}`)
          index += 1
        })
        return lines.join('\n') + '\n\n'
      }

      const renderNode = (node) => {
        if (node.nodeType === Node.TEXT_NODE) {
          return node.textContent || ''
        }

        if (!(node instanceof HTMLElement)) return ''

        const tag = node.tagName.toLowerCase()

        if (tag === 'br') return '\n'
        if (tag === 'h1') return `# ${renderChildren(node).trim()}\n\n`
        if (tag === 'h2') return `## ${renderChildren(node).trim()}\n\n`
        if (tag === 'h3') return `### ${renderChildren(node).trim()}\n\n`
        if (tag === 'strong' || tag === 'b') return `**${renderChildren(node)}**`
        if (tag === 'em' || tag === 'i') return `*${renderChildren(node)}*`
        if (tag === 'code') return `\`${renderChildren(node).replace(/\n/g, ' ').trim()}\``
        if (tag === 'a') {
          const href = node.getAttribute('href') || ''
          const text = renderChildren(node).trim() || href
          return href ? `[${text}](${href})` : text
        }
        if (tag === 'img') {
          const src = node.getAttribute('src') || ''
          const alt = node.getAttribute('alt') || 'Image'
          return src ? `![${alt}](${src})` : ''
        }
        if (tag === 'ul') return renderList(node, false)
        if (tag === 'ol') return renderList(node, true)
        if (tag === 'li') return `${renderChildren(node).trim()}\n`
        if (tag === 'p' || tag === 'div') return `${renderChildren(node).trim()}\n\n`

        return renderChildren(node)
      }

      return renderChildren(doc.body)
        .replace(/\u00a0/g, ' ')
        .replace(/[ \t]+\n/g, '\n')
        .replace(/\n{3,}/g, '\n\n')
        .trim()
    },

    async handleWysiwygPaste(event) {
      const clipboard = event.clipboardData
      if (!clipboard) return

      const items = Array.from(clipboard.items || [])
      const imageItem = items.find(item => (item.type || '').startsWith('image/'))

      if (imageItem) {
        event.preventDefault()

        const imageFile = imageItem.getAsFile()
        if (!imageFile) return

        const mimeType = imageFile.type || 'image/png'
        const extByMime = {
          'image/png': '.png',
          'image/jpeg': '.jpg',
          'image/jpg': '.jpg',
          'image/gif': '.gif',
          'image/webp': '.webp',
          'image/svg+xml': '.svg'
        }
        const ext = extByMime[mimeType] || '.png'
        const generatedName = `pasted_image_${Date.now()}${ext}`

        try {
          const formData = new FormData()
          formData.append('image', imageFile, generatedName)

          const res = await fetch('/api/images/upload', {
            method: 'POST',
            body: formData
          })
          if (!res.ok) throw new Error(`Upload failed: ${res.status}`)

          const uploaded = await res.json()
          const src = uploaded.public_url || uploaded.file_path
          if (!src) throw new Error('Upload succeeded but no image URL returned')

          const editor = this.$refs.wysiwygEditor
          if (editor) {
            const selection = window.getSelection()
            let insertedAtCaret = false

            if (selection && selection.rangeCount > 0) {
              const range = selection.getRangeAt(0)
              if (editor.contains(range.startContainer)) {
                const imageNode = document.createElement('img')
                imageNode.src = src
                imageNode.alt = uploaded.alt_text || generatedName

                range.deleteContents()
                range.insertNode(imageNode)

                const spacer = document.createTextNode(' ')
                imageNode.after(spacer)
                range.setStartAfter(spacer)
                range.collapse(true)
                selection.removeAllRanges()
                selection.addRange(range)
                insertedAtCaret = true
              }
            }

            if (!insertedAtCaret) {
              const imageNode = document.createElement('img')
              imageNode.src = src
              imageNode.alt = uploaded.alt_text || generatedName
              editor.appendChild(imageNode)
              editor.appendChild(document.createTextNode(' '))
            }

            this.updateContentFromWysiwyg()
          }
          return
        } catch (e) {
          console.error('Image paste upload failed', e)
        }
      }

      // Fallback: plain text paste handling
      event.preventDefault()
      const text = clipboard.getData('text/plain')
      document.execCommand('insertText', false, text)
    },

    handleWysiwygKeydown(event) {
      // Handle keyboard shortcuts
      if (event.ctrlKey || event.metaKey) {
        switch (event.key) {
          case 'b':
            event.preventDefault()
            this.execCommand('bold')
            break
          case 'i':
            event.preventDefault()
            this.execCommand('italic')
            break
        }
      }
    }
  }
}
</script>

<!-- Remove all duplicate and misplaced JS and style code above this line. 
     All JS logic should be inside the <script> block above, and only one <style> block below. -->

<style>
.topic-editor {
  padding: 1rem;
}

/* Variable insertion UI */
.variable-insert { display:flex; gap:.4rem; align-items:center; margin-top:.4rem; flex-wrap:wrap; }
.variable-insert select { padding:.25rem .4rem; font-size:.7rem; }
.var-insert-label { font-size:.6rem; text-transform:uppercase; letter-spacing:.5px; color:#475569; }

/* Editor mode segmented control */

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
  border-left: 4px solid #205493;
  border-radius: .75rem;
  padding: 1rem;
  margin-bottom: 1.5rem;
  color: #495057;
  font-size: 0.95rem;
  line-height: 1.5;
}

/* Form styling */
.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #495057;
  font-size: 14px;
}

.form-input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  font-size: 16px;
  line-height: 1.5;
  box-sizing: border-box;
  background: white;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.form-input:focus {
  outline: none;
  border-color: #205493;
  box-shadow: 0 0 0 2px rgba(32, 84, 147, 0.1);
}

.title-input {
  font-weight: 500;
}

/* Editor content styling */
.markdown-textarea {
  width: 100%;
  min-height: 400px;
  padding: 1.25rem;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  font-family: 'Courier New', 'Monaco', 'Menlo', monospace;
  font-size: 14px;
  line-height: 1.6;
  background: white;
  resize: vertical;
  box-sizing: border-box;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.markdown-textarea:focus {
  outline: none;
  border-color: #205493;
  box-shadow: 0 0 0 2px rgba(32, 84, 147, 0.1);
}

.wysiwyg-content {
  width: 100%;
  min-height: 400px;
  padding: 1.25rem;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
  font-size: 14px;
  line-height: 1.6;
  background: white;
  overflow-y: auto;
  cursor: text;
  box-sizing: border-box;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}
/* Visual paragraph separation (mirrors published KB CSS) */
.wysiwyg-content p { margin: 0 0 1rem 0; line-height: 1.7; }
.wysiwyg-content p:last-child { margin-bottom: 0; }

.wysiwyg-content:focus {
  outline: none;
  border-color: #205493;
  box-shadow: 0 0 0 2px rgba(32, 84, 147, 0.1);
}

/* Preview area (when user selects Preview mode) */
.preview-mode .preview-content p { margin: 0 0 1rem 0; line-height: 1.7; }
.preview-mode .preview-content p:last-child { margin-bottom: 0; }

/* Editor actions styling */
.editor-actions {
  /* margin-top: 2rem; */
  padding-top: 1.5rem;
  border-top: 1px solid #e9ecef;
  display: flex;
  gap: 0.75rem;
  align-items: center;
}
/* Simple resource picker styles */
.tabs { display:flex; gap:.5rem; margin-bottom: .75rem; }
/* Use global .btn styles for tab buttons */
.mode-btn { font-size: 0.8rem; }

.resource-list { max-height: 260px; overflow:auto; border:1px solid #eee; border-radius:6px; }
.resource-item { padding:.5rem .75rem; border-bottom:1px solid #f1f3f5; cursor:pointer; }
.resource-item:hover { background:#f8f9fa; }
.resource-item.selected {
  border-color: var(--primary-deep-teal);
  background: var(--extended-sky-blue);
  box-shadow: 0 2px 6px rgba(28, 107, 128, 0.15);
}
.resource-title { font-weight:600; color:#333; }
.resource-sub { font-size:.85rem; color:#666; }
.muted { color:#667085; font-weight:400; font-size:.9em; }
.image-grid { display:grid; grid-template-columns: repeat(auto-fill, minmax(120px, 1fr)); gap:.75rem; max-height:320px; overflow:auto; }
.image-item { border:1px solid #eee; border-radius:6px; padding:.5rem; cursor:pointer; text-align:center; }
.image-item.selected {
  border-color: var(--primary-deep-teal);
  background: var(--extended-sky-blue);
  box-shadow: 0 2px 8px rgba(28, 107, 128, 0.15);
}
.image-item img { max-width:100%; height:80px; object-fit:cover; display:block; margin:0 auto .5rem; }
.image-caption { font-size:.8rem; color:#555; word-break: break-all; }
.image-source-badge {
  display:inline-block;
  margin-top:.35rem;
  padding:.1rem .35rem;
  border-radius:999px;
  font-size:.65rem;
  text-transform:uppercase;
  letter-spacing:.3px;
  color:#475569;
  background:#f1f5f9;
}

/* Title input styling */
.title-label {
  display: block;
  margin-bottom: 1.5rem;
  font-weight: 600;
  color: #495057;
}

.title-label input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  font-size: 16px;
  line-height: 1.5;
  box-sizing: border-box;
  margin-top: 0.5rem;
  background: white;
}

.title-label input:focus {
  outline: none;
  border-color: #205493;
  box-shadow: 0 0 0 2px rgba(0, 122, 204, 0.1);
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

/* Save section */
.save-section {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.75rem;
  margin-bottom: 2rem;
}

/* Remove local global button override; use shared .btn styles from assets/style.css */

/* Save success message */
.save-success-message {
  background: #d4edda;
  border: 1px solid #c3e6cb;
  border-radius: 4px;
  padding: 0.5rem 0.75rem;
  color: #155724;
  font-size: 0.9rem;
  animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
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

/* Editor layout styles */
.editor-layout {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

/* Content section styles */
.content-section {
  display: flex;
  flex-direction: column;
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.content-label {
  font-weight: 600;
  color: #495057;
}

.cheatsheet-link {
  color: #205493;
  text-decoration: none;
  font-size: 0.875rem;
}

.cheatsheet-link:hover {
  text-decoration: underline;
}

/* Preview section styles */
.preview-section {
  display: flex;
  flex-direction: column;
}

/* Frontmatter section styles */
.frontmatter-section {
  display: flex;
  flex-direction: column;
  margin-bottom: 2rem;
}

.frontmatter-label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #495057;
}

.frontmatter-textarea {
  width: 100%;
  min-height: 140px;
  padding: 0.75rem;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.4;
  resize: vertical;
  box-sizing: border-box;
}

.frontmatter-textarea:focus {
  outline: none;
  border-color: #205493;
  box-shadow: 0 0 0 2px rgba(0, 122, 204, 0.1);
}

/* Responsive design for frontmatter */
@media (min-width: 768px) {
  .frontmatter-section {
    max-width: 50%;
  }
}

@media (max-width: 767px) {
  .frontmatter-section {
    width: 100%;
  }
}

/* Content toolbar styles */
.content-toolbar {
  display: flex;
  gap: 0.75rem;
  padding: 0.75rem;
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  margin-bottom: 0.5rem;
  align-items: center;
  flex-wrap: wrap;
}

.toolbar-group {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.toolbar-separator {
  width: 1px;
  height: 24px;
  background: #dee2e6;
  margin: 0 0.25rem;
}

.toolbar-btn {
  padding: 0.5rem 0.75rem;
  background: white;
  color: #495057;
  border: 1px solid #dee2e6;
  border-radius: 3px;
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.toolbar-btn:hover {
  background: #e9ecef;
  color: #212529;
  border-color: #adb5bd;
}

.toolbar-btn:active {
  background: #dee2e6;
  color: #000;
}

.toolbar-btn.active {
  background: #205493;
  color: white;
  border-color: #205493;
}

.mode-btn {
  font-size: 0.8rem;
  padding: 0.4rem 0.6rem;
}

/* Dropdown styles */
.dropdown {
  position: relative;
  display: inline-block;
}

.dropdown-btn {
  position: relative;
}

.dropdown-content {
  display: none;
  position: absolute;
  top: 100%;
  left: 0;
  background: white;
  min-width: 180px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  border: 1px solid #dee2e6;
  border-radius: 4px;
  z-index: 100;
  margin-top: 2px;
}

.dropdown:hover .dropdown-content {
  display: block;
}

.dropdown-item {
  display: block;
  width: 100%;
  padding: 0.5rem 0.75rem;
  background: none;
  border: none;
  text-align: left;
  cursor: pointer;
  font-size: 0.875rem;
  color: #495057;
  transition: background-color 0.2s ease;
}

.dropdown-item:hover {
  background: #f8f9fa;
}

.dropdown-item:first-child {
  border-radius: 4px 4px 0 0;
}

.dropdown-item:last-child {
  border-radius: 0 0 4px 4px;
}

/* Content textarea styles */
.content-textarea {
  width: 100%;
  min-height: 300px;
  padding: 1.25rem;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 14px;
  line-height: 1.5;
  resize: vertical;
  box-sizing: border-box;
}

.content-textarea:focus {
  outline: none;
  border-color: #205493;
  box-shadow: 0 0 0 2px rgba(0, 122, 204, 0.1);
}

/* WYSIWYG editor styles */
.wysiwyg-textarea {
  width: 100%;
  min-height: 300px;
  padding: 1.25rem;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
  font-size: 14px;
  line-height: 1.6;
  background: white;
  overflow-y: auto;
  cursor: text;
  box-sizing: border-box;
}

.wysiwyg-textarea:focus {
  outline: none;
  border-color: #205493;
  box-shadow: 0 0 0 2px rgba(0, 122, 204, 0.1);
}

.wysiwyg-textarea h1,
.wysiwyg-textarea h2,
.wysiwyg-textarea h3,
.wysiwyg-textarea h4,
.wysiwyg-textarea h5 {
  margin-top: 1.5rem;
  margin-bottom: 0.5rem;
  font-weight: 600;
}

.wysiwyg-textarea p {
  margin-bottom: 1rem;
}

.wysiwyg-textarea code {
  background: #f8f9fa;
  padding: 0.2rem 0.4rem;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
  font-size: 0.9em;
}

.wysiwyg-textarea blockquote {
  border-left: 4px solid #dee2e6;
  padding-left: 1rem;
  margin: 1rem 0;
  color: #6c757d;
}

.wysiwyg-textarea table {
  border-collapse: collapse;
  width: 100%;
  margin: 1rem 0;
}

.wysiwyg-textarea th,
.wysiwyg-textarea td {
  border: 1px solid #dee2e6;
  padding: 0.5rem;
  text-align: left;
}

.wysiwyg-textarea th {
  background: #f8f9fa;
  font-weight: 600;
}

.wysiwyg-textarea img {
  max-width: 100%;
  height: auto;
  border-radius: 4px;
  margin: 0.5rem 0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* Modal overlay styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(2px);
}

.modal-content {
  background: white;
  border-radius: 8px;
  max-width: 90vw;
  max-height: 85vh;
  min-width: 500px;
  overflow-y: auto;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
  position: relative;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #dee2e6;
  background: #f8f9fa;
  border-radius: 8px 8px 0 0;
}

.modal-header h3 {
  margin: 0;
  color: #495057;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #6c757d;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.2s ease;
}

.close-btn:hover {
  color: #495057;
  background: rgba(0, 0, 0, 0.1);
}

.modal-body {
  padding: 1.5rem;
  overflow-y: auto;
  flex: 1;
}

/* Image modal styles */
.image-mode-tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.tab-btn {
  padding: 0.5rem 1rem;
  background: #f8f9fa;
  color: #495057;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
  transition: all 0.2s ease;
}

.tab-btn:hover {
  background: #e9ecef;
  color: #212529;
}

.tab-btn.active {
  background: #205493;
  color: white;
  border-color: #205493;
  font-weight: 600;
}

.image-upload, .image-url-input-container, .existing-images {
  margin-top: 1rem;
}

.file-input {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  margin-bottom: 0.5rem;
}

.file-preview {
  margin-top: 1rem;
  padding: 1rem;
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 4px;
}

.selected-file {
  margin-bottom: 1rem;
  font-weight: 500;
  color: #495057;
}

.help-text {
  margin: 0;
  color: #6c757d;
  font-size: 0.875rem;
}

.image-url-input {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  margin-bottom: 0.5rem;
}

.images-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 1rem;
}

.image-item {
  border: 1px solid #dee2e6;
  border-radius: 4px;
  padding: 0.5rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.image-item:hover {
  border-color: #205493;
  background: #f8f9fa;
}

.image-item img {
  width: 100%;
  height: 100px;
  object-fit: cover;
  border-radius: 3px;
}

.image-item .image-name {
  margin-top: 0.5rem;
  font-size: 0.875rem;
  text-align: center;
  word-break: break-word;
}

.no-images {
  text-align: center;
  color: #6c757d;
  padding: 2rem;
}

/* Link modal styles */
.link-mode-tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.manual-section,
.existing-links {
  margin-top: 1.5rem;
}

.link-input {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  margin-bottom: 0.5rem;
}

.link-url-input {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  margin-bottom: 0.5rem;
}

.links-list {
  max-height: 300px;
  overflow-y: auto;
}

.link-item {
  border: 1px solid #dee2e6;
  border-radius: 4px;
  padding: 1rem;
  margin-bottom: 0.5rem;
  cursor: pointer;
  transition: all 0.2s ease;
  background: white;
}

.link-item:hover {
  border-color: #205493;
  background: #f8f9fa;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.link-title {
  font-weight: bold;
  margin-bottom: 0.25rem;
  color: #495057;
}

.link-url {
  color: #205493;
  font-size: 0.875rem;
  margin-bottom: 0.25rem;
  word-break: break-all;
}

.link-type {
  font-size: 0.75rem;
  color: #6c757d;
  text-transform: uppercase;
  background: #f8f9fa;
  padding: 0.2rem 0.4rem;
  border-radius: 2px;
  display: inline-block;
}

.no-links {
  text-align: center;
  color: #6c757d;
  padding: 2rem;
}

/* Button styles */
.btn-primary {
  background: #205493;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.875rem;
  margin-right: 0.5rem;
  margin-bottom: 0.5rem;
}

.btn-primary:hover {
  background: #174a7e;
}

.btn-primary:disabled {
  background: #6c757d;
  cursor: not-allowed;
}

/* Table modal styles */
.table-creator {
  max-width: 600px;
}

.table-size-controls {
  margin-bottom: 1.5rem;
}

.table-size-controls label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #495057;
}

.size-slider {
  width: 100%;
  margin-bottom: 1rem;
}

.table-preview {
  margin-bottom: 1.5rem;
}

.table-preview h4 {
  margin-bottom: 0.75rem;
  color: #495057;
}

.table-grid {
  border: 1px solid #dee2e6;
  border-radius: 4px;
  overflow: hidden;
  background: white;
}

.table-row {
  display: flex;
}

.table-cell {
  flex: 1;
  padding: 0.5rem;
  border-right: 1px solid #dee2e6;
  border-bottom: 1px solid #dee2e6;
  font-size: 0.875rem;
  min-height: 40px;
  display: flex;
  align-items: center;
}

.table-cell:last-child {
  border-right: none;
}

.table-row:last-child .table-cell {
  border-bottom: none;
}

.table-cell.header {
  background: #f8f9fa;
  font-weight: 600;
  color: #495057;
}

.table-actions {
  display: flex;
  gap: 0.75rem;
  justify-content: flex-end;
}

.btn-secondary {
  background: #6c757d;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.875rem;
  margin-left: 0.5rem;
}

.btn-secondary:hover {
  background: #545b62;
}
</style>