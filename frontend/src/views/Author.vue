<template>
  <div class="author-view">
    <Breadcrumbs />
    <h2>✏️ Author</h2>
    <p>Write, edit, and organize topics here.</p>
  </div>
</template>

<script>
import Breadcrumbs from '@/components/Breadcrumbs.vue'

export default {
  name: 'Author',
  components: { Breadcrumbs }
}
</script>

<style scoped>
.author-view {
  padding-top: 0px; /* Top padding to account for fixed header */
}
</style>