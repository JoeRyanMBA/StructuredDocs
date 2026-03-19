<template>
  <aside class="sidebar" :class="{ 'collapsed': !open }">
    <nav class="sidebar-nav">
      <ul>
        <li v-for="item in visibleTabs" :key="item.key" :class="{ 'has-submenu': item.children }">
          <a @click="handleParentClick(item)" :class="{ 'router-link-active': isParentActive(item) }">
            <span class="nav-icon">{{ item.icon }}</span>
            <span class="nav-label">{{ item.label }}</span>
            <span v-if="item.children" class="arrow" :class="{ 'open': openSubmenu === item.key }">▶</span>
          </a>
          <ul v-if="item.children && openSubmenu === item.key" class="submenu">
            <li v-for="child in item.children" :key="child.key">
              <router-link
                :to="{ name: child.route }"
                active-class="no-active"
                exact-active-class="no-active"
                :class="{ 'router-link-active': isChildActive(child, item) }"
              >
                <span class="nav-icon">{{ child.icon }}</span>
                <span class="nav-label">{{ child.label }}</span>
              </router-link>
            </li>
          </ul>
        </li>
      </ul>
    </nav>
  </aside>
</template>

<script>
import { store } from '../store';

export default {
  name: 'Sidebar',
  props: {
    open: { type: Boolean, default: false }
  },
  data() {
    return {
      openSubmenu: null,
      TABS: [
        {
          key: 'home',
          label: 'Home',
          icon: '🏠',
          route: 'Dashboard'
        },
        {
          key: 'author',
          label: 'Author',
          icon: '✍️',
          route: 'AuthorHome'
        },
        {
          key: 'projects',
          label: 'Projects',
          icon: '🎯',
          route: 'Projects',
          // No child "Add New" link; Tasks/Milestones/Stakeholders/Tags remain
            children: [
            { key: 'all-tasks', label: 'Tasks', route: 'Tasks', icon: '📋' },
            { key: 'all-milestones', label: 'Milestones', route: 'AllMilestones', icon: '🎯' },
            { key: 'all-stakeholders', label: 'Stakeholders', route: 'AllStakeholders', icon: '👥' },
            { key: 'all-tags', label: 'Tags', route: 'AllTags', icon: '🏷️' }
          ]
        },
        {
          key: 'collections',
          label: 'Collections',
          icon: '📑',
          route: 'Collections',
          children: [
            { key: 'import-dashboard', label: 'Import', route: 'ImportDashboard', icon: '📥' },
            { key: 'publish-dashboard', label: 'Publish', route: 'PublicationsHome', icon: '📤' }
          ]
        },
        {
          key: 'topics',
          label: 'Topics',
          icon: '📝',
          route: 'TopicsList'
        },
        {
          key: 'snippets',
          label: 'Snippets',
          icon: '📑',
          route: 'SnippetsLibrary'
        },
        {
          key: 'reviews',
          label: 'Reviews',
          icon: '✅',
          route: 'ReviewsHome',
          children: [
            { key: 'reviews-tasks', label: 'Tasks', route: 'ReviewTasks', icon: '📋' },
            { key: 'reviews-history', label: 'History', route: 'ReviewHistory', icon: '🕘' }
          ]
        },
        {
          key: 'admin',
          label: 'Admin',
          icon: '⚙️',
          adminOnly: true,
          route: 'Admin',
          children: [
            { key: 'design-buttons', label: 'Button Catalog', route: 'ButtonCatalog', icon: '🎛️' },
            { key: 'design-icons', label: 'Icon Catalog', route: 'IconCatalog', icon: '🖼️' },
            { key: 'admin-users', label: 'Manage Users', route: 'AdminUsers', icon: '👥' },
            { key: 'admin-feedback', label: 'Feedback', route: 'AdminFeedback', icon: '💬' },
            { key: 'admin-bugs', label: 'Bugs', route: 'AdminBugs', icon: '🐞' }
          ]
        }
      ]
    };
  },
  computed: {
    currentUser() {
      return store.user;
    },
    visibleTabs() {
      return this.TABS.filter(tab => {
        if (tab.adminOnly) {
          return this.currentUser && this.currentUser.role === 'admin';
        }
        return true;
      });
    }
  },
  methods: {
    toggleSubmenu(key) {
      this.openSubmenu = this.openSubmenu === key ? null : key;
    },
    handleParentClick(item) {
      if (item.children) {
        this.toggleSubmenu(item.key);
      }
      this.$router.push({ name: item.route }).then(() => {
        this.$emit('close');
        // Special scroll behavior: if navigating to Projects, scroll to list section if present
        if (item.route === 'Projects') {
          this.$nextTick(() => {
            const el = document.querySelector('[ref="projectsSection"]') || document.querySelector('#projectsSection');
            if (el && typeof el.scrollIntoView === 'function') {
              el.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
          });
        }
      });
    },
    isParentActive(item) {
      // Parent is active if its own route matches OR any child with a different route matches.
      if (this.$route.name === item.route) return true;
      if (item.children) {
        // If a child shares the same route name as the parent, don't count it to avoid double highlight
        return item.children.some(child => this.$route.name === child.route && child.route !== item.route);
      }
      return false;
    },
    isChildActive(child, item) {
        if (this.$route.name !== child.route) return false;
        // If a child shares the same route as its parent, prefer highlighting the parent only
        if (item && child.route === item.route) return false;
        return true;
    }
  }
};
</script>

<style scoped>
.sidebar {
  width: 250px;
  position: fixed;
  top: calc(var(--header-height) + var(--ticker-height));
  left: 0;
  bottom: 0;
  background: #343a40;
  color: #f8f9fa;
  padding-top: 1rem;
  z-index: 1000;
  transition: transform 240ms cubic-bezier(0.2, 0.8, 0.2, 1);
}

/* Desktop: sidebar always visible */
@media (min-width: 769px) {
  .sidebar {
    transform: translateX(0) !important; /* Always visible on desktop, override any collapsed state */
  }
}

/* Mobile: sidebar is hidden by default, overlays when shown */
@media (max-width: 768px) {
  .sidebar {
    transform: translateX(-100%);
    z-index: 1100; /* overlay ticker and content when open on mobile */
  }
  
  .sidebar.collapsed {
    transform: translateX(-100%);
  }
  
  .sidebar:not(.collapsed) {
    transform: translateX(0);
  }
}

.sidebar-nav ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.sidebar-nav li a, .sidebar-nav li > a {
  display: flex;
  align-items: center;
  padding: 0.75rem 1.5rem;
  color: #f8f9fa;
  text-decoration: none;
  transition: background 0.2s;
  user-select: none; /* prevent text selection/I-beam */
}

.sidebar-nav li a:hover {
  background: #495057;
}

.sidebar-nav .router-link-active {
  background: var(--primary-deep-teal);
  color: white;
}

.submenu {
  list-style: none;
  padding-left: 0;
  margin: 0;
  background-color: #2c3e50; /* Slightly different background for submenu */
}

.submenu li a {
  padding-left: 3rem; /* Indent sub-items */
}

.nav-icon {
  margin-right: 1rem;
  width: 20px;
  text-align: center;
}

.nav-label {
  flex-grow: 1;
}

.arrow {
  transition: transform 0.2s;
  cursor: default;
}

.arrow.open {
  transform: rotate(90deg);
}

.submenu {
  list-style: none;
  padding-left: 1.5rem;
  background: #2c3034;
}

.submenu li a {
  /* top right bottom left */
  padding: 0.6rem 1.5rem 0.6rem 2.5rem;
  font-size: 0.9rem;
  cursor: pointer; /* keep hand cursor on submenu links */
}

/* subtle fade-in for submenu */
.submenu { animation: fadeIn 160ms ease-in; }
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-2px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Ensure top-level items show the arrow (default) cursor, not text I-beam */
.sidebar-nav > ul > li > a {
  cursor: default;
}

/* Also prevent text selection on labels/icons to avoid I-beam over text */
.nav-label,
.nav-icon,
.arrow {
  user-select: none;
}
</style>
