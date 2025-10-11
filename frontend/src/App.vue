<template>
  <div :class="[{ 'login-bg': isLoginPage }, { 'sidebar-layout': !isLoginPage, 'sidebar-open': sidebarOpen && !isLoginPage }]">
    <HeaderBar v-if="!isLoginPage" @toggle-sidebar="toggleSidebar" :sidebarOpen="sidebarOpen" />
    <SideBar v-if="!isLoginPage" :open="sidebarOpen" @close="closeSidebar" />
    <transition name="fade">
      <div v-if="!isLoginPage && sidebarOpen" class="sidebar-backdrop mobile-only" @click="closeSidebar" aria-hidden="true"></div>
    </transition>
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
    <VersionFooter />
    <ToastContainer />
  </div>
</template>

<script>
import SideBar from '@/components/SideBar.vue'
import HeaderBar from '@/components/HeaderBar.vue'
import NotificationTicker from './components/NotificationTicker.vue'
import FeedbackWidget from '@/components/FeedbackWidget.vue';
import ToastContainer from '@/components/ToastContainer.vue'
import VersionFooter from '@/components/VersionFooter.vue'

export default {
  components: { SideBar, HeaderBar, NotificationTicker, FeedbackWidget, ToastContainer, VersionFooter },
  data() {
    return {
      notifications: [],
      notificationsLoading: false,
      sidebarOpen: false
    }
  },
  computed: {
    // Ensure deduplicated notifications (by id+message) for ticker and children
    uniqueNotifications() {
      const seen = new Set()
      return (this.notifications || []).filter(n => {
        const key = `${n?.id ?? 'x'}|${n?.message ?? ''}`
        if (seen.has(key)) return false
        seen.add(key)
        return true
      })
    },
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
  mounted() {
    // Close sidebar when switching from mobile to desktop
    window.addEventListener('resize', this.handleResize)
  },
  beforeUnmount() {
    window.removeEventListener('resize', this.handleResize)
  },
  methods: {

    toggleSidebar() {
      this.sidebarOpen = !this.sidebarOpen
      // Only prevent scrolling on mobile when sidebar is open
      if (window.innerWidth <= 768) {
        document.documentElement.style.overflow = this.sidebarOpen ? 'hidden' : ''
      }
    },
    closeSidebar() {
      this.sidebarOpen = false
      document.documentElement.style.overflow = ''
    },
    handleResize() {
      // Close mobile sidebar when switching to desktop view
      if (window.innerWidth > 768 && this.sidebarOpen) {
        this.closeSidebar()
      }
    },
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
  min-height: 100vh;
  position: relative;
}

.ticker-bar {
  position: fixed;
/*  top: calc(var(--header-height) + 0.5rem); */
  left: 0;
  right: 0;
  height: var(--ticker-height);
  z-index: 998;
  background: #fff;
  border-bottom: 1px solid #e9ecef;
  box-shadow: 0 2px 4px #0000001a;
  display: flex;
  align-items: center;
}

.content {
  padding: 2rem;
  margin-left: 0;
  margin-top: calc(var(--header-height) + var(--ticker-height) + 0.5rem);
  width: 100%;
  cursor: default;
  transition: margin-left 240ms cubic-bezier(0.2, 0.8, 0.2, 1), width 240ms cubic-bezier(0.2, 0.8, 0.2, 1);
}

/* Desktop: sidebar pushes content over */
@media (min-width: 769px) {
  .sidebar-layout .content {
    margin-left: var(--sidebar-width);
    width: calc(100% - var(--sidebar-width));
  }
}

.sidebar-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.3);
  z-index: 900; /* below header (1100) and sidebar (1000) but above content */
  display: none; /* Hidden by default */
}

/* Show backdrop only on mobile when sidebar is open */
@media (max-width: 768px) {
  .sidebar-backdrop.mobile-only {
    display: block;
  }
}

/* Backdrop fade transition */
.fade-enter-active, .fade-leave-active { transition: opacity 180ms ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

.login-bg {
  min-height: 100vh;
  background: linear-gradient(135deg, var(--primary-light-teal) 0%, #005E7B 100%) !important;
}

.login-content {
  margin-top: 0 !important;
  max-width: 100vw;
  padding: 0;
  margin-left: 0;
  /* Ensure full available width so inner flex centering in LoginView isn't constrained by sidebar calc width */
  width: 100% !important;
  margin-right: 0;
}

@media (max-width: 768px) {
  .sidebar-layout {
    padding-top: var(--header-height);
  }
  .content {
    margin-left: 0;
    padding: 1rem;
    width: 100%;
    margin-top: calc(var(--header-height) + var(--ticker-height) + 0.25rem);
  }
  .login-content {
    margin-top: 0 !important;
    padding: 0;
  }
  .ticker-bar {
    left: 0;
    margin-top: 0;
  }
}
</style>