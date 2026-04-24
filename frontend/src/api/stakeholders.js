// src/api/stakeholders.js
import { apiPost } from './base.js'

export async function createStakeholder(stakeholder) {
  return apiPost('/api/stakeholders/', stakeholder)
}

export async function addStakeholderToProject(projectId, stakeholderId, role = 'stakeholder') {
  return apiPost(`/api/projects/${projectId}/stakeholders`, { stakeholder_id: stakeholderId, role })
}
