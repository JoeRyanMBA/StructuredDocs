<template>
  
    <div class="author-view">
    <div class="page-header">
      <h1>Author Dashboard</h1>
      <p class="subtitle">Manage your topics and content</p>
    </div>
</template>

<script>
export default {
  name: 'Author',
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