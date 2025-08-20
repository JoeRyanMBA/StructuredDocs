<template>
  <NotificationTicker
    :notifications="mergedNotifications"
    contextType="global"
    @mark-read="markNotificationRead"
  />
  <div class="author-view">
    <Breadcrumbs />
    <h2>✏️ Author</h2>
    <p>Write, edit, and organize topics here.</p>
  </div>
</template>

<script>
import Breadcrumbs from '@/components/Breadcrumbs.vue'
import NotificationTicker from '../components/NotificationTicker.vue'

export default {
  name: 'Author',
  components: { Breadcrumbs, NotificationTicker },
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

<style scoped>
.author-view {
  padding-top: 0px; /* Top padding to account for fixed header */
}
</style>