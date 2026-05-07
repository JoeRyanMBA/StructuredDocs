import { htmlToMarkdown } from './src/utils/htmlToMarkdown.js';
import { JSDOM } from 'jsdom';

const dom = new JSDOM();
global.document = dom.window.document;
global.DOMParser = dom.window.DOMParser;
global.Node = dom.window.Node;
global.HTMLElement = dom.window.HTMLElement;
global.HTMLLIElement = dom.window.HTMLLIElement;

const html = `<ul><li>Level 1<ul><li data-list-level="2" style="margin-left: 1.5rem; list-style-type: circle;">Level 2 </li></ul></li></ul>`;

console.error("RESULT:\n" + JSON.stringify(htmlToMarkdown(html)));
