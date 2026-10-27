import assert from 'node:assert/strict'
import test from 'node:test'
import { JSDOM } from 'jsdom'
import createDOMPurify from 'dompurify'
import { renderCollectionTopic, substituteCollectionVariables } from '../src/utils/collectionPreview.js'

const { window } = new JSDOM('')
const purifier = createDOMPurify(window)
const snippets = {
  1: { content: 'Universal content', tags: [] },
  2: { content: 'Selected audience', tags: [{ id: 7 }] },
  3: { content: 'Other audience', tags: [{ id: 8 }] },
}
const reference = id => `<div class="sd-snippet-ref" data-snippet-id="${id}">Placeholder</div>`
const options = {
  document: window.document,
  sanitize: html => purifier.sanitize(html),
  getSnippet: async id => snippets[id],
  mapping: { product: 'Widget' },
  tagIds: [7],
}

test('renders full topic HTML with variables and matching audience snippets', async () => {
  const html = await renderCollectionTopic(`## {{product}}\n\n${'Full content '.repeat(50)}\n\n${reference(1)}\n\n${reference(2)}\n\n${reference(3)}`, options)
  assert.match(html, /<h2>Widget<\/h2>/)
  assert.match(html, /Universal content/)
  assert.match(html, /Selected audience/)
  assert.doesNotMatch(html, /Other audience|Placeholder/)
  assert.ok(html.length > 600)
})

test('no audience tags includes universal snippets only and strips unsafe HTML', async () => {
  const html = await renderCollectionTopic(`${reference(1)}\n\n${reference(2)}\n\n<img src="/image.png" onerror="alert(1)">`, { ...options, tagIds: [] })
  assert.match(html, /Universal content/)
  assert.doesNotMatch(html, /Selected audience|onerror/)
})

test('keeps unresolved variables visible', () => {
  assert.equal(substituteCollectionVariables('{{known}} {{unknown}}', { known: 'Resolved' }), 'Resolved {{unknown}}')
})

test('matches export ordering by substituting topic variables before inserting snippets', async () => {
  const html = await renderCollectionTopic(`{{product}}\n\n${reference(1)}`, {
    ...options, getSnippet: async () => ({ content: '{{product}}', tags: [] }),
  })
  assert.match(html, /Widget/)
  assert.match(html, /\{\{product\}\}/)
})

test('does not silently omit unavailable snippets', async () => {
  await assert.rejects(renderCollectionTopic(reference(99), {
    ...options, getSnippet: async () => { throw new Error('Snippet unavailable') },
  }), /Snippet unavailable/)
})