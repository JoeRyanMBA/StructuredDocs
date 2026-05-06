<template>
  <div class="rte-wysiwyg-editor">
    <div class="rte-toolbar" @mousedown.prevent>
      <button type="button" @click="exec('bold')" class="toolbar-btn">𝐁 Bold</button>
      <button type="button" @click="exec('italic')" class="toolbar-btn">𝐼 Italic</button>
      <button type="button" @click="exec('formatBlock', 'code')" class="toolbar-btn">⟨⟩ Code</button>
      <button type="button" @click="exec('formatBlock', 'h2')" class="toolbar-btn">𝐇𝟐 Header</button>
      <button type="button" @click="exec('formatBlock', 'h3')" class="toolbar-btn">𝐇𝟑 Header</button>
      <div :class="['dropdown', 'toolbar-dropdown', { 'is-open': activeListMenu === 'bullet' }]">
        <button
          type="button"
          class="toolbar-btn dropdown-btn"
          aria-haspopup="true"
          :aria-expanded="(activeListMenu === 'bullet').toString()"
          @click.stop="toggleListMenu('bullet')"
        >
          • List <span class="toolbar-dropdown__caret">▾</span>
        </button>
        <div v-show="activeListMenu === 'bullet'" class="dropdown-content" @click.stop>
          <button type="button" class="dropdown-item" @click="applyListLevel('bullet', 1)">Level 1</button>
          <button type="button" class="dropdown-item" @click="applyListLevel('bullet', 2)">Level 2</button>
          <button type="button" class="dropdown-item" @click="applyListLevel('bullet', 3)">Level 3</button>
          <button type="button" class="dropdown-item" @click="applyListLevel('bullet', 4)">Level 4</button>
        </div>
      </div>
      <div :class="['dropdown', 'toolbar-dropdown', { 'is-open': activeListMenu === 'ordered' }]">
        <button
          type="button"
          class="toolbar-btn dropdown-btn"
          aria-haspopup="true"
          :aria-expanded="(activeListMenu === 'ordered').toString()"
          @click.stop="toggleListMenu('ordered')"
        >
          1. List <span class="toolbar-dropdown__caret">▾</span>
        </button>
        <div v-show="activeListMenu === 'ordered'" class="dropdown-content" @click.stop>
          <button type="button" class="dropdown-item" @click="applyListLevel('ordered', 1)">Level 1</button>
          <button type="button" class="dropdown-item" @click="applyListLevel('ordered', 2)">Level 2</button>
          <button type="button" class="dropdown-item" @click="applyListLevel('ordered', 3)">Level 3</button>
          <button type="button" class="dropdown-item" @click="applyListLevel('ordered', 4)">Level 4</button>
        </div>
      </div>
      <slot name="toolbar-extra" />
    </div>
    <div
      ref="editorEl"
      contenteditable="true"
      :spellcheck="spellcheck"
      class="wysiwyg-content"
      @input="onInput"
      @paste="onPaste"
      @keydown="onKeydown"
      @mouseup="saveSelection"
      @keyup="saveSelection"
      @blur="saveSelection"
    ></div>
  </div>
</template>

