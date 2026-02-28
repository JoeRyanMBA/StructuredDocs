import { apiRequest } from './base.js'

export async function listSnippets() {
  return apiRequest('/api/snippets')
}

export async function getSnippet(id) {
  return apiRequest(`/api/snippets/${id}`)
}

export async function createSnippet(data) {
  return apiRequest('/api/snippets', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export async function updateSnippet(id, data) {
  return apiRequest(`/api/snippets/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  })
}

export async function deleteSnippet(id) {
  return apiRequest(`/api/snippets/${id}`, { method: 'DELETE' })
}

export async function setSnippetTags(id, tagIds) {
  return apiRequest(`/api/snippets/${id}/tags`, {
    method: 'PUT',
    body: JSON.stringify({ tag_ids: tagIds }),
  })
}
