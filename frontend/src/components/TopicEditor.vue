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
    <div class="editor-layout">
      <!-- Content Editor with Toolbar -->
      <div class="content-section">
        <div class="content-header">
          <label class="content-label">Content</label>
          <a href="#" @click.prevent="showMarkdownCheatsheet = true" class="cheatsheet-link">
            (Markdown Cheat Sheet)
          </a>
        </div>
        
        <!-- Content Toolbar -->
        <div class="content-toolbar">
          <!-- Editor Mode Toggle -->
          <div class="toolbar-group">
            <button 
              @click="editorMode = 'markdown'" 
              :class="['toolbar-btn', 'mode-btn', { active: editorMode === 'markdown' }]" 
              title="Markdown Mode"
            >
              📝 Markdown
            </button>
            <button 
              @click="editorMode = 'wysiwyg'" 
              :class="['toolbar-btn', 'mode-btn', { active: editorMode === 'wysiwyg' }]" 
              title="WYSIWYG Mode"
            >
              👁️ Visual
            </button>
          </div>
          
          <div class="toolbar-separator"></div>
          
          <!-- Headings -->
          <div class="toolbar-group">
            <div class="dropdown">
              <button class="toolbar-btn dropdown-btn" title="Insert Heading">
                📄 Heading ▾
              </button>
              <div class="dropdown-content">
                <button @click="insertHeading(1)" class="dropdown-item">H1 - Main Heading</button>
                <button @click="insertHeading(2)" class="dropdown-item">H2 - Section</button>
                <button @click="insertHeading(3)" class="dropdown-item">H3 - Subsection</button>
                <button @click="insertHeading(4)" class="dropdown-item">H4 - Sub-subsection</button>
                <button @click="insertHeading(5)" class="dropdown-item">H5 - Minor Heading</button>
              </div>
            </div>
          </div>
          
          <!-- Text Formatting -->
          <div class="toolbar-group">
            <button @click="insertMarkdown('**', '**')" class="toolbar-btn" title="Bold">
              <strong>B</strong>
            </button>
            <button @click="insertMarkdown('*', '*')" class="toolbar-btn" title="Italic">
              <em>I</em>
            </button>
            <button @click="insertMarkdown('`', '`')" class="toolbar-btn" title="Code">
              &lt;/&gt;
            </button>
          </div>
          
          <div class="toolbar-separator"></div>
          
          <!-- Lists -->
          <div class="toolbar-group">
            <button @click="insertList('bullet')" class="toolbar-btn" title="Bulleted List">
              • List
            </button>
            <button @click="insertList('numbered')" class="toolbar-btn" title="Numbered List">
              1. List
            </button>
          </div>
          
          <div class="toolbar-separator"></div>
          
          <!-- Insert Elements -->
          <div class="toolbar-group">
            <button @click="showImagePicker" class="toolbar-btn" title="Insert Image">
              🖼️ Image
            </button>
            <button @click="showLinkPicker" class="toolbar-btn" title="Insert Link">
              🔗 Link
            </button>
            <button @click="showTableModal = true" class="toolbar-btn" title="Insert Table">
              📊 Table
            </button>
          </div>
        </div>
        
        <!-- Content Input Area -->
        <div v-if="editorMode === 'markdown'" class="markdown-editor">
          <textarea
            ref="contentTextarea"
            v-model="content"
            rows="15"
            placeholder="Enter topic content (Markdown)"
            class="content-textarea"
          ></textarea>
        </div>
        
        <div v-else class="wysiwyg-editor">
          <div
            ref="wysiwygEditor"
            contenteditable="true"
            @input="updateContentFromWysiwyg"
            @paste="handleWysiwygPaste"
            @keydown="handleWysiwygKeydown"
            class="wysiwyg-textarea"
          ></div>
        </div>
      </div>

      <!-- Preview Section (only for Markdown mode) -->
      <div v-if="editorMode === 'markdown'" class="preview-section">
        <label class="preview-label">Preview</label>
        <div class="preview-pane">
          <div class="preview" v-html="renderedMarkdown"></div>
        </div>
      </div>

      <!-- Frontmatter Section -->
      <div class="frontmatter-section">
        <label class="frontmatter-label">Frontmatter</label>
        <textarea
          v-model="frontmatter"
          rows="7"
          placeholder="Enter YAML frontmatter"
          class="frontmatter-textarea"
        ></textarea>
      </div>
    </div>

    <!-- Save Button and Success Message -->
    <div class="save-section">
      <button @click="save" :disabled="isSaving">
        <span v-if="isSaving">Saving…</span>
        <span v-else>Save</span>
      </button>
      
      <!-- Local success message -->
      <div v-if="saveSuccess" class="save-success-message">
        {{ saveSuccess }}
      </div>
    </div>

    <!-- Markdown Cheatsheet Modal -->
    <div v-if="showMarkdownCheatsheet" class="modal-overlay" @click="showMarkdownCheatsheet = false">
      <div class="modal-content cheatsheet-modal" @click.stop>
        <div class="modal-header">
          <h3>📝 Markdown Quick Reference</h3>
          <button class="btn-close" @click="showMarkdownCheatsheet = false">✕</button>
        </div>
        <div class="modal-body">
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
            <div class="cheatsheet-section">
              <strong>Tables:</strong>
              <pre>| Header 1 | Header 2 |
