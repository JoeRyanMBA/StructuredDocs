<template>
  <div class="create-notification-view">
    
    <h1>Create Notification</h1>
    <form @submit.prevent="submitNotification">
      <div class="form-group">
        <label for="title">Title</label>
        <input id="title" v-model="title" required />
      </div>
      <div class="form-group">
        <label for="message">Message</label>
        <textarea id="message" v-model="message" required></textarea>
      </div>
      <div class="form-group">
        <label for="type">Notification Type</label>
        <select id="type" v-model="type">
          <option value="global">Global (All Dashboards)</option>
          <option value="admin">Admin (Admin Dashboard Only)</option>
          <option value="projects">Projects</option>
          <option value="author">Author</option>
          <option value="collections">Collections</option>
          <option value="import">Import</option>
          <option value="publish">Publish</option>
          <option value="topics">Topics</option>
          <option value="reviews">Reviews</option>
          <option value="snippets">Snippets</option>
        </select>
        <small style="color:#6c757d;display:block;margin-top:0.5rem;">
          Select where this notification should appear. "Global" shows on all dashboards. Others show only on their respective dashboard.
        </small>
      </div>
      <button type="submit" class="section-btn">Create</button>
    </form>
  </div>
</template>

<script>
import { toast } from '@/composables/useToast'
import { apiPost } from '@/api/base.js'
export default {
  name: 'CreateNotificationView',
  data() {
    return {
      title: '',
      message: '',
      type: 'global',
      loading: false
    }
  },
  methods: {
    async submitNotification() {
      this.loading = true
      try {
        await apiPost('/api/notifications', {
          title: this.title,
          message: this.message,
          type: this.type
        })
        toast.success('Notification created!')
        if (this.$root && typeof this.$root.fetchNotifications === 'function') {
          await this.$root.fetchNotifications()
        }
        this.$router.push('/admin')
      } catch (err) {
        toast.error('Failed to create notification.')
        console.error(err)
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style>
.create-notification-view {
  max-width: 500px;
  margin: 2rem auto;
  background: white;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 2rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}
.create-notification-view h1 {
  color: #205493;
  font-size: 2rem;
  margin-bottom: 1.5rem;
}
.form-group {
  margin-bottom: 1.25rem;
}
label {
  display: block;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: #495057;
}
input, textarea, select {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #e9ecef;
  border-radius: 4px;
  font-size: 1rem;
  margin-bottom: 0.25rem;
}
button.section-btn {
  background: #205493;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
}
button.section-btn:hover {
  background: #005E7B;
}
</style>
