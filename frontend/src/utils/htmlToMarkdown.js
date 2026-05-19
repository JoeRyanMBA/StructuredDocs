/**
 * Convert an HTML string to Markdown.
 * Shared by TopicEditor and SnippetsLibrary.
 */
export function htmlToMarkdown(html) {
  const parser = new DOMParser()
  const doc = parser.parseFromString(html || '', 'text/html')
  const inferListLevelFromMargin = (marginValue) => {
    const raw = String(marginValue || '').trim()
    if (!raw) return null

    const match = raw.match(/^(-?\d*\.?\d+)(px|rem)?$/i)
    if (!match) return null

    const value = Number(match[1])
    if (!Number.isFinite(value) || value <= 0) return null

    const unit = (match[2] || 'px').toLowerCase()
    const step = unit === 'rem' ? 1.5 : 24
    return Math.max(2, Math.round(value / step) + 1)
  }

  const getListLevel = (node, fallback = 1) => {
    if (!(node instanceof HTMLElement)) return fallback

    const parsed = Number(node.dataset.listLevel || node.getAttribute('data-list-level') || '')
    if (Number.isFinite(parsed) && parsed > 0) {
      return parsed
    }

    const marginLevel = inferListLevelFromMargin(node.style?.marginLeft)
    if (marginLevel) {
      return marginLevel
    }

    return fallback
  }

  const getListTag = (node, fallback = 'UL') => {
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
  }

  const cleanListItem = (node) => {
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
  }

  const createSemanticList = (tagName) => doc.createElement(tagName.toLowerCase())

  const isEmptySpacer = (node) => {
    if (!node) return false
    
    const text = (node.textContent || '').replace(/[\s\u200B-\u200D\uFEFF]/g, '')
    if (node.nodeType === Node.TEXT_NODE && !text) return true
    
    if (node.nodeType === Node.ELEMENT_NODE) {
      if (node.tagName === 'BR') return true
      if (['P', 'DIV', 'SPAN'].includes(node.tagName)) {
        if (!text) {
          const hasMedia = node.querySelector('img, video, audio, iframe, canvas, object, hr, ul, ol, li, table')
          if (!hasMedia) return true
        }
      }
    }
    return false
  }

  const unwrapListWrappers = (container) => {
    if (!(container instanceof HTMLElement)) return

    const candidates = Array.from(container.childNodes)
    candidates.forEach(node => {
      if (!(node instanceof HTMLElement)) return
      if (!['DIV', 'P', 'SECTION'].includes(node.tagName)) return

      const meaningful = Array.from(node.childNodes).filter(child => {
        if (child.nodeType === Node.TEXT_NODE) {
          return Boolean((child.textContent || '').trim())
        }
        return child instanceof HTMLElement
      })

      if (meaningful.length !== 1) return
      const onlyChild = meaningful[0]
      if (!(onlyChild instanceof HTMLElement) || !['UL', 'OL'].includes(onlyChild.tagName)) return

      node.replaceWith(onlyChild)
    })
  }

  const mergeAdjacentLists = (container) => {
    let node = container.firstChild
    while (node) {
      if (!(node instanceof HTMLElement) || !['UL', 'OL'].includes(node.tagName)) {
        node = node.nextSibling
        continue
      }

      const nodeLevel = getListLevel(node, 1)
      let next = node.nextSibling
      while (next) {
        if (isEmptySpacer(next)) {
          const spacer = next
          next = next.nextSibling
          spacer.remove()
          continue
        }

        if (!(next instanceof HTMLElement) || !['UL', 'OL'].includes(next.tagName)) {
          break
        }

        const adjacentList = next
        const adjacentLevel = getListLevel(adjacentList, 1)
        const adjacentTag = getListTag(adjacentList, node.tagName)
        const nodeTag = getListTag(node, node.tagName)

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
  }

  const collectListEntries = (listNode, inheritedLevel = 1, entries = []) => {
    let lastItemLevel = inheritedLevel

    Array.from(listNode.childNodes).forEach(child => {
      if (child instanceof HTMLLIElement) {
        const level = Math.max(1, getListLevel(child, inheritedLevel))
        const item = cleanListItem(child)
        if (item) {
          entries.push({ level, item, listTag: getListTag(listNode, listNode.tagName) })
          lastItemLevel = level
        }

        Array.from(child.childNodes).forEach(nested => {
          if (nested instanceof HTMLElement && (nested.tagName === 'UL' || nested.tagName === 'OL')) {
            const nestedLevel = Math.max(level + 1, getListLevel(nested, level + 1))
            collectListEntries(nested, nestedLevel, entries)
          }
        })
        return
      }

      if (child instanceof HTMLElement && (child.tagName === 'UL' || child.tagName === 'OL')) {
        const nestedLevel = Math.max(lastItemLevel + 1, getListLevel(child, lastItemLevel + 1))
        collectListEntries(child, nestedLevel, entries)
      }
    })

    return entries
  }

  const buildSemanticList = (entries, defaultTagName) => {
    const fragment = doc.createDocumentFragment()
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
        const nestedList = createSemanticList(targetTagName)
        
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
  }

  const normalizeStyledListGroups = (container) => {
    mergeAdjacentLists(container)

    const nodes = Array.from(container.childNodes)
    let index = 0

    while (index < nodes.length) {
      const current = nodes[index]
      if (!(current instanceof HTMLElement) || !['UL', 'OL'].includes(current.tagName)) {
        index += 1
        continue
      }

      const tagName = getListTag(current, current.tagName)
      const listNodes = [current]
      const spacerNodes = []
      let cursor = index + 1

      while (cursor < nodes.length) {
        const node = nodes[cursor]
        if (isEmptySpacer(node)) {
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

      const hasStyledLevels = listNodes.some(listNode => hasListStructureSignal(listNode, listNode.tagName))

      if (hasStyledLevels) {
        const entries = listNodes.flatMap(listNode =>
          collectListEntries(listNode, getListLevel(listNode, 1))
        )
        const semanticList = buildSemanticList(entries, tagName)
        current.replaceWith(semanticList)
        listNodes.slice(1).forEach(node => node.remove())
        spacerNodes.forEach(node => node.remove())
      }

      index = cursor
    }
  }

  const isStyledListItem = (node) => {
    if (!(node instanceof HTMLElement)) return false
    return Boolean(node.dataset.listLevel) || Boolean(node.style.marginLeft) || Boolean(node.style.listStyleType)
  }

  const hasListStructureSignal = (listNode, tagName) => {
    if (!(listNode instanceof HTMLElement)) return false
    if (getListLevel(listNode, 1) > 1) return true

    return Array.from(listNode.childNodes).some(child => {
      if (!(child instanceof HTMLElement)) return false
      if (child.tagName === tagName) return true
      if (child.tagName === 'UL' || child.tagName === 'OL') return true
      if (child.tagName !== 'LI') return false

      if (isStyledListItem(child)) return true

      return Array.from(child.childNodes).some(nested =>
        nested instanceof HTMLElement && (nested.tagName === 'UL' || nested.tagName === 'OL')
      )
    })
  }

  unwrapListWrappers(doc.body)
  normalizeStyledListGroups(doc.body)

  const normalizeSoftWrappedText = (text) => {
    const lines = text.split('\n')
    const out = []
    let buffer = []

    const flushBuffer = () => {
      if (!buffer.length) return
      const merged = buffer
        .join(' ')
        .replace(/\s{2,}/g, ' ')
        .trim()
      if (merged) out.push(merged)
      buffer = []
    }

    const isStructuralLine = (line) => {
      const t = line.trim()
      if (!t) return true
      return /^(#{1,6}\s+|[-*+]\s+|\d+\.\s+|>\s*|```|\|.*\||-{3,}$|!\[|\[[^\]]+\]:)/.test(t)
    }

    lines.forEach(line => {
      if (!line.trim()) {
        flushBuffer()
        out.push('')
        return
      }
      if (isStructuralLine(line)) {
        flushBuffer()
        out.push(line.trimEnd())
        return
      }
      buffer.push(line.trim())
    })

    flushBuffer()

    return out
      .join('\n')
      .replace(/\n{3,}/g, '\n\n')
  }

  const renderChildren = (node) => {
    let out = ''
    node.childNodes.forEach(child => {
      out += renderNode(child)
    })
    return out
  }

  const getSingleListChild = (node) => {
    if (!(node instanceof HTMLElement)) return null

    const meaningful = Array.from(node.childNodes).filter(child => {
      if (child.nodeType === Node.TEXT_NODE) {
        return Boolean((child.textContent || '').trim())
      }
      return child instanceof HTMLElement
    })

    if (meaningful.length !== 1) return null
    const onlyChild = meaningful[0]
    return onlyChild instanceof HTMLElement && ['UL', 'OL'].includes(onlyChild.tagName) ? onlyChild : null
  }

  const renderListItem = (listItem, depth, index, isOrdered) => {
    const inlineParts = []
    const nestedBlocks = []

    listItem.childNodes.forEach(child => {
      if (child instanceof HTMLElement) {
        const tag = child.tagName.toLowerCase()
        if (tag === 'ul') {
          nestedBlocks.push(renderList(child, depth + 1))
          return
        }
        if (tag === 'ol') {
          nestedBlocks.push(renderList(child, depth + 1))
          return
        }
      }

      inlineParts.push(renderNode(child))
    })

    const marker = isOrdered ? `${index}. ` : '- '
    const text = inlineParts
      .join('')
      .replace(/\n+/g, ' ')
      .replace(/\s{2,}/g, ' ')
      .trim()
    const prefix = `${'    '.repeat(Math.max(0, depth - 1))}${marker}`
    const lines = [`${prefix}${text}`.trimEnd()]

    nestedBlocks.forEach(block => {
      const trimmed = block.trimEnd()
      if (trimmed) {
        lines.push(trimmed)
      }
    })

    return lines.join('\n')
  }

  const renderList = (listNode, depth = 1) => {
    const isOrdered = getListTag(listNode) === 'OL'
    let index = Number(listNode.getAttribute('start') || 1)
    const lines = []

    listNode.childNodes.forEach(child => {
      if (!(child instanceof HTMLElement) || child.tagName.toLowerCase() !== 'li') return
      lines.push(renderListItem(child, depth, index, isOrdered))
      index += 1
    })

    return lines.filter(Boolean).join('\n') + '\n\n'
  }

  const getTableCellAlignment = (cell) => {
    if (!(cell instanceof HTMLElement)) return ''

    const alignAttr = String(cell.getAttribute('align') || '').trim().toLowerCase()
    if (alignAttr === 'left' || alignAttr === 'center' || alignAttr === 'right') {
      return alignAttr
    }

    const styleAlign = String(cell.style?.textAlign || '').trim().toLowerCase()
    if (styleAlign === 'left' || styleAlign === 'center' || styleAlign === 'right') {
      return styleAlign
    }

    return ''
  }

  const tableAlignmentMarker = (alignment) => {
    if (alignment === 'left') return ':---'
    if (alignment === 'center') return ':---:'
    if (alignment === 'right') return '---:'
    return '---'
  }

  const normalizeTableCell = (text) => {
    return String(text || '')
      .replace(/\u00a0/g, ' ')
      .replace(/\n+/g, ' ')
      .replace(/\|/g, '\\|')
      .replace(/\s{2,}/g, ' ')
      .trim()
  }

  const renderTable = (tableNode) => {
    if (!(tableNode instanceof HTMLTableElement)) return ''

    const rows = []
    const directSections = Array.from(tableNode.children).filter(child =>
      child instanceof HTMLElement && ['THEAD', 'TBODY', 'TFOOT'].includes(child.tagName)
    )

    if (directSections.length > 0) {
      directSections.forEach(section => {
        Array.from(section.children).forEach(row => {
          if (row instanceof HTMLTableRowElement) {
            rows.push(row)
          }
        })
      })
    } else {
      Array.from(tableNode.children).forEach(child => {
        if (child instanceof HTMLTableRowElement) {
          rows.push(child)
        }
      })
    }

    const parsedRows = rows
      .map(row => Array.from(row.children).filter(cell =>
        cell instanceof HTMLTableCellElement
      ))
      .filter(cells => cells.length > 0)

    if (!parsedRows.length) return ''

    const columnCount = parsedRows.reduce((max, row) => Math.max(max, row.length), 0)
    if (!columnCount) return ''

    const alignments = Array.from({ length: columnCount }, () => '')
    parsedRows.forEach(row => {
      for (let i = 0; i < columnCount; i += 1) {
        if (alignments[i]) continue
        const cell = row[i]
        const alignment = getTableCellAlignment(cell)
        if (alignment) alignments[i] = alignment
      }
    })

    const rowToMarkdownCells = (rowCells = []) => {
      const cells = []
      for (let i = 0; i < columnCount; i += 1) {
        const cell = rowCells[i]
        const content = cell ? normalizeTableCell(renderChildren(cell)) : ''
        cells.push(content)
      }
      return cells
    }

    const headerCells = rowToMarkdownCells(parsedRows[0])
    const separatorCells = alignments.map(tableAlignmentMarker)
    const bodyRows = parsedRows.slice(1).map(row => rowToMarkdownCells(row))

    const lines = [
      `| ${headerCells.join(' | ')} |`,
      `| ${separatorCells.join(' | ')} |`,
      ...bodyRows.map(cells => `| ${cells.join(' | ')} |`)
    ]

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
    if (tag === 'pre') {
      const codeText = (node.textContent || '').replace(/\u00a0/g, ' ').trimEnd()
      return codeText ? `\`\`\`\n${codeText}\n\`\`\`\n\n` : ''
    }
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
    if (tag === 'table') return renderTable(node)
    if (tag === 'ul' || tag === 'ol') return renderList(node, getListLevel(node, 1))
    if (tag === 'li') return `${renderChildren(node).trim()}\n`
    if (tag === 'div' && node.classList.contains('sd-snippet-ref')) {
      const snippetId = node.getAttribute('data-snippet-id')
      if (snippetId) {
        return `<div class="sd-snippet-ref" data-snippet-id="${snippetId}"></div>\n\n`
      }
    }
    if (tag === 'p' || tag === 'div') {
      const singleListChild = getSingleListChild(node)
      if (singleListChild) {
        return renderList(singleListChild, getListLevel(node, getListLevel(singleListChild, 1)))
      }
      return `${renderChildren(node).trim()}\n\n`
    }

    return renderChildren(node)
  }

  const markdown = renderChildren(doc.body)
    .replace(/\u00a0/g, ' ')
    .replace(/[ \t]+\n/g, '\n')
    .replace(/\n{3,}/g, '\n\n')

  return normalizeSoftWrappedText(markdown).trim()
}
