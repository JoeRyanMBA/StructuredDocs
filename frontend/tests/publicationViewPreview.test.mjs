import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import test from 'node:test'
import { parse } from '@vue/compiler-sfc'
import { JSDOM } from 'jsdom'
import createDOMPurify from 'dompurify'
import { renderCollectionTopic } from '../src/utils/collectionPreview.js'

const source = await readFile(new URL('../src/views/PublicationView.vue', import.meta.url), 'utf8')
const { descriptor } = parse(source)
const { window } = new JSDOM('<!doctype html><html><body></body></html>')
globalThis.document = window.document
const purifier = createDOMPurify(window)
const snippets = {
  1: { content: 'Trainer-only guidance', tags: [{ id: 7 }] },
}
globalThis.publicationViewPreviewTest = {
  apiGet: async () => [],
  getSnippetImpl: async id => snippets[id],
  getSnippet: (...args) => globalThis.publicationViewPreviewTest.getSnippetImpl(...args),
  getPublication: async () => ({}),
  downloadMobileKnowledgeBase: async () => {},
  downloadPublicationPdf: async () => {},
  previewMobileKnowledgeBase: async () => {},
  renderCollectionTopic,
  sanitizeHtml: html => purifier.sanitize(html),
  PublicationNodeView: {},
}
const script = `
  const {
    apiGet, getSnippet, getPublication, downloadMobileKnowledgeBase,
    downloadPublicationPdf, previewMobileKnowledgeBase, renderCollectionTopic,
    sanitizeHtml, PublicationNodeView,
  } = globalThis.publicationViewPreviewTest;
  ${descriptor.script.content.replace(/^import .*$/gm, '')}
`
const { default: component } = await import(`data:text/javascript;base64,${Buffer.from(script).toString('base64')}`)

function createView(overrides = {}) {
  const view = {
    ...component.data(),
    selectedNode: {
      content: '<div class="sd-snippet-ref" data-snippet-id="1">Placeholder</div>',
    },
    selectedTagIds: [],
    ...overrides,
  }
  for (const [name, method] of Object.entries(component.methods)) view[name] = method.bind(view)
  return view
}

test('publication preview applies audience selections and rerenders when they change', async () => {
  const view = createView()

  await view.renderSelectedContent()
  assert.doesNotMatch(view.renderedContent, /Trainer-only guidance|Placeholder/)

  view.selectedTagIds.push(7)
  assert.equal(component.watch.selectedTagIds.deep, true)
  await component.watch.selectedTagIds.handler.call(view)
  await new Promise(resolve => setImmediate(resolve))
  assert.match(view.renderedContent, /Trainer-only guidance/)
  assert.doesNotMatch(view.renderedContent, /Placeholder/)
})

test('publication preview reports snippet loading failures', async () => {
  const original = globalThis.publicationViewPreviewTest.getSnippetImpl
  globalThis.publicationViewPreviewTest.getSnippetImpl = async () => {
    throw new Error('Snippet unavailable')
  }
  try {
    const view = createView({ selectedTagIds: [7] })
    await view.renderSelectedContent()
    assert.equal(view.previewError, 'Snippet unavailable')
    assert.equal(view.previewLoading, false)
  } finally {
    globalThis.publicationViewPreviewTest.getSnippetImpl = original
    window.close()
  }
})
