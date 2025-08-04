<template>
  <nav class="breadcrumbs">
    <router-link to="/">🏠 Home</router-link>
    <span v-for="(crumb, i) in crumbs" :key="i">
      ›
      <router-link :to="crumb.path">{{ crumb.label }}</router-link>
    </span>
  </nav>
</template>

<script>
export default {
  name: 'Breadcrumbs',

  // Log once when component is created
  created() {
    console.log('🔍 Breadcrumbs created')
  },

  // Log once after mount
  mounted() {
    console.log('🔍 Breadcrumbs mounted')
  },

  // Log before every update
  beforeUpdate() {
    console.log('🔄 Breadcrumbs beforeUpdate')
  },

  // Log after every update
  updated() {
    console.log('🔄 Breadcrumbs updated')
  },

  computed: {
    crumbs() {
      console.log('➡️ crumbs() computed running—current path:', this.$route.path)

      // Special handling for Import section to show proper hierarchy
      if (this.$route.path.startsWith('/import')) {
        const crumbs = []
        
        // Always start with Import Dashboard for import-related pages
        crumbs.push({ path: '/import/dashboard', label: 'Import Dashboard' })
        
        // Add specific page crumbs based on the route
        if (this.$route.path === '/import') {
          crumbs.push({ path: '/import', label: 'Import' })
        } else if (this.$route.path === '/import/history') {
          crumbs.push({ path: '/import', label: 'Import' })
          crumbs.push({ path: '/import/history', label: 'Import History' })
        } else if (this.$route.path.includes('/import/') && this.$route.path.includes('/review')) {
          crumbs.push({ path: '/import', label: 'Import' })
          crumbs.push({ path: '/import/history', label: 'Import History' })
          crumbs.push({ path: this.$route.path, label: 'Review Import' })
        } else if (this.$route.path === '/import/dashboard') {
          // Just show Import Dashboard as the current page
          return []
        }
        
        return crumbs
      }

      // Default breadcrumb generation for other sections
      const pathArray = this.$route.path
        .split('/')
        .filter(Boolean)

      return pathArray.map((segment, i) => {
        const path = '/' + pathArray.slice(0, i + 1).join('/')
        const label = segment.charAt(0).toUpperCase() + segment.slice(1)
        return { path, label }
      })
    }
  }
}
</script>

<style scoped>
.breadcrumbs {
  font-size: 0.9rem;
  margin-bottom: 1rem;
  padding: 8px 12px;
  background-color: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  font-weight: 500;
}
.breadcrumbs a {
  text-decoration: none;
  color: #005a9c;
}
.breadcrumbs a:hover {
  text-decoration: underline;
}
.breadcrumbs span {
  margin-left: 0.5rem;
  color: #6c757d;
}
</style>