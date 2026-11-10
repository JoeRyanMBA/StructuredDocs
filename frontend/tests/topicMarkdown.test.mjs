import assert from 'node:assert/strict'
import test from 'node:test'
import { JSDOM } from 'jsdom'

const { window } = new JSDOM('')
globalThis.window = window
globalThis.document = window.document

const [{ renderTopicMarkdown }, { sanitizeHtml }] = await Promise.all([
  import('../src/utils/topicMarkdown.js'),
  import('../src/utils/sanitize.js'),
])

test('renders review content as Markdown with working image elements', () => {
  const markdown = 'Select **Insert Link**. ![](/images/help.png) The link appears.'
  const html = renderTopicMarkdown(markdown)

  assert.match(html, /<strong>Insert Link<\/strong>/)
  assert.match(html, /<img src="\/images\/help\.png" alt="">/)
  assert.doesNotMatch(html, /\*\*Insert Link\*\*|!\[\]/)
})

test('renders image attributes without leaving them as visible Markdown text', () => {
  const html = renderTopicMarkdown('![Example](/images/help.png){width="4.0in"}')

  assert.match(html, /<img src="\/images\/help\.png" alt="Example">/)
  assert.doesNotMatch(html, /width=/)
})

test('sanitizes unsafe HTML from topic content', () => {
  const html = sanitizeHtml(renderTopicMarkdown('<img src="/images/help.png" onerror="alert(1)">'))

  assert.match(html, /<img src="\/images\/help\.png">/)
  assert.doesNotMatch(html, /onerror/)
})
