export async function getCollections() {
  try {
    console.log('🔄 Fetching collections from /api/collections')
    const res = await fetch('/api/collections')
    console.log('📊 Response status:', res.status, res.statusText)
    if (!res.ok) {
      console.error('❌ Response not ok:', res.status, res.statusText)
      throw new Error(res.statusText)
    }
    const data = await res.json()
    console.log('✅ Collections data:', data)
    return data
  } catch (error) {
    console.error('🚨 Error in getCollections:', error)
    throw error
  }
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
