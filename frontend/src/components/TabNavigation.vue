<template>
  <nav class="tab-navigation" aria-label="Main navigation">
    <div class="nav-content">
      <div class="tab-container">
        <router-link
          v-for="tab in TABS"
          :key="tab.key"
          :to="{ name: tab.route }"
          class="tab"
          :class="{ active: isActiveTab(tab.route) }"
        >
          <span class="tab-icon">{{ tab.icon }}</span>
          <span class="tab-label">{{ tab.label }}</span>
        </router-link>
      </div>
      
      <div class="user-section">
        <div class="user-info" @click="toggleUserMenu">
          <span class="user-icon">👤</span>
          <span class="user-name">{{ currentUser?.name || 'User' }}</span>
          <span class="dropdown-arrow">▼</span>
        </div>
        
        <div v-if="showUserMenu" class="user-menu">
          <div class="user-details">
            <div class="user-detail-name">{{ currentUser?.name }}</div>
            <div class="user-detail-email">{{ currentUser?.email }}</div>
            <div class="user-detail-dept">{{ currentUser?.department }}</div>
          </div>
          <div class="menu-divider"></div>
          <button @click="logout" class="logout-btn">
            <span class="logout-icon">🚪</span>
            Logout
          </button>
        </div>
      </div>
    </div>
  </nav>
</template>

<script>
export default {
  name: 'TabNavigation',
  data() {
    return {
      showUserMenu: false,
      currentUser: null,
      TABS: [
        {
          key: 'home',
          label: 'Dashboard',
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
          key: 'author',
          label: 'Author',
          icon: '✏️',
          route: 'AuthorHome'
        },
        {
          key: 'collections',
          label: 'Collections',
          icon: '📑',
          route: 'Collections'
        },
        {
          key: 'import',
          label: 'Import',
          icon: '📥',
          route: 'ImportTopics'
        },
        {
          key: 'publish',
          label: 'Publish',
          icon: '📤',
          route: 'PublicationsHome'
        },
        {
          key: 'topics',
          label: 'Topics',
          icon: '📝',
          route: 'TopicsList'
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
          route: 'AdminHome'
        }
      ]
    }
  },
  mounted() {
    this.loadCurrentUser()
    // Close user menu when clicking outside
    document.addEventListener('click', this.handleClickOutside)
  },
  beforeUnmount() {
    document.removeEventListener('click', this.handleClickOutside)
  },
  methods: {
    isActiveTab(routeName) {
      return this.$route.name === routeName
    },
    
    loadCurrentUser() {
      const userStr = localStorage.getItem('user')
      if (userStr) {
        this.currentUser = JSON.parse(userStr)
      }
    },
    
    toggleUserMenu() {
      this.showUserMenu = !this.showUserMenu
    },
    
    handleClickOutside(event) {
      const userSection = event.target.closest('.user-section')
      if (!userSection) {
        this.showUserMenu = false
      }
    },
    
    logout() {
      localStorage.removeItem('isAuthenticated')
      localStorage.removeItem('user')
      this.currentUser = null
      this.showUserMenu = false
      this.$router.push({ name: 'Login' })
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
  justify-content: space-between;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

.tab-container {
  display: flex;
  overflow-x: auto;
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none; /* IE/Edge */
}

.tab-container::-webkit-scrollbar {
  display: none; /* Chrome/Safari */
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
  margin: 0 2px;
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

/* User Section Styles */
.user-section {
  position: relative;
}

.user-info {
  display: flex;
  align-items: center;
  padding: 0.5rem 1rem;
  background: #fff;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.user-info:hover {
  background: #f8f9fa;
  border-color: #005a9c;
  box-shadow: 0 2px 8px rgba(0, 90, 156, 0.15);
}

.user-icon {
  margin-right: 0.5rem;
  font-size: 1.1rem;
}

.user-name {
  margin-right: 0.5rem;
  font-weight: 500;
  color: #495057;
}

.dropdown-arrow {
  font-size: 0.8rem;
  color: #6c757d;
  transition: transform 0.2s ease;
}

.user-info:hover .dropdown-arrow {
  transform: rotate(180deg);
}

.user-menu {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 0.5rem;
  background: #fff;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  min-width: 200px;
  z-index: 1000;
}

.user-details {
  padding: 1rem;
}

.user-detail-name {
  font-weight: 600;
  color: #495057;
  margin-bottom: 0.25rem;
}

.user-detail-email {
  font-size: 0.9rem;
  color: #6c757d;
  margin-bottom: 0.25rem;
}

.user-detail-dept {
  font-size: 0.85rem;
  color: #868e96;
}

.menu-divider {
  height: 1px;
  background: #dee2e6;
  margin: 0.5rem 0;
}

.logout-btn {
  width: 100%;
  display: flex;
  align-items: center;
  padding: 0.75rem 1rem;
  background: none;
  border: none;
  color: #dc3545;
  cursor: pointer;
  transition: background-color 0.2s ease;
  border-radius: 0 0 8px 8px;
}

.logout-btn:hover {
  background: #f8f9fa;
  color: #c82333;
}

.logout-icon {
  margin-right: 0.5rem;
}

/* Responsive design */
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
}

@media (max-width: 480px) {
  .tab {
    padding: 0.5rem 0.75rem;
  }
  
  .tab-label {
    display: none; /* Show only icons on very small screens */
  }
  
  .tab-icon {
    margin-right: 0;
    font-size: 1.2rem;
  }
}
</style>
