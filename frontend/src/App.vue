<template>
  <div :class="[{ 'login-bg': isLoginPage }, { 'sidebar-layout': !isLoginPage }]">
    <HeaderBar v-if="!isLoginPage" />
    <SideBar v-if="!isLoginPage" />
  <div class="ticker-bar" v-if="!isLoginPage">
      <NotificationTicker
        :notifications="notifications"
        contextType="global"
        @mark-read="markNotificationRead"
      />
    </div>
    <main class="content" :class="{ 'login-content': isLoginPage }">
      <router-view v-slot="{ Component, route }">
        <component
          :is="Component"
          v-bind="route.props"
          :globalNotifications="notifications"
          :markNotificationRead="markNotificationRead"
        />
      </router-view>
    </main>
    <FeedbackWidget />
  </div>
</template>

<script>
import SideBar from '@/components/SideBar.vue'
import HeaderBar from '@/components/HeaderBar.vue'
import NotificationTicker from './components/NotificationTicker.vue'
import FeedbackWidget from '@/components/FeedbackWidget.vue';

export default {
  components: { SideBar, HeaderBar, NotificationTicker, FeedbackWidget },
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

<style>
:root {
  --header-height: 60px;
  --sidebar-width: 250px;
  --ticker-height: 40px; /* Example height */
}

.sidebar-layout {
  display: flex;
  padding-top: var(--header-height);
}

.content {
  padding: 2rem;
  max-width: 1200px;
  margin-left: var(--sidebar-width);
  margin-right: auto;
  margin-top: var(--ticker-height);
  flex-grow: 1;
  width: calc(100% - var(--sidebar-width));
  cursor: default; /* Sets the default cursor for the content area */
}

.login-bg {
  min-height: 100vh;
  background: linear-gradient(135deg, #205493 0%, #005E7B 100%) !important;
}

.login-content {
  margin-top: 0 !important;
  max-width: 100vw;
  padding: 0;
  margin-left: 0;
}

.ticker-bar {
  position: fixed;
  top: var(--header-height);
  left: var(--sidebar-width);
  right: 0;
  z-index: 998; /* Below header, above content */
  background-color: #fff;
}

@media (max-width: 768px) {
  .sidebar-layout {
    padding-top: var(--header-height);
  }
  .content {
    margin-left: 0;
    padding: 1rem;
    width: 100%;
    margin-top: var(--ticker-height);
  }
  .login-content {
    margin-top: 0 !important;
    padding: 0;
  }
  .ticker-bar {
    left: 0;
  }
}
</style>