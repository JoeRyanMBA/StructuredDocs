// src/api/publications.js

export async function createPublication(publication) {
  const res = await fetch('/api/publications', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(publication)
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function deletePublication(publicationId) {
  const res = await fetch(`/api/publications/${publicationId}`, {
    method: 'DELETE'
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function updatePublication(publicationId, data) {
  const res = await fetch(`/api/publications/${publicationId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}
