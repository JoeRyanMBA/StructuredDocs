import assert from 'node:assert/strict'
import test from 'node:test'
import { uploadInlineImageDataUrls } from '../src/utils/uploadInlineImageDataUrls.js'

test('uploads embedded images in Markdown and HTML and reuses duplicate uploads', async () => {
  const dataUrl = 'data:image/jpeg;base64,aGVs\nbG8='
  const content = `![First](${dataUrl})\n<img src="${dataUrl}" alt="" data-sd-image-size="original">`
  const uploads = []

  const rewritten = await uploadInlineImageDataUrls(content, async image => {
    uploads.push(image)
    return '/images/pasted-image.jpg'
  })

  assert.equal(uploads.length, 1)
  assert.deepEqual(uploads[0], {
    mimeType: 'image/jpeg',
    extension: 'jpg',
    base64: 'aGVsbG8=',
  })
  assert.equal(
    rewritten,
    '![First](/images/pasted-image.jpg)\n'
    + '<img src="/images/pasted-image.jpg" alt="" data-sd-image-size="original">'
  )
})

test('does not silently retain embedded image types the upload endpoint cannot store', async () => {
  let uploadCalled = false

  await assert.rejects(
    uploadInlineImageDataUrls('![Image](data:image/avif;base64,YQ==)', async () => {
      uploadCalled = true
      return '/images/image.avif'
    }),
    /Unsupported embedded image type: image\/avif/
  )
  assert.equal(uploadCalled, false)
})
