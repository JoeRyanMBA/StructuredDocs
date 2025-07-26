export async function getCollections() {
  const res = await fetch('/api/collections')
  if (!res.ok) throw new Error(res.statusText)
  return res.json()
}

export async function saveCollections(tree) {
  const res = await fetch('/api/collections', {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(tree)
  })
  if (!res.ok) throw new Error(res.statusText)
  return res.json()
}

export async function getDocuments() {
  const res = await fetch('/api/collections')
  if (!res.ok) throw new Error(res.statusText)
  return res.json()
}

export async function saveDocuments(tree) {
  const res = await fetch('/api/collections', {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(tree)
  })
  if (!res.ok) throw new Error(res.statusText)
  return res.json()
}

export const data = [
  {
    id: 1,
    name: 'Collection A',
    topics: [{ id: 1, title: 'Topic 1' }],
    children: []
  }
]