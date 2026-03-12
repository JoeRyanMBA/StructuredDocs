<template>
  <section class="admin-page">
    <h1>Help Links</h1>
    <p class="subtitle">
      Manage contextual help entries shown as <i class="bi bi-info-circle"></i> icons throughout the
      app. Each entry is keyed to a feature name used in the code. Disable an entry to hide its icon
      without deleting it.
    </p>

    <!-- Available feature keys reference panel -->
    <div class="registry-panel">
      <div class="registry-header" @click="showRegistry = !showRegistry">
        <span><i class="bi bi-map me-2"></i><strong>Available Feature Keys</strong> — where icons can appear in the app</span>
        <i class="bi" :class="showRegistry ? 'bi-chevron-up' : 'bi-chevron-down'"></i>
      </div>
      <div v-if="showRegistry" class="registry-body">
        <table class="registry-table">
          <thead>
            <tr>
              <th>Feature Key</th>
              <th>Where it appears</th>
              <th>Suggested use</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="entry in registryWithStatus" :key="entry.key">
              <td><code>{{ entry.key }}</code></td>
              <td>{{ entry.location }}</td>
              <td class="hint-cell">{{ entry.hint }}</td>
              <td>
                <span v-if="entry.configured" class="badge-configured">
                  <i class="bi bi-check-circle-fill me-1"></i>Configured
                </span>
                <button v-else class="btn btn-outline-primary btn-xs" @click="openCreateForKey(entry)">
                  <i class="bi bi-plus me-1"></i>Set up
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div class="toolbar">
      <button class="btn btn-primary btn-sm" @click="openCreate">
        <i class="bi bi-plus-lg me-1"></i>Add Help Link
      </button>
    </div>

    <div v-if="loading" class="loading">Loading…</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else>
      <table v-if="links.length" class="help-links-table">
        <thead>
          <tr>
            <th>Feature Key</th>
            <th>Where it appears</th>
            <th>Title</th>
            <th>Description</th>
            <th>KB URL</th>
            <th>Enabled</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="link in links" :key="link.id" :class="{ disabled: !link.enabled }">
            <td class="feature-key"><code>{{ link.feature_key }}</code></td>
            <td class="location-cell">{{ locationFor(link.feature_key) }}</td>
            <td>{{ link.title }}</td>
            <td class="description-cell">{{ link.description }}</td>
            <td class="url-cell">
              <a v-if="link.kb_url" :href="link.kb_url" target="_blank" rel="noopener noreferrer" class="kb-url-link">
                <i class="bi bi-box-arrow-up-right me-1"></i>Open
              </a>
              <span v-else class="text-muted">—</span>
            </td>
            <td>
              <button
                class="btn btn-sm"
                :class="link.enabled ? 'btn-success' : 'btn-outline-secondary'"
                @click="toggleEnabled(link)"
                :title="link.enabled ? 'Click to disable' : 'Click to enable'"
              >
                <i class="bi" :class="link.enabled ? 'bi-toggle-on' : 'bi-toggle-off'"></i>
                {{ link.enabled ? 'On' : 'Off' }}
              </button>
            </td>
            <td class="actions">
              <button class="btn-icon btn-secondary" title="Edit" @click="openEdit(link)">
                <i class="bi bi-pencil-square"></i>
              </button>
              <button class="btn-icon btn-danger" title="Delete" @click="confirmDelete(link)">
                <i class="bi bi-trash"></i>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-else class="empty">No help links yet. Click <strong>Add Help Link</strong> to create the first one.</div>
    </div>

    <!-- Create / Edit modal -->
    <div v-if="editing" class="modal-overlay" @click.self="closeEdit">
      <div class="modal-box" @click.stop>
        <div class="modal-header-row modal-header">
          <h3>{{ isNew ? 'Add Help Link' : 'Edit Help Link' }}</h3>
          <button class="plain-close btn-close" @click="closeEdit" aria-label="Close"></button>
        </div>
        <div class="modal-body">
          <div class="mb-3">
            <label class="form-label">
              Feature Key <span class="text-danger">*</span>
            </label>
            <!-- Dropdown for new entries; read-only display for edits -->
            <select v-if="isNew" v-model="form.feature_key" class="form-select" @change="onKeySelected">
              <option value="">— choose a location —</option>
              <optgroup label="Available locations">
                <option
                  v-for="entry in availableKeys"
                  :key="entry.key"
                  :value="entry.key"
                >{{ entry.label }} · {{ entry.location }}</option>
              </optgroup>
            </select>
            <div v-else class="form-control-plaintext">
              <code>{{ form.feature_key }}</code>
              <span class="text-muted ms-2">— {{ locationFor(form.feature_key) }}</span>
              <div class="form-text text-muted">Feature key cannot be changed after creation.</div>
            </div>
          </div>
          <div class="mb-3">
            <label class="form-label">Title <span class="text-danger">*</span></label>
            <input v-model="form.title" class="form-control" placeholder="Short title shown in the modal header" />
          </div>
          <div class="mb-3">
            <label class="form-label">Description</label>
            <textarea v-model="form.description" class="form-control" rows="4"
              placeholder="Explain the feature. Shown when the user clicks the info icon."></textarea>
          </div>
          <div class="mb-3">
            <label class="form-label">Knowledge Base URL</label>
            <input v-model="form.kb_url" class="form-control" type="url"
              placeholder="https://… (optional — shows a 'Learn More' button)" />
          </div>
          <div class="mb-3 form-check">
            <input v-model="form.enabled" class="form-check-input" type="checkbox" id="editEnabled" />
            <label class="form-check-label" for="editEnabled">Enabled (icon visible to users)</label>
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

    <!-- Delete confirmation -->
    <div v-if="deleting" class="modal-overlay" @click.self="cancelDelete">
      <div class="modal-box modal-box--sm" @click.stop>
        <div class="modal-header-row modal-header">
          <h3>Delete Help Link</h3>
          <button class="plain-close btn-close" @click="cancelDelete" aria-label="Close"></button>
        </div>
        <div class="modal-body">
          <p>Delete <strong>{{ deleting.feature_key }}</strong>? This cannot be undone.</p>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="cancelDelete">Cancel</button>
          <button class="btn btn-danger" @click="doDelete" :disabled="saving">
            <span v-if="saving" class="spinner-border spinner-border-sm me-1" role="status"></span>
            {{ saving ? 'Deleting…' : 'Delete' }}
          </button>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
