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
    console.log('🔧 Using fallback mock data for testing')
    // Return mock data when backend is unavailable
    return [
      {
        id: 1,
        name: 'Sample Collection',
        description: 'A sample collection for testing arrow buttons',
        projectId: 1,
        form_number: 'FORM-001',
        topics: [
          {
            id: 1,
            title: 'Sample Topic 1',
            status: 'draft',
            summary: 'First sample topic with arrow buttons',
            children: [
              {
                id: 4,
                title: 'Child Topic 1',
                status: 'draft',
                summary: 'Child topic for testing hierarchy arrows'
              }
            ]
          },
          {
            id: 2,
            title: 'Sample Topic 2',
            status: 'pending_review',
            summary: 'Second sample topic'
          },
          {
            id: 3,
            title: 'Sample Topic 3',
            status: 'approved',
            summary: 'Third sample topic'
          }
        ]
      }
    ]
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

export async function updateCollection(collectionId, data) {
  const res = await fetch(`/api/collections/${collectionId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}
