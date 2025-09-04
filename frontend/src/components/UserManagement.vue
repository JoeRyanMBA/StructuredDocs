<template>
  <div class="user-management">
    <div class="header">
      <div class="spacer"></div>
      <button @click="addUser" class="btn btn-primary">
        <i class="fas fa-plus"></i>
        Add User
      </button>
    </div>
    <!-- Users Table -->
    <div class="users-table">
      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Email</th>
            <th>Role</th>
            <th>Status</th>
            <th>Created</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in users" :key="user.id">
            <td>{{ user.name }}</td>
            <td>{{ user.email }}</td>
            <td>
              <span :class="['role-badge', `role-${user.role}`]">
                {{ user.role }}
              </span>
            </td>
            <td>
              <span :class="['status-badge', user.active ? 'active' : 'inactive']">
                {{ user.active ? 'Active' : 'Inactive' }}
              </span>
            </td>
            <td>{{ formatDate(user.created_at) }}</td>
            <td class="actions">
              <div class="action-buttons">
                <button 
                  @click="editUser(user)" 
                  class="btn-icon btn-secondary"
                  title="Edit user details"
                >
                  <i class="fas fa-edit"></i>
                </button>
                <button 
                  v-if="!user.password_hash && user.active"
                  @click="resendSetupEmail(user)" 
                  class="btn-icon btn-info"
                  :disabled="loading"
                  title="Resend password setup email"
                >
                  <i class="fas fa-envelope"></i>
                </button>
                <button 
                  @click="deleteUser(user)" 
                  class="btn-icon btn-danger"
                  :disabled="user.role === 'admin' && adminCount <= 1"
                  title="Delete user"
                >
                  <i class="fas fa-trash"></i>
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Add/Edit User Modal -->
  <div v-if="showAddUser || editingUser" class="modal-overlay" @click.self="closeModal" style="display: block !important;">
      <div class="modal" @click.stop style="display: block !important;">
        <div class="modal-header">
          <h3>{{ editingUser ? 'Edit User' : 'Add User' }}</h3>
          <button @click="closeModal" class="close-btn">&times;</button>
        </div>
        
        <div class="modal-body">
          <form @submit.prevent="saveUser">
            <div class="form-group">
              <label for="name">Name:</label>
              <input 
                type="text" 
                id="name" 
                v-model="userForm.name" 
                required 
                :disabled="loading"
              />
            </div>
            
            <div class="form-group">
              <label for="email">Email:</label>
              <input 
                type="email" 
                id="email" 
                v-model="userForm.email" 
                required 
                :disabled="loading"
              />
              <small v-if="!editingUser" class="form-help">
                The user will receive an email with instructions to set their password.
              </small>
            </div>
            
            <div class="form-group">
              <label for="role">Role:</label>
              <select 
                id="role" 
                v-model="userForm.role" 
                required 
                :disabled="loading"
              >
                <option value="author">Author</option>
                <option value="admin">Admin</option>
              </select>
            </div>
            
            <div class="form-group">
              <label>
                <input 
                  type="checkbox" 
                  v-model="userForm.active" 
                  :disabled="loading"
                />
                Active
              </label>
            </div>
            
            <div class="form-actions">
              <button type="button" @click="closeModal" class="btn btn-secondary" :disabled="loading">
                Cancel
              </button>
              <button type="submit" class="btn btn-primary" :disabled="loading">
                {{ loading ? 'Saving...' : (editingUser ? 'Update' : 'Create') }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Loading overlay -->
    <div v-if="loading && !showAddUser && !editingUser" class="loading-overlay">
      <div class="loading-container">
        <div class="loading-spinner"></div>
        <p class="loading-text">Loading users...</p>
      </div>
    </div>

    <!-- Error message -->
    <div v-if="error" class="error-message">
      {{ error }}
      <button @click="error = ''" class="message-close-btn">&times;</button>
    </div>

    <!-- Success message -->
    <div v-if="success" class="success-message">
      {{ success }}
      <button @click="success = ''" class="message-close-btn">&times;</button>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'UserManagement',
  data() {
    return {
      users: [],
      showAddUser: false,
      editingUser: null,
      userForm: {
        name: '',
        email: '',
        role: 'author',
        active: true
      },
      loading: false,
      error: '',
      success: ''
    }
  },
  computed: {
    adminCount() {
      return this.users.filter(user => user.role === 'admin' && user.active).length
    }
  },
  mounted() {
    this.loadUsers()
  },
  methods: {
    async loadUsers() {
      this.loading = true
      this.error = ''
      
      try {
        console.log('🔄 UserManagement - Loading users from API...')
        const response = await axios.get('/api/users')
        console.log('✅ UserManagement - API response:', response.data)
        this.users = response.data
        console.log('✅ UserManagement - Users loaded:', this.users.length, 'users')
      } catch (error) {
        console.error('❌ UserManagement - Error loading users:', error)
        this.error = 'Failed to load users: ' + (error.response?.data?.error || error.message)
      } finally {
        this.loading = false
      }
    },
    
    addUser() {
      console.log('🔘 UserManagement - Add User button clicked')
      console.log('🔘 UserManagement - Current showAddUser state:', this.showAddUser)
      console.log('🔘 UserManagement - Current editingUser state:', this.editingUser)
      
      this.showAddUser = true
      
      console.log('🔘 UserManagement - After setting showAddUser=true:', this.showAddUser)
      console.log('🔘 UserManagement - Modal should now be visible')
      
      // Force Vue to update the DOM
      this.$nextTick(() => {
        console.log('🔘 UserManagement - nextTick - showAddUser:', this.showAddUser)
        const modalOverlay = document.querySelector('.modal-overlay')
        const modal = document.querySelector('.modal')
        console.log('🔘 UserManagement - Modal overlay element:', modalOverlay)
        console.log('🔘 UserManagement - Modal element:', modal)
        
        if (modalOverlay) {
          console.log('✅ UserManagement - Modal overlay found in DOM')
          console.log('🔘 UserManagement - Modal overlay styles:', window.getComputedStyle(modalOverlay))
        } else {
          console.log('❌ UserManagement - Modal overlay NOT found in DOM')
        }
        
        if (modal) {
          console.log('✅ UserManagement - Modal found in DOM')
          console.log('🔘 UserManagement - Modal styles:', window.getComputedStyle(modal))
        } else {
          console.log('❌ UserManagement - Modal NOT found in DOM')
        }
      })
    },
    
    editUser(user) {
      console.log('✏️ UserManagement - Edit user clicked:', user)
      this.editingUser = user
      this.userForm = {
        name: user.name,
        email: user.email,
        role: user.role,
        active: user.active
      }
      console.log('✏️ UserManagement - editingUser set:', this.editingUser)
      console.log('✏️ UserManagement - userForm populated:', this.userForm)
    },
    
    async saveUser() {
      this.loading = true
      this.error = ''
      
      try {
        console.log('💾 UserManagement - Saving user:', this.userForm)
        
        if (this.editingUser) {
          // Update existing user
          console.log('🔄 Updating existing user with ID:', this.editingUser.id)
          await axios.put(
            `/api/users/${this.editingUser.id}`,
            this.userForm
          )
          this.success = 'User updated successfully'
        } else {
          // Create new user
          console.log('➕ Creating new user')
          const response = await axios.post('/api/users', this.userForm)
          console.log('✅ User creation response:', response.data)
          
          // Show message about password setup email
          if (response.data.password_setup_required) {
            this.success = response.data.message || 'User created successfully. Password setup email sent.'
          } else {
            this.success = 'User created successfully'
          }
        }
        
        this.closeModal()
        console.log('🔄 Reloading users list...')
        await this.loadUsers()
        
        // Clear success message after 3 seconds
        setTimeout(() => {
          this.success = ''
        }, 3000)
        
      } catch (error) {
        console.error('❌ Error saving user:', error)
        if (error.response?.data?.error) {
          this.error = error.response.data.error
        } else {
          this.error = 'Failed to save user'
        }
      } finally {
        this.loading = false
      }
    },
    
    async deleteUser(user) {
      if (!confirm(`Are you sure you want to delete ${user.name}?`)) {
        return
      }
      
      this.loading = true
      this.error = ''
      
      try {
        await axios.delete(`/api/users/${user.id}`)
        this.success = 'User deleted successfully'
        await this.loadUsers()
        
        // Clear success message after 3 seconds
        setTimeout(() => {
          this.success = ''
        }, 3000)
        
      } catch (error) {
        console.error('❌ Error deleting user:', error)
        if (error.response?.data?.error) {
          this.error = error.response.data.error
        } else {
          this.error = 'Failed to delete user'
        }
      } finally {
        this.loading = false
      }
    },
    
    closeModal() {
      console.log('❌ UserManagement - Close modal called')
      console.log('❌ UserManagement - Before: showAddUser=', this.showAddUser, 'editingUser=', this.editingUser)
      
      this.showAddUser = false
      this.editingUser = null
      this.userForm = {
        name: '',
        email: '',
        role: 'author',
        active: true
      }
      
      console.log('❌ UserManagement - After: showAddUser=', this.showAddUser, 'editingUser=', this.editingUser)
    },
    
    async resendSetupEmail(user) {
      if (!confirm(`Resend password setup email to ${user.name} (${user.email})?`)) {
        return
      }
      
      this.loading = true
      this.error = ''
      
      try {
        console.log('📧 Resending setup email for user:', user.id)
        const response = await axios.post(`/api/users/${user.id}/resend-setup-email`)
        console.log('✅ Setup email response:', response.data)
        
        this.success = response.data.message || 'Password setup email sent successfully'
        
        // Clear success message after 5 seconds
        setTimeout(() => {
          this.success = ''
        }, 5000)
        
      } catch (error) {
        console.error('❌ Error resending setup email:', error)
        if (error.response?.data?.error) {
          this.error = error.response.data.error
        } else {
          this.error = 'Failed to resend setup email'
        }
      } finally {
        this.loading = false
      }
    },
    
    formatDate(dateString) {
      if (!dateString) return ''
      return new Date(dateString).toLocaleDateString()
    }
  }
}
</script>

