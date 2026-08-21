import { apiDelete, apiGet, apiPut } from './base'
import axiosInstance from './axiosInstance'

export async function getAdminSettings() {
  const data = await apiGet('/api/admin/settings')
  return Array.isArray(data) ? data : []
}

export async function updateAdminSettings(entries) {
  return apiPut('/api/admin/settings', entries)
}

export async function listExportBrandingAssets() {
  const data = await apiGet('/api/admin/export-branding/assets')
  return Array.isArray(data) ? data : []
}

export async function uploadExportBrandingAsset(file, targetKey) {
  const formData = new FormData()
  formData.append('file', file)
  if (targetKey) {
    formData.append('target_key', targetKey)
  }

  const response = await axiosInstance.post('/api/admin/export-branding/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return response?.data || {}
}

export async function deleteExportBrandingAsset(filename) {
  const safe = encodeURIComponent(filename)
  return apiDelete(`/api/admin/export-branding/assets/${safe}`)
}

export async function fetchExportBrandingAssetBlob(filename) {
  const safe = encodeURIComponent(filename)
  const response = await axiosInstance.get(`/api/admin/export-branding/assets/${safe}/preview`, {
    responseType: 'blob',
  })
  return response?.data || null
}
