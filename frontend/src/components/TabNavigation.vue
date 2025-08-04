<template>
  <nav class="tab-navigation" aria-label="Main navigation">
    <div class="nav-content">
      <div class="tab-container">
        <router-link
          v-for="tab in visibleTabs"
          :key="tab.key"
          :to="{ name: tab.route }"
          class="tab"
          :class="{ active: isActiveTab(tab.route) }"
        >
          <span class="tab-icon">{{ tab.icon }}</span>
          <span class="tab-label">{{ tab.label }}</span>
        </router-link>
      </div>
    </div>
  </nav>
</template>

<script>
export default {
  name: 'TabNavigation',
  data() {
    return {
      currentUser: {}, // Store user data reactively
      TABS: [
        {
          key: 'home',
          label: 'Home',
          icon: '🏠',
          route: 'Dashboard'
        },
        {
          key: 'projects',
          label: 'Projects',
          icon: '🎯',
          route: 'Projects'
        },
        {
          key: 'tasks',
          label: 'Tasks',
          icon: '✅',
          route: 'Tasks'
        },
                {
          key: 'collections',
          label: 'Collections',
          icon: '📑',
          route: 'Collections'
        },
        {
          key: 'document-builder',
          label: 'Builder',
          icon: '🔨',
          route: 'DocumentBuilder'
        },
                {
          key: 'topics',
          label: 'Topics',
          icon: '📝',
          route: 'TopicsList'
        },
        {
          key: 'author',
          label: 'Author',
          icon: '✏️',
          route: 'AuthorHome'
        },
        {
          key: 'import',
          label: 'Import',
          icon: '📥',
          route: 'ImportDashboard'
        },
        {
          key: 'publish',
          label: 'Publish',
          icon: '📤',
          route: 'PublicationsHome'
        },

        {
          key: 'reviews',
          label: 'Reviews',
          icon: '✅',
          route: 'ReviewsHome'
        },
        {
          key: 'admin',
          label: 'Admin',
          icon: '⚙️',
          route: 'Admin',
          adminOnly: true
        }
      ]
    }
  },
  computed: {
    visibleTabs() {
      const tabs = this.TABS.filter(tab => {
        if (tab.adminOnly) {
          const isAdmin = this.currentUser.role === 'admin'
          console.log(`🔍 TabNavigation - Tab ${tab.label} (adminOnly): visible = ${isAdmin}`)
          console.log(`🔍 TabNavigation - Current user role: ${this.currentUser.role}`)
          return isAdmin
        }
        return true
      })
      console.log('🔍 TabNavigation - Visible tabs:', tabs.map(t => t.label))
      return tabs
    }
  },
  mounted() {
    // Load current user info initially
    this.updateCurrentUser()
    
    // Listen for storage changes to update tabs when user logs in/out
    window.addEventListener('storage', this.handleStorageChange)
    
    // Listen for a custom event that we'll emit after login
    window.addEventListener('userUpdated', this.handleUserUpdate)
    
    console.log('🔍 TabNavigation - Component mounted, initial user check')
  },
  beforeUnmount() {
    window.removeEventListener('storage', this.handleStorageChange)
    window.removeEventListener('userUpdated', this.handleUserUpdate)
  },
  methods: {
    updateCurrentUser() {
      try {
        const user = JSON.parse(localStorage.getItem('user') || '{}')
        this.currentUser = user
        console.log('🔍 TabNavigation - Updated current user:', user)
        console.log('🔍 TabNavigation - User role:', user.role)
        console.log('🔍 TabNavigation - Is admin:', user.role === 'admin')
      } catch {
        console.log('🔍 TabNavigation - Failed to parse user data')
        this.currentUser = {}
      }
    },
    isActiveTab(routeName) {
      return this.$route.name === routeName
    },
    handleStorageChange() {
      // Force reactivity update when localStorage changes from another window
      this.updateCurrentUser()
      console.log('🔍 TabNavigation - Storage changed, triggering update')
    },
    handleUserUpdate() {
      // Handle custom event when user logs in/out in same window
      this.updateCurrentUser()
      console.log('🔍 TabNavigation - User update event received')
    }
  }
}
</script>

<style scoped>
.tab-navigation {
  position: fixed;
  top: 60px; /* Below the header */
  left: 0;
  right: 0;
  background: #f8f9fa;
  border-bottom: 2px solid #e9ecef;
  z-index: 1000;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.nav-content {
  display: flex;
  justify-content: center;
  align-items: center;
  max-width: 100%;
  margin: 0 auto;
  padding: 0 1rem;
  overflow-x: auto;
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none; /* IE/Edge */
}

.nav-content::-webkit-scrollbar {
  display: none; /* Chrome/Safari */
}

.tab-container {
  display: flex;
  min-width: fit-content;
  gap: 2px;
  justify-content: center;
}

.tab {
  display: flex;
  align-items: center;
  padding: 0.75rem 1.5rem;
  text-decoration: none;
  color: #6c757d;
  border-bottom: 3px solid transparent;
  transition: all 0.3s ease;
  white-space: nowrap;
  min-width: fit-content;
  background: transparent;
  border-radius: 8px 8px 0 0;
  margin: 0;
  flex-shrink: 0;
}

.tab:hover {
  color: #005a9c;
  background: rgba(0, 90, 156, 0.05);
  border-bottom-color: rgba(0, 90, 156, 0.3);
}

.tab.active {
  color: #005a9c;
  background: #fff;
  border-bottom-color: #005a9c;
  font-weight: 600;
  box-shadow: 0 -2px 8px rgba(0, 0, 0, 0.1);
}

.tab-icon {
  margin-right: 0.5rem;
  font-size: 1.1rem;
}

.tab-label {
  font-size: 0.95rem;
}

/* Responsive design */
@media (max-width: 1024px) {
  .tab {
    padding: 0.6rem 1.2rem;
    font-size: 0.9rem;
  }
  
  .tab-label {
    font-size: 0.9rem;
  }
}

@media (max-width: 768px) {
  .tab {
    padding: 0.6rem 1rem;
    font-size: 0.9rem;
  }
  
  .tab-icon {
    margin-right: 0.3rem;
    font-size: 1rem;
  }
  
  .tab-label {
    font-size: 0.85rem;
  }
  
  .nav-content {
    padding: 0 0.5rem;
  }
}

@media (max-width: 640px) {
  .tab {
    padding: 0.5rem 0.8rem;
  }
  
  .tab-label {
    font-size: 0.8rem;
  }
}

@media (max-width: 480px) {
  .tab {
    padding: 0.5rem 0.6rem;
    flex-direction: column;
    min-width: 60px;
  }
  
  .tab-label {
    font-size: 0.7rem;
    margin-top: 0.2rem;
  }
  
  .tab-icon {
    margin-right: 0;
    font-size: 1.1rem;
  }
}
</style>