<style>
.user-management {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
  position: relative;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.header .spacer { flex: 1; }

.header h2 {
  margin: 0;
  color: #333;
}

.users-table {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th {
  background: #f8f9fa;
  padding: 15px 12px;
  text-align: left;
  font-weight: 600;
  color: #555;
  border-bottom: 2px solid #e9ecef;
}

td {
  padding: 12px;
  border-bottom: 1px solid #e9ecef;
}

.role-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 400;
  text-transform: uppercase;
}

.role-author {
  background: #e3f2fd;
  color: #1976d2;
}

.role-admin {
  background: #fce4ec;
  color: #c2185b;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 400;
}

.status-badge.active {
  background: #e8f5e8;
  color: #2e7d32;
}

.status-badge.inactive {
  background: #ffebee;
  color: #d32f2f;
}

.actions {
  display: flex;
  gap: 8px;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: var(--primary-deep-teal);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: var(--primary-dark-teal);
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background: #545b62;
}

.btn-danger {
  background: #dc3545;
  color: white;
}

.btn-danger:hover:not(:disabled) {
  background: #c82333;
}

.btn-info {
  background-color: var(--info-dark-blue);
  color: var(--bg-white);
}

.btn-info:hover:not(:disabled) {
  background-color: #1e40af;
}

.btn-sm {
  padding: 6px 12px;
  font-size: 12px;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: flex-start;
  justify-content: center;
  z-index: 1000;
  padding-top: 12rem;
  overflow-y: auto;
}

.modal {
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  z-index: 1001;
  position: relative;
  /* FIX: Ensure modal content is always visible when overlay is shown */
  display: block !important;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #e9ecef;
}

.modal-header h3 {
  margin: 0;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #999;
}

.close-btn:hover {
  color: #333;
}

.modal-body {
  padding: 20px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
  color: #333;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  box-sizing: border-box;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: var(--primary-medium-teal);
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
}

.form-group input[type="checkbox"] {
  width: auto;
  margin-right: 8px;
}

.form-help {
  display: block;
  margin-top: 5px;
  font-size: 12px;
  color: #6c757d;
  font-style: italic;
}

.form-actions button {
  min-width: 100px;
  text-align: center;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.loading-container {
  display: flex;
  align-items: center;
  gap: 10px;
}

.loading-spinner {
  width: 24px;
  height: 24px;
  border: 3px solid rgba(0, 123, 255, 0.3);
  border-top: 3px solid rgba(0, 123, 255, 1);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.loading-text {
  font-size: 14px;
  color: #333;
  font-weight: 500;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-message,
.success-message {
  position: fixed;
  top: 80px;
  right: 20px;
  padding: 15px 20px;
  border-radius: 4px;
  color: white;
  font-weight: 500;
  z-index: 1001;
  display: flex;
  align-items: center;
  gap: 10px;
  max-width: 400px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.success-message {
  background: #28a745;
}

.close-error,
.close-success {
  background: none;
  border: none;
  color: white;
  font-size: 18px;
  cursor: pointer;
  padding: 0;
  margin-left: auto;
}

/* Icon button styling */
.action-buttons {
  display: flex;
  gap: 0.5rem;
  justify-content: center;
}

.btn-icon {
  width: 32px;
  height: 32px;
  padding: 0;
  border-radius: 4px;
  border: 1px solid transparent;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  transition: all 0.2s ease;
}

.btn-icon:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.btn-icon:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-icon.btn-secondary {
  background-color: #6c757d;
  color: white;
}

.btn-icon.btn-secondary:hover:not(:disabled) {
  background-color: #5a6268;
}

.btn-icon.btn-info {
  background-color: #17a2b8;
  color: white;
}

.btn-icon.btn-info:hover:not(:disabled) {
  background-color: #138496;
}

.btn-icon.btn-danger {
  background-color: #dc3545;
  color: white;
}

.btn-icon.btn-danger:hover:not(:disabled) {
  background-color: #c82333;
}

@media (max-width: 768px) {
  .user-management {
    padding: 15px;
  }
  
  .header {
    flex-direction: column;
    align-items: stretch;
    gap: 15px;
  }
  
  .users-table {
    overflow-x: auto;
  }
  
  table {
    min-width: 600px;
  }
  
  .modal {
    width: 95%;
    margin: 20px;
  }
  
  .actions {
    flex-direction: column;
  }
}
</style>
