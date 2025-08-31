<   <div class="publications-home">
    <h2>Publications</h2>iv class="publications-home">
    <h2>Publications</h2>plate>
  <div class="publications-home">
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

export default {
  name: 'PublicationsHome',
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
  margin: 0 auto;
}

.guidance-text {
  background: var(--bg-light-mist-gray);
  border-left: 4px solid var(--primary-deep-teal);
  border-radius: .75rem;
  padding: 1rem;
  margin-bottom: 1.5rem;
  color: var(--text-primary-charcoal);
  font-size: 0.95rem;
  line-height: 1.5;
}

.loading,
.error {
  margin-top: 1rem;
  font-size: 0.9rem;
}

.error {
  color: var(--error-coral-red);
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
  color: var(--primary-medium-teal);
}

.publication-link {
  text-decoration: none;
  color: var(--primary-deep-teal);
  display: block;
}

.publication-link:hover {
  color: var(--primary-medium-teal);
}

.publication-summary {
  color: var(--text-secondary-cool-gray);
  font-weight: normal;
  margin-left: 0.5rem;
}

.empty {
  color: var(--text-secondary-cool-gray);
  font-style: italic;
  text-align: center;
  margin-top: 2rem;
}
</style>