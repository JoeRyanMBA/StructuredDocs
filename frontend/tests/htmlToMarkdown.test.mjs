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

test('htmlToMarkdown preserves tight image wrapping styles', () => {
  const markdown = htmlToMarkdown(
    '<img src="/images/tight.png" alt="Diagram" '
    + 'style="float: left; shape-outside: polygon(0% 0%, 100% 0%, 100% 100%)">'
  )

  assert.match(markdown, /style="float: left; shape-outside: polygon\(0% 0%, 100% 0%, 100% 100%\)"/)
})

test('htmlToMarkdown preserves image presentation settings including watermark mode', () => {
  const markdown = htmlToMarkdown(
    '<img src="/images/watermark.png" alt="Watermark" '
    + 'data-sd-image-size="full" data-sd-image-alignment="center" '
    + 'data-sd-image-wrapping="watermark" '
    + 'style="position: absolute; z-index: -1; top: 0; left: 50%; transform: translateX(-50%); opacity: 0.18; width: 100%">'
  )

  assert.match(markdown, /data-sd-image-size="full"/)
  assert.match(markdown, /data-sd-image-alignment="center"/)
  assert.match(markdown, /data-sd-image-wrapping="watermark"/)
  assert.match(markdown, /style="position: absolute; z-index: -1; top: 0; left: 50%; transform: translateX\(-50%\); opacity: 0.18; width: 100%"/)
})

test('htmlToMarkdown preserves non-wrapped image alignment metadata', () => {
  const markdown = htmlToMarkdown(
    '<img src="/images/aligned.png" alt="Aligned" '
    + 'data-sd-image-size="50%" data-sd-image-alignment="right" '
    + 'data-sd-image-wrapping="none" '
    + 'style="display:block;clear:both;margin:0.5rem 0.5rem 0.5rem auto;width:50%;height:auto">'
  )

  assert.match(markdown, /data-sd-image-alignment="right"/)
  assert.match(markdown, /data-sd-image-wrapping="none"/)
  assert.match(markdown, /style="width:50%; height:auto"/)
})

test('htmlToMarkdown preserves image preset and custom resize dimensions', () => {
  const preset = htmlToMarkdown(
    '<img src="/image.png" style="width:50%;height:auto" data-sd-image-size="50%">'
  )
  const custom = htmlToMarkdown(
    '<img src="/image.png" style="width:240px;height:auto" data-sd-image-size="custom">'
  )

  assert.match(preset, /style="width:50%; height:auto"/)
  assert.match(preset, /data-sd-image-size="50%"/)
  assert.match(custom, /style="width:240px; height:auto"/)
  assert.match(custom, /data-sd-image-size="custom"/)
})

test('htmlToMarkdown preserves explicitly empty image alt text', () => {
  const markdown = htmlToMarkdown('<img src="/images/decorative.png" alt="">')

  assert.match(markdown, /!\[\]\(\/images\/decorative\.png\)/)
})

test('htmlToMarkdown preserves continued numbering across standalone images', () => {
  const markdown = htmlToMarkdown(
    '<ol><li>Step one</li></ol>'
    + '<p><img src="/images/step-one.png" alt="Step one"></p>'
    + '<ol start="2"><li>Step two</li></ol>'
  )

  assert.match(markdown, /1\. Step one/)
  assert.match(markdown, /!\[Step one\]\(\/images\/step-one\.png\)/)
  assert.match(markdown, /2\. Step two/)
  assert.ok(markdown.indexOf('1. Step one') < markdown.indexOf('![Step one]'))
  assert.ok(markdown.indexOf('![Step one]') < markdown.indexOf('2. Step two'))
})

test('htmlToMarkdown preserves list continuation and nesting across images', () => {
  const markdown = htmlToMarkdown(
    '<ol start="3"><li>Complete the form.</li></ol>'
    + '<p><img src="/images/form.png" alt="Form"></p>'
    + '<ol><li data-list-level="2" style="margin-left: 1.5rem; list-style-type: lower-alpha">Select a project.</li>'
    + '<li data-list-level="2" style="margin-left: 1.5rem; list-style-type: lower-alpha">Select a status.</li></ol>'
  )

  assert.match(markdown, /^3\. Complete the form\./)
  assert.match(markdown, /!\[Form\]\(\/images\/form\.png\)/)
  assert.match(markdown, /\n    1\. Select a project\./)
  assert.match(markdown, /\n    2\. Select a status\./)
  assert.ok(markdown.indexOf('![Form]') < markdown.indexOf('    1. Select a project.'))
})
