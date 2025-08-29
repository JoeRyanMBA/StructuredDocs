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
  background: var(--bg-primary-white);
  border-radius: 8px;
  box-shadow: var(--shadow-md);
}
h1 {
  color: var(--primary-deep-teal);
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
  color: var(--text-primary-charcoal);
}
.form-group input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid var(--border-color-gray);
  border-radius: 4px;
  font-size: 1rem;
}
.form-group input:disabled {
  background-color: var(--bg-light-mist-gray);
  cursor: not-allowed;
}
.field-hint {
  display: block;
  margin-top: 0.25rem;
  font-size: 0.875rem;
  color: var(--text-secondary-cool-gray);
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
  background-color: var(--primary-deep-teal);
  color: white;
}
.btn-primary:hover {
  background-color: var(--primary-medium-teal);
}
.btn-primary:disabled {
  background-color: var(--primary-light-teal);
  cursor: not-allowed;
}
.btn-secondary {
  background-color: var(--bg-light-mist-gray);
  border: 1px solid var(--border-color-gray);
  color: var(--text-primary-charcoal);
}
.btn-secondary:hover {
  background-color: var(--extended-lavender-gray);
}
.success-message {
  background-color: var(--extended-cool-mint);
  color: var(--success-mint-green);
  padding: 0.75rem;
  border-radius: 4px;
  margin-bottom: 1.5rem;
  text-align: center;
}
</style>
