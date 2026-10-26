import { marked } from 'marked'

export function substituteCollectionVariables(content, mapping = {}) {
  return String(content || '').replace(/\{\{\s*([^{}]+?)\s*\}\}/g, (token, slug) =>
    Object.hasOwn(mapping, slug) ? String(mapping[slug] ?? '') : token)
}

export async function renderCollectionTopic(content, { document, getSnippet, tagIds = [], mapping = {}, sanitize }) {
  const selectedTags = new Set(tagIds.map(Number))
  const container = document.createElement('div')
  const markdown = substituteCollectionVariables(content, mapping)
    .replace(/(!\[[^\]]*\]\([^)]+\))\{[^}]*\}/g, '$1')
  container.innerHTML = sanitize(marked.parse(markdown))
  for (const element of [...container.querySelectorAll('div.sd-snippet-ref[data-snippet-id]')]) {
    const snippet = await getSnippet(Number(element.dataset.snippetId))
    const visible = !snippet.tags?.length || snippet.tags.some(tag => selectedTags.has(Number(tag.id)))
    if (!visible) {
      element.remove()
      continue
    }
    const fragment = document.createElement('div')
    fragment.innerHTML = sanitize(marked.parse(snippet.content || ''))
    element.replaceWith(...fragment.childNodes)
  }
  return sanitize(container.innerHTML)
}