import { marked } from 'marked'

function slugify(text) {
  return String(text)
    .replace(/[*_`[\]]/g, '')
    .toLowerCase()
    .trim()
    .replace(/[^\w\s-]/g, '')
    .replace(/[\s_]+/g, '-')
    .replace(/^-+|-+$/g, '')
}

function buildRenderer() {
  const renderer = new marked.Renderer()

  renderer.heading = function (token) {
    const slug = slugify(token.text)
    const inner = marked.parseInline(token.text)
    return (
      `<h${token.depth} id="${slug}" class="anchor-heading">` +
      `<a class="anchor-link" href="#${slug}" aria-label="Link to this section">#</a>` +
      inner +
      `</h${token.depth}>\n`
    )
  }

  renderer.image = function (...args) {
    let href = '', title = '', text = ''
    if (args.length === 1 && args[0] && typeof args[0] === 'object') {
      href = args[0].href || ''
      title = args[0].title || ''
      text = args[0].text || ''
    } else {
      href = args[0] || ''
      title = args[1] || ''
      text = args[2] || ''
    }
    const esc = value => String(value ?? '')
      .replace(/&/g, '&amp;')
      .replace(/"/g, '&quot;')
    let output = `<img src="${esc(href)}" alt="${esc(text)}"`
    if (title) output += ` title="${esc(title)}"`
    output += '>'
    return output
  }

  return renderer
}

export function renderTopicMarkdown(content) {
  if (!content) return ''
  const markdown = String(content).replace(/(\!\[[^\]]*\]\([^)]+\))\{[^}]*\}/g, '$1')
  return marked.parse(markdown, {
    breaks: false,
    gfm: true,
    renderer: buildRenderer(),
  })
}
