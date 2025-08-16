<template>
  <header class="header-bar">
    <router-link to="/projects" class="logo-link">
      <img
        class="logo"
        src="https://www.census.gov/etc.clientlibs/census/clientlibs/census-pattern-library/resources/images/USCENSUS_IDENTITY_SOLO_BLACK_1.5in_R_no_padding.svg"
        alt="Census Bureau logo"
      />
    </router-link>
    <router-link to="/projects" class="title-link">
      <h1 class="title">SCCMB Documentation Project Hub</h1>
    </router-link>
    
    <!-- User section with better positioning -->
    <div v-if="isLoggedIn" class="user-section">
      <div class="user-info" @click="toggleUserDropdown">
        <span class="user-icon">👤</span>
        <span class="user-name">{{ currentUser?.name || 'User' }}</span>
        <span class="dropdown-arrow" :class="{ open: showUserDropdown }">▼</span>
      </div>
      
      <div v-if="showUserDropdown" class="user-dropdown" @click.stop>
        <div class="dropdown-items">
          <router-link to="/profile" class="dropdown-item" @click="closeDropdown">
            <i class="fas fa-user-edit"></i> Update Profile
          </router-link>
          <router-link v-if="isAdmin" to="/admin" class="dropdown-item" @click="closeDropdown">
            <i class="fas fa-cog"></i> Admin Dashboard
          </router-link>
          <div class="dropdown-divider"></div>
          <button @click="logout" class="dropdown-item">
            <i class="fas fa-sign-out-alt"></i> Logout
          </button>
        </div>
      </div>
    </div>
    
    <!-- Login button when not logged in and not on login page -->
    <div v-else-if="!isOnLoginPage" class="login-section">
      <router-link to="/login" class="login-btn">
        <i class="fas fa-sign-in-alt"></i> Login
      </router-link>
    </div>
  </header>
</template>

<script>
export default {
  name: 'HeaderBar',
  data() {
    return {
      showUserDropdown: false,
      currentUser: null
    }
  },
  computed: {
    isLoggedIn() {
      const user = JSON.parse(localStorage.getItem('user') || '{}')
      return user && user.id && user.name && user.email
    },
    isAdmin() {
      const user = JSON.parse(localStorage.getItem('user') || '{}')
      return user.role === 'admin'
    },
    isOnLoginPage() {
      return this.$route.name === 'Login'
    }
  },
  mounted() {
    // Load current user info
    this.updateCurrentUser()
    
    // Close dropdown when clicking outside
    document.addEventListener('click', this.handleClickOutside)
    
    // Listen for storage changes to update user info when login/logout occurs
    window.addEventListener('storage', this.handleStorageChange)
    
    // Listen for custom userUpdated event from login
    window.addEventListener('userUpdated', this.handleUserUpdated)
  },
  beforeUnmount() {
    document.removeEventListener('click', this.handleClickOutside)
    window.removeEventListener('storage', this.handleStorageChange)
    window.removeEventListener('userUpdated', this.handleUserUpdated)
  },
  methods: {
    updateCurrentUser() {
      const user = JSON.parse(localStorage.getItem('user') || '{}')
      this.currentUser = user
    },
    handleStorageChange() {
      // Update user info when localStorage changes
      this.updateCurrentUser()
      // Close dropdown if user logs out
      if (!this.isLoggedIn) {
        this.showUserDropdown = false
      }
    },
    handleUserUpdated() {
      // Handle the custom userUpdated event from login
      console.log('🔍 HeaderBar - Received userUpdated event')
      this.updateCurrentUser()
      this.$forceUpdate() // Force Vue to re-render and check computed properties
    },
    toggleUserDropdown() {
      this.showUserDropdown = !this.showUserDropdown
    },
    closeDropdown() {
      this.showUserDropdown = false
    },
    handleClickOutside(event) {
      const userSection = this.$el.querySelector('.user-section')
      if (userSection && !userSection.contains(event.target)) {
        this.showUserDropdown = false
      }
    },
    logout() {
      localStorage.removeItem('user')
      localStorage.removeItem('isAuthenticated')
      this.updateCurrentUser() // Update immediately
      this.$router.push('/login')
    }
  }
}
</script>

<style scoped>
.header-bar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 60px;
  background: #fff;
  color: #205493;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 1rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  z-index: 1100;
}

.logo {
  height: 40px;
}

.logo-link, .title-link {
  text-decoration: none;
  color: inherit;
}

.title-link {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
}

.title-link:hover .title {
  color: #205493;
}

.title {
  margin: 0;
  font-size: 1.5rem;
  font-family: 'Roboto', sans-serif;
  transition: color 0.2s;
  text-align: center;
  white-space: nowrap;
}

/* User Section */
.user-section {
  position: relative;
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  cursor: pointer;
  border-radius: 6px;
  transition: background-color 0.2s;
  border: 1px solid transparent;
}

.user-info:hover {
  background-color: #f8f9fa;
  border-color: #e9ecef;
}

.user-icon {
  font-size: 1.2rem;
}

.user-name {
  font-weight: 500;
  color: #495057;
}

.dropdown-arrow {
  font-size: 0.8rem;
  color: #6c757d;
  transition: transform 0.2s;
}

.dropdown-arrow.open {
  transform: rotate(180deg);
}

.user-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  min-width: 320px;
  width: max-content;
  background: white;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.15);
  z-index: 2000;
  margin-top: 0.5rem;
  overflow: visible;
}

.dropdown-items {
  padding: 0.5rem 0;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1.5rem;
  text-decoration: none;
  color: #495057;
  transition: background-color 0.2s;
  border: none;
  background: none;
  width: 100%;
  text-align: left;
  cursor: pointer;
  font-size: 0.9rem;
  white-space: nowrap;
  min-width: fit-content;
}

.dropdown-item:hover {
  background-color: #f8f9fa;
}

.dropdown-item i {
  width: 16px;
  color: #6c757d;
}

.dropdown-divider {
  height: 1px;
  background-color: #e9ecef;
  margin: 0.5rem 0;
}

/* Login section styles */
.login-section {
  display: flex;
  align-items: center;
}

.login-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background-color: #007bff;
  color: white;
  text-decoration: none;
  border-radius: 4px;
  font-weight: 500;
  transition: background-color 0.2s;
}

.login-btn:hover {
  background-color: #0056b3;
  color: white;
  text-decoration: none;
}

.login-btn i {
  font-size: 0.9rem;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .user-dropdown {
    min-width: 340px;
    right: -1rem;
  }
  
  .title {
    font-size: 1.2rem;
  }
  
  .header-bar {
    padding: 0 0.5rem;
  }
}

@media (max-width: 480px) {
  .user-dropdown {
    min-width: 320px;
    right: -0.5rem;
  }
  
  .dropdown-item {
    font-size: 0.85rem;
    padding: 0.6rem 0.8rem;
  }
}
</style>