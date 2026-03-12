<template>
  <section class="admin-page">
    <h1>Help Links</h1>
    <p class="subtitle">
      Every location in the app where a <i class="bi bi-info-circle"></i> help icon can appear is listed below.
      Click <i class="bi bi-pencil-square"></i> to add a description (and optional KB link), then toggle the row on to show the icon to users.
    </p>

    <div v-if="loading" class="loading">Loading…</div>
    <div v-else-if="error" class="error">{{ error }}</div>

    <table v-else class="locations-table">
      <thead>
        <tr>
          <th class="col-toggle"></th>
          <th>Location</th>
          <th>Where it appears</th>
          <th>Title</th>
          <th>Description</th>
          <th class="col-url">KB</th>
          <th class="col-edit"></th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="row in rows"
          :key="row.key"
          :class="{ 'row-off': !row.link || !row.link.enabled, 'row-saving': row.saving }"
        >
          <!-- Enabled toggle -->
          <td class="toggle-cell">
            <button
              class="toggle-btn"
              :class="row.link && row.link.enabled ? 'is-on' : 'is-off'"
              :title="row.link && row.link.enabled ? 'Disable icon' : 'Enable icon (save description first)'"
              :disabled="row.saving"
              @click="toggleRow(row)"
            >
              <i class="bi" :class="row.link && row.link.enabled ? 'bi-toggle-on' : 'bi-toggle-off'"></i>
            </button>
          </td>

          <!-- Location label -->
          <td class="label-cell"><strong>{{ row.label }}</strong></td>

          <!-- Where it appears -->
          <td class="location-cell">{{ row.location }}</td>

          <!-- Title (always from registry) -->
          <td class="title-cell">{{ row.label }}</td>

          <!-- Description -->
          <td class="desc-cell">
            <span v-if="row.link && row.link.description">{{ row.link.description }}</span>
            <span v-else class="text-muted fst-italic">no description yet</span>
          </td>

          <!-- KB URL -->
          <td class="url-cell">
            <a
              v-if="row.link && row.link.kb_url"
              :href="row.link.kb_url"
              target="_blank"
              rel="noopener noreferrer"
              title="Open KB article"
            ><i class="bi bi-box-arrow-up-right"></i></a>
            <span v-else class="text-muted">—</span>
          </td>

          <!-- Edit (always visible) -->
          <td class="edit-cell">
            <button
              class="btn-icon btn-secondary"
              :title="row.link ? 'Edit description' : 'Add description'"
              :disabled="row.saving"
              @click="openEdit(row)"
            ><i class="bi bi-pencil-square"></i></button>
          </td>
        </tr>
      </tbody>
    </table>

    <!-- Edit modal -->
    <div v-if="editing" class="modal-overlay" @click.self="closeEdit">
      <div class="modal-box" @click.stop>
        <div class="modal-header-row modal-header">
          <h3>Edit: {{ editing.label }}</h3>
          <button class="plain-close btn-close" @click="closeEdit" aria-label="Close"></button>
        </div>
        <div class="modal-body">
          <p class="text-muted mb-3" style="font-size:0.875rem">
            <i class="bi bi-geo-alt me-1"></i>{{ editing.location }}
          </p>
          <div class="mb-3">
            <label class="form-label">Title <span class="text-danger">*</span></label>
            <input v-model="form.title" class="form-control" placeholder="Short title shown in the modal header" />
          </div>
          <div class="mb-3">
            <label class="form-label">Description</label>
            <textarea v-model="form.description" class="form-control" rows="5"
              placeholder="Explain the feature. Shown when the user clicks the info icon."></textarea>
          </div>
          <div class="mb-3">
            <label class="form-label">Knowledge Base URL <span class="text-muted">(optional)</span></label>
            <input v-model="form.kb_url" class="form-control" type="url"
              placeholder="https://… — shows a 'Learn More' button in the help popup" />
          </div>
          <div v-if="saveError" class="alert alert-danger py-2">{{ saveError }}</div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="closeEdit">Cancel</button>
          <button class="btn btn-primary" @click="save" :disabled="saving">
            <span v-if="saving" class="spinner-border spinner-border-sm me-1" role="status"></span>
            {{ saving ? 'Saving…' : 'Save' }}
          </button>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
import { getAdminHelpLinks, createHelpLink, updateHelpLink } from '@/api/helpLinks'
import { toast } from '@/composables/useToast'
import { HELP_FEATURE_KEYS, HELP_KEY_MAP } from '@/config/helpFeatureKeys'

