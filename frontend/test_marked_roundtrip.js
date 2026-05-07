const { JSDOM } = require('jsdom');
const fs = require('fs');
const marked = require('marked');

const dom = new JSDOM();
global.DOMParser = dom.window.DOMParser;
global.Node = dom.window.Node;
global.HTMLElement = dom.window.HTMLElement;
global.HTMLLIElement = dom.window.HTMLLIElement;

const htmlToMarkdownJs = fs.readFileSync('src/utils/htmlToMarkdown.js', 'utf8');
const htmlToMarkdownFnStr = htmlToMarkdownJs.replace('export function htmlToMarkdown', 'function htmlToMarkdown');
eval(htmlToMarkdownFnStr + `

const markdown = \`
- Level 1
    - Level 2
- Level 1 again
\`;

const html = marked.parse(markdown);
console.log('--- HTML from marked ---');
console.log(html);

console.log('--- ROUNDTRIP BACK TO MARKDOWN ---');
console.log(htmlToMarkdown(html));
`);
