import { htmlToMarkdown } from './src/utils/htmlToMarkdown.js';
import { JSDOM } from 'jsdom';
import { marked } from 'marked';

const dom = new JSDOM();
global.document = dom.window.document;
global.DOMParser = dom.window.DOMParser;
global.Node = dom.window.Node;
global.HTMLElement = dom.window.HTMLElement;
global.HTMLLIElement = dom.window.HTMLLIElement;

const markdown = `- Level 1
    - Level 2
        - Level 3`;

const html = marked.parse(markdown, { breaks: false, gfm: true });
console.error("HTML FROM MARKED:\n" + html);

const extractedMd = htmlToMarkdown(html);
console.error("EXTRACTED MD:\n" + extractedMd);
