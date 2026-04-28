// src/api/projects.js
import axiosInstance from './axiosInstance'
import { apiRequest, normalizeListResponse } from './base'

export async function getProjects() {
  const data = await apiRequest('/api/projects/')
  return normalizeListResponse(data, ['projects', 'items', 'results', 'data'])
}

export async function getProjectTimeline(projectId) {
  const res = await axiosInstance.get(`/api/projects/${projectId}/timeline`)
  return res.data
}
