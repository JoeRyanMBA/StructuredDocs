/**
 * Convert an HTML string to Markdown.
 * Shared by TopicEditor and SnippetsLibrary.
 */
export function htmlToMarkdown(html) {
  const parser = new DOMParser()
  const doc = parser.parseFromString(html || '', 'text/html')
  const getListLevel = (node) => {
    if (!(node instanceof HTMLElement)) return 1
    const parsed = Number(node.dataset.listLevel || 1)
    return Number.isFinite(parsed) && parsed > 0 ? parsed : 1
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

  const collectListEntries = (listNode, tagName, inheritedLevel = 1, entries = []) => {
    Array.from(listNode.children).forEach(child => {
      if (!(child instanceof HTMLLIElement)) return

      const level = Math.max(1, getListLevel(child) || inheritedLevel)
      const item = cleanListItem(child)
      if (item) {
        entries.push({ level, item })
      }

      Array.from(child.children).forEach(nested => {
        if (nested instanceof HTMLElement && nested.tagName === tagName) {
          collectListEntries(nested, tagName, level + 1, entries)
        }
      })
    })

    return entries
  }

  const buildSemanticList = (entries, tagName) => {
    const root = createSemanticList(tagName)
    const stack = [{ level: 1, list: root, lastItem: null }]

    const ensureLevel = (rawTargetLevel) => {
      const targetLevel = Math.max(1, Math.min(rawTargetLevel, stack.length + 1))

      while (stack.length > targetLevel) {
        stack.pop()
      }

      while (stack.length < targetLevel) {
        const parent = stack[stack.length - 1]
        if (!(parent?.lastItem instanceof HTMLElement)) {
          break
        }
        const nestedList = createSemanticList(tagName)
        parent.lastItem.appendChild(nestedList)
        stack.push({ level: stack.length + 1, list: nestedList, lastItem: null })
      }
    }

    entries.forEach(({ level, item }) => {
      ensureLevel(level)
      const entry = stack[stack.length - 1]
      if (!entry || !(item instanceof HTMLElement)) return
      entry.list.appendChild(item)
      entry.lastItem = item
    })

    return root
  }

  const normalizeStyledListGroups = (container) => {
    const nodes = Array.from(container.childNodes)
    let index = 0

    while (index < nodes.length) {
      const current = nodes[index]
      if (!(current instanceof HTMLElement) || !['UL', 'OL'].includes(current.tagName)) {
        index += 1
        continue
      }

      const tagName = current.tagName
      const listNodes = [current]
      const spacerNodes = []
      let cursor = index + 1

      while (cursor < nodes.length) {
        const node = nodes[cursor]
        if (node.nodeType === Node.TEXT_NODE && !(node.textContent || '').trim()) {
          spacerNodes.push(node)
          cursor += 1
          continue
        }
        if (node instanceof HTMLElement && node.tagName === tagName) {
          listNodes.push(node)
          cursor += 1
          continue
        }
        break
      }

      const hasStyledLevels = listNodes.some(listNode =>
        Array.from(listNode.children).some(child => child instanceof HTMLElement && isStyledListItem(child))
      )

      if (hasStyledLevels) {
        const entries = listNodes.flatMap(listNode => collectListEntries(listNode, tagName))
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
    const isOrdered = listNode.tagName.toLowerCase() === 'ol'
    let index = Number(listNode.getAttribute('start') || 1)
    const lines = []

    listNode.childNodes.forEach(child => {
      if (!(child instanceof HTMLElement) || child.tagName.toLowerCase() !== 'li') return
      lines.push(renderListItem(child, depth, index, isOrdered))
      index += 1
    })

    return lines.filter(Boolean).join('\n') + '\n\n'
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
    if (tag === 'ul' || tag === 'ol') return renderList(node)
    if (tag === 'li') return `${renderChildren(node).trim()}\n`
    if (tag === 'div' && node.classList.contains('sd-snippet-ref')) {
      const snippetId = node.getAttribute('data-snippet-id')
      if (snippetId) {
        return `<div class="sd-snippet-ref" data-snippet-id="${snippetId}"></div>\n\n`
      }
    }
    if (tag === 'p' || tag === 'div') return `${renderChildren(node).trim()}\n\n`

    return renderChildren(node)
  }

  const markdown = renderChildren(doc.body)
    .replace(/\u00a0/g, ' ')
    .replace(/[ \t]+\n/g, '\n')
    .replace(/\n{3,}/g, '\n\n')

  return normalizeSoftWrappedText(markdown).trim()
}
