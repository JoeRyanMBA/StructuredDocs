
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
          </div>
        </div>

        <!-- Editor Mode Toggle -->
        <div class="editor-mode-toggle">
          <button 
            @click="editorMode = 'markdown'" 
            :class="{ active: editorMode === 'markdown' }"
            class="mode-btn"
          >
            📝 Markdown
          </button>
          <button 
            @click="editorMode = 'wysiwyg'" 
            :class="{ active: editorMode === 'wysiwyg' }"
            class="mode-btn"
          >
            📄 WYSIWYG
          </button>
          <button 
            @click="editorMode = 'preview'" 
            :class="{ active: editorMode === 'preview' }"
            class="mode-btn"
          >
            👁️ Preview
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
              <button @click="insertMarkdown('- ', '')" class="toolbar-btn">• List</button>
              <button @click="showLinkModal = true" class="toolbar-btn">🔗 Link</button>
              <button @click="showImageModal = true" class="toolbar-btn">🖼️ Image</button>
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
              <button @click="execCommand('insertUnorderedList')" class="toolbar-btn">• List</button>
              <button @click="showLinkModal = true" class="toolbar-btn">🔗 Link</button>
              <button @click="showImageModal = true" class="toolbar-btn">🖼️ Image</button>
            </div>
            <div 
              ref="wysiwygEditor"
              @input="onWysiwygInput"
              contenteditable="true" 
              class="wysiwyg-content"
              :innerHTML="renderedMarkdown"
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
            @click="saveTopic" 
            :disabled="isSaving || !title.trim()"
            class="btn btn-primary"
          >
            {{ isSaving ? 'Saving...' : (topicId ? 'Update Topic' : 'Create Topic') }}
          </button>
          
          <button 
            @click="$router.go(-1)" 
            class="btn btn-secondary"
          >
            Cancel
          </button>
        </div>
      </div>

      <!-- Link Modal -->
      <div v-if="showLinkModal" class="modal-overlay" @click="showLinkModal = false">
        <div class="modal-content" @click.stop>
          <div class="modal-header">
            <h3>Insert Link</h3>
            <button @click="showLinkModal = false" class="close-btn">&times;</button>
          </div>
          <div class="modal-body">
            <div class="form-group">
              <label>Link Text</label>
              <input v-model="linkText" type="text" class="form-input" placeholder="Display text">
            </div>
            <div class="form-group">
              <label>URL</label>
              <input v-model="linkUrl" type="url" class="form-input" placeholder="https://example.com">
            </div>
          </div>
          <div class="modal-footer">
            <button @click="insertLink" class="btn btn-primary">Insert Link</button>
            <button @click="showLinkModal = false" class="btn btn-secondary">Cancel</button>
          </div>
        </div>
      </div>

      <!-- Image Modal -->
      <div v-if="showImageModal" class="modal-overlay" @click="showImageModal = false">
        <div class="modal-content" @click.stop>
          <div class="modal-header">
            <h3>Insert Image</h3>
            <button @click="showImageModal = false" class="close-btn">&times;</button>
          </div>
          <div class="modal-body">
            <div class="form-group">
              <label>Image URL</label>
              <input v-model="imageUrl" type="url" class="form-input" placeholder="https://example.com/image.jpg">
            </div>
            <div class="form-group">
              <label>Alt Text</label>
              <input v-model="imageAlt" type="text" class="form-input" placeholder="Description of image">
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
      selectedImageFile: null,
      imageUrl: '',
      imageAlt: '',
      availableImages: [],
      linkInsertMode: 'manual',
      linkText: '',
      linkTitle: '',
      linkUrl: '',
      availableLinks: []
    }
  },
  computed: {
    markdownPreview() {
      if (!this.content) return ''
      // Use marked library if available, otherwise return plain text
      if (typeof marked !== 'undefined') {
        return marked(this.content)
      }
      return this.content.replace(/\n/g, '<br>')
    },
    renderedMarkdown() {
      return marked(this.content || '')
    },
    pageTitle() {
      return this.topicId ? 'Edit Topic' : 'Create a New Topic'
    },
    abbreviatedHtml() {
      const text = this.content || ''
      const shortText = text.length > 200 ? text.substring(0, 200) : text
      return marked(shortText)
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
    content(newContent) {
      if (this.editorMode === 'wysiwyg' && this.$refs.wysiwygEditor) {
        const currentHtml = this.$refs.wysiwygEditor.innerHTML
        const expectedHtml = marked(newContent || '')
        const currentMarkdown = this.htmlToMarkdown(currentHtml)
        if (currentMarkdown !== newContent) {
          this.$refs.wysiwygEditor.innerHTML = expectedHtml
        }
      }
    },
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
  methods: {
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
        alert('Failed to save topic. Please try again.')
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
        this.execCommand('createLink', this.linkUrl)
      }
      
      // Reset modal
      this.linkText = ''
      this.linkUrl = ''
      this.showLinkModal = false
    },

    insertImage() {
      if (!this.imageUrl) return
      
      const imageMarkdown = `![${this.imageAlt || 'Image'}](${this.imageUrl})`
      
      if (this.editorMode === 'markdown') {
        this.insertMarkdown(imageMarkdown, '')
      }
      
      // Reset modal
      this.imageUrl = ''
      this.imageAlt = ''
      this.showImageModal = false
    },

    updateContentFromWysiwyg() {
      if (this.$refs.wysiwygEditor) {
        const html = this.$refs.wysiwygEditor.innerHTML
        this.content = this.htmlToMarkdown(html)
      }
    },

    htmlToMarkdown(html) {
      // Basic HTML to Markdown conversion
      return html
        .replace(/<h1[^>]*>/gi, '# ')
        .replace(/<\/h1>/gi, '\n\n')
        .replace(/<h2[^>]*>/gi, '## ')
        .replace(/<\/h2>/gi, '\n\n')
        .replace(/<h3[^>]*>/gi, '### ')
        .replace(/<\/h3>/gi, '\n\n')
        .replace(/<strong[^>]*>|<b[^>]*>/gi, '**')
        .replace(/<\/strong>|<\/b>/gi, '**')
        .replace(/<em[^>]*>|<i[^>]*>/gi, '*')
        .replace(/<\/em>|<\/i>/gi, '*')
        .replace(/<code[^>]*>/gi, '`')
        .replace(/<\/code>/gi, '`')
        .replace(/<p[^>]*>/gi, '')
        .replace(/<\/p>/gi, '\n\n')
        .replace(/<br[^>]*>/gi, '\n')
        .replace(/<div[^>]*>/gi, '')
        .replace(/<\/div>/gi, '\n')
        .replace(/&nbsp;/gi, ' ')
        .replace(/&amp;/gi, '&')
        .replace(/&lt;/gi, '<')
        .replace(/&gt;/gi, '>')
        .trim()
    },

    handleWysiwygPaste(event) {
      // Basic paste handling
      event.preventDefault()
      const text = event.clipboardData.getData('text/plain')
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
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  font-size: 14px;
  line-height: 1.6;
  background: white;
  overflow-y: auto;
  cursor: text;
  box-sizing: border-box;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.wysiwyg-content:focus {
  outline: none;
  border-color: #205493;
  box-shadow: 0 0 0 2px rgba(32, 84, 147, 0.1);
}

/* Editor actions styling */
.editor-actions {
  /* margin-top: 2rem; */
  padding-top: 1.5rem;
  border-top: 1px solid #e9ecef;
  display: flex;
  gap: 0.75rem;
  align-items: center;
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

/* Save button */
button {
  padding: 0.75rem 1.5rem;
  background: #205493;
  color: white;
  border: none;
  cursor: pointer;
  border-radius: 4px;
  margin-right: 0.75rem;
  margin-bottom: 0.5rem;
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
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
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