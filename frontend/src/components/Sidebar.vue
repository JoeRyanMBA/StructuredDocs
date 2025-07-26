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
      <ul>
        <li v-for="section in SECTIONS" :key="section.key">
          <button
            class="section-toggle"
            @click="toggleSection(section.key)"
            :aria-expanded="sections[section.key]"
          >
            {{ section.label }}
          </button>

          <ul v-show="sections[section.key]">
            <li v-for="link in section.links" :key="link.name">
              <router-link :to="{ name: link.name }">
                {{ link.text }}
              </router-link>
            </li>
          </ul>
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
        author: false,
        organize: false,
        import: false,
        publish: false,
        reviews: false,
        admin: false
      },
      SECTIONS: [
        {
          key: 'author',
          label: '✏️ Author',
          links: [
            { name: 'NewTopic', text: '➕ New Topic' },
            { name: 'TopicsList', text: '📚 Browse Topics' }
                ]
        },
      {
        key: 'collections',
        label: '🗂 Collections',
        links: [
            { name: 'Collections', text: 'Collections' }
              ]
      },

        {
          key: 'import',
          label: '📥 Import',
          links: [
            { name: 'ImportHome',    text: 'Import Home' },
          ]
        },
          {
            key: 'publish',
            label: '📤 Publish',
            links: [
            { name: 'PublicationsHome', text: 'Publication List' }
          ]
  },
        {
          key: 'reviews',
          label: '📝 Reviews',
          links: [
            { name: 'SMEReviews',       text: 'Send Topics for Review' },
            { name: 'IncorporateFeedback', text: 'Incorporate Feedback' },
            { name: 'ReviewHistory',    text: 'View Review History' }
          ]
        },
        {
          key: 'admin',
          label: '🔒 Admin',
          links: [
            { name: 'ManageAuthors', text: 'Manage Authors' },
            { name: 'ManageUsers',   text: 'Manage Reviewers' },
            { name: 'SystemLogs',    text: 'System Logs' }
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
  padding: 1rem;
  transition: transform 0.3s ease;
  overflow-y: auto;
  z-index: 1000;
}

.sidebar.collapsed {
  transform: translateX(-100%);
}

ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

li {
  margin: 0.5rem 0;
}

li > ul {
  margin-left: 1.5rem;
  font-size: 0.9rem;
}

.section-toggle {
  background: none;
  border: none;
  color: #112e51;
  font-size: 1rem;
  cursor: pointer;
  padding: 0;
  margin-bottom: 0.25rem;
  text-align: left;
}

.section-toggle:hover {
  font-weight: bold;
}

a {
  text-decoration: none;
  color: #112e51;
}

a:hover {
  font-weight: bold;
}
</style>