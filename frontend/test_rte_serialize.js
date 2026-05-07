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
      const rootTagName = entries.length > 0 && entries[0].listTag ? entries[0].listTag : defaultTagName
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
          const targetTagName = listTag || defaultTagName
          const nestedList = obj.createSemanticList(targetTagName)
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

const domHtml = `<ul>
  <li data-list-level="1">A</li>
  <li data-list-level="2" style="margin-left: 1.5rem">B</li>
</ul>
<ol>
  <li data-list-level="1">C</li>
  <li data-list-level="2" style="margin-left: 1.5rem">D</li>
</ol>`;

const div = document.createElement('div');
div.innerHTML = domHtml;

Array.from(div.children).forEach(child => {
  if (['UL', 'OL'].includes(child.tagName)) {
     const entries = obj.collectListEntries(child);
     const semanticList = obj.buildSemanticList(entries, child.tagName);
     child.replaceWith(semanticList);
  }
});

console.log('RTE DOM:', div.innerHTML);

