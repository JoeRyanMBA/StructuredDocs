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
}
.breadcrumbs a {
  text-decoration: none;
  color: #005a9c;
}
.breadcrumbs span {
  margin-left: 0.5rem;
}
</style>