<template>
  <div v-if="filteredNotifications.length" class="notification-ticker">
    <div class="ticker-content">
      <div
        v-for="notification in filteredNotifications"
        :key="notification.id"
        class="notification-item"
        :class="{ unread: !notification.read }"
      >
        <a :href="notification.link" @click="markAsRead(notification)" class="notification-link">
          <span class="notification-message">{{ notification.message }}</span>
          <span class="notification-date">{{ formatDate(notification.created_at) }}</span>
        </a>
      </div>
    </div>
    <button v-if="filteredNotifications.length > 1" class="scroll-btn up" @click="scrollUp">▲</button>
    <button v-if="filteredNotifications.length > 1" class="scroll-btn down" @click="scrollDown">▼</button>
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
  margin-bottom: 1rem;
  padding: 0.5rem;
  background: #0094a815;
  border-radius: 6px;
  border-left: 6px solid #0095A8;
  display: flex;
  position: relative;
  overflow: hidden;
  min-height: 48px;
}
.ticker-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  max-height: 48px;
  overflow: hidden;
}
.notification-item {
  padding: 0.25rem 0;
  font-size: .875rem;
  color: #333333;
  transition: background 0.2s;
}
 .notification-item.unread {
  font-weight: normal;

}
.notification-link {
  text-decoration: none;
  color: inherit;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.notification-message {
  margin-right: 1rem;
}
.notification-date {
  font-size: 0.85rem;
  color: #6b7280;
}
.scroll-btn {
  background: none;
  border: none;
  color: #205493;
  font-size: 1.2rem;
  cursor: pointer;
  padding: 0 0.5rem;
  transition: color 0.2s;
}
.scroll-btn:hover {
  color: #003366;
}
</style>
