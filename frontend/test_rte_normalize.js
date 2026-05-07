const { JSDOM } = require('jsdom');
const fs = require('fs');

const dom = new JSDOM();
global.DOMParser = dom.window.DOMParser;
global.Node = dom.window.Node;
global.HTMLElement = dom.window.HTMLElement;
global.HTMLLIElement = dom.window.HTMLLIElement;

const componentStr = fs.readFileSync('src/components/RichTextEditor.vue', 'utf8');

// extract collectListEntries, cleanListItem, buildSemanticList, createSemanticList from the vue component methods
const scriptMatches = componentStr.match(/methods: \{([\s\S]*)\n  \}/);
if (!scriptMatches) { console.error("Methods not found"); process.exit(1); }

// Extremely crude extraction for test
const methodsStr = scriptMatches[1].replace(/this\./g, 'obj.');

eval(`
const obj = {
  createSemanticList(tagName) { return dom.window.dom.window.document.createElement(tagName.toLowerCase()); },
  cleanListItem(node) {
      const clone = node.cloneNode(true)
      if (!(clone instanceof HTMLElement)) return null
      clone.querySelectorAll('ul, ol').forEach(list => list.remove())
      delete clone.dataset.listLevel
      clone.style.removeProperty('margin-left')
      clone.style.removeProperty('list-style-type')
      if (!clone.getAttribute('style')) {
        clone.removeAttribute('style')
      }
      return clone
  },
  collectListEntries(listNode, tagName, inheritedLevel = 1, entries = []) {
      Array.from(listNode.children).forEach(child => {
        if (!(child instanceof HTMLLIElement)) return

        const parsedLevel = Number(child.dataset.listLevel || inheritedLevel)
        const level = Number.isFinite(parsedLevel) && parsedLevel > 0 ? parsedLevel : inheritedLevel
        const item = obj.cleanListItem(child)
        if (item) {
          entries.push({ level, item })
        }

        Array.from(child.children).forEach(nested => {
          if (nested instanceof HTMLElement && nested.tagName === tagName) {
            obj.collectListEntries(nested, tagName, level + 1, entries)
          }
        })
      })
      return entries
  },
  buildSemanticList(entries, tagName) {
      const root = obj.createSemanticList(tagName)
      const stack = [{ list: root, lastItem: null }]

      entries.forEach(({ level, item }) => {
        const targetLevel = Math.max(1, Math.min(level, stack.length + 1))

        while (stack.length > targetLevel) {
          stack.pop()
        }

        while (stack.length < targetLevel) {
          const parent = stack[stack.length - 1]
          if (!(parent?.lastItem instanceof HTMLElement)) break
          const nestedList = obj.createSemanticList(tagName)
          parent.lastItem.appendChild(nestedList)
          stack.push({ list: nestedList, lastItem: null })
        }

        const entry = stack[stack.length - 1]
        if (!entry || !(item instanceof HTMLElement)) return
        entry.list.appendChild(item)
        entry.lastItem = item
      })

      return root
  }
};

const domHtml = \`<ul>
  <li>Level 1
    <ul>
      <li>Level 2</li>
    </ul>
  </li>
</ul>\`;
const div = dom.window.dom.window.document.createElement('div');
div.innerHTML = domHtml;

const listNodes = [div.firstElementChild];
const entries = listNodes.flatMap(listNode => obj.collectListEntries(listNode, 'UL'));
const semanticList = obj.buildSemanticList(entries, 'UL');

console.log('--- OUTPUT AFTER RTE NORMALIZE ---');
console.log(semanticList.outerHTML);
`);
