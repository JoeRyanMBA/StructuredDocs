import assert from 'node:assert/strict'
import test from 'node:test'
import { apiRequest } from '../src/api/base.js'

async function requestWithResponse(response) {
  const originalFetch = globalThis.fetch
  globalThis.fetch = async () => response
  try {
    return await apiRequest('/api/test')
  } finally {
    globalThis.fetch = originalFetch
  }
}

test('formats HTML server errors as readable text', async () => {
  const response = new Response(
    '<!doctype html><html><body><h1><p>Internal Server Error</p></h1></body></html>',
    { status: 500, headers: { 'Content-Type': 'text/html' } },
  )

  await assert.rejects(requestWithResponse(response), {
    message: 'Internal Server Error',
  })
})

test('preserves JSON API error messages', async () => {
  const response = new Response(
    JSON.stringify({ error: 'Replacement reviewer must be different from the current reviewer' }),
    { status: 400, headers: { 'Content-Type': 'application/json' } },
  )

  await assert.rejects(requestWithResponse(response), {
    message: 'Replacement reviewer must be different from the current reviewer',
  })
})
