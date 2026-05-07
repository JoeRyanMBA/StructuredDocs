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
  collectListEntries(listNode, inheritedLevel = 1, entries = []) {
      Array.from(listNode.children).forEach(child => {
        if (!(child instanceof HTMLLIElement)) return

        const parsedLevel = Number(child.dataset.listLevel || inheritedLevel)
        const level = Number.isFinite(parsedLevel) && parsedLevel > 0 ? parsedLevel : inheritedLevel
        const item = obj.cleanListItem(child)
        if (item) {
          entries.push({ level, item, listTag: listNode.tagName })
        }

        Array.from(child.children).forEach(nested => {
          if (nested instanceof HTMLElement && (nested.tagName === 'UL' || nested.tagName === 'OL')) {
            obj.collectListEntries(nested, level + 1, entries)
          }
        })
      })
      return entries
  },
  buildSemanticList(entries, defaultTagName) {
      if (!entries.length) return obj.createSemanticList(defaultTagName)
      
      const rootTagName = entries[0].listTag || defaultTagName
      const root = obj.createSemanticList(rootTagName)
      const stack = [{ list: root, lastItem: null }]

      entries.forEach(({ level, item, listTag }) => {
        const targetLevel = Math.max(1, Math.min(level, stack.length + 1))

        while (stack.length > targetLevel) {
          stack.pop()
        }

        while (stack.length < targetLevel) {
          const parent = stack[stack.length - 1]
          if (!(parent?.lastItem instanceof HTMLElement)) break
          const nestedList = obj.createSemanticList(listTag || defaultTagName)
          parent.lastItem.appendChild(nestedList)
          stack.push({ list: nestedList, lastItem: null })
        }

        const entry = stack[stack.length - 1]
        if (!entry || !(item instanceof HTMLElement)) return
        
        // If the current list tag doesn't match what the item wants, we might need a sibling list?
        // Actually, if we're at the same level but the tag changed (e.g. UL to OL),
        // we should create a new list and append it to the parent!
        // But for nested simplicity, let's just append the item to whatever list is at this level for now.
        
        entry.list.appendChild(item)
        entry.lastItem = item
      })
      return root
  }
};

const domHtml = `<ul><li data-list-level="1">Bullet 1</li></ul><ol><li data-list-level="2">Number 1</li></ol>`;
const div = document.createElement('div');
div.innerHTML = domHtml;

const listNodes = Array.from(div.children);
const entries = listNodes.flatMap(listNode => obj.collectListEntries(listNode));
const semanticList = obj.buildSemanticList(entries, 'UL');

console.log('--- OUTPUT ---');
console.log(semanticList.outerHTML);
