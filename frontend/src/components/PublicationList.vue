<template>
  <div class="publication-list">
    <PublicationCard
      v-for="pub in publications"
      :key="pub.id"
      :publication="pub"
    />
    <p v-if="publications.length === 0" class="empty">
      No publications found.
    </p>
  </div>
</template>
<script>
import PublicationCard from './PublicationCard.vue'

export default {
  name: 'PublicationList',
  components: { PublicationCard },
  props: {
    publications: {
      type: Array,
      required: true
    }
  }
}
</script>

<style>
.publication-list {
  display: flex;
  flex-direction: column;
}
.empty {
  color: #999;
  font-style: italic;
  text-align: center;
  margin-top: 2rem;
}
</style>