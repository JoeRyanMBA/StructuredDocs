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

function unwrapNode(node) {
  if (!node?.parentNode) return
  while (node.firstChild) {
    node.parentNode.insertBefore(node.firstChild, node)
  }
  node.remove()
}

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

function normalizeListMarkup(container) {
  container.querySelectorAll('.ql-ui').forEach((node) => node.remove())

  container.querySelectorAll('[contenteditable]').forEach((node) => {
    node.removeAttribute('contenteditable')
  })

  container.querySelectorAll('[data-list]').forEach((node) => {
    node.removeAttribute('data-list')
  })

  container.querySelectorAll('li').forEach((item) => {
    Array.from(item.children).forEach((child) => {
      const tagName = child.tagName?.toLowerCase()
      if (tagName === 'p' || tagName === 'div') {
        unwrapNode(child)
      }
    })

    Array.from(item.childNodes).forEach((child) => {
      if (
        child.nodeType === Node.ELEMENT_NODE &&
        child.tagName.toLowerCase() === 'span' &&
        !child.attributes.length &&
        !hasMeaningfulContent(child)
      ) {
        child.remove()
      }
    })
  })
}

export function normalizeReviewHtml(html) {
  if (!html) return ''

  const doc = new DOMParser().parseFromString(`<div>${html}</div>`, 'text/html')
  const container = doc.body.firstElementChild
  if (!container) return ''

  normalizeListMarkup(container)

  while (container.lastChild && isIgnorableTrailingNode(container.lastChild)) {
    container.removeChild(container.lastChild)
  }

  return container.innerHTML.trim()
}
