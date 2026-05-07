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

const html = \`<ul>
  <li>Item 1</li>
  <ul>
    <li>Item 2</li>
  </ul>
</ul>\`;

console.log('--- OUTPUT ---');
console.log(htmlToMarkdown(html));
`);
