/**
 * Convert an HTML string to Markdown.
 * Shared by TopicEditor and SnippetsLibrary.
 */
export function htmlToMarkdown(html) {
  const parser = new DOMParser()
  const doc = parser.parseFromString(html || '', 'text/html')

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

  const markdown = renderChildren(doc.body)
    .replace(/\u00a0/g, ' ')
    .replace(/[ \t]+\n/g, '\n')
    .replace(/\n{3,}/g, '\n\n')

  return normalizeSoftWrappedText(markdown).trim()
}
