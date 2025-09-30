// Centralized archive service for toggling and fetching archived entities
// Supports: projects, collections, feedback, bugs

const ENDPOINTS = {
  projects: {
    list: '/api/projects',
    toggle: id => `/api/projects/${id}/archive`,
    filterFn: items => items.filter(p => p.archived)
  },
  collections: {
    list: '/api/collections',
    toggle: id => `/api/collections/${id}/archive`,
    filterFn: items => items.filter(c => c.archived)
  },
  feedback: {
    list: '/api/feedback', // assumes ?status=archived supported or filter client side
    toggle: id => `/api/feedback/${id}/archive`,
    filterFn: items => items.filter(f => f.status === 'archived')
  },
  bugs: {
    list: '/api/feedback?type=bug',
    toggle: id => `/api/feedback/${id}/archive`,
    filterFn: items => items.filter(f => f.status === 'archived')
  }
}

function authHeaders () {
  const token = localStorage.getItem('access_token')
  return token ? { 'Authorization': `Bearer ${token}` } : {}
}

export async function fetchArchived(entityType) {
  const cfg = ENDPOINTS[entityType]
  if (!cfg) throw new Error(`Unsupported entity type: ${entityType}`)
  const res = await fetch(cfg.list, { headers: { ...authHeaders() } })
  if (!res.ok) throw new Error(`Failed to fetch ${entityType} (status ${res.status})`)
  const data = await res.json()
  if (!Array.isArray(data)) return []
  return cfg.filterFn(data)
}

export async function toggleArchive(entityType, id, archived) {
  const cfg = ENDPOINTS[entityType]
  if (!cfg) throw new Error(`Unsupported entity type: ${entityType}`)
  const res = await fetch(cfg.toggle(id), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeaders() },
    body: JSON.stringify({ archived })
  })
  if (!res.ok) {
    let msg = `Failed to update archive state (status ${res.status})`
    try { const err = await res.json(); if (err.error) msg = err.error } catch (_) {}
    throw new Error(msg)
  }
  return res.json()
}

export function isEntityArchived(entityType, entity) {
  if (['projects','collections'].includes(entityType)) return !!entity.archived
  if (['feedback','bugs'].includes(entityType)) return entity.status === 'archived'
  return false
}
