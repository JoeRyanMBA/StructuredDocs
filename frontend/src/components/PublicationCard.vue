<template>
  <router-link
    :to="{ name: 'PublicationView', params: { id: publication.id } }"
    class="publication-card"
  >
    <h3 class="title">{{ publication.title }}</h3>
    <p class="excerpt">{{ publication.excerpt || publication.summary }}</p>
  </router-link>
</template>

<script>
export default {
  name: 'PublicationCard',
  props: {
    publication: {
      type: Object,
      required: true
    }
  }
}
</script>

<style scoped>
.publication-card {
  display: block;
  padding: 1rem;
  margin-bottom: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  text-decoration: none;
  color: inherit;
  transition: background 0.15s;
}
.publication-card:hover {
  background: #f9f9f9;
}
.title {
  margin: 0 0 0.5rem;
  font-size: 1.2rem;
}
.excerpt {
  margin: 0;
  color: #666;
  font-size: 0.9rem;
}
</style>