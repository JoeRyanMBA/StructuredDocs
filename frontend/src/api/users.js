import axios from 'axios'
import { API_BASE } from './base'

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
