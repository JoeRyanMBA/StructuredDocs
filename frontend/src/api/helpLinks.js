// src/api/helpLinks.js
import axios from 'axios'

const AUTH = () => ({ headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } })

/** Returns enabled help links as { [feature_key]: HelpLink } — no auth required. */
export async function getHelpLinksMap() {
  const res = await axios.get('/api/help-links')
  return res.data
}

/** Admin: list all help links (enabled and disabled). */
export async function getAdminHelpLinks() {
  const res = await axios.get('/api/admin/help-links', AUTH())
  return res.data
}

/** Admin: create a new help link. */
export async function createHelpLink(payload) {
  const res = await axios.post('/api/admin/help-links', payload, AUTH())
  return res.data
}

/** Admin: update an existing help link by id. */
export async function updateHelpLink(id, payload) {
  const res = await axios.put(`/api/admin/help-links/${id}`, payload, AUTH())
  return res.data
}

/** Admin: delete a help link by id. */
export async function deleteHelpLink(id) {
  const res = await axios.delete(`/api/admin/help-links/${id}`, AUTH())
  return res.data
}
