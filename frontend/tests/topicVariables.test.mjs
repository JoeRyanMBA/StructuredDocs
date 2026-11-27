import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import test from 'node:test'
import { compileScript, parse } from '@vue/compiler-sfc'
import { generateVariableSlug, sanitizeVariableSlug, variableToken } from '../src/utils/variableTokens.js'

globalThis.__topicVariableToast = { error: () => {}, success: () => {} }
globalThis.__topicVariableGetVariables = async () => []
globalThis.__topicVariableValidate = async () => ({ available: true, slug: 'variable' })
globalThis.__topicVariableCreate = async () => ({ slug: 'variable' })
globalThis.__topicVariableGenerateSlug = generateVariableSlug
globalThis.__topicVariableSanitizeSlug = sanitizeVariableSlug
globalThis.__topicVariableToken = variableToken

const source = await readFile(new URL('../src/components/TopicEditor.vue', import.meta.url), 'utf8')
const { descriptor } = parse(source)
const compiled = compileScript(descriptor, { id: 'topic-variable-test' }).content
const withoutImports = compiled.replace(/^import .*$/gm, '')
const prelude = `
const toast = globalThis.__topicVariableToast;
const getVariables = globalThis.__topicVariableGetVariables;
const validateVariableSlug = (...args) => globalThis.__topicVariableValidate(...args);
const createVariable = (...args) => globalThis.__topicVariableCreate(...args);
const generateVariableSlug = globalThis.__topicVariableGenerateSlug;
const sanitizeVariableSlug = globalThis.__topicVariableSanitizeSlug;
const variableToken = globalThis.__topicVariableToken;
const TagEditor = {};
const SnippetSelector = {};
const RichTextEditor = {};
`
const { default: component } = await import(`data:text/javascript;base64,${Buffer.from(prelude + withoutImports).toString('base64')}`)

function createEditor(text) {
  const textarea = {
    selectionStart: 6,
    selectionEnd: 18,
    focus() {},
    setSelectionRange(start, end) {
      this.selectionStart = start
      this.selectionEnd = end
    },
  }
  const instance = {
    ...component.data.call({ initialTitle: '', initialContent: text, initialFrontmatter: '' }),
    editorMode: 'markdown',
    content: text,
    $refs: { markdownEditor: textarea },
    $nextTick: callback => callback(),
  }
  for (const [name, method] of Object.entries(component.methods)) instance[name] = method.bind(instance)
  for (const [name, getter] of Object.entries(component.computed)) {
    Object.defineProperty(instance, name, { get: getter.bind(instance), configurable: true })
  }
  return { instance, textarea }
}

test('variable helpers create stable tokens from phrases and leading numbers', () => {
  assert.equal(generateVariableSlug('Customer account'), 'customer_account')
  assert.equal(generateVariableSlug('2027 Product Name'), 'variable_2027_product_name')
  assert.equal(sanitizeVariableSlug('Product Name!'), 'product_name')
  assert.equal(variableToken('product_name'), '{{product_name}}')
})

test('creating a variable preserves selected text as the default and inserts the unique token', async () => {
  const { instance, textarea } = createEditor('Use Acme Cloud now.')
  instance.openCreateVariable()

  assert.equal(instance.createVariableValue, 'me Cloud now')
  assert.deepEqual(instance.createVariableBounds, { start: 6, end: 18 })

  let payload
  globalThis.__topicVariableValidate = async () => ({
    available: false,
    suggested: 'me_cloud_now-2',
  })
  globalThis.__topicVariableCreate = async value => {
    payload = value
    return { slug: 'me_cloud_now-2' }
  }

  await instance.submitCreateVariable()

  assert.equal(payload.initial_values[0].value, 'me Cloud now')
  assert.equal(payload.initial_values[0].is_default, true)
  assert.equal(instance.content, 'Use Ac{{me_cloud_now-2}}.')
  assert.equal(textarea.selectionStart, 24)
})

test('variable creation failures remain visible and leave the selection untouched', async () => {
  const { instance } = createEditor('Use Acme Cloud now.')
  instance.openCreateVariable()
  globalThis.__topicVariableValidate = async () => ({ available: true, slug: 'me_cloud_now' })
  globalThis.__topicVariableCreate = async () => { throw new Error('Server unavailable') }

  await instance.submitCreateVariable()

  assert.equal(instance.createVariableError, 'Server unavailable')
  assert.equal(instance.content, 'Use Acme Cloud now.')
  assert.equal(instance.showCreateVariableModal, true)
})
