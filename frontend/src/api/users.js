import axios from 'axios'

// Use Vercel-provided env var in production; fallback to relative for local dev
function computeApiBase() {
  let raw = (import.meta.env.VITE_API_BASE_URL || '').trim();
  if (!raw) return '';
  raw = raw.replace(/\/+$/, '');
  // Prepend scheme if missing, inherit current page protocol
  if (!/^https?:\/\//i.test(raw)) {
    const proto = typeof window !== 'undefined' ? window.location.protocol : 'https:';
    const hostPref = proto === 'https:' ? 'https://' : 'http://';
    raw = hostPref + raw.replace(/^\/*/, '');
  }
  // Force https if site is https to avoid mixed content
  if (typeof window !== 'undefined' && window.location.protocol === 'https:' && raw.startsWith('http://')) {
    raw = raw.replace(/^http:\/\//i, 'https://');
  }
  return raw;
}

const API_BASE = computeApiBase()

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: `${API_BASE}/api`,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  },
  withCredentials: true
})

// User management API
export const usersAPI = {
  // Get all users
  getUsers() {
    return apiClient.get('/users')
  },

  // Create a new user
  createUser(userData) {
    return apiClient.post('/users', userData)
  },

  // Update a user
  updateUser(userId, userData) {
    return apiClient.put(`/users/${userId}`, userData)
  },

  // Delete a user
  deleteUser(userId) {
    return apiClient.delete(`/users/${userId}`)
  },

  // Update user role
  updateUserRole(userId, role) {
    return apiClient.put(`/users/${userId}/role`, { role })
  }
}

export default apiClient