import { getAdminHelpLinks, createHelpLink, updateHelpLink, deleteHelpLink } from '@/api/helpLinks'
import { toast } from '@/composables/useToast'
import { HELP_FEATURE_KEYS, HELP_KEY_MAP } from '@/config/helpFeatureKeys'

export default {
  name: 'AdminHelpLinks',

  data() {
    return {
      links: [],
      loading: true,
      error: null,
      editing: false,
      isNew: false,
      editId: null,
      form: { feature_key: '', title: '', description: '', kb_url: '', enabled: true },
      saving: false,
      saveError: null,
      deleting: null,
      showRegistry: true,
    }
  },

  computed: {
    configuredKeys() {
      return new Set(this.links.map(l => l.feature_key))
    },
    registryWithStatus() {
      return HELP_FEATURE_KEYS.map(e => ({
        ...e,
        configured: this.configuredKeys.has(e.key),
      }))
    },
    /** Only show keys that aren't already configured in the dropdown */
    availableKeys() {
      return HELP_FEATURE_KEYS.filter(e => !this.configuredKeys.has(e.key))
    },
  },

  async mounted() {
    await this.load()
  },

  methods: {
    locationFor(key) {
      return HELP_KEY_MAP[key]?.location || '—'
    },
    onKeySelected() {
      const entry = HELP_KEY_MAP[this.form.feature_key]
      if (entry && !this.form.title) {
        this.form.title = entry.label
      }
    },
    async load() {
      this.loading = true
      this.error = null
      try {
        this.links = await getAdminHelpLinks()
      } catch (e) {
        this.error = e?.response?.data?.error || e.message
      } finally {
        this.loading = false
      }
    },

    openCreate() {
      this.isNew = true
      this.editId = null
      this.form = { feature_key: '', title: '', description: '', kb_url: '', enabled: true }
      this.saveError = null
      this.editing = true
    },

    openCreateForKey(entry) {
      this.isNew = true
      this.editId = null
      this.form = { feature_key: entry.key, title: entry.label, description: entry.hint, kb_url: '', enabled: true }
      this.saveError = null
      this.editing = true
    },

    openEdit(link) {
      this.isNew = false
      this.editId = link.id
      this.form = {
        feature_key: link.feature_key,
        title: link.title,
        description: link.description,
        kb_url: link.kb_url,
        enabled: link.enabled,
      }
      this.saveError = null
      this.editing = true
    },

    closeEdit() {
      this.editing = false
    },

    async save() {
      this.saveError = null
      if (!this.form.feature_key.trim() || !this.form.title.trim()) {
        this.saveError = 'Feature key and title are required.'
        return
      }
      this.saving = true
      try {
        if (this.isNew) {
          await createHelpLink(this.form)
          toast.success('Help link created')
        } else {
          await updateHelpLink(this.editId, this.form)
          toast.success('Help link updated')
        }
        this.editing = false
        await this.load()
      } catch (e) {
        this.saveError = e?.response?.data?.error || e.message
      } finally {
        this.saving = false
      }
    },

    async toggleEnabled(link) {
      try {
        await updateHelpLink(link.id, { enabled: !link.enabled })
        link.enabled = !link.enabled
        toast.success(`Help link ${link.enabled ? 'enabled' : 'disabled'}`)
      } catch (e) {
        toast.error(e?.response?.data?.error || e.message)
      }
    },

    confirmDelete(link) {
      this.deleting = link
    },

    cancelDelete() {
      this.deleting = null
    },

    async doDelete() {
      this.saving = true
      try {
        await deleteHelpLink(this.deleting.id)
        toast.success('Help link deleted')
        this.deleting = null
        await this.load()
      } catch (e) {
        toast.error(e?.response?.data?.error || e.message)
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
  max-width: 1100px;
}

h1 { margin-bottom: 4px; }
.subtitle { color: #6c757d; margin-bottom: 20px; }

/* Registry panel */
.registry-panel {
  border: 1px solid #dee2e6;
  border-radius: 8px;
  margin-bottom: 20px;
  overflow: hidden;
}

.registry-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 16px;
  background: #f8f9fa;
  cursor: pointer;
  user-select: none;
  font-size: 0.9rem;
}

.registry-header:hover { background: #e9ecef; }

.registry-body { padding: 0; }

.registry-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
}

.registry-table th,
.registry-table td {
  padding: 8px 16px;
  border-bottom: 1px solid #dee2e6;
  vertical-align: middle;
}

.registry-table th {
  font-weight: 600;
  background: #fff;
  color: #6c757d;
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.registry-table tr:last-child td { border-bottom: none; }

.hint-cell { color: #6c757d; }

.badge-configured {
  display: inline-flex;
  align-items: center;
  font-size: 0.8rem;
  color: #198754;
  font-weight: 500;
}

.btn-xs {
  padding: 2px 8px;
  font-size: 0.8rem;
}

.location-cell { color: #6c757d; font-size: 0.85em; }

.toolbar {
  margin-bottom: 16px;
}

.help-links-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}

.help-links-table th,
.help-links-table td {
  padding: 10px 12px;
  border-bottom: 1px solid #dee2e6;
  vertical-align: middle;
}

.help-links-table th {
  background: #f8f9fa;
  font-weight: 600;
  white-space: nowrap;
}

.help-links-table tr.disabled td {
  opacity: 0.55;
}

.feature-key code {
  background: #f0f0f0;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.85em;
}

.description-cell {
  max-width: 280px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.url-cell { white-space: nowrap; }
.kb-url-link { font-size: 0.85em; }

.actions {
  display: flex;
  gap: 6px;
  white-space: nowrap;
}

.btn-icon {
  background: none;
  border: 1px solid transparent;
  border-radius: 4px;
  padding: 4px 6px;
  cursor: pointer;
  font-size: 0.95em;
  transition: background 0.15s, border-color 0.15s;
}
.btn-icon.btn-secondary { color: #6c757d; }
.btn-icon.btn-secondary:hover { background: #e9ecef; border-color: #adb5bd; }
.btn-icon.btn-danger { color: #dc3545; }
.btn-icon.btn-danger:hover { background: #f8d7da; border-color: #f1aeb5; }

.empty {
  color: #6c757d;
  padding: 24px 0;
}

.loading, .error {
  padding: 24px 0;
  color: #6c757d;
}
.error { color: #dc3545; }

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
  width: min(560px, 92vw);
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.modal-box--sm { width: min(420px, 92vw); }

.modal-header-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px 12px;
  border-bottom: 1px solid #dee2e6;
}

.modal-header-row h3 {
  margin: 0;
  font-size: 1.05rem;
  font-weight: 600;
}

.modal-body {
  padding: 16px 20px;
  overflow-y: auto;
  flex: 1;
}

.modal-footer {
  padding: 12px 20px 16px;
  border-top: 1px solid #dee2e6;
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
</style>
