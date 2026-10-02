import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import test from 'node:test'
import { compileScript, parse } from '@vue/compiler-sfc'
import { JSDOM } from 'jsdom'

const dom = new JSDOM('<!doctype html><html><body></body></html>')
globalThis.window = dom.window
globalThis.document = dom.window.document
globalThis.Node = dom.window.Node
globalThis.Element = dom.window.Element
globalThis.HTMLElement = dom.window.HTMLElement

const source = await readFile(new URL('../src/components/RichTextEditor.vue', import.meta.url), 'utf8')
const { descriptor } = parse(source)
const compiledScript = compileScript(descriptor, { id: 'rich-text-editor-image-test' }).content
const componentUrl = `data:text/javascript;base64,${Buffer.from(compiledScript).toString('base64')}`
const { default: richTextEditor } = await import(componentUrl)

function createEditorHarness() {
  const editor = document.createElement('div')
  editor.innerHTML = '<p><img src="/image.png" width="600" height="400"> text</p>'
  document.body.append(editor)

  const updates = []
  const instance = {
    ...richTextEditor.data(),
    $refs: { editorEl: editor },
    $emit: (_event, value) => updates.push(value),
  }
  for (const [name, method] of Object.entries(richTextEditor.methods)) {
    instance[name] = method.bind(instance)
  }
  instance.refreshTableContext = () => {}

  return { editor, image: editor.querySelector('img'), instance, updates }
}

test('selected images retain size, alignment, and wrapping choices in emitted HTML', () => {
  const { editor, image, instance, updates } = createEditorHarness()

  instance.onEditorClick({ target: image })
  assert.equal(instance.imageContext.selected, true)

  instance.applyImageOption('size', 'full')
  assert.equal(image.style.width, '100%')
  assert.equal(image.dataset.sdImageSize, 'full')
  assert.equal(instance.imageContext.wrapping, 'none')

  instance.applyImageOption('size', 'original')
  assert.equal(image.style.width, '')
  assert.equal(image.getAttribute('width'), null)
  assert.equal(image.getAttribute('height'), null)

  instance.applyImageOption('alignment', 'center')
  assert.equal(image.style.marginLeft, 'auto')
  assert.equal(image.style.marginRight, 'auto')
  assert.equal(image.dataset.sdImageAlignment, 'center')

  instance.applyImageOption('wrapping', 'text-left')
  assert.equal(image.style.float, 'right')
  assert.equal(image.dataset.sdImageWrapping, 'text-left')

  instance.applyImageOption('wrapping', 'text-right')
  assert.equal(image.style.float, 'left')
  assert.equal(image.dataset.sdImageWrapping, 'text-right')

  instance.applyImageOption('wrapping', 'watermark')
  assert.equal(image.style.position, 'absolute')
  assert.equal(image.style.zIndex, '-1')
  assert.equal(image.style.opacity, '0.18')
  assert.equal(image.dataset.sdImageWrapping, 'watermark')

  instance.applyImageOption('alignment', 'center')
  assert.equal(instance.imageContext.alignment, 'center')
  assert.equal(image.style.left, '50%')
  assert.equal(image.style.transform, 'translateX(-50%)')

  instance.applyImageOption('alignment', 'right')
  assert.equal(instance.imageContext.alignment, 'right')
  assert.equal(image.style.left, '100%')
  assert.equal(image.style.transform, 'translateX(-100%)')

  instance.applyImageOption('alignment', 'left')
  assert.equal(image.style.left, '0px')
  assert.equal(image.style.transform, '')

  instance.applyImageOption('size', 'full')
  assert.equal(instance.imageContext.wrapping, 'watermark')
  assert.equal(image.style.width, '100%')

  instance.applyImageOption('size', 'original')
  assert.equal(instance.imageContext.wrapping, 'watermark')
  assert.equal(image.style.width, '')

  instance.applyImageOption('wrapping', 'none')
  assert.equal(image.style.float, '')
  assert.equal(image.style.position, '')
  assert.doesNotMatch(image.getAttribute('style'), /float/)
  assert.equal(image.dataset.sdImageWrapping, 'none')
  assert.match(updates.at(-1), /data-sd-image-size="original"/)
  assert.match(updates.at(-1), /data-sd-image-alignment="left"/)
  assert.match(updates.at(-1), /data-sd-image-wrapping="none"/)
  assert.equal(editor.querySelector('img'), image)
})

test('image size presets persist percentage widths in emitted HTML', () => {
  const { image, instance, updates } = createEditorHarness()

  instance.onEditorClick({ target: image })
  for (const size of ['25%', '50%', '75%']) {
    instance.applyImageOption('size', size)
    assert.equal(image.style.width, size)
    assert.equal(image.style.height, 'auto')
    assert.equal(image.dataset.sdImageSize, size)
    assert.match(updates.at(-1), new RegExp(`data-sd-image-size="${size}"`))
  }
})

test('drag resizing stores a custom width and maintains image aspect ratio', () => {
  const { image, instance, updates } = createEditorHarness()
  const parent = image.parentElement
  Object.defineProperty(parent, 'clientWidth', { configurable: true, value: 400 })
  image.getBoundingClientRect = () => ({ width: 200, height: 100, right: 200, bottom: 100 })

  instance.onEditorClick({ target: image })
  instance.startImageResize({ clientX: 200, clientY: 100 })
  instance.onImageResizeMove({ clientX: 240, clientY: 120 })

  assert.equal(image.style.width, '240px')
  assert.equal(image.style.height, 'auto')
  assert.equal(image.dataset.sdImageSize, 'custom')
  instance.finishImageResize()
  assert.match(updates.at(-1), /data-sd-image-size="custom"/)
  assert.match(updates.at(-1), /width: 240px/)
})