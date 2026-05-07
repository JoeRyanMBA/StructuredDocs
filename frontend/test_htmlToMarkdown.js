import { htmlToMarkdown } from './frontend/src/utils/htmlToMarkdown.js';
console.log(htmlToMarkdown(`
<ul>
  <li data-list-level="1">Item 1</li>
  <li data-list-level="2">Item 2</li>
  <li data-list-level="3">Item 3</li>
</ul>
`));
