const { JSDOM } = require('jsdom');
const dom = new JSDOM();
const document = dom.window.document;
const HTMLElement = dom.window.HTMLElement;
const HTMLLIElement = dom.window.HTMLLIElement;

const obj = {
  createSemanticList(tagName) { return document.createElement(tagName.toLowerCase()); },
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

const domHtml = `<ol><li data-list-level="2">Isolated Level 2</li></ol>`;
const div = document.createElement('div');
div.innerHTML = domHtml;

const listNodes = [div.firstElementChild];
const entries = listNodes.flatMap(listNode => obj.collectListEntries(listNode, 'OL'));
const semanticList = obj.buildSemanticList(entries, 'OL');

console.log('--- OUTPUT ---');
console.log(semanticList.outerHTML);
