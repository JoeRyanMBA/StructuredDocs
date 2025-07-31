<template>
  <div class="profile-container">
    <h1>Update Your Profile</h1>
    <div v-if="success" class="success-message">
      Profile updated successfully!
    </div>
    <form @submit.prevent="updateProfile" class="profile-form">
      <div class="form-group">
        <label>Name</label>
        <input type="text" v-model="profile.name" required />
      </div>
      <div class="form-group">
        <label>Title</label>
        <input type="text" v-model="profile.title" />
      </div>
      <div class="form-group">
        <label>Organization</label>
        <input type="text" v-model="profile.organization" />
      </div>
      <div class="form-group">
        <label>Email</label>
        <input type="email" v-model="profile.email" disabled />
        <span class="field-hint">Email cannot be changed</span>
      </div>
      <div class="form-actions">
        <button type="button" class="btn-secondary" @click="$router.go(-1)">Cancel</button>
        <button type="submit" class="btn-primary" :disabled="loading">
          {{ loading ? 'Saving...' : 'Save Changes' }}
        </button>
      </div>
    </form>
  </div>
</template>
<script>
export default {
  data() {
    return {
      loading: false,
      success: false,
      profile: {
        name: '',
        email: '',
        title: '',
        organization: ''
      }
    }
  },
  created() {
    const user = JSON.parse(localStorage.getItem('user') || '{}')
    this.profile = {
      name: user.name || '',
      email: user.email || '',
      title: user.title || '',
      organization: user.organization || ''
    }
  },
  methods: {
    async updateProfile() {
      this.loading = true
      this.success = false
      try {
        await new Promise(resolve => setTimeout(resolve, 800))
        const user = JSON.parse(localStorage.getItem('user') || '{}')
        const updatedUser = { ...user, ...this.profile }
        localStorage.setItem('user', JSON.stringify(updatedUser))
        this.success = true
        setTimeout(() => { this.success = false }, 3000)
      } catch (error) {
        console.error('Failed to update profile:', error)
        alert('Failed to update profile. Please try again.')
      } finally {
        this.loading = false
      }
    }
  }
}
</script>
<style scoped>
.profile-container {
  max-width: 600px;
  margin: 2rem auto;
  padding: 2rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}
h1 {
  color: #005a9c;
  margin-bottom: 1.5rem;
  font-size: 1.8rem;
  font-weight: 400;
}
.form-group {
  margin-bottom: 1.5rem;
}
.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #495057;
}
.form-group input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 1rem;
}
.form-group input:disabled {
  background-color: #f8f9fa;
  cursor: not-allowed;
}
.field-hint {
  display: block;
  margin-top: 0.25rem;
  font-size: 0.875rem;
  color: #6c757d;
}
.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 2rem;
}
.btn-primary, .btn-secondary {
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}
.btn-primary {
  background-color: #005a9c;
  color: white;
}
.btn-primary:hover {
  background-color: #004a80;
}
.btn-primary:disabled {
  background-color: #7ab5e0;
  cursor: not-allowed;
}
.btn-secondary {
  background-color: #f8f9fa;
  border: 1px solid #ced4da;
  color: #495057;
}
.btn-secondary:hover {
  background-color: #e9ecef;
}
.success-message {
  background-color: #d4edda;
  color: #155724;
  padding: 0.75rem;
  border-radius: 4px;
  margin-bottom: 1.5rem;
  text-align: center;
}
</style>
