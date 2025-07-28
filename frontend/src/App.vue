<template>
  <HeaderBar />
  <div class="layout">
    <Sidebar />
    <main class="content">
<!--      <Breadcrumbs /> -->
      <router-view />
    </main>
  </div>
</template>

<script>
import Sidebar from '@/components/Sidebar.vue'
import HeaderBar from '@/components/HeaderBar.vue'
import Breadcrumbs from '@/components/Breadcrumbs.vue'

export default {
  components: { Sidebar, HeaderBar, Breadcrumbs }
}
</script>

<style scoped>
.layout {
  display: flex;
}

.content {
  margin-left: 210px;     /* for sidebar */
  padding: 2rem;
}

@media (max-width: 768px) {
  .content {
    margin-left: 0; /* No sidebar margin on mobile */
  }
}
</style>