const { JSDOM } = require("jsdom");
const window = new JSDOM("").window;
const DOMParser = window.DOMParser;

const p = new DOMParser();
const d = p.parseFromString("<p>a</p>    <p>b</p>", "text/html");
console.log(d.body.innerHTML);