|----------|----------|
| Cell 1   | Cell 2   |</pre>
            </div>
            <div class="cheatsheet-section">
              <strong>Blockquotes:</strong>
              <pre>> This is a quote
>> Nested quote</pre>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Image Picker Modal -->
    <div v-if="showImageModal" class="modal-overlay" @click="showImageModal = false">
      <div class="modal-content image-modal" @click.stop>
        <div class="modal-header">
          <h3>🖼️ Insert Image</h3>
          <button class="btn-close" @click="showImageModal = false">✕</button>
        </div>
        <div class="modal-body">
          <div class="image-picker">
            <div class="image-options">
              <button @click="imageInsertMode = 'upload'" :class="['tab-btn', { active: imageInsertMode === 'upload' }]">
                📁 Upload New
              </button>
              <button @click="imageInsertMode = 'existing'" :class="['tab-btn', { active: imageInsertMode === 'existing' }]">
                🖼️ Use Existing
              </button>
              <button @click="imageInsertMode = 'url'" :class="['tab-btn', { active: imageInsertMode === 'url' }]">
                🌐 From URL
              </button>
            </div>
            
            <!-- Upload New Image -->
            <div v-if="imageInsertMode === 'upload'" class="upload-section">
              <input type="file" @change="onImageFileSelected" accept="image/*" class="file-input">
              <p class="help-text">Select an image file to upload</p>
              <div v-if="selectedImageFile" class="file-preview">
                <p class="selected-file">Selected: {{ selectedImageFile.name }}</p>
                <button @click="uploadAndInsertImage" class="btn-primary">Upload and Insert Image</button>
                <button @click="clearSelectedImage" class="btn-secondary">Cancel</button>
              </div>
            </div>
            
            <!-- Use Existing Images -->
            <div v-if="imageInsertMode === 'existing'" class="existing-images">
              <div class="images-grid">
                <div 
                  v-for="image in availableImages" 
                  :key="image.id"
                  class="image-item"
                  @click="insertImageReference(image)"
                >
                  <img :src="image.public_url" :alt="image.filename" class="image-thumbnail">
                  <span class="image-name">{{ image.filename }}</span>
                </div>
              </div>
              <p v-if="availableImages.length === 0" class="no-images">No images available. Upload some images first.</p>
            </div>
            
            <!-- From URL -->
            <div v-if="imageInsertMode === 'url'" class="url-section">
              <input 
                v-model="imageUrl" 
                type="url" 
                placeholder="https://example.com/image.jpg"
                class="url-input"
              >
              <input 
                v-model="imageAlt" 
                type="text" 
                placeholder="Image description (alt text)"
                class="alt-input"
              >
              <button @click="insertImageFromUrl" class="btn-primary">Insert Image</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Link Picker Modal -->
    <div v-if="showLinkModal" class="modal-overlay" @click="showLinkModal = false">
      <div class="modal-content link-modal" @click.stop>
        <div class="modal-header">
          <h3>🔗 Insert Link</h3>
          <button class="btn-close" @click="showLinkModal = false">✕</button>
        </div>
        <div class="modal-body">
          <div class="link-picker">
            <div class="link-options">
              <button @click="linkInsertMode = 'manual'" :class="['tab-btn', { active: linkInsertMode === 'manual' }]">
                ✏️ Manual Entry
              </button>
              <button @click="linkInsertMode = 'existing'" :class="['tab-btn', { active: linkInsertMode === 'existing' }]">
                📋 Use Existing
              </button>
            </div>
            
            <!-- Manual Link Entry -->
            <div v-if="linkInsertMode === 'manual'" class="manual-section">
              <input 
                v-model="linkText" 
                type="text" 
                placeholder="Link text"
                class="link-text-input"
              >
              <input 
                v-model="linkUrl" 
                type="url" 
                placeholder="https://example.com"
                class="link-url-input"
              >
              <button @click="insertManualLink" class="btn-primary">Insert Link</button>
            </div>
            
            <!-- Use Existing Links -->
            <div v-if="linkInsertMode === 'existing'" class="existing-links">
              <div class="links-list">
                <div 
                  v-for="link in availableLinks" 
                  :key="link.id"
                  class="link-item"
                  @click="insertLinkReference(link)"
                >
                  <div class="link-title">{{ link.title }}</div>
                  <div class="link-url">{{ link.url }}</div>
                  <div class="link-type">{{ link.link_type }}</div>
                </div>
              </div>
              <p v-if="availableLinks.length === 0" class="no-links">No links available. Create some links first.</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Table Creation Modal -->
    <div v-if="showTableModal" class="modal-overlay" @click="showTableModal = false">
      <div class="modal-content table-modal" @click.stop>
        <div class="modal-header">
          <h3>📊 Insert Table</h3>
          <button class="btn-close" @click="showTableModal = false">✕</button>
        </div>
        <div class="modal-body">
          <div class="table-creator">
            <div class="table-size-controls">
              <label>Columns: {{ tableCols }}</label>
              <input 
                v-model.number="tableCols" 
                type="range" 
                min="2" 
                max="10" 
                class="size-slider"
              >
              
              <label>Rows: {{ tableRows }}</label>
              <input 
                v-model.number="tableRows" 
                type="range" 
                min="2" 
                max="20" 
                class="size-slider"
              >
            </div>
            
            <div class="table-preview">
              <h4>Preview ({{ tableCols }} × {{ tableRows }}):</h4>
              <div class="table-grid">
                <div 
                  v-for="row in tableRows" 
                  :key="'row-' + row"
                  class="table-row"
                >
                  <div 
                    v-for="col in tableCols" 
                    :key="'col-' + col"
                    class="table-cell"
                    :class="{ header: row === 1 }"
                  >
                    {{ row === 1 ? `Header ${col}` : `Cell ${row}-${col}` }}
                  </div>
                </div>
              </div>
            </div>
            
            <div class="table-actions">
              <button @click="insertTable" class="btn-primary">Insert Table</button>
              <button @click="showTableModal = false" class="btn-secondary">Cancel</button>
            </div>
          </div>
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
      isSaving: false,
      
      // Save success message
      saveSuccess: null,

      // Toolbar and modal states
      showMarkdownCheatsheet: false,
      showImageModal: false,
      showLinkModal: false,
      showTableModal: false,
      
      // Editor mode
      editorMode: 'wysiwyg', // 'markdown' or 'wysiwyg'
      
      // WYSIWYG editor timeout
      wysiwygUpdateTimeout: null,
      
      // Table creation
      tableRows: 3,
      tableCols: 3,
      
      // Image modal data
      imageInsertMode: 'url', // 'upload', 'existing', 'url' - default to URL for now
      selectedImageFile: null,
      imageUrl: '',
      imageAlt: '',
      availableImages: [],
      
      // Link modal data
      linkInsertMode: 'manual', // 'manual', 'existing'
      linkText: '',
      linkTitle: '',
      linkUrl: '',
      availableLinks: []
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

  watch: {
    editorMode(newMode) {
      if (newMode === 'wysiwyg') {
        // Initialize WYSIWYG editor with current markdown content
        this.$nextTick(() => {
          if (this.$refs.wysiwygEditor) {
            this.$refs.wysiwygEditor.innerHTML = this.renderedMarkdown
          }
        })
      }
    },

    content(newContent) {
      console.log('🔄 Content watcher triggered:', newContent ? newContent.substring(0, 100) + '...' : 'empty')
      // Only update WYSIWYG editor if we're in WYSIWYG mode and the content change didn't come from the WYSIWYG editor itself
      if (this.editorMode === 'wysiwyg' && this.$refs.wysiwygEditor) {
        const currentHtml = this.$refs.wysiwygEditor.innerHTML
        const expectedHtml = marked(newContent || '')
        
        console.log('🔍 Checking WYSIWYG sync:')
        console.log('Current HTML:', currentHtml.substring(0, 200))
        console.log('Expected HTML:', expectedHtml.substring(0, 200))
        
        // Only update if the HTML is significantly different to avoid cursor jumping
        // But be more aggressive about updating after a save operation
        const currentMarkdown = this.htmlToMarkdown(currentHtml)
        if (currentMarkdown !== newContent) {
          console.log('📝 Updating WYSIWYG editor with new content')
          this.$refs.wysiwygEditor.innerHTML = expectedHtml
        } else {
          console.log('✅ WYSIWYG editor already in sync')
        }
      }
    },

    // Watch for prop changes and update internal state
    initialContent(newValue) {
      console.log('📥 Initial content prop changed:', newValue ? newValue.substring(0, 100) + '...' : 'empty')
      this.content = newValue
    },

    initialTitle(newValue) {
      console.log('📥 Initial title prop changed:', newValue)
      this.title = newValue
    },

    initialFrontmatter(newValue) {
      console.log('📥 Initial frontmatter prop changed:', newValue ? newValue.substring(0, 100) + '...' : 'empty')
      this.frontmatter = newValue
    }
  },

  methods: {
    updateFrontmatterModified() {
      const user = JSON.parse(localStorage.getItem('user') || '{}')
      const now = new Date().toLocaleString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        timeZoneName: 'short'
      })
      
      // If there's no frontmatter, create it
      if (!this.frontmatter.trim()) {
        this.frontmatter = `---
title: "${this.title}"
author: "${user.name || user.username || 'Unknown User'}"
created: "${now}"
modified: "${now}"
status: "draft"
---`
        return
      }
      
      // Update existing frontmatter
      let frontmatter = this.frontmatter
      
      // Update title if it exists in frontmatter
      if (frontmatter.includes('title:')) {
        frontmatter = frontmatter.replace(/^title:\s*.*$/m, `title: "${this.title}"`)
      }
      
      // Update or add modified field
      if (frontmatter.includes('modified:')) {
        frontmatter = frontmatter.replace(/^modified:\s*.*$/m, `modified: "${now}"`)
      } else {
        // Add modified field after created if it exists, otherwise before the closing ---
        if (frontmatter.includes('created:')) {
          frontmatter = frontmatter.replace(/^(created:\s*.*$)/m, `$1\nmodified: "${now}"`)
        } else {
          // Add before the closing --- or at the end if no closing ---
          if (frontmatter.includes('---') && frontmatter.lastIndexOf('---') > 0) {
            const lastDashIndex = frontmatter.lastIndexOf('---')
            frontmatter = frontmatter.substring(0, lastDashIndex) + `modified: "${now}"\n` + frontmatter.substring(lastDashIndex)
          } else {
            frontmatter += `\nmodified: "${now}"`
          }
        }
      }
      
      this.frontmatter = frontmatter
    },

    async save() {
      this.isSaving = true

      // Update frontmatter before saving
      this.updateFrontmatterModified()

      const payload = {
        title: this.title,
        content: this.content,
        frontmatter: this.frontmatter
      }
      
      console.log('💾 Saving topic with payload:', payload)
      
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
        
        if (!res.ok) {
          throw new Error(`HTTP ${res.status}: ${res.statusText}`)
        }
        
        const data = await res.json()
        console.log('✅ Saved successfully:', data)

        // Show local success message
        this.saveSuccess = this.topicId ? '✅ Topic updated successfully!' : '✅ Topic created successfully!'
        setTimeout(() => {
          this.saveSuccess = null
        }, 3000)

        if (!this.topicId) {
          // For new topics, clear the form after successful save
          this.clearForm()
          this.$emit('update:topicId', data.id)
        } else {
          // For existing topics, update our internal state with the saved data
          // This ensures the editor reflects what was actually saved
          console.log('📝 Updating editor state with saved data')
          console.log('Before update - content:', this.content ? this.content.substring(0, 100) + '...' : 'empty')
          console.log('Server response - content:', data.content ? data.content.substring(0, 100) + '...' : 'empty')
          
          this.title = data.title || this.title
          this.content = data.content || this.content  
          this.frontmatter = data.frontmatter || this.frontmatter
          
          console.log('After update - content:', this.content ? this.content.substring(0, 100) + '...' : 'empty')
          
          // If we're in WYSIWYG mode, update the editor content with the saved content
          if (this.editorMode === 'wysiwyg' && this.$refs.wysiwygEditor) {
            console.log('🎨 Forcing WYSIWYG update after save')
            this.$nextTick(() => {
              const renderedHtml = this.renderedMarkdown
              console.log('Rendered HTML for WYSIWYG:', renderedHtml.substring(0, 200) + '...')
              this.$refs.wysiwygEditor.innerHTML = renderedHtml
            })
          }
          
          this.$emit('save', data)
        }
      } catch (err) {
        console.error('❌ Save error:', err)
        alert('Failed to save topic: ' + err.message)
      } finally {
        this.isSaving = false
      }
    },

    clearForm() {
      this.title = ''
      this.content = ''
      this.frontmatter = ''
    },

    // Toolbar methods
    insertMarkdown(before, after = '') {
      if (this.editorMode === 'markdown') {
        const textarea = this.$refs.contentTextarea
        if (!textarea) return

        const start = textarea.selectionStart
        const end = textarea.selectionEnd
        const selectedText = this.content.substring(start, end)
        const newText = before + selectedText + after
        
        this.content = this.content.substring(0, start) + newText + this.content.substring(end)
        
        // Focus textarea and set cursor position
        this.$nextTick(() => {
          textarea.focus()
          const newCursorPos = start + before.length + selectedText.length
          textarea.setSelectionRange(newCursorPos, newCursorPos)
        })
      } else {
        // WYSIWYG mode - handle different formatting types
        if (!this.$refs.wysiwygEditor) return
        
        this.$refs.wysiwygEditor.focus()
        
        // Handle different markdown patterns
        if (before === '**' && after === '**') {
          document.execCommand('bold')
        } else if (before === '*' && after === '*') {
          document.execCommand('italic')
        } else if (before === '`' && after === '`') {
          // For code, we'll wrap selection in <code> tags
          const selection = window.getSelection()
          if (selection.rangeCount > 0) {
            const range = selection.getRangeAt(0)
            const selectedText = range.toString()
            if (selectedText) {
              const codeElement = document.createElement('code')
              codeElement.textContent = selectedText
              range.deleteContents()
              range.insertNode(codeElement)
              selection.removeAllRanges()
            }
          }
        } else {
          // For other markdown like headings, insert as text and update
          const markdownText = before + after
          this.content += '\n' + markdownText
          
          // Update the WYSIWYG editor
          this.$nextTick(() => {
            if (this.$refs.wysiwygEditor) {
              this.$refs.wysiwygEditor.innerHTML = this.renderedMarkdown
            }
          })
        }
        
        // Update markdown content after formatting
        setTimeout(() => {
          const htmlContent = this.$refs.wysiwygEditor.innerHTML
          const newMarkdown = this.htmlToMarkdown(htmlContent)
          if (newMarkdown !== this.content) {
            this.content = newMarkdown
          }
        }, 100)
      }
    },

    // Enhanced method for heading insertion
    insertHeading(level) {
      if (this.editorMode === 'markdown') {
        const prefix = '#'.repeat(level) + ' '
        this.insertMarkdown(prefix, '')
      } else {
        // WYSIWYG mode - use formatBlock command
        if (!this.$refs.wysiwygEditor) return
        
        this.$refs.wysiwygEditor.focus()
        document.execCommand('formatBlock', false, `h${level}`)
        
        // Update markdown content
        setTimeout(() => {
          const htmlContent = this.$refs.wysiwygEditor.innerHTML
          const newMarkdown = this.htmlToMarkdown(htmlContent)
          if (newMarkdown !== this.content) {
            this.content = newMarkdown
          }
        }, 100)
      }
    },

    // Modal methods
    showMarkdownCheatsheetModal() {
      this.showMarkdownCheatsheet = true
    },

    closeMarkdownCheatsheet() {
      this.showMarkdownCheatsheet = false
    },

    showImagePicker() {
      this.showImageModal = true
      // Only load available images if we need the existing images tab
      // For now, we'll skip this since the backend endpoint isn't working
      // this.loadAvailableImages()
    },

    closeImageModal() {
      this.showImageModal = false
      this.selectedImageFile = null
      this.imageUrl = ''
      this.imageAlt = ''
    },

    showLinkPicker() {
      this.showLinkModal = true
      this.loadAvailableLinks()
    },

    closeLinkModal() {
      this.showLinkModal = false
      this.linkText = ''
      this.linkUrl = ''
    },

    // Image handling methods
    async loadAvailableImages() {
      try {
        const response = await fetch('/api/images')
        if (response.ok) {
          this.availableImages = await response.json()
        }
      } catch (error) {
        console.error('Error loading images:', error)
      }
    },

    onImageFileSelected(event) {
      this.selectedImageFile = event.target.files[0]
    },

    clearSelectedImage() {
      this.selectedImageFile = null
      // Reset the file input
      const fileInput = document.querySelector('.file-input')
      if (fileInput) {
        fileInput.value = ''
      }
    },

    async uploadAndInsertImage() {
      if (!this.selectedImageFile) return

      const formData = new FormData()
      formData.append('image', this.selectedImageFile)

      try {
        const response = await fetch('/api/images/upload', {
          method: 'POST',
          body: formData
        })

        if (response.ok) {
          const imageData = await response.json()
          this.insertImageReference(imageData)
          this.showImageModal = false
          this.clearSelectedImage()
        } else {
          alert('Failed to upload image')
        }
      } catch (error) {
        console.error('Error uploading image:', error)
        alert('Error uploading image')
      }
    },

    insertImageFromUrl() {
      if (!this.imageUrl.trim()) return

      const altText = this.imageAlt.trim() || 'Image'
      // Ensure the URL is properly formatted
      let imageUrl = this.imageUrl.trim()
      
      // If it's a relative path starting with just a filename, make it an absolute path
      if (!imageUrl.startsWith('http') && !imageUrl.startsWith('/') && !imageUrl.startsWith('./') && !imageUrl.startsWith('../')) {
        // If it looks like just a filename, prepend with /images/
        imageUrl = `/images/${imageUrl}`
      }
      
      const imageMarkdown = `![${altText}](${imageUrl})`
      this.insertMarkdown(imageMarkdown)
      this.showImageModal = false
      
      // Clear the form
      this.imageUrl = ''
      this.imageAlt = ''
    },

    insertImageReference(image) {
      // Ensure the image path is correct - should start with /images/ for proper serving
      let imagePath = image.file_path || image.public_url
      if (imagePath && !imagePath.startsWith('/images/') && !imagePath.startsWith('http')) {
        // If it's just a filename, prepend with /images/
        if (!imagePath.includes('/')) {
          imagePath = `/images/${imagePath}`
        }
      }
      
      const imageMarkdown = `![${image.alt_text || image.filename}](${imagePath})`
      this.insertMarkdown(imageMarkdown)
      this.showImageModal = false
    },

    // Link handling methods
    async loadAvailableLinks() {
      try {
        const response = await fetch('/api/links')
        if (response.ok) {
          this.availableLinks = await response.json()
        }
      } catch (error) {
        console.error('Error loading links:', error)
      }
    },

    insertManualLink() {
      if (!this.linkUrl.trim()) return

      const linkText = this.linkText.trim() || this.linkUrl
      const linkMarkdown = `[${linkText}](${this.linkUrl})`
      this.insertMarkdown(linkMarkdown)
      this.showLinkModal = false
      
      // Clear the form
      this.linkText = ''
      this.linkUrl = ''
    },

    insertLinkReference(link) {
      const linkMarkdown = `[${link.title}](${link.url})`
      this.insertMarkdown(linkMarkdown)
      this.showLinkModal = false
    },

    // Table creation methods
    insertTable() {
      let tableMarkdown = ''
      
      // Create header row
      const headerCells = Array.from({ length: this.tableCols }, (_, i) => `Header ${i + 1}`).join(' | ')
      tableMarkdown += `| ${headerCells} |\n`
      
      // Create separator row
      const separatorCells = Array.from({ length: this.tableCols }, () => '---').join(' | ')
      tableMarkdown += `| ${separatorCells} |\n`
      
      // Create data rows
      for (let row = 2; row <= this.tableRows; row++) {
        const dataCells = Array.from({ length: this.tableCols }, (_, i) => `Cell ${row}-${i + 1}`).join(' | ')
        tableMarkdown += `| ${dataCells} |\n`
      }
      
      this.insertMarkdown('\n' + tableMarkdown + '\n')
      this.showTableModal = false
    },

    // List insertion methods
    insertList(type) {
      if (this.editorMode === 'markdown') {
        const textarea = this.$refs.contentTextarea
        if (!textarea) return

        const start = textarea.selectionStart
        const end = textarea.selectionEnd
        const selectedText = this.content.substring(start, end)
        
        let listMarkdown = ''
        if (selectedText.trim()) {
          // Convert selected text to list items
          const lines = selectedText.split('\n').filter(line => line.trim())
          listMarkdown = lines.map((line, index) => {
            const prefix = type === 'bullet' ? '- ' : `${index + 1}. `
            return prefix + line.trim()
          }).join('\n')
        } else {
          // Insert empty list item
          const prefix = type === 'bullet' ? '- ' : '1. '
          listMarkdown = prefix + 'List item'
        }
        
        this.content = this.content.substring(0, start) + listMarkdown + this.content.substring(end)
        
        // Focus textarea and set cursor position
        this.$nextTick(() => {
          textarea.focus()
          const newCursorPos = start + listMarkdown.length
          textarea.setSelectionRange(newCursorPos, newCursorPos)
        })
      } else {
        // WYSIWYG mode - use browser commands for proper list handling
        if (!this.$refs.wysiwygEditor) return
        
        this.$refs.wysiwygEditor.focus()
        
        if (type === 'bullet') {
          document.execCommand('insertUnorderedList')
        } else {
          document.execCommand('insertOrderedList')
        }
        
        // Update the markdown content after a short delay
        setTimeout(() => {
          const htmlContent = this.$refs.wysiwygEditor.innerHTML
          const newMarkdown = this.htmlToMarkdown(htmlContent)
          if (newMarkdown !== this.content) {
            this.content = newMarkdown
          }
        }, 100)
      }
    },

    // WYSIWYG editor methods
    updateContentFromWysiwyg(event) {
      // Store cursor position before updating content
      const selection = window.getSelection()
      const range = selection.rangeCount > 0 ? selection.getRangeAt(0) : null
      const cursorOffset = range ? range.startOffset : 0
      const cursorContainer = range ? range.startContainer : null
      
      // Use a longer debounced approach to avoid interfering with undo/redo
      clearTimeout(this.wysiwygUpdateTimeout)
      this.wysiwygUpdateTimeout = setTimeout(() => {
        const htmlContent = event.target.innerHTML
        const newMarkdown = this.htmlToMarkdown(htmlContent)
        
        // Debug logging
        console.log('WYSIWYG HTML content:', htmlContent)
        console.log('Converted markdown:', newMarkdown)
        console.log('Current content:', this.content)
        
        // Only update if content actually changed to preserve undo stack
        if (newMarkdown !== this.content) {
          console.log('Content changed, updating markdown')
          this.content = newMarkdown
        } else {
          console.log('Content unchanged, skipping update')
        }
        
        // Restore cursor position
        this.$nextTick(() => {
          if (cursorContainer && range && this.$refs.wysiwygEditor) {
            try {
              const newSelection = window.getSelection()
              const newRange = document.createRange()
              
              // Try to restore cursor to the same position
              if (this.$refs.wysiwygEditor.contains(cursorContainer)) {
                newRange.setStart(cursorContainer, Math.min(cursorOffset, cursorContainer.textContent?.length || 0))
                newRange.collapse(true)
                newSelection.removeAllRanges()
                newSelection.addRange(newRange)
              }
            } catch (e) {
              // If cursor restoration fails, just focus the editor
              this.$refs.wysiwygEditor.focus()
            }
          }
        })
      }, 1000) // Longer delay to avoid interfering with typing and undo/redo
    },

    handleWysiwygKeydown(event) {
      // Handle keyboard shortcuts
      if (event.ctrlKey || event.metaKey) {
        switch (event.key) {
          case 'z':
            if (event.shiftKey) {
              // Ctrl+Shift+Z or Cmd+Shift+Z = Redo
              event.preventDefault()
              event.stopPropagation()
              document.execCommand('redo')
              return false
            } else {
              // Ctrl+Z or Cmd+Z = Undo
              event.preventDefault()
              event.stopPropagation()
              document.execCommand('undo')
              return false
            }
          case 'y':
            // Ctrl+Y = Redo (Windows style)
            event.preventDefault()
            event.stopPropagation()
            document.execCommand('redo')
            return false
          case 'b':
            // Ctrl+B = Bold
            event.preventDefault()
            event.stopPropagation()
            document.execCommand('bold')
            return false
          case 'i':
            // Ctrl+I = Italic
            event.preventDefault()
            event.stopPropagation()
            document.execCommand('italic')
            return false
        }
      }
    },

    handleWysiwygPaste(event) {
      event.preventDefault()
      const text = event.clipboardData.getData('text/plain')
      document.execCommand('insertText', false, text)
    },

    htmlToMarkdown(html) {
      // Basic HTML to Markdown conversion
      let markdown = html
        .replace(/<h1[^>]*>(.*?)<\/h1>/gi, '# $1\n')
        .replace(/<h2[^>]*>(.*?)<\/h2>/gi, '## $1\n')
        .replace(/<h3[^>]*>(.*?)<\/h3>/gi, '### $1\n')
        .replace(/<h4[^>]*>(.*?)<\/h4>/gi, '#### $1\n')
        .replace(/<h5[^>]*>(.*?)<\/h5>/gi, '##### $1\n')
        .replace(/<h6[^>]*>(.*?)<\/h6>/gi, '###### $1\n')
        .replace(/<strong[^>]*>(.*?)<\/strong>/gi, '**$1**')
        .replace(/<b[^>]*>(.*?)<\/b>/gi, '**$1**')
        .replace(/<em[^>]*>(.*?)<\/em>/gi, '*$1*')
        .replace(/<i[^>]*>(.*?)<\/i>/gi, '*$1*')
        .replace(/<code[^>]*>(.*?)<\/code>/gi, '`$1`')
        // Handle images - convert <img> tags back to markdown
        .replace(/<img[^>]*src="([^"]*)"[^>]*alt="([^"]*)"[^>]*>/gi, '![$2]($1)')
        .replace(/<img[^>]*alt="([^"]*)"[^>]*src="([^"]*)"[^>]*>/gi, '![$1]($2)')
        .replace(/<img[^>]*src="([^"]*)"[^>]*>/gi, '![]($1)')
        .replace(/<ul[^>]*>(.*?)<\/ul>/gis, (match, content) => {
          return content.replace(/<li[^>]*>(.*?)<\/li>/gi, '- $1\n')
        })
        .replace(/<ol[^>]*>(.*?)<\/ol>/gis, (match, content) => {
          let counter = 1
          return content.replace(/<li[^>]*>(.*?)<\/li>/gi, () => `${counter++}. $1\n`)
        })
        .replace(/<p[^>]*>(.*?)<\/p>/gi, '$1\n\n')
        .replace(/<br\s*\/?>/gi, '\n')
        .replace(/<div[^>]*>(.*?)<\/div>/gi, '$1\n')
        .replace(/&nbsp;/gi, ' ')
        .replace(/&amp;/gi, '&')
        .replace(/&lt;/gi, '<')
        .replace(/&gt;/gi, '>')
        .replace(/\n{3,}/g, '\n\n') // Remove excessive line breaks
        .trim()

      return markdown
    }
  },

  beforeUnmount() {
    // Clean up timeout to prevent memory leaks
    if (this.wysiwygUpdateTimeout) {
      clearTimeout(this.wysiwygUpdateTimeout)
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

/* Save section */
.save-section {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.5rem;
  margin-bottom: 2rem;
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
  color: #007acc;
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
  border-color: #007acc;
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
  gap: 0.5rem;
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
  gap: 0.25rem;
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
  background: #007acc;
  color: white;
  border-color: #007acc;
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
  padding: 1rem;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 14px;
  line-height: 1.5;
  resize: vertical;
}

.content-textarea:focus {
  outline: none;
  border-color: #007acc;
  box-shadow: 0 0 0 2px rgba(0, 122, 204, 0.1);
}

/* WYSIWYG editor styles */
.wysiwyg-textarea {
  width: 100%;
  min-height: 300px;
  padding: 1rem;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  font-size: 14px;
  line-height: 1.6;
  background: white;
  overflow-y: auto;
  cursor: text;
}

.wysiwyg-textarea:focus {
  outline: none;
  border-color: #007acc;
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
  background: #007acc;
  color: white;
  border-color: #007acc;
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
  border-color: #007acc;
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
  border-color: #007acc;
  background: #f8f9fa;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.link-title {
  font-weight: bold;
  margin-bottom: 0.25rem;
  color: #495057;
}

.link-url {
  color: #007acc;
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
  background: #007acc;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.875rem;
}

.btn-primary:hover {
  background: #005a9c;
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
  gap: 0.5rem;
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
}

.btn-secondary:hover {
  background: #545b62;
}
</style>