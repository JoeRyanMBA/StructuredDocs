<template>
  <div :class="[{ 'login-bg': isLoginPage }, { 'sidebar-layout': !isPublicPage, 'sidebar-open': sidebarOpen && !isPublicPage }]">
    <HeaderBar v-if="!isPublicPage" @toggle-sidebar="toggleSidebar" :sidebarOpen="sidebarOpen" />
    <Sidebar v-if="!isPublicPage" :open="sidebarOpen" @close="closeSidebar" />
    <transition name="fade">
      <div v-if="!isPublicPage && sidebarOpen" class="sidebar-backdrop mobile-only" @click="closeSidebar" aria-hidden="true"></div>
    </transition>
    <div class="ticker-bar" v-if="!isPublicPage">
      <NotificationTicker
        :notifications="notifications"
        :contextType="notificationContextType"
        @mark-read="markNotificationRead"
      />
    </div>
    <main class="content" :class="{ 'login-content': isPublicPage }">
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
    <SessionTimeoutModal
      :show="sessionWarning"
      :secondsRemaining="sessionSecondsRemaining"
      :expired="sessionExpired"
      @extend="sessionExtend"
      @logout="sessionLogout"
    />
  </div>
</template>

<script>
import Sidebar from '@/components/SideBar.vue'
import HeaderBar from '@/components/HeaderBar.vue'
import NotificationTicker from './components/NotificationTicker.vue'
import FeedbackWidget from '@/components/FeedbackWidget.vue';
import ToastContainer from '@/components/ToastContainer.vue'
import VersionFooter from '@/components/VersionFooter.vue'
import SessionTimeoutModal from '@/components/SessionTimeoutModal.vue'
import { useSessionTimeout } from '@/composables/useSessionTimeout'
import { apiGet, apiRequest } from '@/api/base.js'

export default {
  components: { Sidebar, HeaderBar, NotificationTicker, FeedbackWidget, ToastContainer, VersionFooter, SessionTimeoutModal },
  setup() {
    const { showWarning, secondsRemaining, sessionExpired, startWatcher, stopWatcher, extendSession, performLogout } = useSessionTimeout()
    return {
      sessionWarning: showWarning,
      sessionSecondsRemaining: secondsRemaining,
      sessionExpired,
      sessionExtend: extendSession,
      sessionLogout: performLogout,
      startSessionWatcher: startWatcher,
      stopSessionWatcher: stopWatcher,
    }
  },
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
    },
    isPublicPage() {
      return this.$route.name === 'Login' || this.$route.name === 'ReviewPortal' || this.$route.name === 'BulkReviewPortal';
    },
    notificationContextType() {
      const path = this.$route?.path || ''

      if (path.startsWith('/author')) return 'author'
      if (path.startsWith('/admin') || path.startsWith('/notifications')) return 'admin'
      if (path.startsWith('/projects') || path.startsWith('/all-tags') || path.startsWith('/all-stakeholders') || path.startsWith('/all-milestones')) return 'projects'
      if (path.startsWith('/collections') || path.startsWith('/organize')) return 'collections'
      if (path.startsWith('/import')) return 'import'
      if (path.startsWith('/publications') || path.startsWith('/publish')) return 'publish'
      if (path.startsWith('/reviews') || path.startsWith('/review/')) return 'reviews'
      if (path.startsWith('/topics') || path.startsWith('/all-images') || path.startsWith('/all-links')) return 'topics'

      return 'global'
    }
  },
  watch: {
    $route() {
      // force update on route change
    }
  },
  created() {
    this.fetchNotifications()
    // Start session watcher if user is already logged in
    if (localStorage.getItem('access_token')) {
      this.startSessionWatcher()
    }
    // Restart watcher after login and stop it after logout
    window.addEventListener('userUpdated', this._onUserUpdated)
  },
  mounted() {
    // Close sidebar when switching from mobile to desktop
    window.addEventListener('resize', this.handleResize)
  },
  beforeUnmount() {
    window.removeEventListener('resize', this.handleResize)
    window.removeEventListener('userUpdated', this._onUserUpdated)
    this.stopSessionWatcher()
  },
  methods: {
    _onUserUpdated() {
      if (localStorage.getItem('access_token')) {
        this.startSessionWatcher()
        this.fetchNotifications()
      } else {
        this.stopSessionWatcher()
        this.notifications = []
      }
    },
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
        const data = await apiGet('/api/notifications')
        this.notifications = Array.isArray(data) ? data : []
      } catch (err) {
        console.error('Failed to fetch notifications:', err)
        this.notifications = []
      } finally {
        this.notificationsLoading = false
      }
    },
    async markNotificationRead(id) {
      try {
        await apiRequest(`/api/notifications/${id}`, { method: 'PATCH' })
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
  top: var(--header-height);
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
  margin-top: calc(var(--header-height) + var(--ticker-height));
  width: 100%;
  cursor: default;
  transition: margin-left 240ms cubic-bezier(0.2, 0.8, 0.2, 1), width 240ms cubic-bezier(0.2, 0.8, 0.2, 1);
}

/* Desktop: sidebar pushes content over */
@media (min-width: 769px) {
  .sidebar-layout .content {
    /* Push content to the right of the fixed sidebar */
    margin-left: var(--sidebar-width) !important;
    width: calc(100% - var(--sidebar-width)) !important;
    margin-top: calc(var(--header-height) + var(--ticker-height)) !important;
    padding: 2rem !important; /* Ensure padding is maintained */
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