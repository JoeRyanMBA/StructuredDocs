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
globalThis.HTMLLIElement = dom.window.HTMLLIElement
globalThis.DOMParser = dom.window.DOMParser

const { htmlToMarkdown } = await import('../src/utils/htmlToMarkdown.js')
const { marked } = await import('marked')

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

test('closes the list dropdown before applying a selected list level', () => {
  const { instance } = createEditorHarness()
  instance.activeListMenu = 'ordered'
  let appliedLevel
  instance.insertList = (type, level) => {
    assert.equal(instance.activeListMenu, null)
    appliedLevel = [type, level]
  }

  instance.applyListLevel('ordered', 2)

  assert.deepEqual(appliedLevel, ['ordered', 2])
  assert.equal(instance.activeListMenu, null)
})

test('continues ordered-list numbering across standalone images', () => {
  const { editor, instance } = createEditorHarness()
  editor.innerHTML = [
    '<ol><li>Step one</li></ol>',
    '<p><img src="/step-one.png" alt="Step one"></p>',
    '<ol><li>Step two</li></ol>',
    '<p><img src="/step-two.png" alt="Step two"></p>',
    '<ol><li>Step three</li></ol>',
  ].join('')

  instance.continueOrderedListsAfterImages()

  const lists = editor.querySelectorAll('ol')
  assert.equal(lists[0].getAttribute('start'), null)
  assert.equal(lists[1].getAttribute('start'), '2')
  assert.equal(lists[2].getAttribute('start'), '3')
})

test('does not change explicit list starts or lists separated by text', () => {
  const { editor, instance } = createEditorHarness()
  editor.innerHTML = [
    '<ol><li>Step one</li></ol>',
    '<p><img src="/step-one.png" alt="Step one"></p>',
    '<ol start="5"><li>Step five</li></ol>',
    '<p>Separate instructions</p>',
    '<ol><li>New sequence</li></ol>',
  ].join('')

  instance.continueOrderedListsAfterImages()

  const lists = editor.querySelectorAll('ol')
  assert.equal(lists[1].getAttribute('start'), '5')
  assert.equal(lists[2].getAttribute('start'), null)
})

for (const [type, tag, marker] of [['bullet', 'ul', '-'], ['ordered', 'ol', '1.']]) {
  test(`${type} levels preserve ancestors and round-trip as nested lists`, () => {
    const { editor, instance } = createEditorHarness()
    editor.innerHTML = `<${tag}><li>Level 1<${tag}><li>Level 2</li><li>Level 3</li></${tag}></li></${tag}>`
    const item = editor.querySelectorAll('li')[2]
    const range = document.createRange()
    range.selectNodeContents(item)
    range.collapse(true)
    window.getSelection().removeAllRanges()
    window.getSelection().addRange(range)
    instance.saveSelection()

    assert.deepEqual(instance.getIntersectingListItems(range), [item])
    instance.applyListLevel(type, 3)

    assert.equal(editor.querySelectorAll(`${tag} > li > ${tag} > li > ${tag} > li`).length, 1)
    assert.equal(editor.querySelectorAll('li').length, 3)
    const markdown = htmlToMarkdown(editor.innerHTML)
    assert.equal(markdown.trimEnd(), `${marker} Level 1\n    ${marker} Level 2\n        ${marker} Level 3`)
    const preview = document.createElement('div')
    preview.innerHTML = marked.parse(markdown)
    assert.equal(preview.querySelectorAll(`${tag} > li > ${tag} > li > ${tag} > li`).length, 1)
    editor.remove()
  })
}
