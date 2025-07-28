<template>
  <div class="publications-home">
    <Breadcrumbs />
    <h2>All Publications</h2>
    
    <p class="guidance-text">
      These are all published collections. Each publication represents a finalized version of a collection that can be exported or shared.
    </p>

    <div v-if="loading" class="loading">Loading publications...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else>
      <ul v-if="publications.length > 0" class="publications-list">
        <li v-for="pub in publications" :key="pub.id" class="publication-item">
          <router-link :to="{ name: 'PublicationView', params: { id: pub.id } }" class="publication-link">
            {{ pub.title }}
            <span v-if="pub.excerpt || pub.summary" class="publication-summary">
              - {{ pub.excerpt || pub.summary }}
            </span>
          </router-link>
        </li>
      </ul>
      <p v-else class="empty">
        No publications found.
      </p>
    </div>
  </div>
</template>

<script>
import Breadcrumbs from '@/components/Breadcrumbs.vue'

export default {
  name: 'PublicationsHome',
  components: { Breadcrumbs },
  data() {
    return { 
      publications: [],
      loading: true,
      error: null
    }
  },
  async created() {
    try {
      const res = await fetch('/api/publications')
      if (!res.ok) throw new Error(`Failed to fetch publications: ${res.statusText}`)
      this.publications = await res.json()
    } catch (err) {
      console.error('Failed to fetch publications:', err)
      this.error = 'Failed to load publications'
    } finally {
      this.loading = false
    }
  }
}
</script>

<style scoped>
.publications-home {
  padding-top: 0px; /* Top padding to account for fixed header */
  padding-left: 2rem;
  padding-right: 2rem;
  padding-bottom: 2rem;
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

.loading,
.error {
  margin-top: 1rem;
  font-size: 0.9rem;
}

.error {
  color: #c00;
}

.publications-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.publication-item {
  margin-bottom: 0.5rem;
  padding: 0.25rem 0;
}

.publication-item:hover .publication-link {
  color: #1d4ed8;
}

.publication-link {
  text-decoration: none;
  color: #2563eb;
  display: block;
}

.publication-link:hover {
  color: #1d4ed8;
}

.publication-summary {
  color: #666;
  font-weight: normal;
  margin-left: 0.5rem;
}

.empty {
  color: #999;
  font-style: italic;
  text-align: center;
  margin-top: 2rem;
}
</style>