export default {
  name: 'AdminHelpLinks',

  data() {
    return {
      linksByKey: {},   // { [feature_key]: link }
      loading: true,
      error: null,
      // per-row saving spinners
      rowSaving: {},
      // edit modal
      editing: null,    // the row being edited
      form: { title: '', description: '', kb_url: '' },
      saving: false,
      saveError: null,
    }
  },

  computed: {
    rows() {
      return HELP_FEATURE_KEYS.map(entry => ({
        ...entry,
        link: this.linksByKey[entry.key] || null,
        saving: !!this.rowSaving[entry.key],
      }))
    },
  },

  async mounted() {
    await this.load()
  },

  methods: {
    async load() {
      this.loading = true
      this.error = null
      try {
        const links = await getAdminHelpLinks()
        this.linksByKey = Object.fromEntries(links.map(l => [l.feature_key, l]))
      } catch (e) {
        this.error = e?.response?.data?.error || e.message
      } finally {
        this.loading = false
      }
    },

    async toggleRow(row) {
      if (!row.link) {
        // No entry yet — nudge them to add a description first
        this.openEdit(row)
        return
      }
      this.rowSaving = { ...this.rowSaving, [row.key]: true }
      try {
        const updated = await updateHelpLink(row.link.id, { enabled: !row.link.enabled })
        this.linksByKey = { ...this.linksByKey, [row.key]: updated }
        toast.success(`Help icon ${updated.enabled ? 'enabled' : 'disabled'}`)
      } catch (e) {
        toast.error(e?.response?.data?.error || e.message)
      } finally {
        const next = { ...this.rowSaving }
        delete next[row.key]
        this.rowSaving = next
      }
    },

    openEdit(row) {
      this.editing = row
      this.form = {
        title: row.link ? row.link.title : row.label,
        description: row.link ? row.link.description : '',
        kb_url: row.link ? row.link.kb_url : '',
      }
      this.saveError = null
    },

    closeEdit() {
      this.editing = null
    },

    async save() {
      this.saveError = null
      if (!this.form.title.trim()) {
        this.saveError = 'Title is required.'
        return
      }
      this.saving = true
      try {
        if (this.editing.link) {
          const updated = await updateHelpLink(this.editing.link.id, this.form)
          this.linksByKey = { ...this.linksByKey, [this.editing.key]: updated }
        } else {
          // Create the entry disabled — user turns it on with the toggle
          const created = await createHelpLink({
            feature_key: this.editing.key,
            ...this.form,
            enabled: false,
          })
          this.linksByKey = { ...this.linksByKey, [this.editing.key]: created }
        }
        toast.success('Saved — use the toggle to show the icon to users')
        this.editing = null
      } catch (e) {
        this.saveError = e?.response?.data?.error || e.message
      } finally {
        this.saving = false
      }
    },
  },
}
</script>

<style scoped>
.admin-page {
  padding: 24px;
  max-width: 1000px;
}

h1 { margin-bottom: 4px; }
.subtitle { color: #6c757d; margin-bottom: 24px; }

.loading, .error { padding: 24px 0; color: #6c757d; }
.error { color: #dc3545; }

/* Main table */
.locations-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  overflow: hidden;
}

.locations-table th,
.locations-table td {
  padding: 11px 14px;
  border-bottom: 1px solid #dee2e6;
  vertical-align: middle;
}

.locations-table thead th {
  background: #f8f9fa;
  font-weight: 600;
  white-space: nowrap;
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: #495057;
}

.locations-table tbody tr:last-child td { border-bottom: none; }

.locations-table tbody tr.row-off td:not(.toggle-cell) { opacity: 0.5; }
.locations-table tbody tr.row-saving { pointer-events: none; opacity: 0.7; }

/* Toggle button */
.toggle-cell { width: 32px; padding-right: 4px; }

.toggle-btn {
  background: none;
  border: none;
  padding: 0;
  cursor: pointer;
  font-size: 1.5rem;
  line-height: 1;
  transition: color 0.15s;
}

.toggle-btn.is-on  { color: #198754; }
.toggle-btn.is-off { color: #adb5bd; }
.toggle-btn:disabled { cursor: not-allowed; }

/* Column widths */
.col-toggle { width: 36px; }
.col-url    { width: 44px; text-align: center; }
.col-edit   { width: 40px; }

.label-cell    { white-space: nowrap; font-size: 0.9rem; }
.location-cell { color: #6c757d; font-size: 0.85em; }
.title-cell    { white-space: nowrap; font-size: 0.85rem; color: #495057; }
.desc-cell     { max-width: 300px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; font-size: 0.85rem; color: #495057; }

.url-cell { text-align: center; }
.url-cell a { color: #0d6efd; }

.edit-cell { text-align: center; }

.btn-icon {
  background: none;
  border: 1px solid transparent;
  border-radius: 4px;
  padding: 4px 6px;
  cursor: pointer;
  font-size: 0.95em;
  transition: background 0.15s;
}
.btn-icon.btn-secondary { color: #6c757d; }
.btn-icon.btn-secondary:hover { background: #e9ecef; border-color: #adb5bd; }

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1055;
}

.modal-box {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.2);
  width: min(540px, 92vw);
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.modal-header-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px 12px;
  border-bottom: 1px solid #dee2e6;
}

.modal-header-row h3 { margin: 0; font-size: 1.05rem; font-weight: 600; }

.modal-body { padding: 16px 20px; overflow-y: auto; flex: 1; }

.modal-footer {
  padding: 12px 20px 16px;
  border-top: 1px solid #dee2e6;
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
</style>

