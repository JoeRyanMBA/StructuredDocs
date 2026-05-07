import { htmlToMarkdown } from './src/utils/htmlToMarkdown.js';
import { JSDOM } from 'jsdom';

try {
const dom = new JSDOM();
global.document = dom.window.document;
global.DOMParser = dom.window.DOMParser;
global.Node = dom.window.Node;
global.HTMLElement = dom.window.HTMLElement;
global.HTMLLIElement = dom.window.HTMLLIElement;

const html = `
<ul>
  <li>Level 1
    <ol>
      <li>Level 2</li>
    </ol>
  </li>
</ul>
`;
console.error("RESULT:\n" + htmlToMarkdown(html));
} catch(e) { console.error("ERROR", e); }
