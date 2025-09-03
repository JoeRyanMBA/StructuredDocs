<template>
  <header class="header-bar">
    <router-link to="/projects" class="logo-link">
      <span class="logo-wrapper">
        <span v-show="!logoLoaded" class="logo-skeleton" aria-hidden="true"></span>
        <img
          class="logo"
          :src="logoSrc"
          alt="StructuredDocs logo"
          decoding="async"
          @load="onLogoLoad"
          @error="onLogoError"
        />
      </span>
    </router-link>
    <router-link to="/projects" class="title-link">
      <h1 class="title">Documentation Project Hub</h1>
    </router-link>
    
    <!-- User section with better positioning -->
    <div v-if="isLoggedIn" class="user-section">
      <div class="user-info" @click="toggleUserDropdown">
        <span class="user-icon">👤</span>
        <span class="user-name">{{ firstName }}</span>
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
import { store } from '../store';

export default {
  name: 'HeaderBar',
  data() {
    return {
  showUserDropdown: false,
  logoLoaded: false,
    }
  },
  computed: {
    // Use base-aware path for public asset so it resolves under subpaths
    logoSrc() {
      return `${import.meta.env.BASE_URL}StructuredDocs_logo.svg`
    },
    currentUser() {
      return store.user;
    },
    firstName() {
      if (store.user && store.user.name) {
        return store.user.name.split(' ')[0];
      }
      return 'User';
    },
    isLoggedIn() {
      return !!store.user;
    },
    isAdmin() {
      return store.user && store.user.role === 'admin';
    },
    isOnLoginPage() {
      return this.$route.name === 'Login'
    }
  },
  mounted() {
    // Close dropdown when clicking outside
    document.addEventListener('click', this.handleClickOutside)
    
    // Listen for custom userUpdated event from login
    window.addEventListener('userUpdated', this.handleUserUpdated)
  },
  beforeUnmount() {
    document.removeEventListener('click', this.handleClickOutside)
    window.removeEventListener('userUpdated', this.handleUserUpdated)
  },
  methods: {
    onLogoLoad() {
      this.logoLoaded = true
    },
    onLogoError(e) {
      // Fallback to symbol logo if full logo fails
      const fallback = `${import.meta.env.BASE_URL}StructuredDocsLogoSymbol.svg`
      if (e && e.target && e.target.src !== fallback) {
        e.target.src = fallback
      }
    },
    handleUserUpdated() {
      // This method can now be simplified or removed if not needed for other purposes
      this.$forceUpdate();
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
      store.setUser(null);
      localStorage.removeItem('isAuthenticated');
      localStorage.removeItem('access_token');
      this.$router.push('/login');
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
  color: #005B6E;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 1rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  z-index: 1100;
}

.logo {
  height: 55px;
}

.logo-wrapper {
  position: relative;
  display: inline-block;
  width: 140px; /* reserve space similar to logo natural width */
  height: 55px; /* match logo height */
}

.logo-skeleton {
  position: absolute;
  inset: 0;
  border-radius: 4px;
  background: linear-gradient(90deg, #f2f4f7 25%, #e9eef3 37%, #f2f4f7 63%);
  background-size: 400% 100%;
  animation: logo-shimmer 1.2s ease-in-out infinite;
}

@keyframes logo-shimmer {
  0% { background-position: 100% 0; }
  100% { background-position: 0 0; }
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
  color: #005B6E;
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
  background-color: var(--primary-deep-teal);
  color: white;
  text-decoration: none;
  font-weight: 500;
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 1rem;
  transition: background-color 0.3s ease, transform 0.2s ease;
}

.login-btn:hover {
  background-color: var(--primary-medium-teal);
  transform: translateY(-2px);
  text-decoration:none;
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