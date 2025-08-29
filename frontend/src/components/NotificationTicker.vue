<template>
  <div class="notification-ticker">
    <div v-if="filteredNotifications.length > 0" class="ticker-content-wrapper">
      <button v-if="filteredNotifications.length > 1" class="scroll-btn up" @click="scrollUp" :disabled="currentIndex === 0">▲</button>
      <div class="ticker-content">
        <div
          v-if="currentNotification"
          class="notification-item"
          :class="{ unread: !currentNotification.read }"
        >
          <a :href="currentNotification.link" @click="markAsRead(currentNotification)" class="notification-link">
            <span class="notification-message">{{ currentNotification.message }}</span>
            <span class="notification-date">{{ formatDate(currentNotification.created_at) }}</span>
          </a>
        </div>
      </div>
      <button v-if="filteredNotifications.length > 1" class="scroll-btn down" @click="scrollDown" :disabled="currentIndex === filteredNotifications.length - 1">▼</button>
    </div>
    <div v-else class="no-notifications">
      <span>No new notifications.</span>
    </div>
  </div>
</template>

<script>
export default {
  name: 'NotificationTicker',
  props: {
    notifications: {
      type: Array,
      required: true
    },
    contextType: {
      type: String,
      default: 'global' // e.g., 'global', 'project', 'publish', 'review'
    }
  },
  data() {
    return {
      currentIndex: 0
    }
  },
  computed: {
    filteredNotifications() {
      // Show global + context-specific notifications
      return this.notifications.filter(n =>
        n.type === 'global' || n.type === this.contextType
      )
    },
    currentNotification() {
      return this.filteredNotifications[this.currentIndex] || null
    }
  },
  methods: {
    scrollUp() {
      if (this.currentIndex > 0) {
        this.currentIndex--
      }
    },
    scrollDown() {
      if (this.currentIndex < this.filteredNotifications.length - 1) {
        this.currentIndex++
      }
    },
    markAsRead(notification) {
      if (!notification.read) {
        // Call API to mark as read
        this.$emit('mark-read', notification.id)
        notification.read = true
      }
    },
    formatDate(dateStr) {
      if (!dateStr) {
        return 'Recently'
      }
      try {
        const d = new Date(dateStr)
        if (isNaN(d.getTime())) {
          return 'Recently'
        }
        return d.toLocaleDateString()
      } catch (error) {
        return 'Recently'
      }
    }
  }
}
</script>

<style scoped>
.notification-ticker {
  position: relative; /* Changed from fixed to relative */
  height: auto; /* Let content determine height */
  min-height: var(--ticker-height);
  background-color: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
  padding: 0.5rem 1rem;
  display: flex;
  align-items: center;
  z-index: 999;
}

.ticker-content-wrapper {
  display: flex;
  align-items: center;
  width: 100%;
}

.ticker-content {
  flex-grow: 1;
  overflow: hidden;
}

.notification-item {
  display: flex;
  align-items: center;
  padding: 0.25rem 0;
}

.scroll-btn {
  background: none;
  border: none;
  color: #6c757d;
  cursor: pointer;
  padding: 0 0.5rem;
  font-size: 1em;
  align-self: center;
}

.scroll-btn.up {
  margin-left: 1rem;
}

@media (max-width: 768px) {
  .notification-ticker {
    left: 0;
  }
}

.ticker-content-wrapper {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.ticker-content {
  overflow: hidden;
  height: auto; /* Adjust height to show all items */
  flex-grow: 1;
}

.notification-item {
  display: flex;
  align-items: center;
  height: 1.5em;
  transition: transform 0.3s ease-in-out;
}

.notification-link {
  color: inherit;
  text-decoration: none;
  display: flex;
  align-items: center;
  width: 100%;
}

.notification-link:hover {
  color: #205493;
}

.notification-message {
  flex-grow: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  text-align: center;
}

.notification-date {
  margin-left: 1rem;
  font-size: 0.8em;
  color: #adb5bd;
  white-space: nowrap;
}

.unread .notification-message {
  font-weight: 500;
  color: var(--extended-plum);
}

.scroll-btn {
  background: none;
  border: none;
  color: #6c757d;
  cursor: pointer;
  padding: 0 0.5rem;
  font-size: 0.8em;
}

.scroll-btn:hover {
  color: #205493;
}

.no-notifications {
  width: 100%;
  text-align: center;
  font-style: italic;
  color: #6c757d;
}
</style>

