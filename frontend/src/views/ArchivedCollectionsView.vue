<template>
  <div class="archived-page">
    <h2>Archived Collections</h2>
    <div class="toolbar">
      <button class="btn btn-sm btn-secondary" @click="load" :disabled="loading">Refresh</button>
    </div>
  <div v-if="loading" class="loading">Loading...</div>
  <table v-else-if="collections.length" class="table archived-table">
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

<style scoped>
.archived-page { padding: 1rem; }
.table { width: 100%; border-collapse: collapse; }
.table th, .table td { padding: 0.5rem 0.75rem; border-bottom: 1px solid #ddd; }
.row-archived { opacity: 0.75; }
.loading { font-style: italic; }
.empty { margin-top: 1rem; color: #666; }
.btn-icon.btn-archive { background: var(--warning-bg, #ffc107); color: #222; }
.btn-icon.btn-archive:hover { filter: brightness(0.95); }
</style>
