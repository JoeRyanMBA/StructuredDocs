<template>
  <div class="collections-view">
    <Breadcrumbs />
    <h2>📁 Collections</h2>
    
    <p class="guidance-text">
      Create a new collection (document) by typing the name in the Collection name box, and then selecting Add Collection. Existing collections appear below.
    </p>
    
    <form @submit.prevent="createCollection">
      <input v-model="newCollectionName" placeholder="Collection name" required />
      <button type="submit">Add Collection</button>
    </form>
  
    <p style="margin-top: 20px; margin-bottom: 10px; font-weight: 500;">Select a collection to organize:</p>
  
    <ul>
      <li v-for="col in collections" :key="col.id">
        <div v-if="col.id !== undefined && col.id !== null">
          <router-link
            :to="{ name: 'Organize', params: { id: String(col.id) } }"
            style="text-decoration: none; color: #2563eb; cursor: pointer;"
          >
            {{ col.name }}
          </router-link>
        </div>
        <span v-else>
          {{ col.name || 'Unnamed Collection' }} (No ID available)
        </span>
      </li>
    </ul>
  </div>
</template>

<script>
import Breadcrumbs from '@/components/Breadcrumbs.vue'
import CollectionTree from '@/components/CollectionTree.vue'
import { getCollections } from '@/api/collections.js'

export default {
  name: 'CollectionsTree',
  components: { Breadcrumbs, CollectionTree },
  data() {
    return {
      collections: [],
      newCollectionName: ''
    }
  },
  async created() {
    try {
      this.collections = await getCollections()
    } catch (error) {
      console.error('Failed to load collections:', error)
      this.collections = []
    }
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

<style scoped>
.collections-view {
  padding: 70px 2rem 2rem 2rem; /* Top padding to account for fixed header */
}

.guidance-text {
  background: #f8f9fa;
  border-left: 4px solid #007acc;
  padding: 1rem;
  margin-bottom: 1.5rem;
  color: #495057;
  font-size: 0.95rem;
  line-height: 1.5;
}
</style>