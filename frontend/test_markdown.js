const { JSDOM } = require('jsdom');
const fs = require('fs');

const dom = new JSDOM();
global.DOMParser = dom.window.DOMParser;
global.Node = dom.window.Node;
global.HTMLElement = dom.window.HTMLElement;
global.HTMLLIElement = dom.window.HTMLLIElement;

const htmlToMarkdownJs = fs.readFileSync('src/utils/htmlToMarkdown.js', 'utf8');
const htmlToMarkdownFnStr = htmlToMarkdownJs.replace('export function htmlToMarkdown', 'function htmlToMarkdown');
eval(htmlToMarkdownFnStr + `
const html = \`<ul data-list-level="1">
  <li data-list-level="1">Top Level 1</li>
  <li data-list-level="2">Nested Level 2</li>
  <li data-list-level="3">Deep Level 3</li>
  <li data-list-level="2">Nested Level 2</li>
  <li data-list-level="1">Top Level 2</li>
</ul>\`;

console.log('--- OUTPUT ---');
console.log(htmlToMarkdown(html));
`);
