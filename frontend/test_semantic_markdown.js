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
const html = \`
<ul>
  <li>
    Top Level 1
    <ul>
      <li>Nested Level 2
        <ul>
          <li>Deep Level 3</li>
        </ul>
      </li>
      <li>Nested Level 2</li>
    </ul>
  </li>
  <li>Top Level 2</li>
</ul>\`;

console.log('--- OUTPUT ---');
console.log(htmlToMarkdown(html));
`);
