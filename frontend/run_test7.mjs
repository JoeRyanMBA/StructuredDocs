import { htmlToMarkdown } from './src/utils/htmlToMarkdown.js';
import { JSDOM } from 'jsdom';

const dom = new JSDOM();
global.document = dom.window.document;
global.DOMParser = dom.window.DOMParser;
global.Node = dom.window.Node;
global.HTMLElement = dom.window.HTMLElement;
global.HTMLLIElement = dom.window.HTMLLIElement;

const html = `
<ul>
  <li data-list-level="1">Level 1</li>
  <li data-list-level="2">Level 2</li>
</ul>
`;
console.error("RESULT:\n" + JSON.stringify(htmlToMarkdown(html)));
