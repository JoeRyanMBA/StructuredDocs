// src/api/stakeholders.js

export async function createStakeholder(stakeholder) {
  const res = await fetch('/api/stakeholders/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(stakeholder)
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function addStakeholderToProject(projectId, stakeholderId, role = 'stakeholder') {
  const res = await fetch(`/api/projects/${projectId}/stakeholders`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ stakeholder_id: stakeholderId, role })
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}
