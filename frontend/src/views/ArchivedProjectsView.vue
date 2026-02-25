<template>
  <div class="archived-page">
    <h2>Archived Projects</h2>
    <div class="projects-list-panel">
      <div class="filter-row">
        <div class="filter-group actions-group">
          <div class="button-group">
            <button class="btn btn-sm btn-secondary" @click="load" :disabled="loading">Refresh</button>
          </div>
        </div>
      </div>
    </div>
  <div v-if="loading" class="loading">Loading...</div>
  <div v-else-if="projects.length" class="archived-table-container">
    <table class="table archived-table">
      <thead>
        <tr>
          <th>Name</th>
          <th>Status</th>
          <th>Created</th>
          <th>Updated</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="p in projects" :key="p.id" class="row-archived">
          <td>{{ p.name }}</td>
          <td>{{ p.status }}</td>
          <td>{{ formatDate(p.created_at) }}</td>
          <td>{{ formatDate(p.updated_at) }}</td>
          <td>
            <ArchiveToggleButton :archived="true" entity-label="project" @toggle="() => restore(p)" />
          </td>
        </tr>
      </tbody>
    </table>
  </div>
  <p v-else class="empty">No archived projects.</p>
  </div>
</template>

<script>
import ArchiveToggleButton from '@/components/ArchiveToggleButton.vue'
import { useArchive } from '@/composables/useArchive'

export default {
  name: 'ArchivedProjectsView',
  components: { ArchiveToggleButton },
  setup() {
    const { items, load, restore } = useArchive('projects')
    function formatDate(dt) { return dt ? new Date(dt).toLocaleDateString() : '' }
    load()
    return { projects: items, load, restore, formatDate }
  }
}
</script>
