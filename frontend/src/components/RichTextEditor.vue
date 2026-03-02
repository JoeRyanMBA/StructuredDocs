<template>
  <div class="rte-wysiwyg-editor">
    <div class="rte-toolbar">
      <button type="button" @click="exec('bold')" class="toolbar-btn">𝐁 Bold</button>
      <button type="button" @click="exec('italic')" class="toolbar-btn">𝐼 Italic</button>
      <button type="button" @click="exec('formatBlock', 'code')" class="toolbar-btn">⟨⟩ Code</button>
      <button type="button" @click="exec('formatBlock', 'h2')" class="toolbar-btn">𝐇𝟐 Header</button>
      <button type="button" @click="exec('formatBlock', 'h3')" class="toolbar-btn">𝐇𝟑 Header</button>
      <button type="button" @click="exec('insertUnorderedList')" class="toolbar-btn">• List</button>
      <button type="button" @click="exec('insertOrderedList')" class="toolbar-btn">1. List</button>
      <button type="button" @click="openLinkDialog" class="toolbar-btn">🔗 Link</button>
      <button type="button" @click="openImgDialog" class="toolbar-btn">🖼 Image</button>
      <slot name="toolbar-extra" />
    </div>
    <div v-if="linkDialogVisible" class="rte-inline-dialog">
      <span class="rte-dialog-label">URL:</span>
      <input v-model="dialogUrl" type="url" placeholder="https://…" class="rte-dialog-input" @keydown.enter="confirmLink" @keydown.esc="cancelDialog" ref="linkInput" />
      <button type="button" class="rte-dialog-btn" @click="confirmLink">Insert</button>
      <button type="button" class="rte-dialog-btn rte-dialog-cancel" @click="cancelDialog">✕</button>
    </div>
    <div v-if="imgDialogVisible" class="rte-inline-dialog">
      <span class="rte-dialog-label">URL:</span>
      <input v-model="dialogUrl" type="url" placeholder="https://…" class="rte-dialog-input" @keydown.enter="confirmImg" @keydown.esc="cancelDialog" ref="imgInput" />
      <span class="rte-dialog-label">Alt:</span>
      <input v-model="dialogAlt" type="text" placeholder="Alt text" class="rte-dialog-input rte-dialog-alt" @keydown.enter="confirmImg" @keydown.esc="cancelDialog" />
      <button type="button" class="rte-dialog-btn" @click="confirmImg">Insert</button>
      <button type="button" class="rte-dialog-btn rte-dialog-cancel" @click="cancelDialog">✕</button>
    </div>
    <div
      ref="editorEl"
      contenteditable="true"
      class="wysiwyg-content"
      @input="onInput"
      @paste="onPaste"
      @keydown="onKeydown"
    ></div>
  </div>
</template>

