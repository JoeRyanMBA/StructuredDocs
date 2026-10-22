<template>
  <aside class="sidebar" :class="{ 'collapsed': !open }">
    <nav class="sidebar-nav" aria-label="Main navigation">
      <ul>
        <li v-for="item in visibleTabs" :key="item.key" :class="{ 'has-submenu': item.children }">
          <a
            :href="$router.resolve({ name: item.route }).href"
            @click.exact.prevent="handleParentClick(item)"
            :aria-label="item.label"
            :title="item.label"
            :aria-expanded="item.children ? String(openSubmenu === item.key) : undefined"
            :class="{ 'router-link-active': isParentActive(item) }"
          >
            <span class="nav-icon" aria-hidden="true">{{ item.icon }}</span>
            <span class="nav-label">{{ item.label }}</span>
            <span v-if="item.children" class="arrow" :class="{ 'open': openSubmenu === item.key }">▶</span>
          </a>
          <ul v-if="item.children && openSubmenu === item.key" class="submenu">
            <li v-for="child in item.children" :key="child.key">
              <router-link
                :to="{ name: child.route }"
                :aria-label="child.label"
                :title="child.label"
                active-class="no-active"
                exact-active-class="no-active"
                :class="{ 'router-link-active': isChildActive(child, item) }"
              >
                <span class="nav-icon" aria-hidden="true">{{ child.icon }}</span>
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
          key: 'author',
          label: 'Author',
          icon: '✍️',
          route: 'AuthorHome',
          children: [
            { key: 'topics', label: 'Topics', route: 'TopicsList', icon: '📝' },
            { key: 'snippets', label: 'Snippets', route: 'SnippetsLibrary', icon: '📑' }
          ]
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
  width: var(--sidebar-width);
  position: fixed;
  top: calc(var(--header-height) + var(--ticker-height));
  left: 0;
  bottom: 0;
  background: var(--primary-deep-teal);
  color: #f8f9fa;
  padding-top: 1rem;
  z-index: 1000;
  overflow-x: hidden;
  overflow-y: auto;
  transition: width 240ms cubic-bezier(0.2, 0.8, 0.2, 1), transform 240ms cubic-bezier(0.2, 0.8, 0.2, 1);
}

/* Expand over the content so hovering does not move the page. */
@media (min-width: 769px) {
  .sidebar {
    width: var(--sidebar-rail-width);
    transform: translateX(0);
  }

  .sidebar:hover,
  .sidebar:focus-within {
    width: var(--sidebar-width);
    box-shadow: 4px 0 12px #00000026;
  }

  .sidebar:not(:hover):not(:focus-within) .nav-label,
  .sidebar:not(:hover):not(:focus-within) .arrow,
  .sidebar:not(:hover):not(:focus-within) .submenu {
    display: none;
  }

  .sidebar:not(:hover):not(:focus-within) .nav-icon {
    margin-right: 0;
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
  padding: 0.75rem 1.5rem 0.75rem 0.75rem;
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

.sidebar-nav .router-link-active .nav-label {
  font-weight: 700;
}

.submenu {
  list-style: none;
  padding-left: 0;
  margin: 0;
  background-color: var(--primary-medium-teal);
}

.submenu li a {
  padding-left: 3rem; /* Indent sub-items */
}

.nav-icon {
  margin-right: 1rem;
  width: 20px;
  flex-shrink: 0;
  text-align: center;
}

.nav-label {
  flex-grow: 1;
  white-space: nowrap;
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
  background: var(--primary-medium-teal);
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
