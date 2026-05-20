// src/api/publications.js

import axiosInstance from './axiosInstance'
import { apiDelete, apiGet, apiPost, apiPut } from './base'

function buildTagQuery(tagIds = []) {
  const params = new URLSearchParams()
  tagIds.forEach(id => {
    if (id !== null && id !== undefined && `${id}` !== '') {
      params.append('tag_ids', id)
    }
  })
  const query = params.toString()
  return query ? `?${query}` : ''
}

function triggerBrowserDownload(blob, filename) {
  const objectUrl = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = objectUrl
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(objectUrl)
}

export async function createPublication(publication) {
  return apiPost('/api/publications', publication)
}

export async function deletePublication(publicationId) {
  return apiDelete(`/api/publications/${publicationId}`)
}

export async function updatePublication(publicationId, data) {
  return apiPut(`/api/publications/${publicationId}`, data)
}

export async function getPublications() {
  const data = await apiGet('/api/publications')
  return Array.isArray(data) ? data : (data?.publications || [])
}

export async function getPublication(publicationId) {
  return apiGet(`/api/publications/${publicationId}`)
}

function toSaveTree(nodes = []) {
  return nodes
    .map(node => {
      const topicId = node?.topic_id ?? node?.topic?.id
      if (!topicId) return null
      return {
        topic_id: topicId,
        children: toSaveTree(node.children || [])
      }
    })
    .filter(Boolean)
}

export async function refreshPublication(publicationId) {
  const publication = await getPublication(publicationId)
  const tree = toSaveTree(publication?.tree || [])
  return apiPost(`/api/publications/${publicationId}/nodes`, { tree })
}

export async function downloadPublicationPdf(publicationId, filename = 'publication.pdf', tagIds = []) {
  const query = buildTagQuery(tagIds)
  const response = await axiosInstance.get(`/api/publications/${publicationId}/export/pdf${query}`, {
    responseType: 'blob'
  })
  triggerBrowserDownload(response.data, filename)
}

export async function downloadMobileKnowledgeBase(publicationId, filename = 'publication_mobile_kb.html', tagIds = []) {
  const query = buildTagQuery(tagIds)
  const response = await axiosInstance.get(`/api/publications/${publicationId}/export/mobile-kb${query}`, {
    responseType: 'blob'
  })
  triggerBrowserDownload(response.data, filename)
}

export async function previewMobileKnowledgeBase(publicationId, tagIds = []) {
  const query = buildTagQuery(tagIds)
  const response = await axiosInstance.get(`/api/publications/${publicationId}/preview/mobile-kb${query}`, {
    responseType: 'text',
    transformResponse: [data => data]
  })

  const html = typeof response.data === 'string' ? response.data : ''
  const blob = new Blob([html], { type: 'text/html' })
  const objectUrl = URL.createObjectURL(blob)
  const previewWindow = window.open(objectUrl, '_blank', 'width=375,height=812,scrollbars=yes,resizable=yes,toolbar=no,menubar=no')

  if (previewWindow) {
    previewWindow.focus()
    previewWindow.addEventListener('beforeunload', () => URL.revokeObjectURL(objectUrl), { once: true })
  } else {
    URL.revokeObjectURL(objectUrl)
    throw new Error('Preview window was blocked by the browser')
  }
}
