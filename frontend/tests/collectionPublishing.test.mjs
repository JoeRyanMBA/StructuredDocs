import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import test, { after, beforeEach } from 'node:test'
import { parse } from '@vue/compiler-sfc'
import { JSDOM } from 'jsdom'

const dom = new JSDOM('<!doctype html><html><body></body></html>')
globalThis.window = dom.window
globalThis.document = dom.window.document
globalThis.Element = dom.window.Element
globalThis.SVGElement = dom.window.SVGElement
globalThis.Node = dom.window.Node
const { ref, createApp, compile, h, nextTick } = await import('vue')

let state
globalThis.collectionPublishingTest = {
  ref,
  axiosInstance: {
    async post(path, body) {
      state.requests.push(['POST', path, body])
      if (state.saveError) throw state.saveError
      return { data: { publication_id: 42 } }
    },
    async get(path, options) {
      state.requests.push(['GET', path, options])
      if (state.exportError) throw state.exportError
      return { data: new Blob(['exported content']) }
    },
  },
  toast: {
    success: message => state.successes.push(message),
    error: message => state.errors.push(message),
  },
}

async function loadModule(path, bindings) {
  const source = await readFile(new URL(path, import.meta.url), 'utf8')
  const script = `${bindings}\n${source.replace(/^import .*$/gm, '')}`
  return import(`data:text/javascript;base64,${Buffer.from(script).toString('base64')}`)
}

const collections = await loadModule('../src/api/collections.js',
  'const { axiosInstance } = globalThis.collectionPublishingTest;')
const publications = await loadModule('../src/api/publications.js',
  'const { axiosInstance } = globalThis.collectionPublishingTest;')
Object.assign(globalThis.collectionPublishingTest, {
  savePublication: collections.publishCollection,
  downloadMobileKnowledgeBase: publications.downloadMobileKnowledgeBase,
  downloadPublicationPdf: publications.downloadPublicationPdf,
})
const { useCollectionPublishing } = await loadModule('../src/composables/useCollectionPublishing.js', `
  const { ref, savePublication, downloadMobileKnowledgeBase, downloadPublicationPdf, toast } = globalThis.collectionPublishingTest;
`)
Object.assign(globalThis.collectionPublishingTest, {
  useCollectionPublishing,
  draggable: {
    props: ['list'],
    setup: (props, { slots }) => () => h('div', props.list.map(element => slots.item({ element }))),
  },
})
const treeSource = await readFile(new URL('../src/components/CollectionTree.vue', import.meta.url), 'utf8')
const { descriptor: treeDescriptor } = parse(treeSource)
const treeScript = `
  const { useCollectionPublishing, draggable } = globalThis.collectionPublishingTest;
  const TopicItem = { render: () => null }, VariableSelectionModal = { render: () => null };
  const getCollections = async () => [], getDocuments = async () => [];
  ${treeDescriptor.script.content.replace(/^import .*$/gm, '')}
`
const { default: collectionTree } = await import(`data:text/javascript;base64,${Buffer.from(treeScript).toString('base64')}`)
collectionTree.render = compile(treeDescriptor.template.content)

const organizeSource = await readFile(new URL('../src/views/Organize.vue', import.meta.url), 'utf8')
const { descriptor } = parse(organizeSource)
const organizeScript = `
  const CollectionTree = {}, TopicItem = {}, draggable = {}, VariableSelectionModal = {},
    TagEditor = {}, OrganizeTopicNode = {}, CollectionTopicPane = {}, HelpIcon = {};
  const { toast } = globalThis.collectionPublishingTest;
  ${descriptor.script.content.replace(/^import .*$/gm, '')}
`
const { default: organize } = await import(`data:text/javascript;base64,${Buffer.from(organizeScript).toString('base64')}`)

beforeEach(context => {
  context.mock.method(console, 'error', () => {})
  state = { requests: [], successes: [], errors: [], downloads: [] }
  document.body.replaceChildren()
  context.mock.method(dom.window.HTMLAnchorElement.prototype, 'click', function () {
    state.downloads.push(this.download)
  })
  URL.createObjectURL = () => 'blob:export'
  URL.revokeObjectURL = () => {}
})

after(() => dom.window.close())

