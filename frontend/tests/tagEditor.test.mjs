import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import test from 'node:test'
import { parse } from '@vue/compiler-sfc'

const source = await readFile(new URL('../src/components/TagEditor.vue', import.meta.url), 'utf8')
const { descriptor } = parse(source)
const script = `
  const apiRequest = (...args) => globalThis.tagEditorTest.apiRequest(...args)
  ${descriptor.script.content.replace(/^import .*$/gm, '')}
`
const { default: component } = await import(`data:text/javascript;base64,${Buffer.from(script).toString('base64')}`)

function createEditor() {
  const editor = {
    ...component.data(),
    entityType: 'topic',
    entityId: 7,
    $emit() {},
  }
  for (const [name, method] of Object.entries(component.methods)) {
    editor[name] = method.bind(editor)
  }
  for (const [name, getter] of Object.entries(component.computed)) {
    Object.defineProperty(editor, name, { get: getter.bind(editor) })
  }
  return editor
}

test('tag assignment writes are serialized so the latest selection is persisted', async () => {
  const requests = []
  let releaseFirst
  globalThis.tagEditorTest = {
    apiRequest: (url, options) => new Promise(resolve => {
      requests.push({ url, options, resolve })
      if (requests.length === 1) releaseFirst = resolve
      else resolve()
    }),
  }
  const editor = createEditor()
  const first = editor.addTag({ id: 1, name: 'First' })
  const second = editor.addTag({ id: 2, name: 'Second' })
  let flushed = false
  const flush = editor.flush().then(() => { flushed = true })

  await new Promise(resolve => setImmediate(resolve))
  assert.equal(requests.length, 1)
  assert.equal(flushed, false)
  releaseFirst()
  await Promise.all([first, second, flush])

  assert.equal(requests.length, 2)
  assert.equal(flushed, true)
  assert.deepEqual(JSON.parse(requests[0].options.body).tag_ids, [1, 2])
  assert.deepEqual(JSON.parse(requests[1].options.body).tag_ids, [1, 2])
  assert.equal(requests[0].url, '/api/tags/entity/topic/7')
})
