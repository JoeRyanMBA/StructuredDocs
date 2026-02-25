<template>
  <div class="archived-page">
    <h2>Archived Feedback</h2>
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
          <th>Subject</th>
          <th>Type</th>
          <th>Submitted</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="f in items" :key="f.id" class="row-archived">
          <td>{{ f.subject || f.title || '(no subject)' }}</td>
          <td>{{ f.type || 'feedback' }}</td>
          <td>{{ formatDate(f.created_at) }}</td>
          <td>
            <ArchiveToggleButton :archived="true" entity-label="feedback" @toggle="() => restore(f)" />
          </td>
        </tr>
      </tbody>
    </table>
  </div>
    <p v-else class="empty">No archived feedback.</p>
  </div>
</template>

<script>
import ArchiveToggleButton from '@/components/ArchiveToggleButton.vue'
import { useArchive } from '@/composables/useArchive'

export default {
  name: 'ArchivedFeedbackView',
  components: { ArchiveToggleButton },
  setup() {
    const { items, load, restore } = useArchive('feedback')
    function formatDate(dt) { return dt ? new Date(dt).toLocaleDateString() : '' }
    load()
    return { items, load, restore, formatDate }
  }
}
</script>