for (const [type, endpoint, filename] of [
  ['pdf', 'pdf', 'Field Guide.pdf'],
  ['html', 'mobile-kb', 'Field Guide_mobile_kb.html'],
]) {
  test(`publishing ${type} saves first and downloads the returned publication with audience tags`, async () => {
    const workflow = useCollectionPublishing()
    await workflow.publishCollection(5, type, {
      filename: 'Field Guide',
      tagIds: [7, 9],
      beforePublish: async () => {
        state.requests.push(['save collection'])
        return true
      },
    })
    assert.deepEqual(state.requests, [
      ['save collection'],
      ['POST', '/api/collections/5/publish', {}],
      ['GET', `/api/publications/42/export/${endpoint}?tag_ids=7&tag_ids=9`, { responseType: 'blob' }],
    ])
    assert.deepEqual(state.downloads, [filename])
    assert.equal(state.successes.length, 1)
    assert.equal(workflow.publishing.value, false)
  })

  test(`${type} publishing guards unsaved topic edits and failed collection saves`, async () => {
    for (const [unsaved, saved] of [[true, true], [false, false], [false, true]]) {
      state.requests = []
      const workflow = useCollectionPublishing()
      let saveAttempts = 0
      await organize.methods.publishCurrentCollection.call({
        publishCollection: workflow.publishCollection,
        currentCollection: { id: 5, name: 'Field Guide' },
        audienceTagIds: [7],
        $refs: { topicPane: { hasUnsavedChanges: () => unsaved } },
        saveChanges: async () => { saveAttempts++; return saved },
      }, type)
      assert.equal(saveAttempts, unsaved ? 0 : 1)
      assert.equal(state.requests.length, !unsaved && saved ? 2 : 0)
    }
  })

  test(`the collection ${type} button saves and downloads directly without navigation`, async () => {
    let release
    const container = document.createElement('div')
    document.body.append(container)
    const app = createApp(collectionTree, {
      tree: [{ id: 5, name: 'Field Guide', topics: [{ id: 1 }], children: [] }],
      audienceTagIds: [7],
      beforePublish: () => new Promise(resolve => { release = resolve }),
    })
    app.config.globalProperties.$router = { push() { assert.fail('Publishing must not navigate') } }
    app.mount(container)
    try {
      const button = container.querySelector(type === 'pdf' ? '.publish-pdf' : '.publish-html')
      assert.match(button.textContent, /Publish as/)
      button.click()
      await nextTick()
      assert.equal(button.disabled, true)
      assert.match(button.textContent, /Publishing/)
      button.click()
      release(true)
      await new Promise(resolve => setImmediate(resolve))
      await nextTick()
      assert.deepEqual(state.downloads, [filename])
      assert.equal(state.requests.length, 2)
      assert.equal(state.requests.at(-1)[1], `/api/publications/42/export/${endpoint}?tag_ids=7`)
      assert.equal(button.disabled, false)
      assert.match(button.textContent, /Publish as/)
    } finally {
      app.unmount()
    }
  })
}

test('variable configuration resumes the selected export even when the modal emits close', async () => {
  const workflow = useCollectionPublishing()
  state.saveError = {
    response: { status: 400, data: { requires_variable_selection: true, variables_info: [{ id: 1 }], unresolved_variables: ['product'] } },
  }
  await workflow.publishCollection(5, 'pdf', { filename: 'Guide', tagIds: [7] })
  assert.equal(workflow.showVariableModal.value, true)
  assert.deepEqual(workflow.variableModalData.value.unresolvedVariables, ['product'])
  assert.deepEqual(state.downloads, [])
  state.saveError = null
  const completion = workflow.completeCollectionPublish()
  workflow.closeVariableModal()
  await completion
  assert.deepEqual(state.downloads, ['Guide.pdf'])
  assert.match(state.requests.at(-1)[1], /\/42\/export\/pdf\?tag_ids=7$/)
  assert.equal(workflow.pendingPublishAction.value, null)
  assert.equal(workflow.showVariableModal.value, false)
})

test('canceling variable configuration never exports or republishes', async () => {
  const workflow = useCollectionPublishing()
  state.saveError = { response: { status: 400, data: { requires_variable_selection: true } } }
  await workflow.publishCollection(5, 'html')
  workflow.closeVariableModal()
  await workflow.completeCollectionPublish()
  assert.equal(state.requests.length, 1)
  assert.deepEqual(state.downloads, [])
})

test('export failures retain the saved publication and report failure without success', async () => {
  const workflow = useCollectionPublishing()
  state.exportError = new Error('PDF generation failed')
  await workflow.publishCollection(5, 'pdf')
  assert.equal(state.requests.length, 2)
  assert.deepEqual(state.downloads, [])
  assert.deepEqual(state.successes, [])
  assert.deepEqual(state.errors, ['Publication saved, but export failed: PDF generation failed'])
  assert.equal(workflow.publishing.value, false)
})

test('snapshot failures do not trigger downloads and allow retry', async () => {
  const workflow = useCollectionPublishing()
  state.saveError = new Error('Unable to save snapshot')
  await workflow.publishCollection(5, 'pdf')
  assert.equal(state.requests.length, 1)
  assert.deepEqual(state.downloads, [])
  assert.match(state.errors[0], /Unable to save snapshot/)
  state.saveError = null
  await workflow.publishCollection(5, 'pdf')
  assert.deepEqual(state.downloads, ['publication.pdf'])
})

test('repeated clicks do not create concurrent snapshots or downloads', async () => {
  const workflow = useCollectionPublishing()
  let release
  const first = workflow.publishCollection(5, 'pdf', {
    beforePublish: () => new Promise(resolve => { release = resolve }),
  })
  await workflow.publishCollection(5, 'html')
  assert.equal(workflow.publishing.value, true)
  assert.deepEqual(state.requests, [])
  release(true)
  await first
  assert.equal(state.requests.length, 2)
  assert.deepEqual(state.downloads, ['publication.pdf'])
})
