<!-- filepath: c:\Dev\StructuredDocs\frontend\src\views\Collections.vue -->
<template>
  <form @submit.prevent="createCollection">
    <input v-model="newCollectionName" placeholder="Collection name" required />
    <button type="submit">Add Collection</button>
  </form>
  <ul>
    <li v-for="col in collections" :key="col.id">
      <router-link
        v-if="col.id !== undefined && col.id !== null"
        :to="{ name: 'Organize', params: { id: String(col.id) } }"
      >
        Organize
      </router-link>
      <span v-else>
        (No ID available)
      </span>
    </li>
  </ul>
</template>

<script>
import CollectionTree from '@/components/CollectionTree.vue'
import { getCollections } from '@/api/collections.js'

export default {
  name: 'CollectionsTree',
  components: { CollectionTree },
  data() {
    return {
      collections: [],
      newCollectionName: ''
    }
  },
  async created() {
    this.collections = await getCollections()
  },
  methods: {
    async createCollection() {
      const res = await fetch('/api/collections', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: this.newCollectionName })
      });
      if (res.ok) {
        this.collections = await getCollections();
        this.newCollectionName = '';
      }
    }
  }
}
</script>