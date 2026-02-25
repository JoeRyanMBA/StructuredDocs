<template>
  <div class="archived-page">
    <h2>Archived Collections</h2>
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
  <div v-else-if="collections.length" class="archived-table-container">
    <table class="table archived-table">
      <thead>
        <tr>
          <th>Name</th>
          <th>Form #</th>
          <th>Project</th>
          <th>Topics</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="c in collections" :key="c.id" class="row-archived">
          <td>{{ c.name }}</td>
          <td>{{ c.form_number }}</td>
          <td>{{ c.projectName || '-' }}</td>
          <td>{{ c.topics_count ?? '-' }}</td>
          <td>
            <ArchiveToggleButton :archived="true" entity-label="collection" @toggle="() => restore(c)" />
          </td>
        </tr>
      </tbody>
    </table>
  </div>
  <p v-else class="empty">No archived collections.</p>
  </div>
</template>

<script>
import ArchiveToggleButton from '@/components/ArchiveToggleButton.vue'
import { useArchive } from '@/composables/useArchive'

export default {
  name: 'ArchivedCollectionsView',
  components: { ArchiveToggleButton },
  setup() {
    const { items, load, restore } = useArchive('collections')
    load()
    return { collections: items, load, restore }
  }
}
</script>
