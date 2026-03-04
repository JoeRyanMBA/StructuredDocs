import DOMPurify from 'dompurify'

/**
 * Sanitize an HTML string using DOMPurify.
 * Strips script tags, event handlers, and other XSS vectors while preserving
 * legitimate formatting from TinyMCE/Quill.
 *
 * @param {string} dirty - Raw HTML string
 * @returns {string} Sanitized HTML safe for v-html
 */
export function sanitizeHtml(dirty) {
  if (!dirty) return ''
  return DOMPurify.sanitize(dirty, {
    USE_PROFILES: { html: true },
    FORBID_TAGS: ['script', 'iframe', 'object', 'embed', 'form'],
    FORBID_ATTR: ['onerror', 'onload', 'onclick', 'onmouseover'],
  })
}
