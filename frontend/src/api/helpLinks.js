// src/api/helpLinks.js
import axios from 'axios'
import axiosInstance from './axiosInstance'

/** Returns enabled help links as { [feature_key]: HelpLink } — no auth required. */
export async function getHelpLinksMap() {
  const res = await axios.get('/api/help-links')
  return res.data
}

/** Admin: list all help links (enabled and disabled). */
export async function getAdminHelpLinks() {
  const res = await axiosInstance.get('/api/admin/help-links')
  return res.data
}

/** Admin: create a new help link. */
export async function createHelpLink(payload) {
  const res = await axiosInstance.post('/api/admin/help-links', payload)
  return res.data
}

/** Admin: update an existing help link by id. */
export async function updateHelpLink(id, payload) {
  const res = await axiosInstance.put(`/api/admin/help-links/${id}`, payload)
  return res.data
}

/** Admin: delete a help link by id. */
export async function deleteHelpLink(id) {
  const res = await axiosInstance.delete(`/api/admin/help-links/${id}`)
  return res.data
}
