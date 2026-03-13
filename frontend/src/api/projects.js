// src/api/projects.js
import axiosInstance from './axiosInstance'

export async function getProjects() {
  const res = await fetch('/api/projects/');
  if (!res.ok) throw new Error(res.statusText);
  return res.json();
}

export async function getProjectTimeline(projectId) {
  const res = await axiosInstance.get(`/api/projects/${projectId}/timeline`)
  return res.data
}
