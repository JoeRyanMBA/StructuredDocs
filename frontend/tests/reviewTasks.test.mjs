import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import test from 'node:test'
import { parse } from '@vue/compiler-sfc'
import { JSDOM } from 'jsdom'

const dom = new JSDOM('<!doctype html><html><body></body></html>', { url: 'http://localhost/' })
globalThis.window = dom.window
globalThis.document = dom.window.document
globalThis.Element = dom.window.Element
globalThis.SVGElement = dom.window.SVGElement
globalThis.Node = dom.window.Node

const Vue = await import('vue')

async function loadComponent(path, bindings) {
  const source = await readFile(new URL(path, import.meta.url), 'utf8')
  const { descriptor } = parse(source)
  const script = `${bindings}\n${descriptor.script.content.replace(/^import .*$/gm, '')}`
  const { default: component } = await import(`data:text/javascript;base64,${Buffer.from(script).toString('base64')}`)
  component.render = Vue.compile(descriptor.template.content)
  return component
}

globalThis.reviewTasksTest = { result: null, error: null }
const card = await loadComponent('../src/components/ReviewCard.vue', `
  const toast = { success() {}, error() {} };
  const startReview = async () => {};
  const submitReview = async () => {};
`)
globalThis.reviewTasksTest.card = card
const page = await loadComponent('../src/views/ReviewsListView.vue', `
  const ReviewCard = globalThis.reviewTasksTest.card;
  const getReviewTasks = async () => {
    if (globalThis.reviewTasksTest.error) throw globalThis.reviewTasksTest.error;
    return globalThis.reviewTasksTest.result;
  };
  const toast = { error() {} };
`)

function review(id, status) {
  return {
    id, topic_id: id, topic_title: `Topic ${id}`, status, priority: 'medium',
    requester_name: 'Sender', reviewer_name: 'Reviewer',
    recommendation: 'approve', feedback: '', completed_at: null,
  }
}

async function mountPage() {
  const container = document.createElement('div')
  document.body.append(container)
  const app = Vue.createApp(page)
  app.config.globalProperties.$router = { push() {} }
  app.mount(container)
  await Promise.resolve()
  await Vue.nextTick()
  return { app, container }
}

test('review tasks tabs separate received, sent and completed work', async () => {
  globalThis.reviewTasksTest.result = {
    assigned: [review(1, 'pending')],
    sent: [review(2, 'pending')],
    completed: [review(3, 'completed'), review(4, 'completed')],
    stakeholder_linked: true,
  }
  const { app, container } = await mountPage()
  try {
    assert.match(container.textContent, /Needs My Review \(1\)/)
    assert.match(container.textContent, /Topic 1/)
    assert.match(container.textContent, /Start Review/)

    container.querySelectorAll('.tab-btn')[1].click()
    await Vue.nextTick()
    assert.match(container.textContent, /Topic 2/)
    assert.match(container.textContent, /Reviewer: Reviewer/)
    assert.doesNotMatch(container.textContent, /Start Review/)

    container.querySelectorAll('.tab-btn')[2].click()
    await Vue.nextTick()
    assert.match(container.textContent, /Topic 3/)
    assert.match(container.textContent, /Topic 4/)
    assert.doesNotMatch(container.textContent, /Start Review/)
  } finally {
    app.unmount()
    container.remove()
  }
})

test('missing stakeholder and API failures are visible instead of showing the global queue', async () => {
  globalThis.reviewTasksTest.result = { assigned: [], sent: [], completed: [], stakeholder_linked: false }
  const first = await mountPage()
  try {
    assert.match(first.container.textContent, /No stakeholder matches your account email/)
    assert.match(first.container.textContent, /No pending reviews assigned to you/)
  } finally {
    first.app.unmount()
    first.container.remove()
  }

  globalThis.reviewTasksTest.error = new Error('Unable to resolve reviewer')
  const second = await mountPage()
  try {
    assert.match(second.container.querySelector('[role="alert"]').textContent, /Unable to resolve reviewer/)
  } finally {
    second.app.unmount()
    second.container.remove()
    globalThis.reviewTasksTest.error = null
  }
})
