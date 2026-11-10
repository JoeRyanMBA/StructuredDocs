import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import test from 'node:test'
import { compileStyle, parse } from '@vue/compiler-sfc'
import { JSDOM } from 'jsdom'
import { renderTopicMarkdown } from '../src/utils/topicMarkdown.js'

const markdown = '1. First level\n   1. Second level\n      1. Third level\n         1. Fourth level'
const html = '<ol><li>First level<ol><li>Second level<ol><li>Third level<ol start="3"><li>Fourth level</li></ol></li></ol></li></ol></li></ol>'

for (const [view, contentClass] of [
  ['BulkReviewPortal', 'topic-content'],
  ['ReviewPortal', 'content-text'],
]) {
  const source = await readFile(new URL(`../src/views/${view}.vue`, import.meta.url), 'utf8')
  const { descriptor } = parse(source)
  const scopeId = 'data-v-review-lists'
  const styles = descriptor.styles.map(style => compileStyle({
    source: style.content,
    id: scopeId,
    scoped: style.scoped,
  }).code).join('\n')

  for (const [format, content] of [['Markdown', markdown], ['HTML', html]]) {
    test(`${view} read-only ${format} lists use the topic editor's numbering levels`, () => {
      const dom = new JSDOM(`<style>${styles}</style><div class="${contentClass}" ${scopeId}>${renderTopicMarkdown(content)}</div>`)
      try {
        const lists = [...dom.window.document.querySelectorAll('ol')]
        assert.equal(lists.length, 4)
        assert.deepEqual(
          lists.map(list => dom.window.getComputedStyle(list).listStyleType),
          ['decimal', 'lower-alpha', 'lower-roman', 'upper-alpha']
        )
        if (format === 'HTML') assert.equal(lists[3].start, 3)
      } finally {
        dom.window.close()
      }
    })
  }
}
