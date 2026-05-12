<template>
  <div class="rte-wysiwyg-editor">
    <div class="rte-toolbar" @mousedown.prevent>
      <button type="button" @click="exec('bold')" class="toolbar-btn">𝐁 Bold</button>
      <button type="button" @click="exec('italic')" class="toolbar-btn">𝐼 Italic</button>
      <button type="button" @click="applyInlineCode" class="toolbar-btn">⟨⟩ Code</button>
      <button type="button" @click="exec('formatBlock', 'h2')" class="toolbar-btn">𝐇𝟐 Header</button>
      <button type="button" @click="exec('formatBlock', 'h3')" class="toolbar-btn">𝐇𝟑 Header</button>
      <button type="button" @click="clearFormatting()" class="toolbar-btn" title="Clear formatting from selected text">Tx Clear</button>
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
      :lang="spellcheckLang"
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
    spellcheckLang: { type: String, default: 'en-US' },
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
    spellcheck(newVal) {
      this.setSpellcheck(newVal)
    },
    spellcheckLang(newVal) {
      const el = this.$refs.editorEl
      if (!el) return
      el.setAttribute('lang', newVal || 'en-US')
    },
  },
  mounted() {
    if (this.$refs.editorEl) {
      this.$refs.editorEl.innerHTML = this.modelValue || ''
      this.setSpellcheck(this.spellcheck)
      this.$refs.editorEl.setAttribute('lang', this.spellcheckLang || 'en-US')
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
    clearFormatting() {
      if (!this.restoreSelection()) {
        this.$refs.editorEl?.focus()
      }

      const editor = this.$refs.editorEl
      const selection = window.getSelection()
      if (!editor || !selection || selection.rangeCount === 0) return

      const range = selection.getRangeAt(0)
      if (!editor.contains(range.commonAncestorContainer) || range.collapsed) return

      const plainText = this.fragmentToPlainText(range.cloneContents()).trim()
      range.deleteContents()
      this.insertPlainText(range, plainText)
      this.saveSelection()
      this.emitUpdate()
    },
    exec(command, value = null) {
      if (!this.restoreSelection()) {
        this.$refs.editorEl?.focus()
      }
      document.execCommand(command, false, value)
      this.saveSelection()
      this.emitUpdate()
    },
    applyInlineCode() {
      if (!this.restoreSelection()) {
        this.$refs.editorEl?.focus()
      }

      const editor = this.$refs.editorEl
      const selection = window.getSelection()
      if (!editor || !selection || selection.rangeCount === 0) return

      const range = selection.getRangeAt(0)
      if (!editor.contains(range.commonAncestorContainer)) return

      const activeCode = range.startContainer instanceof Node
        ? (range.startContainer.nodeType === Node.ELEMENT_NODE
            ? range.startContainer.closest?.('code')
            : range.startContainer.parentElement?.closest('code'))
        : null

      if (activeCode instanceof HTMLElement) {
        const textNode = document.createTextNode(activeCode.textContent || '')
        activeCode.replaceWith(textNode)
        const newRange = document.createRange()
        newRange.selectNodeContents(textNode)
        selection.removeAllRanges()
        selection.addRange(newRange)
        this.saveSelection()
        this.emitUpdate()
        return
      }

      const selectedText = selection.toString()
      if (!selectedText) return

      const escapedText = selectedText
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')

      document.execCommand('insertHTML', false, `<code>${escapedText}</code>`)
      this.saveSelection()
      this.emitUpdate()
    },
    insertList(type, level = 1) {
      const safeLevel = Math.max(1, Math.min(4, Number(level) || 1))
      const command = type === 'ordered' ? 'insertOrderedList' : 'insertUnorderedList'
      const listTag = type === 'ordered' ? 'OL' : 'UL'
      const originalRange = this.getSelectedRange()
      const selectedItemsBeforeCommand = originalRange ? this.getIntersectingListItems(originalRange) : []
      const selectedBlockCount = this.getSelectionBlockCount(originalRange)
      const multiBlockSelection = selectedBlockCount > 1

      if (!this.restoreSelection()) {
        this.$refs.editorEl?.focus()
      }

      const currentItemBeforeCommand = this.getCurrentListItem()
      const targetListSelector = listTag.toLowerCase()
      const isAlreadyInTargetList = selectedItemsBeforeCommand.length > 0
        ? selectedItemsBeforeCommand.every(item => item.closest(targetListSelector))
        : currentItemBeforeCommand?.closest(targetListSelector) instanceof HTMLElement

      if (!isAlreadyInTargetList) {
        document.execCommand(command, false, null)
      }

      const listItems = isAlreadyInTargetList
        ? this.getExistingListItems({
            listTag,
            multiBlockSelection,
            selectedItemsBeforeCommand,
            currentItem: currentItemBeforeCommand,
          })
        : this.getAffectedListItems({
            listTag,
            multiBlockSelection,
            selectedItemsBeforeCommand,
            selectedBlockCount,
          })

      if (listItems.length) {
        listItems.forEach(listItem => this.setListItemLevel(listItem, safeLevel, listTag))
        this.applyVisualListLevel(listItems, safeLevel, type)
        this.normalizeStyledListGroups()
      }

      this.placeCaretAtEnd(this.getCurrentListItem() || this.$refs.editorEl)
      this.saveSelection()
      this.emitUpdate()
    },
    getExistingListItems({ listTag, multiBlockSelection, selectedItemsBeforeCommand, currentItem }) {
      const targetListSelector = listTag.toLowerCase()

      if (selectedItemsBeforeCommand.length > 0) {
        return selectedItemsBeforeCommand.filter(item => item.closest(targetListSelector))
      }

      const currentList = currentItem?.closest(targetListSelector)
      if (!(currentItem instanceof HTMLLIElement) || !(currentList instanceof HTMLElement)) {
        return currentItem ? [currentItem] : []
      }

      if (multiBlockSelection) {
        return Array.from(currentList.children).filter(child => child instanceof HTMLLIElement)
      }

      return [currentItem]
    },
    isRangeInEditor(range) {
      const editor = this.$refs.editorEl
      if (!(editor instanceof HTMLElement) || !range) return false

      return editor.contains(range.commonAncestorContainer)
    },
    getSelectedRange() {
      const selection = window.getSelection()
      if (selection && selection.rangeCount > 0) {
        const range = selection.getRangeAt(0)
        if (this.isRangeInEditor(range)) {
          return range.cloneRange()
        }
      }

      return this._savedRange?.cloneRange() || null
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
    getAffectedListItems({ listTag, multiBlockSelection, selectedItemsBeforeCommand, selectedBlockCount = 0 }) {
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

      if (multiBlockSelection && selectedBlockCount > 1) {
        const editor = this.$refs.editorEl
        const candidateLists = editor
          ? Array.from(editor.querySelectorAll(listTag.toLowerCase()))
          : []
        const newestList = candidateLists.at(-1)
        if (newestList instanceof HTMLElement) {
          return Array.from(newestList.children)
            .filter(child => child instanceof HTMLLIElement)
            .slice(-selectedBlockCount)
        }
      }

      return [currentItem]
    },
    applyVisualListLevel(listItems, level, type) {
      const markerStyles = type === 'ordered'
        ? { 1: 'decimal', 2: 'lower-alpha', 3: 'lower-roman', 4: 'upper-alpha' }
        : { 1: 'disc', 2: 'circle', 3: 'square', 4: 'disc' }

      listItems.forEach(listItem => {
        if (!(listItem instanceof HTMLLIElement)) return
        const actualLevel = Math.max(1, Math.min(4, level))
        const marginLeft = actualLevel > 1 ? `${(actualLevel - 1) * 1.5}rem` : ''
        const markerStyle = markerStyles[actualLevel] || markerStyles[1]

        if (actualLevel > 1) {
          listItem.dataset.listLevel = String(actualLevel)
          listItem.style.marginLeft = marginLeft
          listItem.style.listStyleType = markerStyle
        } else {
          delete listItem.dataset.listLevel
          listItem.style.removeProperty('margin-left')
          listItem.style.listStyleType = markerStyle
        }
      })
    },
    createSemanticList(tagName) {
      return document.createElement(tagName.toLowerCase())
    },
    getPreviousAdjacentList(listNode, tagName) {
      let sibling = listNode?.previousSibling || null

      while (sibling) {
        if (sibling.nodeType === Node.TEXT_NODE && !(sibling.textContent || '').trim()) {
          sibling = sibling.previousSibling
          continue
        }

        return sibling instanceof HTMLElement && ['UL', 'OL'].includes(sibling.tagName) ? sibling : null
      }

      return null
    },
    isEmptySpacer(node) {
    if (!node) return false
    
    // Quick out for text nodes with no non-whitespace characters
    if (node.nodeType === Node.TEXT_NODE) {
      if (!node.textContent) return true
      return node.textContent.replace(/[\s\u200B-\u200D\uFEFF\u00A0]+/g, '') === ''
    }
    
    if (node.nodeType === Node.ELEMENT_NODE) {
      if (node.tagName === 'BR') return true
      
      // For block-level and inline spacers, check their content
      if (['P', 'DIV', 'SPAN'].includes(node.tagName) || node.tagName === 'LI') {
        const textContent = (node.textContent || '').replace(/[\s\u200B-\u200D\uFEFF\u00A0]+/g, '')
        
        // If there's real text, it's not a spacer
        if (textContent.length > 0) return false
        
        // Check for meaningful media or structural elements
        const mediaNodes = node.querySelectorAll('img, video, audio, iframe, canvas, object, hr, table, input, button')
        if (mediaNodes.length > 0) return false
        
        // We only care if it might be an un-merged list or contain one. 
        // If it's a P/DIV that contains a real UL, it shouldn't be skipped.
        const lists = node.querySelectorAll('ul, ol')
        for (let i = 0; i < lists.length; i++) {
          if (lists[i].textContent.replace(/[\s\u200B-\u200D\uFEFF\u00A0]+/g, '').length > 0) {
            return false // Contains a list with actual text!
          }
        }
        
        return true
      }
    }
    
    return false
  },
    mergeAdjacentLists(container = this.$refs.editorEl) {
      if (!(container instanceof HTMLElement)) return

      let node = container.firstChild
      while (node) {
        if (!(node instanceof HTMLElement) || !['UL', 'OL'].includes(node.tagName)) {
          node = node.nextSibling
          continue
        }

        const nodeLevel = this.getListLevel(node)
        let next = node.nextSibling
        while (next) {
          if (this.isEmptySpacer(next)) {
            const spacer = next
            next = next.nextSibling
            spacer.remove()
            continue
          }

          if (!(next instanceof HTMLElement) || !['UL', 'OL'].includes(next.tagName)) {
            break
          }

          const adjacentList = next
          const adjacentLevel = this.getListLevel(adjacentList)
          const adjacentTag = this.getListTag(adjacentList, node.tagName)
          const nodeTag = this.getListTag(node, node.tagName)

          if (adjacentLevel !== nodeLevel || adjacentTag !== nodeTag) {
            break
          }

          next = adjacentList.nextSibling
          while (adjacentList.firstChild) {
            node.appendChild(adjacentList.firstChild)
          }
          adjacentList.remove()
        }

        node = next
      }
    },
    cleanListItem(node) {
      const clone = node.cloneNode(true)
      if (!(clone instanceof HTMLElement)) return null
      clone.querySelectorAll('ul, ol').forEach(list => list.remove())
      delete clone.dataset.listLevel
      clone.style.removeProperty('margin-left')
      clone.style.removeProperty('list-style-type')
      if (!clone.getAttribute('style')) {
        clone.removeAttribute('style')
      }
      return clone
    },
    collectListEntries(listNode, inheritedLevel = 1, entries = []) {
      Array.from(listNode.children).forEach(child => {
        if (!(child instanceof HTMLLIElement)) return

        const parsedLevel = Number(child.dataset.listLevel || inheritedLevel)
        const level = Number.isFinite(parsedLevel) && parsedLevel > 0 ? parsedLevel : inheritedLevel
        const item = this.cleanListItem(child)
        if (item) {
          entries.push({ level, item, listTag: this.getListTag(listNode, listNode.tagName) })
        }

        Array.from(child.children).forEach(nested => {
          if (nested instanceof HTMLElement && (nested.tagName === 'UL' || nested.tagName === 'OL')) {
            this.collectListEntries(nested, level + 1, entries)
          }
        })
      })

      return entries
    },
    buildSemanticList(entries, defaultTagName) {
      const fragment = document.createDocumentFragment()
      const stack = []

      const ensureLevel = (rawTargetLevel, latestListTag) => {
        const targetLevel = Math.max(1, Math.min(rawTargetLevel, stack.length + 1))

        while (stack.length > targetLevel) {
          stack.pop()
        }

        if (stack.length === targetLevel) {
          const currentEntry = stack[stack.length - 1]
          if (currentEntry.list.tagName.toUpperCase() !== (latestListTag || defaultTagName).toUpperCase()) {
            stack.pop()
          }
        }

        while (stack.length < targetLevel) {
          const parent = stack.length > 0 ? stack[stack.length - 1] : null
          if (stack.length > 0 && !(parent?.lastItem instanceof HTMLElement)) {
            break
          }
          const targetTagName = latestListTag || defaultTagName
          const nestedList = this.createSemanticList(targetTagName)
          
          if (stack.length === 0) {
            fragment.appendChild(nestedList)
          } else {
            parent.lastItem.appendChild(nestedList)
          }
          stack.push({ level: stack.length + 1, list: nestedList, lastItem: null })
        }
      }

      entries.forEach(({ level, item, listTag }) => {
        ensureLevel(level, listTag)
        const entry = stack[stack.length - 1]
        if (!entry || !(item instanceof HTMLElement)) return
        
        entry.list.appendChild(item)
        entry.lastItem = item
      })

      return fragment
    },
    fragmentToPlainText(fragment) {
      const blockTags = new Set(['P', 'DIV', 'LI', 'H1', 'H2', 'H3', 'H4', 'H5', 'H6', 'PRE', 'BLOCKQUOTE'])
      let output = ''

      const appendNode = (node) => {
        if (node.nodeType === Node.TEXT_NODE) {
          output += node.textContent || ''
          return
        }
        if (!(node instanceof HTMLElement)) return

        if (node.tagName === 'BR') {
          output += '\n'
          return
        }

        node.childNodes.forEach(appendNode)
        if (blockTags.has(node.tagName)) {
          output += '\n'
        }
      }

      fragment.childNodes.forEach(appendNode)
      return output.replace(/\n{3,}/g, '\n\n')
    },
    insertPlainText(range, text) {
      const selection = window.getSelection()
      const lines = String(text || '').split('\n')
      const fragment = document.createDocumentFragment()

      lines.forEach((line, index) => {
        fragment.appendChild(document.createTextNode(line))
        if (index < lines.length - 1) {
          fragment.appendChild(document.createElement('br'))
        }
      })

      range.insertNode(fragment)
      range.collapse(false)
      if (selection) {
        selection.removeAllRanges()
        selection.addRange(range)
      }
    },
    normalizeStyledListGroups() {
      const container = this.$refs.editorEl
      if (!(container instanceof HTMLElement)) return

      this.mergeAdjacentLists(container)

      const nodes = Array.from(container.childNodes)
      let index = 0

      while (index < nodes.length) {
        const current = nodes[index]
        if (!(current instanceof HTMLElement) || !['UL', 'OL'].includes(current.tagName)) {
          index += 1
          continue
        }

        const tagName = this.getListTag(current, current.tagName)
        const listNodes = [current]
        const spacerNodes = []
        let cursor = index + 1

        while (cursor < nodes.length) {
          const node = nodes[cursor]
          if (this.isEmptySpacer(node)) {
            spacerNodes.push(node)
            cursor += 1
            continue
          }
          if (node instanceof HTMLElement && ['UL', 'OL'].includes(node.tagName)) {
            listNodes.push(node)
            cursor += 1
            continue
          }
          break
        }

        const hasStyledLevels = listNodes.some(listNode =>
          Array.from(listNode.querySelectorAll('li')).some(child =>
            child instanceof HTMLElement && (child.dataset.listLevel || child.style.marginLeft || child.style.listStyleType)
          )
        )

        if (hasStyledLevels) {
          const entries = listNodes.flatMap(listNode => this.collectListEntries(listNode))
          const semanticList = this.buildSemanticList(entries, tagName)
          current.replaceWith(semanticList)
          listNodes.slice(1).forEach(node => node.remove())
          spacerNodes.forEach(node => node.remove())
        }

        index = cursor
      }
    },
    getCurrentListItem() {
      const editor = this.$refs.editorEl
      const range = this.getSelectedRange()
      if (!editor || !range) return null

      let node = range.startContainer
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
    getListTag(node, fallback = 'UL') {
      if (!(node instanceof HTMLElement)) return fallback.toUpperCase()
      const tag = node.tagName.toUpperCase()
      if (tag === 'OL') return 'OL'
      if (tag !== 'UL') return fallback.toUpperCase()
      const styleValue = String(node.style?.listStyleType || node.getAttribute('style') || '').toLowerCase()
      if (/(^|\s)(decimal|decimal-leading-zero|lower-alpha|lower-roman|upper-alpha|upper-roman|alpha|roman)(\s|;|$)/.test(styleValue)) {
        return 'OL'
      }

      const hasOrderedChildMarker = Array.from(node.children).some(child => {
        if (!(child instanceof HTMLElement) || child.tagName !== 'LI') return false
        const liStyle = String(child.style?.listStyleType || child.getAttribute('style') || '').toLowerCase()
        return /(^|\s)(decimal|decimal-leading-zero|lower-alpha|lower-roman|upper-alpha|upper-roman|alpha|roman)(\s|;|$)/.test(liStyle)
      })
      if (hasOrderedChildMarker) return 'OL'
      return 'UL'
    },
    setListItemLevel(listItem, targetLevel, listTag) {
      if (!(listItem instanceof HTMLLIElement)) return

      let current = listItem
      let currentDepth = this.getListDepth(current)

      while (currentDepth < targetLevel) {
        const currentList = current.parentElement
        if (!(currentList instanceof HTMLElement)) break

        let previousItem = current.previousElementSibling
        if (!(previousItem instanceof HTMLLIElement)) {
          const previousList = this.getPreviousAdjacentList(currentList, listTag)
          if (previousList instanceof HTMLElement) {
            while (currentList.firstChild) {
              previousList.appendChild(currentList.firstChild)
            }
            currentList.remove()
            previousItem = previousList.lastElementChild
          }
        }

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
    setSpellcheck(enabled) {
      const el = this.$refs.editorEl
      if (!el) return false

      const value = Boolean(enabled)
      // Keep both property and attribute in sync for broad browser compatibility.
      el.spellcheck = value
      el.setAttribute('spellcheck', value ? 'true' : 'false')

      // Some browsers update spellcheck underlines only after focus changes.
      if (document.activeElement === el) {
        el.blur()
        requestAnimationFrame(() => {
          el.focus()
        })
      }
      return true
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
          return true
        }
      }
      return false
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
.wysiwyg-content ul,
.wysiwyg-content ol {
  margin: 0 0 1rem 0;
  padding-left: 1.5rem;
}
.wysiwyg-content li > ul,
.wysiwyg-content li > ol {
  margin: 0.25rem 0 0;
}
.wysiwyg-content ul {
  list-style-type: disc;
}
.wysiwyg-content ul ul {
  list-style-type: circle;
}
.wysiwyg-content ul ul ul {
  list-style-type: square;
}
.wysiwyg-content ul ul ul ul {
  list-style-type: disc;
}
.wysiwyg-content ol {
  list-style-type: decimal;
}
.wysiwyg-content ol ol {
  list-style-type: lower-alpha;
}
.wysiwyg-content ol ol ol {
  list-style-type: lower-roman;
}
.wysiwyg-content ol ol ol ol {
  list-style-type: upper-alpha;
}
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

.rte-wysiwyg-editor .wysiwyg-content code {
  background: #f8f9fa;
  padding: 0.2rem 0.4rem;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
  font-size: 0.9em;
}
</style>
