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
globalThis.HTMLTableCellElement = dom.window.HTMLTableCellElement

const source = await readFile(new URL('../src/components/RichTextEditor.vue', import.meta.url), 'utf8')
const { descriptor } = parse(source)
const compiledScript = compileScript(descriptor, { id: 'rich-text-editor-keyboard-test' }).content
const componentUrl = `data:text/javascript;base64,${Buffer.from(compiledScript).toString('base64')}`
const { default: richTextEditor } = await import(componentUrl)

function createEditorHarness() {
  const editor = document.createElement('div')
  editor.contentEditable = 'true'
  editor.innerHTML = '<p>Topic text</p>'
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
  instance.handleTableShortcut = () => false
  instance.handleTableTab = () => false

  return { editor, instance, updates }
}

test('Tab inserts a tab in the WYSIWYG topic editor without leaving it', () => {
  const { editor, instance, updates } = createEditorHarness()
  const text = editor.querySelector('p').firstChild
  const range = document.createRange()
  range.setStart(text, 5)
  range.collapse(true)
  const selection = window.getSelection()
  selection.removeAllRanges()
  selection.addRange(range)

  let prevented = false
  instance.onKeydown({
    key: 'Tab',
    shiftKey: false,
    preventDefault() {
      prevented = true
    },
  })

  assert.equal(prevented, true)
  assert.equal(editor.textContent, 'Topic\t text')
  assert.match(updates.at(-1), /Topic\t text/)
})
