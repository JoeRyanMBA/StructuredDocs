const marked = require('marked');

const md = `- Level 1\n    - Level 2\n`;
console.log(marked.parse(md.replace(/(\!\[[^\]]*\]\([^)]+\))\{[^}]*\}/g, '$1')));
