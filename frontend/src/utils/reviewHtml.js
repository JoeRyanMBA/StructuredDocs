const MEANINGFUL_VOID_TAGS = new Set([
  'img',
  'hr',
  'iframe',
  'video',
  'audio',
  'canvas',
  'svg',
  'table',
  'embed',
  'object',
])

function hasMeaningfulContent(node) {
  if (!node) return false

  if (node.nodeType === Node.TEXT_NODE) {
    return Boolean((node.textContent || '').replace(/\u00a0/g, ' ').trim())
  }

  if (node.nodeType !== Node.ELEMENT_NODE) {
    return false
  }

  const tagName = node.tagName.toLowerCase()
  if (MEANINGFUL_VOID_TAGS.has(tagName)) return true
  if (tagName === 'br') return false

  return Array.from(node.childNodes).some(child => hasMeaningfulContent(child))
}

function isIgnorableTrailingNode(node) {
  if (!node) return false

  if (node.nodeType === Node.TEXT_NODE) {
    return !((node.textContent || '').replace(/\u00a0/g, ' ').trim())
  }

  if (node.nodeType !== Node.ELEMENT_NODE) {
    return true
  }

  return !hasMeaningfulContent(node)
}

export function normalizeReviewHtml(html) {
  if (!html) return ''

  const doc = new DOMParser().parseFromString(`<div>${html}</div>`, 'text/html')
  const container = doc.body.firstElementChild
  if (!container) return ''

  while (container.lastChild && isIgnorableTrailingNode(container.lastChild)) {
    container.removeChild(container.lastChild)
  }

  return container.innerHTML.trim()
}

