<template>
  <div>
    <!-- Collapse toggle for small screens -->
    <button
      v-if="!isWideScreen"
      class="edge-toggle"
      @click="collapsed = !collapsed"
      :aria-expanded="!collapsed"
      aria-label="Toggle sidebar"
    >
      ☰
    </button>

    <nav
      class="sidebar"
      :class="{ collapsed }"
      aria-label="Sidebar navigation"
    >
      <ul class="nav-list">
        <li v-for="section in SECTIONS" :key="section.key" class="nav-item">
          <!-- Direct link sections (like Home) -->
          <router-link 
            v-if="section.directLink"
            :to="{ name: section.directLink }"
            class="nav-link direct-link"
          >
            <span class="nav-icon">{{ section.icon }}</span>
            <span class="nav-text">{{ section.text }}</span>
          </router-link>

          <!-- Collapsible sections with sub-items -->
          <template v-else>
            <button
              class="nav-link collapsible-link"
              @click="toggleSection(section.key)"
              :aria-expanded="sections[section.key]"
            >
              <span class="nav-icon">{{ section.icon }}</span>
              <span class="nav-text">{{ section.text }}</span>
              <span class="expand-icon" :class="{ 'expanded': sections[section.key] }">
                <svg width="12" height="12" viewBox="0 0 12 12" fill="currentColor">
                  <path d="M4 2l4 4-4 4V2z"/>
                </svg>
              </span>
            </button>

            <ul v-show="sections[section.key]" class="sub-nav">
              <li v-for="link in section.links" :key="link.name" class="sub-nav-item">
                <router-link :to="{ name: link.name }" class="sub-nav-link">
                  {{ link.text }}
                </router-link>
              </li>
            </ul>
          </template>
        </li>
      </ul>
    </nav>
  </div>
</template>

<script>
export default {
  name: 'Sidebar',
  data() {
    return {
      collapsed: window.innerWidth < 768,
      isWideScreen: window.innerWidth >= 768,
      sections: {
        home: true,
        projects: true,
        author: false,
        collections: false,
        organize: false,
        import: false,
        publish: false,
        reviews: false,
        admin: false
      },
      SECTIONS: [
        {
          key: 'home',
          icon: '🏠',
          text: 'Home',
          directLink: 'Dashboard'
        },
        {
          key: 'projects',
          icon: '🎯',
          text: 'Projects',
          directLink: 'Projects'
        },
        {
          key: 'author',
          icon: '✏️',
          text: 'Author',
          directLink: 'AuthorHome'
        },
        {
          key: 'collections',
          icon: '📑',
          text: 'Collections',
          directLink: 'Collections'
        },
        {
          key: 'import',
          icon: '📥',
          text: 'Import',
          links: [
            { name: 'ImportTopics', text: 'New Import' },
            { name: 'ImportDashboard', text: 'Dashboard' },
            { name: 'ImportHistory', text: 'History' }
          ]
        },
        {
          key: 'publish',
          icon: '📤',
          text: 'Publish',
          links: [
            { name: 'PublicationsHome', text: 'Dashboard' },
            { name: 'PublicationsList', text: 'All Publications' },
            { name: 'PublishMobileKB', text: 'Mobile KB' },
            { name: 'PublishPDF', text: 'PDF Export' }
          ]
        },
        {
          key: 'reviews',
          icon: '📝',
          text: 'Reviews',
          links: [
            { name: 'ReviewsHome', text: 'Dashboard' },
            { name: 'SMEReviews', text: 'Send Reviews' },
            { name: 'IncorporateFeedback', text: 'Incorporate Feedback' },
            { name: 'ReviewHistory', text: 'History' }
          ]
        },
        {
          key: 'admin',
          icon: '🔒',
          text: 'Admin',
          links: [
            { name: 'Admin', text: 'Dashboard' },
            { name: 'AdminUsers', text: 'User Management' },
            { name: 'SystemLogs', text: 'System Logs' },
            { name: 'PerformanceMetrics', text: 'Performance' },
            { name: 'CreateNotification', text: 'Create Notification' }
          ]
        }
      ]
    }
  },
  mounted() {
    window.addEventListener('resize', this.updateLayout)
  },
  beforeUnmount() {
    window.removeEventListener('resize', this.updateLayout)
  },
  methods: {
    updateLayout() {
      this.isWideScreen = window.innerWidth >= 768
      this.collapsed    = !this.isWideScreen
    },
    toggleSection(key) {
      this.sections[key] = !this.sections[key]
    }
  }
}
</script>

<style scoped>
.edge-toggle {
  position: fixed;
  top: 40%;
  left: 0;
  width: 28px;
  height: 80px;
  background: #005a9c;
  color: white;
  border: none;
  border-radius: 0 4px 4px 0;
  cursor: pointer;
  z-index: 1001;
  box-shadow: 2px 0 5px rgba(0, 0, 0, 0.2);
  font-size: 1.2rem;
}

.sidebar {
  position: fixed;
  top: 60px;
  left: 0;
  width: 200px;
  min-height: calc(100vh - 60px);
  background: #f9f9f9;
  box-shadow: 2px 0 10px rgba(0, 0, 0, 0.05);
  padding: 0.5rem 0;
  transition: transform 0.3s ease;
  overflow-y: auto;
  z-index: 1000;
}

.sidebar.collapsed {
  transform: translateX(-100%);
}

.nav-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.nav-item {
  margin: 0;
  border-bottom: 1px solid #e9ecef;
}

.nav-item:last-child {
  border-bottom: none;
}

.nav-link {
  display: flex;
  align-items: center;
  width: 100%;
  padding: 0.75rem 1rem;
  text-decoration: none;
  color: #495057;
  background: none;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 0.9rem;
  text-align: left;
}

.nav-link:hover {
  background-color: #e9ecef;
  color: #205493;
}

.direct-link.router-link-active {
  background-color: #205493;
  color: white;
}

.direct-link.router-link-active .nav-icon {
  opacity: 1;
}

.nav-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  margin-right: 0.75rem;
  opacity: 0.7;
  transition: opacity 0.2s ease;
}

.nav-text {
  flex: 1;
  font-weight: 500;
}

.expand-icon {
  margin-left: auto;
  transition: transform 0.2s ease;
  display: flex;
  align-items: center;
  opacity: 0.6;
}

.expand-icon.expanded {
  transform: rotate(90deg);
}

.expand-icon svg {
  transition: transform 0.2s ease;
}

.collapsible-link:hover .expand-icon {
  opacity: 1;
}

.sub-nav {
  list-style: none;
  padding: 0;
  margin: 0;
  background-color: #f1f3f4;
}

.sub-nav-item {
  margin: 0;
}

.sub-nav-link {
  display: block;
  padding: 0.5rem 1rem 0.5rem 3rem;
  text-decoration: none;
  color: #6c757d;
  font-size: 0.85rem;
  transition: all 0.2s ease;
  border-left: 3px solid transparent;
}

.sub-nav-link:hover {
  background-color: #e9ecef;
  color: #495057;
  border-left-color: #205493;
}

.sub-nav-link.router-link-active {
  background-color: #d4edda;
  color: #155724;
  border-left-color: #28a745;
  font-weight: 500;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .sidebar {
    width: 250px;
  }
  
  .nav-link {
    padding: 1rem;
  }
  
  .nav-icon {
    width: 24px;
    margin-right: 1rem;
  }
}
</style>