<template>
  <div class="button-catalog">
    <div class="dashboard-header">
      <h1>Button Catalog</h1>
      <p class="subtitle">Live examples of button styles, their source, and where they are used</p>
    </div>

    <div class="section-card">
      <div class="catalog-controls">
        <input v-model="filter" class="filter-input" placeholder="Filter by name or usage..." />
      </div>

      <div class="table-wrapper">
        <table class="catalog-table">
          <thead>
            <tr>
              <th style="width: 240px">Example</th>
              <th>Name</th>
              <th>Classes</th>
              <th>Stylesheet</th>
              <th>Where used</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in filteredRows" :key="row.name">
              <td>
                <component :is="row.exampleTag" v-bind="row.exampleBind" :class="row.classes">
                  <template v-if="row.icon" #default>
                    <i :class="row.icon" />
                    <span v-if="row.text">{{ row.text }}</span>
                  </template>
                  <template v-else #default>
                    {{ row.text }}
                  </template>
                </component>
              </td>
              <td>{{ row.name }}</td>
              <td><code>{{ row.classes }}</code></td>
              <td>{{ row.stylesheet }}</td>
              <td>
                <ul>
                  <li v-for="(loc, i) in row.usedIn" :key="i">{{ loc }}</li>
                </ul>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div class="section-card mt-8">
      <h2>Notes</h2>
      <ul>
        <li>All buttons should use variables defined in <code>src/assets/style.css</code>.</li>
        <li>Avoid local overrides except for page-specific layouts.</li>
      </ul>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ButtonCatalog',
  data() {
    return {
      filter: '',
      rows: [
        {
          name: 'Primary',
          classes: 'btn btn-primary',
          text: 'Primary',
          icon: 'bi bi-check-lg',
          stylesheet: 'assets/style.css (.btn, .btn-primary)',
          usedIn: [
            'TopicsListView.vue (Search button)',
            'AllLinksView.vue (Create First Link)',
            'AllImagesView.vue (Refresh, Copy in modal)',
            'AllTasksView.vue (Create Task)'
          ],
          exampleTag: 'button',
          exampleBind: { type: 'button' }
        },
        {
          name: 'Secondary',
          classes: 'btn btn-secondary',
          text: 'Secondary',
          icon: 'bi bi-sliders',
          stylesheet: 'assets/style.css (.btn-secondary)',
          usedIn: [
            'TopicsListView.vue (Clear Filters, bulk actions)',
            'AllLinksView.vue (Clear Filters, Close modal)',
            'AuthorDashboard.vue (Clear Filters)'
          ],
          exampleTag: 'button',
          exampleBind: { type: 'button' }
        },
        {
          name: 'Danger',
          classes: 'btn btn-danger',
          text: 'Delete',
          icon: 'bi bi-trash',
          stylesheet: 'assets/style.css (.btn-danger)',
          usedIn: [
            'TopicsListView.vue (Bulk delete)',
            'AllMilestonesView.vue (Delete)',
            'AllTagsView.vue (Delete)'
          ],
          exampleTag: 'button',
          exampleBind: { type: 'button' }
        },
        {
          name: 'Info',
          classes: 'btn btn-info',
          text: 'Info',
          icon: 'bi bi-info-circle',
          stylesheet: 'assets/style.css (.btn-info)',
          usedIn: [
            'ReviewPortal.vue (Preview Changes)'
          ],
          exampleTag: 'button',
          exampleBind: { type: 'button' }
        },
        {
          name: 'Success',
          classes: 'btn btn-success',
          text: 'Save',
          icon: 'bi bi-check-lg',
          stylesheet: 'assets/style.css (.btn-success)',
          usedIn: [
            'ReviewPortal.vue (Submit Review)'
          ],
          exampleTag: 'button',
          exampleBind: { type: 'button' }
        },
        {
          name: 'Outline',
          classes: 'btn btn-outline',
          text: 'Preview',
          icon: 'bi bi-eye',
          stylesheet: 'assets/style.css (.btn-outline)',
          usedIn: [
            'ReviewPortal.vue (Preview Changes)'
          ],
          exampleTag: 'button',
          exampleBind: { type: 'button' }
        },
        {
          name: 'Small Primary',
          classes: 'btn btn-primary btn-sm',
          text: 'Search',
          icon: 'bi bi-search',
          stylesheet: 'assets/style.css (.btn-sm + .btn-primary)',
          usedIn: [
            'TopicsListView.vue (Search)',
            'AllTagsView.vue (Apply Filters)',
            'AllMilestonesView.vue (Apply Filters)'
          ],
          exampleTag: 'button',
          exampleBind: { type: 'button' }
        },
        {
          name: 'Small Secondary',
          classes: 'btn btn-secondary btn-sm',
          text: 'Clear',
          icon: 'bi bi-eraser',
          stylesheet: 'assets/style.css (.btn-sm + .btn-secondary)',
          usedIn: [
            'TopicsListView.vue (Clear Filters)',
            'AllLinksView.vue (Clear Filters)',
            'AllImagesView.vue (Clear Search)'
          ],
          exampleTag: 'button',
          exampleBind: { type: 'button' }
        },
        {
          name: 'Icon: Edit',
          classes: 'btn-icon btn-secondary',
          text: '',
          icon: 'bi bi-pencil-square',
          stylesheet: 'assets/style.css (.btn-icon, .btn-icon.btn-secondary)',
          usedIn: [
            'TopicsListView.vue (Edit topic)',
            'AdminBugs.vue (Edit bug)',
            'AdminFeedback.vue (Edit feedback)'
          ],
          exampleTag: 'button',
          exampleBind: { type: 'button', title: 'Edit' }
        },
        {
          name: 'Icon: Submit for Review',
          classes: 'btn-icon btn-send-review',
          text: '',
          icon: 'bi bi-send',
          stylesheet: 'assets/style.css (.btn-icon.btn-send-review)',
          usedIn: [
            'TopicsListView.vue actions',
            'AuthorDashboard.vue actions'
          ],
          exampleTag: 'button',
          exampleBind: { type: 'button', title: 'Submit for review' }
        },
        {
          name: 'Icon: Sequential Review',
          classes: 'btn-icon btn-seq-review',
          text: '',
          icon: 'bi bi-arrow-right-circle',
          stylesheet: 'assets/style.css (.btn-icon.btn-seq-review)',
          usedIn: [
            'TopicsListView.vue actions',
            'AuthorDashboard.vue actions'
          ],
          exampleTag: 'button',
          exampleBind: { type: 'button', title: 'Sequential review' }
        },
        {
          name: 'Icon: Publish',
          classes: 'btn-icon btn-publish',
          text: '',
          icon: 'bi bi-share',
          stylesheet: 'assets/style.css (.btn-icon.btn-publish)',
          usedIn: [
            'TopicsListView.vue actions',
            'AuthorDashboard.vue actions'
          ],
          exampleTag: 'button',
          exampleBind: { type: 'button', title: 'Publish' }
        },
        {
          name: 'Icon: Archive',
          classes: 'btn-icon btn-archive',
          text: '',
          icon: 'bi bi-archive',
          stylesheet: 'assets/style.css (.btn-icon.btn-archive)',
          usedIn: [
            'AdminBugs.vue actions',
            'AdminFeedback.vue actions'
          ],
          exampleTag: 'button',
          exampleBind: { type: 'button', title: 'Archive' }
        },
        {
          name: 'Link Button',
          classes: 'link-btn',
          text: 'Create your first item',
          icon: '',
          stylesheet: 'assets/style.css (.link-btn)',
          usedIn: [
            'AuthorDashboard.vue (empty states)',
            'PublishDashboard.vue (empty states)',
            'CollectionsDashboard.vue (empty states)'
          ],
          exampleTag: 'button',
          exampleBind: { type: 'button' }
        },
        {
          name: 'Create (solid)',
          classes: 'create-btn',
          text: 'Create',
          icon: '',
          stylesheet: 'assets/style.css (.create-btn)',
          usedIn: [
            'CollectionsDashboard.vue (modal)',
            'TasksView.vue (modal)'
          ],
          exampleTag: 'button',
          exampleBind: { type: 'button' }
        },
        {
          name: 'Toggle',
          classes: 'toggle-btn',
          text: 'Toggle',
          icon: 'bi bi-toggle-on',
          stylesheet: 'assets/style.css (.toggle-btn)',
          usedIn: [
            'ReviewPortal.vue (Compare toggles)'
          ],
          exampleTag: 'button',
          exampleBind: { type: 'button' }
        },
        {
          name: 'Section',
          classes: 'section-btn',
          text: 'Go to Section',
          icon: 'bi bi-arrow-right',
          stylesheet: 'assets/style.css (.section-btn)',
          usedIn: [
            'AdminDashboard.vue (links)',
            'ImportDashboard.vue (links)'
          ],
          exampleTag: 'a',
          exampleBind: { href: '#' }
        },
        {
          name: 'Card Action',
          classes: 'card-action-btn',
          text: 'View',
          icon: 'bi bi-eye',
          stylesheet: 'assets/style.css (.card-action-btn)',
          usedIn: [
            'ImportDashboard.vue (cards)',
            'ReviewsDashboard.vue (cards)'
          ],
          exampleTag: 'button',
          exampleBind: { type: 'button' }
        },
        {
          name: 'Remove (x small)',
          classes: 'remove-btn',
          text: '×',
          icon: '',
          stylesheet: 'assets/style.css (.remove-btn)',
          usedIn: [
            'ReviewPortal.vue (remove item)'
          ],
          exampleTag: 'button',
          exampleBind: { type: 'button', title: 'Remove' }
        },
        {
          name: 'Login (full-width)',
          classes: 'login-btn',
          text: 'Sign in',
          icon: 'bi bi-box-arrow-in-right',
          stylesheet: 'assets/style.css (.login-btn)',
          usedIn: [
            'LoginView.vue',
            'HeaderBar.vue'
          ],
          exampleTag: 'button',
          exampleBind: { type: 'button' }
  },
        {
          name: 'Cancel (neutral)',
          classes: 'cancel-btn',
          text: 'Cancel',
          icon: '',
          stylesheet: 'assets/style.css (.cancel-btn)',
          usedIn: [
            'CollectionsDashboard.vue (modal)',
            'TasksView.vue (modal)',
            'TopicEditor.vue (dialogs)'
          ],
          exampleTag: 'button',
          exampleBind: { type: 'button' }
        },
        {
          name: 'Export',
          classes: 'export-btn',
          text: 'Download PDF',
          icon: 'bi bi-download',
          stylesheet: 'assets/style.css (.export-btn)',
          usedIn: [
            'PublishPDFView.vue'
          ],
          exampleTag: 'button',
          exampleBind: { type: 'button' }
        },
        {
          name: 'Submit',
          classes: 'submit-btn',
          text: 'Submit Review',
          icon: 'bi bi-check-lg',
          stylesheet: 'assets/style.css (.submit-btn)',
          usedIn: [
            'ReviewPortal.vue (form submission)',
            'NotificationManagement.vue (save changes)'
          ],
          exampleTag: 'button',
          exampleBind: { type: 'submit' }
        },
        {
          name: 'Create First',
          classes: 'create-first-btn',
          text: 'Create Your First Task',
          icon: 'bi bi-plus-lg',
          stylesheet: 'assets/style.css (.create-first-btn)',
          usedIn: [
            'TasksView.vue (empty state)',
            'ProjectsView.vue (empty state)',
            'CollectionsDashboard.vue (empty states)'
          ],
          exampleTag: 'button',
          exampleBind: { type: 'button' }
        }
      ]
    }
  },
  computed: {
    filteredRows() {
      const q = (this.filter || '').toLowerCase()
      if (!q) return this.rows
      return this.rows.filter(r =>
        r.name.toLowerCase().includes(q) ||
        r.classes.toLowerCase().includes(q) ||
        r.usedIn.some(u => u.toLowerCase().includes(q))
      )
    }
  }
}
</script>

<style scoped>
.table-wrapper {
  overflow-x: auto;
}
.catalog-controls {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 1rem;
}
.catalog-table {
  width: 100%;
  border-collapse: collapse;
}
.catalog-table th,
.catalog-table td {
  border: 1px solid var(--border-light-gray);
  padding: 0.75rem;
  vertical-align: middle;
}
.catalog-table thead th {
  background: var(--bg-light-mist-gray);
  text-align: left;
}
.catalog-table code {
  background: var(--bg-light-mist-gray);
  border: 1px solid var(--border-light-gray);
  border-radius: 4px;
  padding: 2px 6px;
  font-size: 0.8rem;
}
</style>
