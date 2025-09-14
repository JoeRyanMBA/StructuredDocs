&lt;template&gt;
  &lt;div class="notification-management"&gt;
    &lt;div class="page-header"&gt;
      &lt;div class="page-header-content"&gt;
        &lt;h1&gt;Notification Management&lt;/h1&gt;
        &lt;p class="subtitle"&gt;View and manage system notifications&lt;/p&gt;
      &lt;/div&gt;
      &lt;div class="header-actions"&gt;
        &lt;button @click="$router.push('/notifications/new')" class="btn btn-primary"&gt;
          &lt;i class="fas fa-plus"&gt;&lt;/i&gt; Create Notification
        &lt;/button&gt;
      &lt;/div&gt;
    &lt;/div&gt;

    &lt;div class="notifications-section"&gt;
      &lt;div v-if="loading" class="loading-state"&gt;
        &lt;div class="loading-content"&gt;
          &lt;div class="loading-spinner"&gt;⏳&lt;/div&gt;
          &lt;h3&gt;Loading Notifications...&lt;/h3&gt;
        &lt;/div&gt;
      &lt;/div&gt;

      &lt;div v-else-if="error" class="error-state"&gt;
        &lt;div class="error-content"&gt;
          &lt;div class="error-icon"&gt;⚠️&lt;/div&gt;
          &lt;h3&gt;Error Loading Notifications&lt;/h3&gt;
          &lt;p&gt;{{ error }}&lt;/p&gt;
          &lt;button @click="fetchNotifications" class="btn btn-primary"&gt;🔄 Retry&lt;/button&gt;
        &lt;/div&gt;
      &lt;/div&gt;

      &lt;div v-else-if="notifications.length === 0" class="empty-state"&gt;
        &lt;div class="empty-content"&gt;
          &lt;div class="empty-icon"&gt;🔔&lt;/div&gt;
          &lt;h3&gt;No Notifications&lt;/h3&gt;
          &lt;p&gt;There are no notifications in the system yet.&lt;/p&gt;
          &lt;button @click="$router.push('/notifications/new')" class="btn btn-primary"&gt;
            &lt;i class="fas fa-plus"&gt;&lt;/i&gt; Create First Notification
          &lt;/button&gt;
        &lt;/div&gt;
      &lt;/div&gt;

      &lt;div v-else class="notifications-table-container"&gt;
        &lt;table class="notifications-table"&gt;
          &lt;thead&gt;
            &lt;tr&gt;
              &lt;th&gt;ID&lt;/th&gt;
              &lt;th&gt;Message&lt;/th&gt;
              &lt;th&gt;Type&lt;/th&gt;
              &lt;th&gt;Status&lt;/th&gt;
              &lt;th&gt;Target&lt;/th&gt;
              &lt;th&gt;Created&lt;/th&gt;
              &lt;th&gt;Actions&lt;/th&gt;
            &lt;/tr&gt;
          &lt;/thead&gt;
          &lt;tbody&gt;
            &lt;tr v-for="notification in notifications" :key="notification.id" class="notification-row"&gt;
              &lt;td class="id-cell"&gt;{{ notification.id }}&lt;/td&gt;
              &lt;td class="message-cell"&gt;
                &lt;div class="notification-message"&gt;{{ notification.message }}&lt;/div&gt;
              &lt;/td&gt;
              &lt;td&gt;
                &lt;span class="type-badge" :class="notification.type"&gt;
                  {{ formatType(notification.type) }}
                &lt;/span&gt;
              &lt;/td&gt;
              &lt;td&gt;
                &lt;span class="status-badge" :class="notification.is_active ? 'active' : 'inactive'"&gt;
                  {{ notification.is_active ? 'Active' : 'Inactive' }}
                &lt;/span&gt;
              &lt;/td&gt;
              &lt;td class="target-cell"&gt;
                {{ notification.target_audience || 'All Users' }}
              &lt;/td&gt;
              &lt;td class="date-cell"&gt;
                {{ formatDate(notification.created_at) }}
              &lt;/td&gt;
              &lt;td class="actions-cell"&gt;
                &lt;div class="notification-actions"&gt;
                  &lt;button 
                    @click="editNotification(notification)" 
                    class="btn btn-sm btn-secondary"
                    title="Edit notification"
                  &gt;
                    &lt;i class="fas fa-edit"&gt;&lt;/i&gt; Edit
                  &lt;/button&gt;
                  &lt;button 
                    @click="toggleNotification(notification)" 
                    class="btn btn-sm"
                    :class="notification.is_active ? 'btn-warning' : 'btn-success'"
                    :title="notification.is_active ? 'Deactivate notification' : 'Activate notification'"
                  &gt;
                    &lt;i class="fas" :class="notification.is_active ? 'fa-pause' : 'fa-play'"&gt;&lt;/i&gt;
                    {{ notification.is_active ? 'Deactivate' : 'Activate' }}
                  &lt;/button&gt;
                  &lt;button 
                    @click="deleteNotification(notification)" 
                    class="btn btn-sm btn-danger"
                    title="Delete notification"
                  &gt;
                    &lt;i class="fas fa-trash"&gt;&lt;/i&gt; Delete
                  &lt;/button&gt;
                &lt;/div&gt;
              &lt;/td&gt;
            &lt;/tr&gt;
          &lt;/tbody&gt;
        &lt;/table&gt;
      &lt;/div&gt;
    &lt;/div&gt;
  &lt;/div&gt;
