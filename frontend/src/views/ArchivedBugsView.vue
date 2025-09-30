<template>
  <div class="archived-page">
    <h2>Archived Bug Reports</h2>
    <div class="toolbar">
      <button class="btn btn-sm btn-secondary" @click="load" :disabled="loading">Refresh</button>
    </div>
  <div v-if="loading" class="loading">Loading...</div>
  <table v-else-if="items.length" class="table archived-table">
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
