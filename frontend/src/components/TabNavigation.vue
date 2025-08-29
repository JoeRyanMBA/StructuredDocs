<template>
  <nav class="tab-navigation" aria-label="Main navigation">
    <div class="nav-content">
      <div class="tab-container">
        <div
          v-for="tab in visibleTabs"
          :key="tab.key"
          class="tab-item"
        >
          <component :is="tab.children ? 'div' : 'router-link'"
            :to="tab.children ? null : { name: tab.route }"
            class="tab"
            :class="{ active: isActiveTab(tab) }"
            @click="tab.children ? toggleDropdown(tab.key) : null"
          >
            <span class="tab-icon">{{ tab.icon }}</span>
            <span class="tab-label">{{ tab.label }}</span>
            <span v-if="tab.children" class="dropdown-arrow">▼</span>
          </component>
          <div
            v-if="tab.children && activeDropdown === tab.key"
            class="dropdown-menu"
            @mouseleave="activeDropdown = null"
          >
            <router-link
              v-for="child in tab.children"
              :key="child.key"
              :to="{ name: child.route }"
              class="dropdown-item"
            >
              <span class="tab-icon">{{ child.icon }}</span>
              <span class="tab-label">{{ child.label }}</span>
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </nav>
</template>

<script>
import { store } from '../store';

export default {
  name: 'TabNavigation',
  data() {
    return {
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
          children: [
            { key: 'projects-list', label: 'View All', route: 'Projects' },
            { key: 'project-create', label: 'Add New', route: 'ProjectCreate' }
          ]
        },
        {
          key: 'collections',
          label: 'Collections',
          icon: '📑',
          children: [
            { key: 'collections-list', label: 'View All', route: 'Collections' },
            { key: 'collection-create', label: 'Add New', route: 'CollectionCreate' }
          ]
        },
        {
          key: 'topics',
          label: 'Topics',
          icon: '📝',
          children: [
            { key: 'topics-list', label: 'View All', route: 'TopicsList' },
            { key: 'topic-create', label: 'Add New', route: 'TopicCreate' }
          ]
        },
        {
          key: 'admin',
          label: 'Admin',
          icon: '⚙️',
          adminOnly: true,
          children: [
            { key: 'admin-dashboard', label: 'Dashboard', route: 'Admin' },
            { key: 'admin-users', label: 'Manage Users', route: 'AdminUsers' },
            { key: 'admin-settings', label: 'Settings', route: 'AdminSettings' }
          ]
        }
      ],
      activeDropdown: null
    }
  },
  computed: {
    currentUser() {
      return store.user;
    },
    visibleTabs() {
      const tabs = this.TABS.filter(tab => {
        if (tab.adminOnly) {
          const isAdmin = this.currentUser && this.currentUser.role === 'admin'
          return isAdmin
        }
        return true
      })
      return tabs
    }
  },
  methods: {
    toggleDropdown(tabKey) {
      this.activeDropdown = this.activeDropdown === tabKey ? null : tabKey;
    },
    isActiveTab(tab) {
      if (tab.children) {
        return tab.children.some(child => this.$route.name === child.route);
      }
      return this.$route.name === tab.route;
    }
  }
}
</script>

<style>
.tab-navigation {
  position: fixed;
  top: var(--header-height); /* Below the header */
  left: 0;
  right: 0;
  height: var(--tabs-height);
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

.tab-item {
  position: relative;
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  left: 0;
  background: #fff;
  border: 1px solid #e9ecef;
  border-radius: 0 0 8px 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  z-index: 1100;
  min-width: 100%;
}

.dropdown-item {
  display: flex;
  align-items: center;
  padding: 0.75rem 1.5rem;
  text-decoration: none;
  color: #6c757d;
  white-space: nowrap;
}

.dropdown-item:hover {
  background: rgba(0, 90, 156, 0.05);
  color: #205493;
}

.dropdown-arrow {
  margin-left: 0.5rem;
  font-size: 0.7rem;
  transition: transform 0.2s ease;
}

.tab-item:hover .dropdown-arrow {
  transform: rotate(180deg);
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
  color: #205493;
  background: rgba(0, 90, 156, 0.05);
  border-bottom-color: rgba(0, 90, 156, 0.3);
}

.tab.active {
  color: #205493;
  background: #fff;
  border-bottom-color: #205493;
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
