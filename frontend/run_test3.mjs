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
  <li>Level 1
    <ul>
      <li>Level 2
         <ul><li>Level 3</li></ul>
      </li>
    </ul>
  </li>
</ul>
`;
console.error("RESULT:\n" + htmlToMarkdown(html));
