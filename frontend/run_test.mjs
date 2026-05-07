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
<p>Hello</p>
<ul data-list-level="1" style="list-style-type: disc;">
  <li data-list-level="1">Level 1</li>
  <li data-list-level="2" style="margin-left: 1.5rem; list-style-type: circle;">Level 2</li>
  <li data-list-level="2" style="margin-left: 1.5rem; list-style-type: circle;">Level 2 B</li>
  <li data-list-level="3" style="margin-left: 3rem; list-style-type: square;">Level 3</li>
</ul>
`;
console.error("RESULT:\n" + htmlToMarkdown(html));
} catch(e) { console.error("ERROR", e); }
