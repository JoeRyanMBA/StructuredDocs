<template>
  <div :class="[{ 'login-bg': isLoginPage }]">
    <HeaderBar v-if="!isLoginPage" />
    <TabNavigation v-if="!isLoginPage" />
    <!-- NotificationTicker: always below TabNavigation -->
    <div class="full-width" v-if="!isLoginPage">
      <NotificationTicker
        :notifications="notifications"
        contextType="global"
        @mark-read="markNotificationRead"
      />
    </div>
    <main class="content" :class="{ 'login-content': isLoginPage }">
      <!-- <Breadcrumbs /> -->
      <router-view v-slot="{ Component, route }">
        <component
          :is="Component"
          v-bind="route.props"
          :notifications="notifications"
          :markNotificationRead="markNotificationRead"
        />
      </router-view>
    </main>
  </div>
</template>

<script>
import TabNavigation from '@/components/TabNavigation.vue'
import HeaderBar from '@/components/HeaderBar.vue'
import Breadcrumbs from '@/components/Breadcrumbs.vue'
import NotificationTicker from './components/NotificationTicker.vue'

export default {
  components: { TabNavigation, HeaderBar, Breadcrumbs, NotificationTicker },
  data() {
    return {
      notifications: [],
      notificationsLoading: false
    }
  },
  computed: {
    isLoginPage() {
      return this.$route.name === 'Login';
    }
  },
  watch: {
    $route() {
      // force update on route change
    }
  },
  created() {
    this.fetchNotifications()
  },
  methods: {
    async fetchNotifications() {
      this.notificationsLoading = true
      try {
        const res = await fetch('/api/notifications')
        if (res.ok) {
          const data = await res.json()
          this.notifications = Array.isArray(data) ? data : []
        } else {
          this.notifications = []
        }
      } catch (err) {
        console.error('Failed to fetch notifications:', err)
        this.notifications = []
      } finally {
        this.notificationsLoading = false
      }
    },
    async markNotificationRead(id) {
      try {
        await fetch(`/api/notifications/${id}`, {
          method: 'PATCH'
        })
        this.notifications = this.notifications.map(n => n.id === id ? { ...n, read: true } : n)
      } catch (err) {
        console.error('Failed to mark notification as read:', err)
      }
    }
  }
}
</script>

<style scoped>
.content {
  margin-top: 40px; /* Space for header (60px) + tabs (60px) */
  padding: 2rem;
  max-width: 1200px;
  margin-left: auto;
  margin-right: auto;
}

.login-bg {
  min-height: 100vh;
  background: linear-gradient(135deg, #005a9c 0%, #0074cc 100%) !important;
}

.login-content {
  margin-top: 0 !important;
  max-width: 100vw;
  padding: 0;
}

@media (max-width: 768px) {
  .content {
    margin-top: 110px; /* Slightly less space on mobile */
    padding: 1rem;
  }
  .login-content {
    margin-top: 0 !important;
    padding: 0;
  }
}
</style>