<script>
export default {
  name: 'RichTextEditor',
  props: {
    modelValue: { type: String, default: '' },
  },
  emits: ['update:modelValue', 'paste'],
  data() {
    return {
      linkDialogVisible: false,
      imgDialogVisible: false,
      dialogUrl: '',
      dialogAlt: '',
    }
  },
  watch: {
    modelValue(newVal) {
      const el = this.$refs.editorEl
      if (el && el.innerHTML !== newVal) {
        el.innerHTML = newVal || ''
      }
    },
  },
  mounted() {
    if (this.$refs.editorEl) {
      this.$refs.editorEl.innerHTML = this.modelValue || ''
    }
  },
  methods: {
    exec(command, value = null) {
      this.$refs.editorEl?.focus()
      document.execCommand(command, false, value)
      this.emitUpdate()
    },
    onInput() {
      if (this._inputTimer) clearTimeout(this._inputTimer)
      this._inputTimer = setTimeout(() => this.emitUpdate(), 300)
    },
    onPaste(event) {
      this.$emit('paste', event)
    },
    onKeydown(event) {
      if (event.ctrlKey || event.metaKey) {
        if (event.key === 'b') { event.preventDefault(); this.exec('bold') }
        else if (event.key === 'i') { event.preventDefault(); this.exec('italic') }
      }
    },
    emitUpdate() {
      this.$emit('update:modelValue', this.$refs.editorEl?.innerHTML || '')
    },
    // --- Public API (callable via $refs) ---
    saveSelection() {
      const el = this.$refs.editorEl
      if (!el) { this._savedRange = null; return }
      const sel = window.getSelection()
      if (sel && sel.rangeCount > 0) {
        const range = sel.getRangeAt(0)
        if (el.contains(range.startContainer)) {
          this._savedRange = range.cloneRange()
          return
        }
      }
      this._savedRange = null
    },
    restoreSelection() {
      const el = this.$refs.editorEl
      if (!el || !this._savedRange) return false
      el.focus()
      const sel = window.getSelection()
      if (!sel) return false
      sel.removeAllRanges()
      sel.addRange(this._savedRange)
      return true
    },
    setContent(html) {
      if (this.$refs.editorEl) {
        this.$refs.editorEl.innerHTML = html || ''
      }
    },
    getContent() {
      return this.$refs.editorEl?.innerHTML || ''
    },
    getEditorEl() {
      return this.$refs.editorEl
    },
    focus() {
      this.$refs.editorEl?.focus()
    },
    openLinkDialog() {
      this.saveSelection()
      this.dialogUrl = ''
      this.imgDialogVisible = false
      this.linkDialogVisible = true
      this.$nextTick(() => this.$refs.linkInput?.focus())
    },
    openImgDialog() {
      this.dialogUrl = ''
      this.dialogAlt = ''
      this.linkDialogVisible = false
      this.imgDialogVisible = true
      this.$nextTick(() => this.$refs.imgInput?.focus())
    },
    confirmLink() {
      const url = this.dialogUrl.trim()
      if (!url) { this.cancelDialog(); return }
      this.restoreSelection()
      document.execCommand('createLink', false, url)
      this.emitUpdate()
      this.cancelDialog()
    },
    confirmImg() {
      const url = this.dialogUrl.trim()
      if (!url) { this.cancelDialog(); return }
      document.execCommand('insertImage', false, url)
      if (this.dialogAlt.trim()) {
        const el = this.$refs.editorEl
        if (el) {
          const imgs = el.querySelectorAll('img')
          const last = imgs[imgs.length - 1]
          if (last && !last.alt) last.alt = this.dialogAlt.trim()
        }
      }
      this.emitUpdate()
      this.cancelDialog()
    },
    cancelDialog() {
      this.linkDialogVisible = false
      this.imgDialogVisible = false
      this.dialogUrl = ''
      this.dialogAlt = ''
    },
  },
}
</script>

<style>
.rte-wysiwyg-editor {
  height: 100%;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

.rte-toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem;
  padding: 0.5rem;
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-bottom: none;
  border-radius: 4px 4px 0 0;
}

/* wysiwyg-content styles (mirrors TopicEditor for standalone use) */
.wysiwyg-content {
  width: 100%;
  min-height: 0;
  height: 100%;
  padding: 1.25rem;
  border: 1px solid #dee2e6;
  border-radius: 0 0 4px 4px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
  font-size: 14px;
  line-height: 1.6;
  background: white;
  overflow-y: auto;
  cursor: text;
  box-sizing: border-box;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}
.wysiwyg-content p { margin: 0 0 1rem 0; line-height: 1.7; }
.wysiwyg-content p:last-child { margin-bottom: 0; }
.wysiwyg-content:focus {
  outline: none;
  border-color: #205493;
  box-shadow: 0 0 0 2px rgba(32, 84, 147, 0.1);
}

/* toolbar-btn styles (mirrors TopicEditor global styles for self-contained use) */
.rte-toolbar .toolbar-btn {
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
.rte-toolbar .toolbar-btn:hover {
  background: #e9ecef;
  color: #212529;
  border-color: #adb5bd;
}
.rte-toolbar .toolbar-btn:active {
  background: #dee2e6;
  color: #000;
}

.rte-inline-dialog {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.35rem;
  padding: 0.4rem 0.5rem;
  background: #f0f4ff;
  border: 1px solid #c5d3f0;
  border-top: none;
  border-bottom: none;
}
.rte-dialog-label {
  font-size: 0.8rem;
  color: #495057;
  white-space: nowrap;
}
.rte-dialog-input {
  flex: 1;
  min-width: 160px;
  padding: 0.25rem 0.5rem;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 0.82rem;
}
.rte-dialog-input:focus { outline: none; border-color: #205493; }
.rte-dialog-alt { max-width: 140px; flex: 0 1 140px; }
.rte-dialog-btn {
  padding: 0.25rem 0.65rem;
  background: #205493;
  color: #fff;
  border: none;
  border-radius: 4px;
  font-size: 0.82rem;
  cursor: pointer;
  white-space: nowrap;
}
.rte-dialog-btn:hover { background: #1a4376; }
.rte-dialog-cancel { background: #6c757d; }
.rte-dialog-cancel:hover { background: #5a6268; }

/* wysiwyg-content is defined globally in TopicEditor but included here for standalone pages */
.rte-wysiwyg-editor .wysiwyg-content {
  border-radius: 0 0 4px 4px;
}
</style>
