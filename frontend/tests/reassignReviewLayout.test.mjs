import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import test from 'node:test'
import { parse as parseTemplate } from '@vue/compiler-dom'
import { compileStyle, parse } from '@vue/compiler-sfc'
import { JSDOM } from 'jsdom'

const source = await readFile(new URL('../src/views/ReviewsDashboard.vue', import.meta.url), 'utf8')
const { descriptor } = parse(source)
const scopeId = 'data-v-reassign-layout'
const modalCss = await readFile(new URL('../src/styles/modal.css', import.meta.url), 'utf8')
const globalStyles = await Promise.all([
  '../node_modules/bootstrap/dist/css/bootstrap.min.css',
  '../src/assets/style.css',
  '../src/style.css',
].map(async path => (await readFile(new URL(path, import.meta.url), 'utf8'))
  .replace(/@import[^;]+;/g, modalCss)))
const scopedStyles = descriptor.styles.map(style => compileStyle({
  source: style.content,
  id: scopeId,
  scoped: style.scoped,
}).code)

function findActions(node) {
  if (node.props?.some(prop => prop.name === 'class' && prop.value?.content === 'reassign-actions')) {
    return node
  }
  for (const child of node.children || []) {
    const actions = findActions(child)
    if (actions) return actions
  }
}

const actions = findActions(parseTemplate(descriptor.template.content))
assert.ok(actions)

for (const state of ['enabled', 'disabled', 'cancel-hover', 'confirm-hover', 'confirm-active']) {
  test(`reassign actions retain equal heights and no vertical offsets: ${state}`, () => {
    const dom = new JSDOM(`<style>${[...globalStyles, ...scopedStyles].join('\n')}</style><div class="reassign-modal">${actions.loc.source}</div>`)
    try {
      for (const element of dom.window.document.querySelectorAll('body *')) {
        element.setAttribute(scopeId, '')
      }
      for (const sheet of dom.window.document.styleSheets) {
        for (const rule of sheet.cssRules) {
          if (rule.selectorText) {
            rule.selectorText = rule.selectorText
              .replaceAll(':hover', '.test-hover')
              .replaceAll(':active', '.test-active')
          }
        }
      }
      const [cancel, confirm] = dom.window.document.querySelectorAll('button')
      confirm.disabled = state === 'disabled'
      if (state === 'cancel-hover') cancel.classList.add('test-hover')
      if (state === 'confirm-hover') confirm.classList.add('test-hover')
      if (state === 'confirm-active') confirm.classList.add('test-active')

      for (const button of [cancel, confirm]) {
        const computed = dom.window.getComputedStyle(button)
        assert.equal(computed.height, '36px')
        assert.equal(computed.marginTop, '0px')
        assert.equal(computed.marginBottom, '0px')
        assert.equal(computed.transform, 'none')
      }
    } finally {
      dom.window.close()
    }
  })
}