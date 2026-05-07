import { htmlToMarkdown } from './src/utils/htmlToMarkdown.js';
import { JSDOM } from 'jsdom';

const dom = new JSDOM();
global.document = dom.window.document;
global.DOMParser = dom.window.DOMParser;
global.Node = dom.window.Node;
global.HTMLElement = dom.window.HTMLElement;
global.HTMLLIElement = dom.window.HTMLLIElement;

const html = `
<ul data-list-level="1">
  <li data-list-level="1">Level 1</li>
  <li data-list-level="2" style="margin-left: 1.5rem;">Level 2</li>
  <li data-list-level="3" style="margin-left: 3rem;">Level 3</li>
</ul>
`;
console.error("RESULT:\n" + htmlToMarkdown(html));
