<template>
  <div class="notification-management">
    
    <div class="page-header">
      <div class="page-header-content">
        <h1>Notification Management</h1>
        <p class="subtitle">View and manage system notifications</p>
      </div>
      <div class="header-actions">
        <button @click="$router.push('/notifications/new')" class="btn btn-primary">
          <span class="icon-plus">➕︎</span> Create Notification
        </button>
      </div>
    </div>

    <div class="notifications-section">
      <div v-if="loading" class="loading-state">
        <div class="loading-content">
          <div class="loading-spinner"></div>
        </div>
      </div>

      <div v-else-if="error" class="error-state">
        <div class="error-content">
          <div class="error-icon">⚠️</div>
          <h3>Error Loading Notifications</h3>
          <p>{{ error }}</p>
          <button @click="fetchNotifications" class="btn btn-primary">🔄 Retry</button>
        </div>
      </div>

      <div v-else-if="notifications.length === 0" class="empty-state">
        <div class="empty-content">
          <div class="empty-icon">🔔</div>
          <h3>No Notifications</h3>
          <p>There are no notifications in the system yet.</p>
          <button @click="$router.push('/notifications/new')" class="btn btn-primary">
            <span class="icon-plus">➕︎</span> Create First Notification
          </button>
        </div>
      </div>

      <div v-else class="notifications-table-container">
        <table class="notifications-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Message</th>
              <th>Type</th>
              <th>Status</th>
              <th>Target</th>
              <th>Created</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="notification in notifications" :key="notification.id" class="notification-row">
              <td class="id-cell">{{ notification.id }}</td>
              <td class="message-cell">
                <div class="notification-message">{{ notification.message }}</div>
              </td>
              <td>
                <span class="type-badge" :class="notification.type">
                  {{ formatType(notification.type) }}
                </span>
              </td>
              <td>
                <span class="status-badge" :class="notification.is_active ? 'active' : 'inactive'">
                  {{ notification.is_active ? 'Active' : 'Inactive' }}
                </span>
              </td>
              <td class="target-cell">
                {{ notification.target_audience || 'All Users' }}
              </td>
              <td class="date-cell">
                {{ formatDate(notification.created_at) }}
              </td>
              <td class="actions-cell">
                <div class="notification-actions">
                  <button
                    @click="editNotification(notification)"
                    class="btn btn-secondary btn-sm"
                    title="Edit notification"
                  >
                    <i class="bi bi-pencil-square"></i> Edit
                  </button>
                  <button
                    @click="toggleNotification(notification)"
                    class="btn btn-sm"
                    :class="notification.is_active ? 'btn-outline' : 'btn-success'"
                    :title="notification.is_active ? 'Deactivate notification' : 'Activate notification'"
                  >
                    <i :class="['bi', notification.is_active ? 'bi-pause-fill' : 'bi-play-fill']"></i>
                    {{ notification.is_active ? 'Deactivate' : 'Activate' }}
                  </button>
                  <button
                    @click="deleteNotification(notification)"
                    class="btn btn-danger btn-sm"
                    title="Delete notification"
                  >
                    <i class="bi bi-trash"></i> Delete
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import { toast } from '@/composables/useToast'
import { apiGet, apiPost, apiDelete, normalizeListResponse } from '@/api/base.js'

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

function toFriendlyNotificationError(error) {
  if (isSessionExpiredError(error)) {
    return 'Your session has expired. Please sign in again.'
  }
  return error?.message || 'Failed to load notifications.'
}

