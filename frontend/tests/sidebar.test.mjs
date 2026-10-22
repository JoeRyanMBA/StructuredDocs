import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import test from 'node:test'
import { compileScript, parse } from '@vue/compiler-sfc'
import { JSDOM } from 'jsdom'

const dom = new JSDOM('<!doctype html><html><body></body></html>')
for (const key of ['window', 'document', 'Node', 'Element', 'HTMLElement', 'SVGElement']) {
  globalThis[key] = dom.window[key]
}
const { createApp, h, nextTick, ref } = await import('vue')
const source = await readFile(new URL('../src/components/SideBar.vue', import.meta.url), 'utf8')
const { descriptor } = parse(source)
const script = compileScript(descriptor, { id: 'sidebar-test' }).content
  .replace("import { store } from '../store';", 'const store = { user: null };')
const { default: sidebar } = await import(`data:text/javascript;base64,${Buffer.from(script).toString('base64')}`)
sidebar.template = descriptor.template.content

test('collapsed navigation keeps named keyboard links and submenu navigation', async () => {
  const container = document.createElement('div')
  document.body.append(container)
  const destinations = []
  const open = ref(false)
  const app = createApp({ render: () => h(sidebar, { open: open.value }) })
  app.component('router-link', {
    props: ['to'],
    template: '<a :href="`/${to.name}`"><slot /></a>',
  })
  app.config.globalProperties.$route = { name: 'Dashboard' }
  app.config.globalProperties.$router = {
    resolve: ({ name }) => ({ href: `/${name}` }),
    push: async (destination) => { destinations.push(destination) },
  }
  app.mount(container)
  try {
    assert.ok(container.querySelector('.sidebar.collapsed'))
    const home = container.querySelector('a[aria-label="Home"]')
    assert.equal(home.getAttribute('href'), '/Dashboard')
    home.focus()
    assert.equal(document.activeElement, home)
    assert.equal(container.querySelector('a[aria-label="Admin"]'), null)

    const projects = container.querySelector('a[aria-label="Projects"]')
    projects.click()
    await nextTick()
    assert.equal(projects.getAttribute('aria-expanded'), 'true')
    assert.deepEqual(destinations, [{ name: 'Projects' }])
    assert.ok(container.querySelector('.submenu a[aria-label="Tasks"]'))

    open.value = true
    await nextTick()
    assert.equal(container.querySelector('.sidebar').classList.contains('collapsed'), false)
  } finally {
    app.unmount()
    container.remove()
  }
})
