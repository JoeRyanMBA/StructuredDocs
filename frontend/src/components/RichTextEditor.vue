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
      <div :class="['dropdown', 'toolbar-dropdown', { 'is-open': activeTableMenu }]">
        <button
          type="button"
          class="toolbar-btn dropdown-btn"
          aria-haspopup="true"
          :aria-expanded="activeTableMenu.toString()"
          @click.stop="toggleTableMenu"
        >
          ▦ Table <span class="toolbar-dropdown__caret">▾</span>
        </button>
        <div v-show="activeTableMenu" class="dropdown-content" @click.stop>
          <button type="button" class="dropdown-item" @click="insertTable(2, 2)">Insert 2 x 2</button>
          <button type="button" class="dropdown-item" @click="insertTable(3, 3)">Insert 3 x 3</button>
          <button type="button" class="dropdown-item" @click="insertTable(4, 4)">Insert 4 x 4</button>
          <button type="button" class="dropdown-item" @click="insertTableFromPrompt()">Custom size...</button>
          <div class="dropdown-divider"></div>
          <button type="button" class="dropdown-item" :disabled="!tableContext.inTable" @click="addTableRow('above')">Add Row Above (Alt+Shift+Up)</button>
          <button type="button" class="dropdown-item" :disabled="!tableContext.inTable" @click="addTableRow('below')">Add Row Below (Alt+Shift+Down)</button>
          <button type="button" class="dropdown-item" :disabled="!tableContext.canDeleteRow" @click="deleteCurrentRow">Delete Row</button>
          <div class="dropdown-divider"></div>
          <button type="button" class="dropdown-item" :disabled="!tableContext.inTable" @click="addTableColumn('left')">Add Column Left (Alt+Shift+Left)</button>
          <button type="button" class="dropdown-item" :disabled="!tableContext.inTable" @click="addTableColumn('right')">Add Column Right (Alt+Shift+Right)</button>
          <button type="button" class="dropdown-item" :disabled="!tableContext.canDeleteColumn" @click="deleteCurrentColumn">Delete Column</button>
          <div class="dropdown-divider"></div>
          <button type="button" class="dropdown-item" :disabled="!tableContext.inTable" @click="toggleTableHeaderRow">Toggle Header Row</button>
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
      activeTableMenu: false,
      tableContext: {
        inTable: false,
        canDeleteRow: false,
        canDeleteColumn: false,
      },
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
      this.activeTableMenu = false
      this.activeListMenu = this.activeListMenu === menu ? null : menu
      this.saveSelection()
    },
    closeListMenu() {
      this.activeListMenu = null
    },
    toggleTableMenu() {
      this.activeListMenu = null
      this.activeTableMenu = !this.activeTableMenu
      this.refreshTableContext()
      this.saveSelection()
    },
    closeTableMenu() {
      this.activeTableMenu = false
    },
    closeToolbarMenus() {
      this.closeListMenu()
      this.closeTableMenu()
    },
    onDocumentMouseDown(event) {
      if (!this.$el?.contains(event.target)) {
        this.closeToolbarMenus()
      }
    },
    applyListLevel(type, level) {
      this.insertList(type, level)
      this.closeListMenu()
    },
    insertTableFromPrompt() {
      const rowsInput = window.prompt('Number of rows (including header row):', '3')
      if (rowsInput === null) return
      const colsInput = window.prompt('Number of columns:', '3')
      if (colsInput === null) return

      const rows = Number.parseInt(rowsInput, 10)
      const cols = Number.parseInt(colsInput, 10)
      if (!Number.isFinite(rows) || !Number.isFinite(cols)) return
      this.insertTable(rows, cols)
    },
    insertTable(rows = 3, cols = 3) {
      const rowCount = Math.max(1, Math.min(20, Number(rows) || 3))
      const colCount = Math.max(1, Math.min(12, Number(cols) || 3))

      if (!this.restoreSelection()) {
        this.$refs.editorEl?.focus()
      }

      const selection = window.getSelection()
      const editor = this.$refs.editorEl
      if (!selection || !editor || selection.rangeCount === 0) return
      const range = selection.getRangeAt(0)
      if (!editor.contains(range.startContainer)) return

      const table = document.createElement('table')
      table.className = 'sd-editor-table'

      const thead = document.createElement('thead')
      const headerRow = document.createElement('tr')
      for (let c = 0; c < colCount; c += 1) {
        const th = document.createElement('th')
        th.textContent = `Column ${c + 1}`
        headerRow.appendChild(th)
      }
      thead.appendChild(headerRow)
      table.appendChild(thead)

      const bodyRows = Math.max(1, rowCount - 1)
      const tbody = document.createElement('tbody')
      for (let r = 0; r < bodyRows; r += 1) {
        const tr = document.createElement('tr')
        for (let c = 0; c < colCount; c += 1) {
          tr.appendChild(document.createElement('td'))
        }
        tbody.appendChild(tr)
      }
      table.appendChild(tbody)

      range.deleteContents()
      range.insertNode(table)

      const spacer = document.createElement('p')
      spacer.innerHTML = '<br>'
      table.after(spacer)

      const targetCell = table.querySelector('tbody td') || table.querySelector('th')
      this.placeCaretInCell(targetCell)

      this.closeTableMenu()
      this.saveSelection()
      this.emitUpdate()
    },
    getCurrentTableCell() {
      const range = this.getSelectedRange()
      if (!range) return null

      let node = range.startContainer
      if (node?.nodeType === Node.TEXT_NODE) {
        node = node.parentNode
      }

      return node instanceof Element ? node.closest('td, th') : null
    },
    getCurrentTable() {
      return this.getCurrentTableCell()?.closest('table') || null
    },
    getCurrentTableRow() {
      return this.getCurrentTableCell()?.closest('tr') || null
    },
    getColumnCount(table) {
      if (!(table instanceof HTMLTableElement)) return 0
      const rows = Array.from(table.querySelectorAll('tr'))
      return rows.reduce((max, row) => Math.max(max, row.children.length), 0)
    },
    refreshTableContext() {
      const cell = this.getCurrentTableCell()
      const table = cell?.closest('table') || null
      const row = cell?.closest('tr') || null
      const inTable = Boolean(table && row)

      if (!inTable) {
        this.tableContext = { inTable: false, canDeleteRow: false, canDeleteColumn: false }
        return
      }

      const totalRows = table.querySelectorAll('tr').length
      const totalCols = this.getColumnCount(table)

      this.tableContext = {
        inTable: true,
        canDeleteRow: totalRows > 1,
        canDeleteColumn: totalCols > 1,
      }
    },
    createTableRow(columnCount, useHeaderCells = false) {
      const row = document.createElement('tr')
      for (let i = 0; i < columnCount; i += 1) {
        row.appendChild(document.createElement(useHeaderCells ? 'th' : 'td'))
      }
      return row
    },
    addTableRow(position = 'below') {
      if (!this.restoreSelection()) this.$refs.editorEl?.focus()
      const row = this.getCurrentTableRow()
      const table = this.getCurrentTable()
      if (!(row instanceof HTMLTableRowElement) || !(table instanceof HTMLTableElement)) return

      const useHeaderCells = row.parentElement?.tagName === 'THEAD'
      const newRow = this.createTableRow(Math.max(1, row.children.length), useHeaderCells)
      if (position === 'above') {
        row.before(newRow)
      } else {
        row.after(newRow)
      }

      this.placeCaretInCell(newRow.cells[0])
      this.saveSelection()
      this.emitUpdate()
    },
    deleteCurrentRow() {
      if (!this.restoreSelection()) this.$refs.editorEl?.focus()
      const row = this.getCurrentTableRow()
      const table = this.getCurrentTable()
      if (!(row instanceof HTMLTableRowElement) || !(table instanceof HTMLTableElement)) return

      const allRows = table.querySelectorAll('tr')
      if (allRows.length <= 1) return

      const targetRow = row.previousElementSibling || row.nextElementSibling
      row.remove()

      if (table.tHead && table.tHead.rows.length === 0) table.tHead.remove()
      if (table.tBodies.length > 0) {
        Array.from(table.tBodies).forEach(section => {
          if (section.rows.length === 0) section.remove()
        })
      }

      if (targetRow instanceof HTMLTableRowElement && targetRow.cells.length) {
        this.placeCaretInCell(targetRow.cells[0])
      } else {
        this.placeCaretAtEnd(table)
      }

      this.saveSelection()
      this.emitUpdate()
    },
    addTableColumn(position = 'right') {
      if (!this.restoreSelection()) this.$refs.editorEl?.focus()
      const cell = this.getCurrentTableCell()
      const table = this.getCurrentTable()
      if (!(cell instanceof HTMLTableCellElement) || !(table instanceof HTMLTableElement)) return

      const columnIndex = cell.cellIndex
      const insertIndex = position === 'left' ? columnIndex : columnIndex + 1

      Array.from(table.querySelectorAll('tr')).forEach((row, rowIndex) => {
        const isHeaderRow = row.parentElement?.tagName === 'THEAD'
        const tagName = isHeaderRow ? 'th' : 'td'
        const newCell = document.createElement(tagName)
        if (isHeaderRow) {
          newCell.textContent = `Column ${insertIndex + 1}`
        }

        if (insertIndex >= row.children.length) {
          row.appendChild(newCell)
        } else {
          row.insertBefore(newCell, row.children[insertIndex])
        }

        if (rowIndex === 0 && isHeaderRow) {
          // Keep header labels sequential.
          Array.from(row.children).forEach((headerCell, idx) => {
            if (!String(headerCell.textContent || '').trim() || /^Column \d+$/.test(String(headerCell.textContent || '').trim())) {
              headerCell.textContent = `Column ${idx + 1}`
            }
          })
        }
      })

      const targetRow = cell.parentElement
      const targetCell = targetRow?.children[insertIndex] || targetRow?.lastElementChild
      this.placeCaretInCell(targetCell)
      this.saveSelection()
      this.emitUpdate()
    },
    deleteCurrentColumn() {
      if (!this.restoreSelection()) this.$refs.editorEl?.focus()
      const cell = this.getCurrentTableCell()
      const table = this.getCurrentTable()
      if (!(cell instanceof HTMLTableCellElement) || !(table instanceof HTMLTableElement)) return

      const columnCount = this.getColumnCount(table)
      if (columnCount <= 1) return

      const columnIndex = cell.cellIndex
      Array.from(table.querySelectorAll('tr')).forEach(row => {
        if (row.children[columnIndex]) {
          row.children[columnIndex].remove()
        }
      })

      if (table.tHead?.rows.length) {
        const headerRow = table.tHead.rows[0]
        Array.from(headerRow.cells).forEach((headerCell, idx) => {
          if (!String(headerCell.textContent || '').trim() || /^Column \d+$/.test(String(headerCell.textContent || '').trim())) {
            headerCell.textContent = `Column ${idx + 1}`
          }
        })
      }

      const row = this.getCurrentTableRow()
      const targetIndex = Math.max(0, columnIndex - 1)
      const targetCell = row?.children[targetIndex] || row?.lastElementChild
      if (targetCell) this.placeCaretInCell(targetCell)

      this.saveSelection()
      this.emitUpdate()
    },
    toggleTableHeaderRow() {
      if (!this.restoreSelection()) this.$refs.editorEl?.focus()
      const table = this.getCurrentTable()
      if (!(table instanceof HTMLTableElement)) return

      if (table.tHead?.rows.length) {
        const headerRow = table.tHead.rows[0]
        const plainRow = document.createElement('tr')
        Array.from(headerRow.cells).forEach(cell => {
          const td = document.createElement('td')
          td.innerHTML = cell.innerHTML
          plainRow.appendChild(td)
        })
        const tbody = table.tBodies[0] || table.createTBody()
        tbody.insertBefore(plainRow, tbody.firstChild)
        table.tHead.remove()
        this.placeCaretInCell(plainRow.cells[0])
      } else {
        const firstBodyRow = table.tBodies[0]?.rows[0] || table.rows[0]
        if (!(firstBodyRow instanceof HTMLTableRowElement)) return

        const headerRow = document.createElement('tr')
        Array.from(firstBodyRow.cells).forEach((cell, idx) => {
          const th = document.createElement('th')
          const existing = String(cell.textContent || '').trim()
          th.textContent = existing || `Column ${idx + 1}`
          headerRow.appendChild(th)
        })

        if (firstBodyRow.parentElement?.tagName === 'TBODY') {
          firstBodyRow.remove()
        } else {
          firstBodyRow.parentElement?.removeChild(firstBodyRow)
        }

        let thead = table.tHead
        if (!thead) {
          thead = table.createTHead()
        }
        thead.appendChild(headerRow)
        this.placeCaretInCell(headerRow.cells[0])
      }

      this.saveSelection()
      this.emitUpdate()
    },
    getLastBodyRow(table) {
      if (!(table instanceof HTMLTableElement)) return null
      const bodies = Array.from(table.tBodies)
      for (let i = bodies.length - 1; i >= 0; i -= 1) {
        const body = bodies[i]
        if (body.rows.length > 0) {
          return body.rows[body.rows.length - 1]
        }
      }
      const allRows = Array.from(table.rows)
      return allRows.length ? allRows[allRows.length - 1] : null
    },
    handleTableTab(event) {
      if (event.key !== 'Tab' || event.shiftKey) return false

      const cell = this.getCurrentTableCell()
      const row = this.getCurrentTableRow()
      const table = this.getCurrentTable()
      if (!(cell instanceof HTMLTableCellElement) || !(row instanceof HTMLTableRowElement) || !(table instanceof HTMLTableElement)) {
        return false
      }

      const lastRow = this.getLastBodyRow(table)
      const isLastRow = row === lastRow
      const isLastCell = cell.cellIndex === row.cells.length - 1
      if (!isLastRow || !isLastCell) {
        return false
      }

      event.preventDefault()
      const columnCount = Math.max(1, row.cells.length)
      const targetBody = row.parentElement?.tagName === 'TBODY'
        ? row.parentElement
        : (table.tBodies[0] || table.createTBody())
      const newRow = this.createTableRow(columnCount, false)
      targetBody.appendChild(newRow)
      this.placeCaretInCell(newRow.cells[0])
      this.saveSelection()
      this.emitUpdate()
      return true
    },
    handleTableShortcut(event) {
      if (!event.altKey || !event.shiftKey) return false

      const table = this.getCurrentTable()
      if (!(table instanceof HTMLTableElement)) return false

      if (event.key === 'ArrowUp') {
        event.preventDefault()
        this.addTableRow('above')
        return true
      }

      if (event.key === 'ArrowDown') {
        event.preventDefault()
        this.addTableRow('below')
        return true
      }

      if (event.key === 'ArrowLeft') {
        event.preventDefault()
        this.addTableColumn('left')
        return true
      }

      if (event.key === 'ArrowRight') {
        event.preventDefault()
        this.addTableColumn('right')
        return true
      }

      return false
    },
    placeCaretInCell(cell) {
      if (!(cell instanceof HTMLElement)) return false
      const selection = window.getSelection()
      if (!selection) return false

      const range = document.createRange()
      range.selectNodeContents(cell)
      range.collapse(false)
      selection.removeAllRanges()
      selection.addRange(range)
      return true
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
      this.refreshTableContext()
      if (this._inputTimer) clearTimeout(this._inputTimer)
      this._inputTimer = setTimeout(() => this.emitUpdate(), 300)
    },
    onPaste(event) {
      this.$emit('paste', event)
    },
    onKeydown(event) {
      if (this.handleTableShortcut(event)) return
      if (this.handleTableTab(event)) return

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
          this.refreshTableContext()
          return true
        }
      }
      this.refreshTableContext()
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
        this.refreshTableContext()
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

.rte-toolbar .dropdown-divider {
  height: 1px;
  margin: 0.2rem 0;
  background: #e5e7eb;
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

.rte-wysiwyg-editor .wysiwyg-content table {
  width: 100%;
  border-collapse: collapse;
  margin: 0 0 1rem;
}

.rte-wysiwyg-editor .wysiwyg-content th,
.rte-wysiwyg-editor .wysiwyg-content td {
  border: 1px solid #ced4da;
  padding: 0.45rem 0.55rem;
  vertical-align: top;
  min-width: 80px;
}

.rte-wysiwyg-editor .wysiwyg-content th {
  background: #f1f5f9;
  font-weight: 600;
}
</style>