export default {
  name: 'NotificationManagement',
  data() {
    return {
      notifications: [],
      loading: true,
      error: null
    }
  },
  async mounted() {
    await this.fetchNotifications()
  },
  methods: {
    async fetchNotifications() {
      this.loading = true
      this.error = null
      try {
        const payload = await apiGet('/api/notifications?include_inactive=true')
        this.notifications = normalizeListResponse(payload, ['notifications', 'items', 'results', 'data'])
      } catch (error) {
        console.error('Error fetching notifications:', error)
        const friendlyError = toFriendlyNotificationError(error)
        if (this.notifications.length > 0) {
          toast.error(friendlyError)
        } else {
          this.error = friendlyError
        }
      } finally {
        this.loading = false
      }
    },
    editNotification(notification) {
      this.$router.push(`/notifications/edit/${notification.id}`)
    },
    async toggleNotification(notification) {
      try {
        await apiPost(`/api/notifications/${notification.id}/toggle`)
        await this.fetchNotifications()
      } catch (error) {
        console.error('Error toggling notification:', error)
        toast.error(toFriendlyNotificationError(error))
      }
    },
    async deleteNotification(notification) {
      if (!confirm(`Are you sure you want to delete the notification "${notification.message}"?`)) return
      try {
        await apiDelete(`/api/notifications/${notification.id}`)
        await this.fetchNotifications()
      } catch (error) {
        console.error('Error deleting notification:', error)
        toast.error(toFriendlyNotificationError(error))
      }
    },
    formatType(type) {
      if (!type) return 'General'
      return type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())
    },
    formatDate(dateString) {
      if (!dateString) return '-'
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
      })
    }
  }
}
</script>

<style scoped>
.notification-management {
  max-width: none;
  width: 100%;
  margin: 0 auto;
  padding: 2rem;
  box-sizing: border-box;
}
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
}
.page-header-content h1 { margin: 0 0 0.5rem 0; color: var(--primary-deep-teal); }
.page-header-content .subtitle { margin: 0; color: var(--text-secondary-cool-gray); }
.header-actions { flex-shrink: 0; }
.notifications-section {
  background: var(--bg-white);
  border-radius: var(--border-radius-lg);
  padding: 1.5rem;
  box-shadow: var(--box-shadow-sm);
  border: 1px solid var(--border-light-gray);
}
.loading-state, .error-state, .empty-state { text-align: center; padding: 4rem 2rem; }
.loading-content, .error-content, .empty-content { display: flex; flex-direction: column; align-items: center; gap: 1rem; }
.loading-spinner, .error-icon, .empty-icon { font-size: 3rem; }
.notifications-table-container { width: 100%; overflow-x: auto; }
.notifications-table { width: 100%; min-width: 0; table-layout: auto; }
.notifications-table th, .notifications-table td { padding: 1rem; border-bottom: 1px solid var(--border-light-gray); }
.notifications-table th { background-color: var(--bg-light-mist-gray); font-weight: 600; color: var(--text-dark-gray); }
.notification-row:hover { background-color: var(--bg-light-mist-gray); }
.notification-message { max-width: none; overflow-wrap: anywhere; white-space: normal; }
.type-badge, .status-badge { padding: 0.25rem 0.75rem; border-radius: var(--border-radius-pill); font-size: 0.8rem; font-weight: 500; text-transform: capitalize; }
.type-badge.info { background-color: var(--info-light-blue); color: var(--info-dark-blue); }
.type-badge.warning { background-color: var(--warning-light-yellow); color: var(--warning-dark-yellow); }
.type-badge.success { background-color: var(--success-light-green); color: var(--success-dark-green); }
.type-badge.error { background-color: var(--error-light-red); color: var(--error-dark-red); }
.status-badge.active { background-color: var(--success-light-green); color: var(--success-dark-green); }
.status-badge.inactive { background-color: var(--extended-lavender-gray); color: var(--text-medium-gray); }
.notification-actions { display: flex; gap: 0.5rem; flex-wrap: wrap; }
.id-cell, .date-cell { white-space: nowrap; }
.target-cell { max-width: none; overflow-wrap: anywhere; white-space: normal; }
.actions-cell { width: auto; }

@media (max-width: 1024px) {
  .notification-management {
    padding: 1.25rem;
  }

  .notifications-section {
    padding: 1rem;
  }

  .notifications-table th,
  .notifications-table td {
    padding: 0.75rem;
    font-size: 0.92rem;
  }
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    gap: 0.75rem;
  }

  .header-actions {
    width: 100%;
  }

  .header-actions .btn {
    width: 100%;
  }

  .notification-actions {
    flex-direction: column;
    align-items: stretch;
  }

  .notification-actions .btn {
    width: 100%;
    justify-content: center;
  }
}
</style>