<template>
  <div class="publications-home">
    <h2>All Publications</h2>
    <PublicationList :publications="publications" />
  </div>
</template>

<script>
import PublicationList from '@/components/PublicationList.vue'

export default {
  name: 'PublicationsHome',
  components: { PublicationList },
  data() {
    return { publications: [] }
  },
  async created() {
    try {
      const res = await fetch('/api/publications')
      if (!res.ok) throw new Error(res.statusText)
      this.publications = await res.json()
    } catch (err) {
      console.error('Failed to fetch publications:', err)
    }
  }
}
</script>

<style scoped>
/* your styles here */
</style>