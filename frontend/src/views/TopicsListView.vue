<template>
  <div class="topics-list">
    <Breadcrumbs />
    <h2>All Topics</h2>

    <div v-if="loading" class="loading">Loading…</div>
    <div v-else-if="error" class="error">{{ error }}</div>

    <table v-else>
      <thead>
        <tr>
          <th>ID</th>
          <th>Title</th>
          <th>Status</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="t in topics" :key="t.id">
          <td>{{ t.id }}</td>
          <td>{{ t.title }}</td>
          <td>
            <span :class="`badge badge--${t.status}`">
              {{ t.status }}
            </span>
          </td>
          <td class="actions-cell">
            <router-link
              :to="{ name: 'EditTopic', params: { id: t.id } }"
              class="action-link"
            >
              Edit
            </router-link>

            <button
              v-if="t.status === 'draft'"
              @click="publish(t.id)"
              class="action-button publish"
            >
              Publish
            </button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
import Breadcrumbs from '@/components/Breadcrumbs.vue'

export default {
  name: 'TopicListView',
  components: { Breadcrumbs },

  data() {
    return {
      topics: [],
      loading: true,
      error: null
    }
  },

  created() {
    this.fetchTopics()
  },

  methods: {
    async fetchTopics() {
      this.loading = true
      this.error = null

      try {
        const res = await fetch('/api/topics/')
        if (!res.ok) throw new Error(`Status ${res.status}`)
        this.topics = await res.json()
      } catch (err) {
        console.error(err)
        this.error = 'Failed to load topics'
      } finally {
        this.loading = false
      }
    },

    async publish(id) {
      try {
        const res = await fetch(`/api/topics/${id}/publish`, {
          method: 'POST'
        })
        if (!res.ok) throw new Error(`Publish failed (${res.status})`)
        await this.fetchTopics()
      } catch (err) {
        console.error(err)
        this.error = 'Publish action failed'
      }
    }
  }
}
</script>

<style scoped>
.topics-list {
  padding: 2rem;
}

.loading,
.error {
  margin-top: 1rem;
  font-size: 0.9rem;
}

.error {
  color: #c00;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1rem;
}

th,
td {
  text-align: left;
  padding: 0.5rem;
  border-bottom: 1px solid #ddd;
}

.badge {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  text-transform: capitalize;
}

.badge--draft {
  background: #fff4c2;
  color: #996800;
}

.badge--published {
  background: #d4f4dd;
  color: #217a2b;
}

.badge--archived {
  background: #f0f0f0;
  color: #666;
}

.actions-cell {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.action-link {
  color: #005a9c;
  text-decoration: none;
}

.action-button {
  padding: 0.4rem 0.8rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.action-button.publish {
  background: #28a745;
  color: white;
}
</style>