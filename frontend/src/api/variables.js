import { apiGet, apiPost } from '@/api/base'

export function getVariables() {
  return apiGet('/api/variables')
}

export function validateVariableSlug(slug) {
  return apiGet(`/api/variables/validate_slug?slug=${encodeURIComponent(slug)}`)
}

export function createVariable(payload) {
  return apiPost('/api/variables', payload)
}
