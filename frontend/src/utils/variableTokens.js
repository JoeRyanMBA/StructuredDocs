export function generateVariableSlug(value) {
  const normalized = String(value || '')
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '_')
    .replace(/_+/g, '_')
    .replace(/^_+|_+$/g, '')
  if (!normalized) return 'variable'
  const slug = /^[a-z]/.test(normalized) ? normalized : `variable_${normalized}`
  return slug.slice(0, 100).replace(/[_-]+$/g, '')
}

export function sanitizeVariableSlug(value) {
  return String(value || '')
    .toLowerCase()
    .replace(/\s+/g, '_')
    .replace(/[^a-z0-9_-]/g, '')
    .replace(/^[^a-z]+/, '')
}

export function variableToken(slug) {
  return `{{${slug}}}`
}