&lt;/template&gt;

&lt;script&gt;
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
        const response = await fetch('/api/notifications')
        if (!response.ok) {
          throw new Error('Failed to fetch notifications')
        }
        this.notifications = await response.json()
      } catch (error) {
        console.error('Error fetching notifications:', error)
        this.error = error.message
      } finally {
        this.loading = false
      }
    },
    
    editNotification(notification) {
      this.$router.push(`/notifications/edit/${notification.id}`)
    },
    
    async toggleNotification(notification) {
      try {
        const response = await fetch(`/api/notifications/${notification.id}/toggle`, {
          method: 'POST'
        })
        
        if (!response.ok) {
          throw new Error('Failed to toggle notification')
        }
        
        // Refresh the list
        await this.fetchNotifications()
      } catch (error) {
        console.error('Error toggling notification:', error)
        alert('Failed to toggle notification')
      }
    },
    
    async deleteNotification(notification) {
      if (!confirm(`Are you sure you want to delete the notification "${notification.message}"?`)) {
        return
      }
      
      try {
        const response = await fetch(`/api/notifications/${notification.id}`, {
          method: 'DELETE'
        })
        
        if (!response.ok) {
          throw new Error('Failed to delete notification')
        }
        
        // Refresh the list
        await this.fetchNotifications()
      } catch (error) {
        console.error('Error deleting notification:', error)
        alert('Failed to delete notification')
      }
    },
    
    formatType(type) {
      return type ? type.replace('_', ' ').replace(/\b\w/g, l =&gt; l.toUpperCase()) : 'General'
    },
    
    formatDate(dateString) {
      if (!dateString) return '-'
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    }
  }
}
&lt;/script&gt;

&lt;style scoped&gt;
.notification-management {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
}

.page-header-content h1 {
  margin: 0 0 0.5rem 0;
  color: var(--primary-deep-teal);
}

.page-header-content .subtitle {
  margin: 0;
  color: var(--text-secondary-cool-gray);
}

.header-actions {
  flex-shrink: 0;
}

.notifications-section {
  background: var(--bg-white);
  border-radius: var(--border-radius-lg);
  padding: 1.5rem;
  box-shadow: var(--box-shadow-sm);
  border: 1px solid var(--border-light-gray);
}

.loading-state, .error-state, .empty-state {
  text-align: center;
  padding: 4rem 2rem;
}

.loading-content, .error-content, .empty-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.loading-spinner, .error-icon, .empty-icon {
  font-size: 3rem;
}

.notifications-table-container {
  overflow-x: auto;
}

.notifications-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 800px;
}

.notifications-table th,
.notifications-table td {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid var(--border-light-gray);
}

.notifications-table th {
  background-color: var(--bg-light-mist-gray);
  font-weight: 600;
  color: var(--text-dark-gray);
}

.notification-row:hover {
  background-color: var(--bg-light-mist-gray);
}

.notification-message {
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.type-badge, .status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: var(--border-radius-pill);
  font-size: 0.8rem;
  font-weight: 500;
  text-transform: capitalize;
}

.type-badge.info { background-color: var(--info-light-blue); color: var(--info-dark-blue); }
.type-badge.warning { background-color: var(--warning-light-yellow); color: var(--warning-dark-yellow); }
.type-badge.success { background-color: var(--success-light-green); color: var(--success-dark-green); }
.type-badge.error { background-color: var(--error-light-red); color: var(--error-dark-red); }

.status-badge.active { background-color: var(--success-light-green); color: var(--success-dark-green); }
.status-badge.inactive { background-color: var(--extended-lavender-gray); color: var(--text-medium-gray); }

.notification-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: nowrap;
}

.id-cell, .date-cell {
  white-space: nowrap;
}

.target-cell {
  max-width: 150px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.actions-cell {
  width: 200px;
}
&lt;/style&gt;