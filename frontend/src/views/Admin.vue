<template>
  <div class="admin-view">
    <Breadcrumbs />
    <h2>🔒 Admin</h2>
    <p>Manage users, reviewers, and system logs.</p>
  </div>
</template>

<script>
import Breadcrumbs from '@/components/Breadcrumbs.vue'

export default {
  name: 'Admin',
  components: { Breadcrumbs }
}
</script>

<style scoped>
.admin-view {
  padding-top: 70px; /* Top padding to account for fixed header */
}
</style>