<script>
export default {
  name: 'RichTextEditor',
  props: {
    modelValue: { type: String, default: '' },
    spellcheck: { type: Boolean, default: false },
  },
  emits: ['update:modelValue', 'paste'],
  data() {
    return {
      _inputTimer: null,
      _savedRange: null,
      activeListMenu: null,
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
    document.addEventListener('mousedown', this.onDocumentMouseDown)
  },
  beforeUnmount() {
    if (this._inputTimer) {
      clearTimeout(this._inputTimer)
    }
    document.removeEventListener('mousedown', this.onDocumentMouseDown)
  },
  methods: {
    toggleListMenu(menu) {
      this.activeListMenu = this.activeListMenu === menu ? null : menu
      this.saveSelection()
    },
    closeListMenu() {
      this.activeListMenu = null
    },
    onDocumentMouseDown(event) {
      if (!this.$el?.contains(event.target)) {
        this.closeListMenu()
      }
    },
    applyListLevel(type, level) {
      this.insertList(type, level)
      this.closeListMenu()
    },
    exec(command, value = null) {
      if (!this.restoreSelection()) {
        this.$refs.editorEl?.focus()
      }
      document.execCommand(command, false, value)
      this.saveSelection()
      this.emitUpdate()
    },
    insertList(type, level = 1) {
      const safeLevel = Math.max(1, Math.min(4, Number(level) || 1))
      const command = type === 'ordered' ? 'insertOrderedList' : 'insertUnorderedList'
      const listTag = type === 'ordered' ? 'OL' : 'UL'
      const originalRange = this.getSelectedRange()
      const selectedItemsBeforeCommand = originalRange ? this.getIntersectingListItems(originalRange) : []
      const multiBlockSelection = this.getSelectionBlockCount(originalRange) > 1

      if (!this.restoreSelection()) {
        this.$refs.editorEl?.focus()
      }

      document.execCommand(command, false, null)

      const listItems = this.getAffectedListItems({
        listTag,
        multiBlockSelection,
        selectedItemsBeforeCommand,
      })

      if (listItems.length) {
        listItems.forEach(listItem => this.setListItemLevel(listItem, safeLevel, listTag))
      }

      this.placeCaretAtEnd(listItems[listItems.length - 1] || this.getCurrentListItem() || this.$refs.editorEl)
      this.saveSelection()
      this.emitUpdate()
    },
    getSelectedRange() {
      const selection = window.getSelection()
      if (!selection || selection.rangeCount === 0) return this._savedRange?.cloneRange() || null
      return selection.getRangeAt(0).cloneRange()
    },
    getIntersectingListItems(range) {
      const editor = this.$refs.editorEl
      if (!editor || !range) return []

      return Array.from(editor.querySelectorAll('li')).filter(node => range.intersectsNode(node))
    },
    getSelectionBlockCount(range) {
      const editor = this.$refs.editorEl
      if (!editor || !range) return 0

      const selector = 'p,div,li,h1,h2,h3,h4,h5,h6,pre,blockquote'
      const blocks = Array.from(editor.querySelectorAll(selector)).filter(node => range.intersectsNode(node))
      if (blocks.length > 0) return blocks.length

      return range.toString().trim() ? 1 : 0
    },
    getAffectedListItems({ listTag, multiBlockSelection, selectedItemsBeforeCommand }) {
      const selectionRange = this.getSelectedRange()
      const intersectingAfterCommand = this.getIntersectingListItems(selectionRange)
      if (intersectingAfterCommand.length > 1) {
        return intersectingAfterCommand
      }

      const currentItem = this.getCurrentListItem()
      const currentList = currentItem?.closest(listTag.toLowerCase())
      if (!(currentItem instanceof HTMLLIElement) || !(currentList instanceof HTMLElement)) {
        return currentItem ? [currentItem] : []
      }

      if (multiBlockSelection || selectedItemsBeforeCommand.length > 1) {
        return Array.from(currentList.children).filter(child => child instanceof HTMLLIElement)
      }

      return [currentItem]
    },
    getCurrentListItem() {
      const editor = this.$refs.editorEl
      const selection = window.getSelection()
      if (!editor || !selection || selection.rangeCount === 0) return null

      let node = selection.getRangeAt(0).startContainer
      if (node?.nodeType === Node.TEXT_NODE) {
        node = node.parentNode
      }

      return node instanceof Element ? node.closest('li') : null
    },
    getListDepth(listItem) {
      let depth = 1
      let currentList = listItem?.parentElement

      while (currentList) {
        const parentListItem = currentList.parentElement?.closest('li')
        if (!parentListItem) break
        depth += 1
        currentList = parentListItem.parentElement
      }

      return depth
    },
    setListItemLevel(listItem, targetLevel, listTag) {
      if (!(listItem instanceof HTMLLIElement)) return

      let current = listItem
      let currentDepth = this.getListDepth(current)

      while (currentDepth < targetLevel) {
        const currentList = current.parentElement
        const previousItem = current.previousElementSibling
        if (!(previousItem instanceof HTMLLIElement)) break

        let nestedList = Array.from(previousItem.children).find(child => child.tagName === listTag)
        if (!nestedList) {
          nestedList = document.createElement(listTag.toLowerCase())
          previousItem.appendChild(nestedList)
        }

        nestedList.appendChild(current)
        if (currentList instanceof HTMLElement && !currentList.children.length) {
          currentList.remove()
        }
        currentDepth += 1
      }

      while (currentDepth > targetLevel) {
        const currentList = current.parentElement
        const parentItem = currentList?.closest('li')
        const parentList = parentItem?.parentElement
        if (!(currentList instanceof HTMLElement) || !(parentItem instanceof HTMLLIElement) || !(parentList instanceof HTMLElement)) {
          break
        }

        parentList.insertBefore(current, parentItem.nextSibling)
        if (!currentList.children.length) {
          currentList.remove()
        }
        currentDepth -= 1
      }
    },
    placeCaretAtEnd(node) {
      if (!(node instanceof Node)) return
      const selection = window.getSelection()
      if (!selection) return

      const range = document.createRange()
      range.selectNodeContents(node)
      range.collapse(false)
      selection.removeAllRanges()
      selection.addRange(range)
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
.rte-toolbar .toolbar-btn.is-active {
  background: #205493;
  color: #fff;
  border-color: #205493;
}

.rte-toolbar .dropdown {
  position: relative;
  display: inline-block;
}

.rte-toolbar .dropdown-btn {
  position: relative;
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
}

.rte-toolbar .dropdown-content {
  position: absolute;
  top: 100%;
  left: 0;
  min-width: 180px;
  margin-top: 2px;
  background: #fff;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 100;
}

.rte-toolbar .dropdown.is-open .dropdown-content {
  display: block;
}

.rte-toolbar .dropdown-item {
  display: block;
  width: 100%;
  padding: 0.5rem 0.75rem;
  background: none;
  border: none;
  color: #495057;
  cursor: pointer;
  font-size: 0.875rem;
  text-align: left;
  transition: background-color 0.2s ease;
}

.rte-toolbar .dropdown-item:hover {
  background: #f8f9fa;
}

.rte-toolbar .dropdown-item:first-child {
  border-radius: 4px 4px 0 0;
}

.rte-toolbar .dropdown-item:last-child {
  border-radius: 0 0 4px 4px;
}

.rte-toolbar .toolbar-dropdown__caret {
  font-size: 0.7rem;
  color: #667085;
}

/* wysiwyg-content is defined globally in TopicEditor but included here for standalone pages */
.rte-wysiwyg-editor .wysiwyg-content {
  border-radius: 0 0 4px 4px;
}
</style>
