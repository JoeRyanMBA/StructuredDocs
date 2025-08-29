// src/api/projects.js
export async function getProjects() {
  const res = await fetch('/api/projects/');
  if (!res.ok) throw new Error(res.statusText);
  return res.json();
}
