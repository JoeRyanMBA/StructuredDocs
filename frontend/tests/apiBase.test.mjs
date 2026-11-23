import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import test from 'node:test'

const source = await readFile(new URL('../src/api/base.js', import.meta.url), 'utf8')
const nodeSource = source.replaceAll('import.meta.env', '({})')
const { apiRequest } = await import(`data:text/javascript;base64,${Buffer.from(nodeSource).toString('base64')}`)

test('custom headers retain authentication through token refresh and retry', async t => {
  const originalFetch = globalThis.fetch
  const originalStorage = globalThis.localStorage
  t.after(() => {
    globalThis.fetch = originalFetch
    if (originalStorage === undefined) delete globalThis.localStorage
    else globalThis.localStorage = originalStorage
  })

  const storage = new Map([
    ['access_token', 'old.access.token'],
    ['refresh_token', 'refresh.token.value'],
  ])
  globalThis.localStorage = {
    getItem: key => storage.get(key) ?? null,
    setItem: (key, value) => storage.set(key, value),
    removeItem: key => storage.delete(key),
  }
  const calls = []
  globalThis.fetch = async (url, options) => {
    calls.push({ url, options })
    if (calls.length === 1) return new Response('{"msg":"Token has expired"}', { status: 401 })
    if (calls.length === 2) {
      return Response.json({ access_token: 'new.access.token' })
    }
    return Response.json([{ id: 1, name: 'Trainer' }])
  }

  const body = JSON.stringify({ tag_ids: [1] })
  const result = await apiRequest('/api/tags/entity/topic/86', {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json', 'X-Test': 'value' },
    body,
  })

  assert.deepEqual(result, [{ id: 1, name: 'Trainer' }])
  assert.equal(calls.length, 3)
  assert.equal(calls[0].options.headers.Authorization, 'Bearer old.access.token')
  assert.equal(calls[1].url, '/api/users/refresh')
  assert.equal(calls[1].options.headers.Authorization, 'Bearer refresh.token.value')
  assert.equal(calls[2].options.headers.Authorization, 'Bearer new.access.token')
  assert.equal(calls[2].options.headers['X-Test'], 'value')
  assert.equal(calls[2].options.method, 'PUT')
  assert.equal(calls[2].options.body, body)
  assert.equal(calls[2].options.credentials, 'include')
})
