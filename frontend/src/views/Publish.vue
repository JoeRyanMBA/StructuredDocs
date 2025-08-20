<template>
  <NotificationTicker
    :notifications="mergedNotifications"
    contextType="global"
    @mark-read="markNotificationRead"
  />
  <div>
    <h2>📤 Publish</h2>
    <p>Export topics to PDF or HTML files.</p>
  </div>
</template>

<script>
import NotificationTicker from '../components/NotificationTicker.vue'

export default {
  name: 'Publish',
  components: { NotificationTicker },
  props: {
    notifications: {
      type: Array,
      default: () => []
    },
    globalNotifications: {
      type: Array,
      default: () => []
    },
    markNotificationRead: {
      type: Function,
      default: () => {}
    }
  },
  computed: {
    mergedNotifications() {
      // Combine global and dashboard-specific notifications, removing duplicates by id
      const all = [...(this.globalNotifications || []), ...(this.notifications || [])]
      const seen = new Set()
      return all.filter(n => {
        if (!n || !n.id) return true
        if (seen.has(n.id)) return false
        seen.add(n.id)
        return true
      })
    }
  }
}
</script>