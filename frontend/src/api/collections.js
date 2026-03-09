import { apiRequest } from './base.js'

export async function getCollections() {
  try {
    console.log('🔄 Fetching collections from /api/collections')
    const data = await apiRequest('/api/collections')
    console.log('✅ Collections data:', data)
    return data
  } catch (error) {
    console.error('🚨 Error in getCollections:', error)
    return []
  }
}

export async function getCollection(id) {
  return apiRequest(`/api/collections/${id}`)
}

export async function saveCollections(tree) {
  return apiRequest('/api/collections', {
    method: 'PUT',
    body: JSON.stringify(tree)
  })
}

export async function getDocuments() {
  return apiRequest('/api/collections')
}

export async function saveDocuments(tree) {
  return apiRequest('/api/collections', {
    method: 'PUT',
    body: JSON.stringify(tree)
  })
}

export async function updateCollection(collectionId, data) {
  return apiRequest(`/api/collections/${collectionId}`, {
    method: 'PUT',
    body: JSON.stringify(data)
  })
}
