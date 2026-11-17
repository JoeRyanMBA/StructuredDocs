import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import test, { after } from 'node:test'
import { parse } from '@vue/compiler-sfc'
import { JSDOM } from 'jsdom'

const dom = new JSDOM('<!doctype html><html><body></body></html>')
globalThis.window = dom.window
globalThis.document = dom.window.document
globalThis.Document = dom.window.Document
globalThis.Element = dom.window.Element
globalThis.SVGElement = dom.window.SVGElement
const { createApp, compile, nextTick } = await import('vue')

globalThis.brandingPreviewTest = {
  fetchExportBrandingAssetBlob: async () => new Blob(['image']),
  toFriendlyAuthError: (error, fallback) => error.message || fallback,
}
const source = await readFile(new URL('../src/views/AdminSettings.vue', import.meta.url), 'utf8')
const { descriptor } = parse(source)
const script = `
  const { toFriendlyAuthError } = globalThis.brandingPreviewTest;
  const fetchExportBrandingAssetBlob = (...args) => globalThis.brandingPreviewTest.fetchExportBrandingAssetBlob(...args);
  ${descriptor.script.content.replace(/^import[\s\S]*?from ['"][^'"]+['"]\s*/gm, '')}
`
const { default: settings } = await import(`data:text/javascript;base64,${Buffer.from(script).toString('base64')}`)
settings.render = compile(descriptor.template.content)
settings.mounted = () => {}

function mountSettings() {
  const container = document.createElement('div')
  document.body.append(container)
  const app = createApp(settings)
  const vm = app.mount(container)
  vm.brandingAssets = [{ name: 'logo.png', used_by: [] }]
  return { app, vm, container }
}

after(() => {
  dom.window.close()
  delete globalThis.brandingPreviewTest
})

test('invalid image previews show recovery instructions and preserve the asset and selection', async context => {
  const revoked = []
  context.mock.method(URL, 'revokeObjectURL', url => revoked.push(url))
  const { app, vm, container } = mountSettings()
  try {
    vm.edits.export_html_logo = 'logo.png'
    vm.assetPreviewUrls['logo.png'] = 'blob:invalid'
    await nextTick()
    container.querySelector('.asset-thumb-image').dispatchEvent(new dom.window.Event('error'))
    await nextTick()

    assert.equal(container.querySelector('.asset-thumb-image'), null)
    assert.match(container.querySelector('[role="status"]').textContent, /Re-upload the original image/)
    assert.equal(vm.brandingAssets.length, 1)
    assert.equal(vm.edits.export_html_logo, 'logo.png')
    assert.deepEqual(revoked, ['blob:invalid'])
  } finally {
    app.unmount()
    container.remove()
  }
})

test('preview request failures are visible and a successful retry clears the error', async context => {
  context.mock.method(URL, 'createObjectURL', () => 'blob:valid')
  context.mock.method(URL, 'revokeObjectURL', () => {})
  const { app, vm, container } = mountSettings()
  try {
    const fetchMock = context.mock.method(globalThis.brandingPreviewTest, 'fetchExportBrandingAssetBlob', async () => {
      throw new Error('Preview failed')
    })
    await vm.ensureAssetPreviewUrl('logo.png')
    await nextTick()
    assert.match(container.querySelector('[role="status"]').textContent, /Preview failed/)
    assert.equal(vm.pendingAssetPreviews['logo.png'], undefined)

    fetchMock.mock.restore()
    await vm.ensureAssetPreviewUrl('logo.png')
    await nextTick()
    assert.equal(container.querySelector('[role="status"]'), null)
    assert.equal(container.querySelector('.asset-thumb-image').getAttribute('src'), 'blob:valid')
  } finally {
    app.unmount()
    container.remove()
  }
})
