import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import test from 'node:test'
import { parse as parseTemplate } from '@vue/compiler-dom'
import { compileStyle, parse } from '@vue/compiler-sfc'
import { JSDOM } from 'jsdom'

const read = path => readFile(new URL(path, import.meta.url), 'utf8')
const [bootstrap, buttons, modal, layout, source] = await Promise.all([
  read('../node_modules/bootstrap/dist/css/bootstrap.min.css'),
  read('../src/assets/style.css'),
  read('../src/styles/modal.css'),
  read('../src/style.css'),
  read('../src/components/CollectionTopicPane.vue'),
])
const { descriptor } = parse(source)
const scopeId = 'data-v-button-styles'
const scoped = compileStyle({ source: descriptor.styles[0].content, id: scopeId, scoped: true })
assert.deepEqual(scoped.errors, [])

function findFooter(node) {
  if (node.props?.some(prop => prop.name === 'class' && prop.value?.content === 'modal-footer')) return node
  for (const child of node.children || []) {
    const result = findFooter(child)
    if (result) return result
  }
}

const footer = findFooter(parseTemplate(descriptor.template.content))
assert.ok(footer)

// jsdom does not resolve custom properties in computed styles.
const colors = {
  '--primary-deep-teal': '#005B6E',
  '--primary-medium-teal': '#008C9E',
  '--border-light-gray': '#E9ECEF',
  '--extended-seafoam-green': '#48C9B0',
}
const css = [bootstrap, buttons, layout.replace(/@import[^;]+;/, modal), scoped.code]
  .join('\n')
  .replace(/var\((--[\w-]+)\)/g, (value, name) => colors[name] || value)
  .replaceAll(':hover', '.test-hover')
  .replaceAll(':active', '.test-active')

test('unsaved topic modal uses the standard palette when enabled and saving', () => {
  const dom = new JSDOM(`<style>${css}</style>${footer.loc.source}`)
  try {
    const { document, getComputedStyle } = dom.window
    for (const element of document.querySelectorAll('body *')) element.setAttribute(scopeId, '')
    const [cancel, discard, save] = document.querySelectorAll('button')
    assert.equal(getComputedStyle(save).backgroundColor, 'rgb(0, 91, 110)')
    for (const button of [cancel, discard]) {
      assert.equal(getComputedStyle(button).backgroundColor, 'rgb(233, 236, 239)')
      assert.equal(getComputedStyle(button).color, 'rgb(0, 91, 110)')
    }
    save.classList.add('test-hover')
    assert.equal(getComputedStyle(save).backgroundColor, 'rgb(0, 140, 158)')
    save.classList.add('test-active')
    assert.equal(getComputedStyle(save).backgroundColor, 'rgb(0, 91, 110)')
    cancel.classList.add('test-hover', 'test-active')
    assert.equal(getComputedStyle(cancel).backgroundColor, 'rgb(233, 236, 239)')
    save.disabled = true
    assert.equal(getComputedStyle(save).backgroundColor, 'rgb(0, 91, 110)')
    assert.equal(getComputedStyle(save).opacity, '0.6')
  } finally {
    dom.window.close()
  }
})

test('disabled standard buttons retain their role colors outside modals', () => {
  const dom = new JSDOM(`<style>${css}</style>
    <button class="btn btn-primary" disabled>Save</button>
    <button class="btn btn-secondary" disabled>Cancel</button>`)
  try {
    const [save, cancel] = dom.window.document.querySelectorAll('button')
    assert.equal(dom.window.getComputedStyle(save).backgroundColor, 'rgb(0, 91, 110)')
    assert.equal(dom.window.getComputedStyle(cancel).backgroundColor, 'rgb(233, 236, 239)')
    assert.equal(dom.window.getComputedStyle(cancel).color, 'rgb(0, 91, 110)')
  } finally {
    dom.window.close()
  }
})
