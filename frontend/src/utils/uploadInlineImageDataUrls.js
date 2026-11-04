const INLINE_IMAGE_DATA_URL = /data:(image\/[a-z0-9.+-]+);base64,([a-z0-9+/=\r\n]+)/gi

const IMAGE_EXTENSIONS = {
  'image/png': 'png',
  'image/jpeg': 'jpg',
  'image/jpg': 'jpg',
  'image/gif': 'gif',
  'image/bmp': 'bmp',
  'image/x-ms-bmp': 'bmp',
  'image/webp': 'webp',
  'image/svg+xml': 'svg',
}

export async function uploadInlineImageDataUrls(content, uploadImage) {
  const uploadedUrls = new Map()

  for (const match of content.matchAll(INLINE_IMAGE_DATA_URL)) {
    const dataUrl = match[0]
    if (uploadedUrls.has(dataUrl)) continue

    const mimeType = match[1].toLowerCase()
    const extension = IMAGE_EXTENSIONS[mimeType]
    if (!extension) {
      throw new Error(`Unsupported embedded image type: ${mimeType}`)
    }

    const publicUrl = await uploadImage({
      mimeType,
      extension,
      base64: match[2].replace(/\s/g, ''),
    })
    if (!publicUrl) {
      throw new Error('Image upload succeeded but no image URL was returned.')
    }

    uploadedUrls.set(dataUrl, publicUrl)
  }

  return content.replace(INLINE_IMAGE_DATA_URL, dataUrl => uploadedUrls.get(dataUrl) || dataUrl)
}
