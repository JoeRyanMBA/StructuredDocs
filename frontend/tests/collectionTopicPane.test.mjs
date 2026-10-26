import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import test from 'node:test'
import { parse } from '@vue/compiler-sfc'

const source = await readFile(new URL('../src/components/CollectionTopicPane.vue', import.meta.url), 'utf8')
const { descriptor } = parse(source)
const script = 'const TopicEditor = {};\n' + descriptor.script.content.replace(/^import .*$/gm, '')
const { default: component } = await import(`data:text/javascript;base64,${Buffer.from(script).toString('base64')}`)

function createPane(overrides = {}) {
  const events = []
  const pane = {
    ...component.data(), collectionBusy: false, attachTopic: async () => true,
    $emit: (...event) => events.push(event), $refs: {},
  }
  for (const [name, method] of Object.entries(component.methods)) pane[name] = method.bind(pane)
  for (const [name, getter] of Object.entries(component.computed)) {
    Object.defineProperty(pane, name, { get: getter.bind(pane) })
  }
  Object.assign(pane, { renderPreview: async () => {}, loadContext: async () => {}, ...overrides })
  return { pane, events }
}

test('canceling an empty new-topic draft restores the previous selection without saving', () => {
  const previous = { id: 1, title: 'Existing topic', content: 'Existing body' }
  const { pane } = createPane({ topic: previous })
  pane.newTopic()
  assert.equal(pane.creating, true)
  assert.equal(pane.topic.id, null)
  pane.requestPreview()
  assert.equal(pane.creating, false)
  assert.equal(pane.editing, false)
  assert.equal(pane.topic, previous)
})

test('saving a root topic attaches it once and returns to preview', async () => {
  const attached = []
  const { pane, events } = createPane({ attachTopic: async (...args) => { attached.push(args); return true } })
  pane.newTopic()
  pane.$refs.editor = { saveTopic: async () => ({ id: 10, title: 'New topic', content: 'Body' }) }
  assert.equal(await pane.saveEditor(), true)
  assert.equal(attached.length, 1)
  assert.equal(attached[0][0].id, 10)
  assert.equal(attached[0][1], null)
  assert.equal(pane.editing, false)
  assert.equal(pane.creating, false)
  assert.equal(pane.pendingAttachment, null)
  assert.equal(events.find(event => event[0] === 'selected')[1].id, 10)
})

test('new child topics retain the intended parent until first save', async () => {
  let attachedParent
  const { pane } = createPane({ attachTopic: async (topic, parentId) => { attachedParent = parentId; return true } })
  pane.newTopic({ id: 4, title: 'Parent topic' })
  pane.$refs.editor = { saveTopic: async () => ({ id: 11, title: 'Child topic', content: '' }) }
  await pane.saveEditor()
  assert.equal(attachedParent, 4)
})

test('failed collection attachment can be retried without creating a duplicate topic', async () => {
  let topicSaves = 0
  let attachmentAttempts = 0
  const { pane } = createPane({ attachTopic: async () => ++attachmentAttempts > 1 })
  pane.newTopic()
  pane.$refs.editor = { saveTopic: async () => { topicSaves++; return { id: 12, title: 'Saved topic', content: '' } } }
  assert.equal(await pane.saveEditor(), false)
  assert.equal(pane.pendingAttachment.topic.id, 12)
  assert.match(pane.attachmentError, /Topic #12 was saved/)
  assert.equal(pane.editing, false)
  await pane.retryAttachment()
  assert.equal(topicSaves, 1)
  assert.equal(attachmentAttempts, 2)
  assert.equal(pane.pendingAttachment, null)
  assert.equal(pane.attachmentError, '')
})

test('failed topic saves leave the draft open and never attach an unsaved topic', async () => {
  let attachmentAttempts = 0
  const { pane } = createPane({ attachTopic: async () => { attachmentAttempts++; return true } })
  pane.newTopic()
  pane.$refs.editor = { saveTopic: async () => undefined }
  assert.equal(await pane.saveEditor(), false)
  assert.equal(pane.creating, true)
  assert.equal(pane.editing, true)
  assert.equal(pane.saving, false)
  assert.equal(attachmentAttempts, 0)
})

test('starting another topic protects unsaved editor content', () => {
  const previous = { id: 1, title: 'Existing topic', content: '' }
  const { pane } = createPane({ topic: previous })
  pane.$refs.editor = { isDirty: true }
  pane.newTopic()
  assert.equal(pane.topic, previous)
  assert.equal(typeof pane.pendingAction, 'function')
  pane.finishPending()
  assert.equal(pane.topic.id, null)
  assert.equal(pane.creating, true)
})