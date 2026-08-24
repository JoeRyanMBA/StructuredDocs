export function normalizePublicationIdValue(value) {
  const asString = String(value ?? '').trim()
  if (!asString) return ''

  const parsed = Number.parseInt(asString, 10)
  return Number.isFinite(parsed) && parsed > 0 ? String(parsed) : ''
}

export function resolveSelectedPublicationId(currentSelection, publications, searchTerm = '') {
  const selection = normalizePublicationIdValue(currentSelection)
  const rows = Array.isArray(publications) ? publications : []

  const filtered = rows.filter((pub) => {
    const term = (searchTerm || '').trim().toLowerCase()
    if (!term) return true

    const title = (pub?.title || '').toLowerCase()
    const idText = String(pub?.id ?? '').toLowerCase()
    return title.includes(term) || idText.includes(term)
  })

  if (selection && filtered.some((pub) => String(pub?.id) === selection)) {
    return selection
  }

  if (filtered.length === 1) {
    return String(filtered[0].id)
  }

  return ''
}
