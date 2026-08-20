import { apiGet, apiPut } from './base'

export async function getAdminSettings() {
  const data = await apiGet('/api/admin/settings')
  return Array.isArray(data) ? data : []
}

export async function updateAdminSettings(entries) {
  return apiPut('/api/admin/settings', entries)
}
