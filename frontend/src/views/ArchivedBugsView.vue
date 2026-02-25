<template>
  <div class="archived-page">
    <h2>Archived Bug Reports</h2>
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
  <div v-else-if="items.length" class="archived-table-container">
    <table class="table archived-table">
      <thead>
        <tr>
          <th>Title</th>
          <th>Created</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="b in items" :key="b.id" class="row-archived">
          <td>{{ b.title || b.subject || '(no title)' }}</td>
          <td>{{ formatDate(b.created_at) }}</td>
          <td>
            <ArchiveToggleButton :archived="true" entity-label="bug report" @toggle="() => restore(b)" />
          </td>
        </tr>
      </tbody>
    </table>
  </div>
    <p v-else class="empty">No archived bug reports.</p>
  </div>
</template>

<script>
import ArchiveToggleButton from '@/components/ArchiveToggleButton.vue'
import { useArchive } from '@/composables/useArchive'

export default {
  name: 'ArchivedBugsView',
  components: { ArchiveToggleButton },
  setup() {
    const { items, load, restore } = useArchive('bugs')
    function formatDate(dt) { return dt ? new Date(dt).toLocaleDateString() : '' }
    load()
    return { items, load, restore, formatDate }
  }
}
</script>
