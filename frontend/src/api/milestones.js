// src/api/milestones.js
import { apiDelete, apiPost, apiPut } from './base.js'

export async function createMilestone(milestone) {
  return apiPost('/api/milestones/', milestone)
}

export async function deleteMilestone(milestoneId) {
  return apiDelete(`/api/milestones/${milestoneId}`)
}

export async function updateMilestone(milestoneId, data) {
  return apiPut(`/api/milestones/${milestoneId}`, data)
}
