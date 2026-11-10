import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import test from 'node:test'
import { compileStyle, parse } from '@vue/compiler-sfc'
import { JSDOM } from 'jsdom'

const source = await readFile(new URL('../src/views/BulkReviewPortal.vue', import.meta.url), 'utf8')
const { descriptor } = parse(source)
const scopeId = 'data-v-bulk-theme'
const localCss = descriptor.styles.map(style => style.content).join('\n')
const scopedCss = descriptor.styles.map(style => compileStyle({
  source: style.content,
  id: scopeId,
  scoped: style.scoped,
}).code).join('\n')
const sharedCss = await readFile(new URL('../src/assets/style.css', import.meta.url), 'utf8')
const editorCss = await readFile(new URL('../src/styles/review-editor.css', import.meta.url), 'utf8')

test('bulk portal uses defined shared theme tokens instead of its own palette', () => {
  assert.doesNotMatch(localCss, /#[\da-f]{3,8}\b|rgba?\(|hsla?\(/i)
  assert.doesNotMatch(localCss, /(?:^|\n)\.btn(?:-(?:primary|secondary|success|outline))?(?=[\s:{])/)
  for (const [, token] of localCss.matchAll(/var\((--[\w-]+)\)/g)) {
    assert.ok(sharedCss.includes(`${token}:`), `Shared token ${token} must exist`)
  }
})

test('bulk portal controls use shared button variants', () => {
  const template = descriptor.template.content
  assert.match(template, /activeView === 'read' \? 'btn-primary' : 'btn-secondary'/)
  assert.match(template, /activeView === 'edit' \? 'btn-primary' : 'btn-secondary'/)
  assert.match(template, /class="btn btn-outline btn-sm" @click="resetEdits"/)
  assert.match(template, /class="btn btn-success" :disabled="submitting \|\| !form.recommendation"/)
})

test('bulk portal resolves shared colors and responds to theme changes', () => {
  const tokens = Object.fromEntries([...sharedCss.matchAll(/(--[\w-]+):\s*([^;]+);/g)]
    .map(([, name, value]) => [name, value]))
  const resolveTokens = css => css.replace(/var\((--[\w-]+)\)/g, (_, name) => resolveTokens(tokens[name]))
  // JSDOM does not resolve custom properties in background shorthands.
  const themedCss = () => resolveTokens(`${sharedCss}\n${editorCss}\n${scopedCss}`)
  const dom = new JSDOM(`<style>${themedCss()}</style>
    <div class="bulk-review-portal" ${scopeId}>
      <header class="portal-header" ${scopeId}></header>
      <button class="btn btn-primary" ${scopeId}>Continue</button>
      <button class="btn btn-secondary" ${scopeId}>Previous</button>
      <button class="btn btn-success" ${scopeId}>Send</button>
      <div class="editor-section review-editor-theme" ${scopeId}>
        <div class="ql-toolbar ql-snow"><button class="ql-active"><svg><path class="ql-stroke"></path></svg></button></div>
      </div>
    </div>`)
  try {
    const { document, getComputedStyle } = dom.window
    const background = selector => getComputedStyle(document.querySelector(selector)).backgroundColor
    assert.equal(background('.portal-header'), 'rgb(0, 91, 110)')
    assert.equal(background('.btn-primary'), 'rgb(0, 91, 110)')
    assert.equal(background('.btn-secondary'), 'rgb(233, 236, 239)')
    assert.equal(background('.btn-success'), 'rgb(46, 204, 113)')
    assert.equal(
      getComputedStyle(document.querySelector('.ql-stroke')).stroke,
      'rgb(0, 91, 110)'
    )
    tokens['--primary-deep-teal'] = '#123456'
    document.querySelector('style').textContent = themedCss()
    assert.equal(background('.portal-header'), 'rgb(18, 52, 86)')
    assert.equal(background('.btn-primary'), 'rgb(18, 52, 86)')
  } finally {
    dom.window.close()
  }
})

test('single-review portal uses shared tokens, button variants, and editor styles', async () => {
  const source = await readFile(new URL('../src/views/ReviewPortal.vue', import.meta.url), 'utf8')
  const { descriptor } = parse(source)
  const css = descriptor.styles.map(style => style.content).join('\n')
  assert.doesNotMatch(css, /#[\da-f]{3,8}\b|rgba?\(|hsla?\(/i)
  assert.doesNotMatch(css, /(?:^|\n)\.btn(?:-(?:primary|secondary|success|outline))?(?=[\s:{])/)
  for (const [, token] of css.matchAll(/var\((--[\w-]+)[,)]/g)) {
    assert.ok(sharedCss.includes(`${token}:`), `Shared token ${token} must exist`)
  }
  assert.match(source, /import '@\/styles\/review-editor\.css'/)
  assert.match(descriptor.template.content, /class="quill-wrapper review-editor-theme review-image-content"/)
  assert.match(descriptor.template.content, /activeView === 'read' \? 'btn-primary' : 'btn-secondary'/)
  assert.match(descriptor.template.content, /activeView === 'edit' \? 'btn-primary' : 'btn-secondary'/)
})
