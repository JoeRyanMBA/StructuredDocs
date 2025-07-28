<template>
  <HeaderBar />
  <TabNavigation />
  <main class="content">
<!--    <Breadcrumbs /> -->
    <router-view />
  </main>
</template>

<script>
import TabNavigation from '@/components/TabNavigation.vue'
import HeaderBar from '@/components/HeaderBar.vue'
import Breadcrumbs from '@/components/Breadcrumbs.vue'

export default {
  components: { TabNavigation, HeaderBar, Breadcrumbs }
}
</script>

<style scoped>
.content {
  margin-top: 120px; /* Space for header (60px) + tabs (60px) */
  padding: 2rem;
  max-width: 1200px;
  margin-left: auto;
  margin-right: auto;
}

@media (max-width: 768px) {
  .content {
    margin-top: 110px; /* Slightly less space on mobile */
    padding: 1rem;
  }
}
</style>