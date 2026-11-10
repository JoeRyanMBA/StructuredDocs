import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import test, { after, afterEach } from 'node:test'
import { parse } from '@vue/compiler-sfc'
import { JSDOM } from 'jsdom'

const { window } = new JSDOM('<!doctype html><html><body></body></html>', { pretendToBeVisual: true })
for (const name of ['window', 'document', 'Node', 'Element', 'HTMLElement', 'Text', 'DOMParser', 'MutationObserver']) {
  globalThis[name] = name === 'window' ? window : window[name]
}
globalThis.getComputedStyle = window.getComputedStyle.bind(window)

const [{ default: Quill }, { reactive, markRaw }, { normalizeReviewHtml }, { renderTopicMarkdown }, { sanitizeHtml }] = await Promise.all([
  import('quill'),
  import('vue'),
  import('../src/utils/reviewHtml.js'),
  import('../src/utils/topicMarkdown.js'),
  import('../src/utils/sanitize.js'),
])
const source = await readFile(new URL('../src/views/BulkReviewPortal.vue', import.meta.url), 'utf8')
const { descriptor } = parse(source)
const script = descriptor.script.content.replace(/^import .*$/gm, '').replace('export default', 'return')
const submissions = []
const editors = []
const component = new Function(
  'Quill', 'markRaw', 'HelpIcon', 'normalizeReviewHtml', 'renderTopicMarkdown', 'sanitizeHtml', 'submitBulkTopicFeedback',
  script
)(Quill, markRaw, {}, normalizeReviewHtml, renderTopicMarkdown, sanitizeHtml, async (...args) => {
  submissions.push(args)
  return { batch_complete: true, completed_count: 1 }
})

function createPortal() {
  document.body.innerHTML = '<div id="editor"></div>'
  const portal = reactive({
    ...component.data.call(component.methods),
    batch: { total: 1, topics: [{ review_id: 42, topic_content: 'Keep these words and remove these words.' }] },
    $route: { params: { token: 'test-token' } },
    $refs: { quillEditor: document.querySelector('#editor') },
  })
  for (const [name, method] of Object.entries(component.methods)) portal[name] = method.bind(portal)
  for (const [name, getter] of Object.entries(component.computed)) {
    Object.defineProperty(portal, name, { get: getter.bind(portal) })
  }
  portal.initQuill()
  editors.push(portal.quillInstance)
  portal.form.recommendation = 'approve_with_changes'
  return portal
}

afterEach(() => {
  for (const editor of editors.splice(0)) editor.scroll.observer.disconnect()
  window.getSelection().removeAllRanges()
})
after(() => window.close())

test('bulk reviewer word deletions are included in submitted feedback', async () => {
  const portal = createPortal()
  portal.quillInstance.deleteText(21, 'remove these words'.length, 'user')
  assert.equal(portal.currentHasEdits, true)
  await portal.submitCurrentFeedback()
  assert.equal(submissions.at(-1)[0], 'test-token')
  assert.equal(submissions.at(-1)[1], 42)
  assert.equal(submissions.at(-1)[2].recommendation, 'approve_with_changes')
  assert.equal(submissions.at(-1)[2].edited_content, '<p>Keep these words and .</p>')
})

test('native contenteditable deletions are captured by Quill before submission', async () => {
  const portal = createPortal()
  portal.quillInstance.root.querySelector('p').firstChild.textContent = 'Keep these words.'
  portal.quillInstance.update('user')
  assert.equal(portal.currentHasEdits, true)
  await portal.submitCurrentFeedback()
  assert.equal(submissions.at(-1)[2].edited_content, '<p>Keep these words.</p>')
})

test('saved edits survive reinitializing the editor after switching views', async () => {
  const portal = createPortal()
  portal.quillInstance.deleteText(21, 'remove these words'.length, 'user')
  component.watch.activeView.call(portal, 'read')
  document.body.innerHTML = '<div id="editor"></div>'
  portal.$refs.quillEditor = document.querySelector('#editor')
  portal.initQuill()
  editors.push(portal.quillInstance)
  assert.equal(portal.quillInstance.getText(), 'Keep these words and .\n')
  await portal.submitCurrentFeedback()
  assert.equal(submissions.at(-1)[2].edited_content, '<p>Keep these words and .</p>')
})

test('resetting reviewer edits submits no content changes', async () => {
  const portal = createPortal()
  portal.quillInstance.deleteText(21, 'remove these words'.length, 'user')
  portal.resetEdits()
  assert.equal(portal.currentHasEdits, false)
  assert.equal(portal.quillInstance.getText(), 'Keep these words and remove these words.\n')
  await portal.submitCurrentFeedback()
  assert.equal(Object.hasOwn(submissions.at(-1)[2], 'edited_content'), false)
})

test('opening the editor without editing submits no content changes', async () => {
  const portal = createPortal()
  assert.equal(portal.currentHasEdits, false)
  await portal.submitCurrentFeedback()
  assert.equal(Object.hasOwn(submissions.at(-1)[2], 'edited_content'), false)
})
