<template>
  <div class="edit-notification">
    <h2>Edit Notification</h2>
    <form @submit.prevent="saveNotification">
      <div class="form-group">
        <label for="title">Title</label>
        <input id="title" v-model="notification.title" required />
      </div>
      <div class="form-group">
        <label for="message">Message</label>
        <textarea id="message" v-model="notification.message" required></textarea>
      </div>
      <div class="form-group">
        <label for="type">Type</label>
        <select id="type" v-model="notification.type">
          <option value="global">Global</option>
          <option value="admin">Admin</option>
          <option value="reviewer">Reviewer</option>
          <option value="author">Author</option>
        </select>
      </div>
      <button type="submit" class="section-btn">Save Changes</button>
      <button type="button" class="section-btn secondary" @click="cancelEdit">Cancel</button>
    </form>
  </div>
</template>

<script>
export default {
  name: 'EditNotification',
  data() {
    return {
      notification: {
        title: '',
        message: '',
        type: 'global',
      },
      loading: true,
      error: null,
    }
  },
  async created() {
    const id = this.$route.params.id
    try {
      // Fetch notification from backend API
      const response = await fetch(`/api/notifications/${id}`)
      if (!response.ok) throw new Error('Failed to fetch notification')
      const data = await response.json()
      this.notification = {
        title: data.title || '',
        message: data.message || '',
        type: data.type || 'global',
      }
    } catch (err) {
      this.error = 'Failed to load notification.'
    } finally {
      this.loading = false
    }
  },
  methods: {
    async saveNotification() {
      // Update notification via backend API
      const id = this.$route.params.id
      try {
        const response = await fetch(`/api/notifications/${id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(this.notification)
        })
        if (!response.ok) throw new Error('Failed to update notification')
        alert('Notification updated!')
        this.$router.push('/admin')
      } catch (err) {
        alert('Failed to update notification.')
      }
    },
    cancelEdit() {
      this.$router.back()
    },
  },
}
</script>

<style scoped>
.edit-notification {
  max-width: 500px;
  margin: 2rem auto;
  background: white;
  border: 1px solid var(--extended-lavender-gray);
  border-radius: 8px;
  padding: 2rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}
.edit-notification h2 {
  margin-bottom: 1.5rem;
  color: var(--text-primary-charcoal);
  font-size: 1.5rem;
  font-weight: 600;
}
.form-group {
  margin-bottom: 1.25rem;
}
label {
  display: block;
  margin-bottom: 0.5rem;
  color: var(--text-primary-charcoal);
  font-weight: 500;
}
input, textarea, select {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid var(--extended-lavender-gray);
  border-radius: 4px;
  font-size: 1rem;
  margin-bottom: 0.25rem;
}
.section-btn {
  padding: 0.5rem 1rem;
  border: 1px solid var(--primary-deep-teal);
  border-radius: 4px;
  background: var(--primary-deep-teal);
  color: white;
  cursor: pointer;
  font-size: 0.875rem;
  transition: all 0.2s ease;
  margin-right: 0.5rem;
}
.section-btn.secondary {
  background: white;
  color: var(--primary-deep-teal);
}
.section-btn.secondary:hover {
  background: var(--bg-light-mist-gray);
}
</style>
