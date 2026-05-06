/**
 * Convert an HTML string to Markdown.
 * Shared by TopicEditor and SnippetsLibrary.
 */
export function htmlToMarkdown(html) {
  const parser = new DOMParser()
  const doc = parser.parseFromString(html || '', 'text/html')
  const isStyledListItem = (node) => {
    if (!(node instanceof HTMLElement)) return false
    return Boolean(node.dataset.listLevel) || Boolean(node.style.marginLeft)
  }

  const sanitizeStyledList = (listNode) => {
    const clone = listNode.cloneNode(true)
    if (!(clone instanceof HTMLElement)) return ''

    clone.querySelectorAll('li').forEach(node => {
      if (!(node instanceof HTMLElement)) return
      if (!node.dataset.listLevel || node.dataset.listLevel === '1') {
        delete node.dataset.listLevel
      }
      if (!node.style.marginLeft) {
        node.style.removeProperty('margin-left')
      }
      if (!node.getAttribute('style')) {
        node.removeAttribute('style')
      }
    })

    return clone.outerHTML
  }

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
    if (tag === 'ul' || tag === 'ol') {
      if (Array.from(node.children).some(child => isStyledListItem(child))) {
        return `${sanitizeStyledList(node)}\n\n`
      }
      return renderList(node)
    }
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
