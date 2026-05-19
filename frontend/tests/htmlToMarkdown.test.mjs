import assert from 'node:assert/strict'
import test from 'node:test'
import { JSDOM } from 'jsdom'

const dom = new JSDOM('<!doctype html><html><body></body></html>')
globalThis.window = dom.window
globalThis.document = dom.window.document
globalThis.DOMParser = dom.window.DOMParser
globalThis.Node = dom.window.Node
globalThis.HTMLElement = dom.window.HTMLElement
globalThis.HTMLLIElement = dom.window.HTMLLIElement
globalThis.HTMLTableElement = dom.window.HTMLTableElement
globalThis.HTMLTableRowElement = dom.window.HTMLTableRowElement
globalThis.HTMLTableCellElement = dom.window.HTMLTableCellElement

const { htmlToMarkdown } = await import('../src/utils/htmlToMarkdown.js')

test('htmlToMarkdown preserves table structure and alignment markers', () => {
  const html = `
    <table>
      <thead>
        <tr>
          <th align="center">Leave Type</th>
          <th align="center">Annual Entitlement</th>
          <th align="center">Notes</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Annual Leave</td>
          <td>20 days</td>
          <td>Accrues from Day 1</td>
        </tr>
      </tbody>
    </table>
  `

  const markdown = htmlToMarkdown(html)

  assert.match(markdown, /\| Leave Type \| Annual Entitlement \| Notes \|/)
  assert.match(markdown, /\| :---: \| :---: \| :---: \|/)
  assert.match(markdown, /\| Annual Leave \| 20 days \| Accrues from Day 1 \|/)
})
