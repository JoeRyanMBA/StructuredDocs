<template>
  <nav class="tab-navigation" aria-label="Main navigation">
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
  </nav>
</template>

<script>
export default {
  name: 'TabNavigation',
  data() {
    return {
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
          key: 'reviews',
          label: 'Reviews',
          icon: '📝',
          route: 'ReviewsHome'
        },
        {
          key: 'admin',
          label: 'Admin',
          icon: '🔒',
          route: 'AdminHome'
        }
      ]
    }
  },
  methods: {
    isActiveTab(routeName) {
      return this.$route.name === routeName
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

.tab-container {
  display: flex;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
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
