export function resolveImageUrl(path, options = {}) {
  const { apiBase = '', apiBaseHost = '' } = options
  const raw = (path || '').trim()
  if (!raw) return ''

  const encodePathSegments = (value) => {
    return value
      .split('/')
      .map((segment, index) => {
        if (index === 0) return segment
        try {
          return encodeURIComponent(decodeURIComponent(segment))
        } catch (_e) {
          return encodeURIComponent(segment)
        }
      })
      .join('/')
  }

  if (raw.startsWith('http://') || raw.startsWith('https://')) {
    try {
      const parsed = new URL(raw)
      const normalizedPath = encodePathSegments(parsed.pathname)
      const query = parsed.search || ''

      if (normalizedPath.startsWith('/images/')) {
        return apiBaseHost ? `${apiBaseHost}${normalizedPath}${query}` : `${normalizedPath}${query}`
      }

      return `${parsed.origin}${normalizedPath}${query}`
    } catch (_e) {
      return raw
    }
  }

  if (raw.startsWith('images/')) {
    const normalized = `/${raw}`
    const encoded = encodePathSegments(normalized)
    return apiBaseHost ? `${apiBaseHost}${encoded}` : encoded
  }

  if (raw.startsWith('/images/')) {
    const encoded = encodePathSegments(raw)
    return apiBaseHost ? `${apiBaseHost}${encoded}` : encoded
  }

  if (raw.startsWith('/')) {
    const encoded = encodePathSegments(raw)
    return apiBase ? `${apiBase}${encoded}` : encoded
  }

  return encodePathSegments(raw)
}

export function getImageUrl(image, options = {}) {
  const importLike = Boolean(image?.document_id) ||
    (image?.public_url || '').includes('/images/imports/') ||
    (image?.file_path || '').includes('/images/imports/') ||
    image?.source === 'import'

  const path = image?.public_url ||
    image?.file_path ||
    (importLike && image?.document_id && image?.filename
      ? `/images/imports/${image.document_id}/${image.filename}`
      : (image?.filename ? `/images/${image.filename}` : ''))
  return resolveImageUrl(path, options)
}

export function getImageUrlCandidates(image, options = {}) {
  const candidates = []
  const importLike = Boolean(image?.document_id) ||
    (image?.public_url || '').includes('/images/imports/') ||
    (image?.file_path || '').includes('/images/imports/') ||
    image?.source === 'import'

  const addCandidate = (value) => {
    const url = resolveImageUrl(value, options)
    if (!url) return
    if (!candidates.includes(url)) {
      candidates.push(url)
    }
  }

  addCandidate(image?.public_url)
  addCandidate(image?.file_path)

  if (image?.document_id && image?.filename) {
    addCandidate(`/images/imports/${image.document_id}/${image.filename}`)
  }

  if (image?.filename && !importLike) {
    addCandidate(`/images/${image.filename}`)
  }

  return candidates
}

export function getRetryImageSrc(currentSrc, image, retryAttempted, options = {}) {
  const candidates = getImageUrlCandidates(image, options)
  const current = currentSrc || ''
  const currentIndex = candidates.findIndex((url) => current.includes(url))
  const nextIndex = currentIndex + 1

  if (nextIndex < candidates.length) {
    const nextUrl = candidates[nextIndex]
    const sep = nextUrl.includes('?') ? '&' : '?'
    return { src: `${nextUrl}${sep}retry=${Date.now()}`, shouldMarkRetried: false }
  }

  if (current && !retryAttempted) {
    const sep = current.includes('?') ? '&' : '?'
    return { src: `${current}${sep}retry=${Date.now()}`, shouldMarkRetried: true }
  }

  return null
}