import fs from 'fs'
import path from 'path'
import { JSDOM } from 'jsdom'

const code = fs.readFileSync('src/utils/htmlToMarkdown.js', 'utf-8')
const exportedCode = code.replace('export default function htmlToMarkdown', 'function htmlToMarkdown') + '\nexport { htmlToMarkdown };'
fs.writeFileSync('temp_htmlToMarkdown11.mjs', exportedCode)

import { htmlToMarkdown } from './temp_htmlToMarkdown11.mjs'

const dom = new JSDOM()
global.document = dom.window.document
global.Node = dom.window.Node
global.HTMLElement = dom.window.HTMLElement

const html = `<ul><li>A<ul><li data-list-level="2" style="margin-left: 1.5rem">B</li></ul></li></ul>`
console.log("RESULT:\n" + htmlToMarkdown(html))
