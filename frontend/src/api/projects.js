// src/api/projects.js
import axiosInstance from './axiosInstance'
import { apiRequest } from './base'

export async function getProjects() {
  const data = await apiRequest('/api/projects/')

  // Defensive normalization for endpoint variants.
  if (Array.isArray(data)) return data
  if (Array.isArray(data?.projects)) return data.projects
  return []
}

export async function getProjectTimeline(projectId) {
  const res = await axiosInstance.get(`/api/projects/${projectId}/timeline`)
  return res.data
}
