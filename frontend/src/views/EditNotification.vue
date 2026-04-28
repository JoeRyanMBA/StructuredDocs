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
      </div>
      <button type="submit" class="section-btn">Save Changes</button>
      <button type="button" class="section-btn secondary" @click="cancelEdit">Cancel</button>
    </form>
  </div>
</template>

<script>
import { toast } from '@/composables/useToast'
import { apiGet, apiPut } from '@/api/base.js'

function isSessionExpiredError(error) {
  const message = String(error?.message || '').toLowerCase()
  return (
    message.includes('signature verification failed') ||
    message.includes('token has expired') ||
    message.includes('jwt') ||
    message.includes('unauthorized') ||
    message.includes('401')
  )
}

function toFriendlyNotificationError(error, fallback) {
  if (isSessionExpiredError(error)) {
    return 'Your session has expired. Please sign in again.'
  }
  return error?.message || fallback
}

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
      error: null
    }
  },
  async created() {
    const id = this.$route.params.id
    try {
      const data = await apiGet(`/api/notifications/${id}`)
      this.notification = {
        title: data.title || '',
        message: data.message || '',
        type: data.type || 'global',
      }
    } catch (err) {
      this.error = toFriendlyNotificationError(err, 'Failed to load notification.')
      toast.error(this.error)
    } finally {
      this.loading = false
    }
  },
  methods: {
    async saveNotification() {
      const id = this.$route.params.id
      try {
        await apiPut(`/api/notifications/${id}`, this.notification)
        toast.success('Notification updated!')
        this.$router.push('/admin')
      } catch (err) {
        toast.error(toFriendlyNotificationError(err, 'Failed to update notification.'))
      }
    },
    cancelEdit() {
      this.$router.back()
    }
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
