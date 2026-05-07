const marked = require('marked');

const md = `- Level 1\n    - Level 2`;
console.log(marked.parse(md));
