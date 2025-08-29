// src/api/milestones.js

export async function createMilestone(milestone) {
  const res = await fetch('/api/milestones', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(milestone)
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function deleteMilestone(milestoneId) {
  const res = await fetch(`/api/milestones/${milestoneId}`, {
    method: 'DELETE'
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function updateMilestone(milestoneId, data) {
  const res = await fetch(`/api/milestones/${milestoneId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}
