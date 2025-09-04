<template>
  <section class="admin-page">
  <h1>Feedback</h1>
  <p class="subtitle">User-submitted feedback from the floating widget.</p>

    <div v-if="loading" class="loading">Loading…</div>
    <div v-else>
      <div class="controls">
        <input v-model="filters.q" placeholder="Search message..." @input="load" />
        <select v-model="filters.type" @change="load">
          <option value="">All feedback types</option>
          <option value="suggestion">Suggestion</option>
          <option value="other">Other</option>
        </select>
        <select v-model="filters.status" @change="load">
          <option value="">Any status</option>
          <option value="new">New</option>
          <option value="in_progress">In Progress</option>
          <option value="resolved">Resolved</option>
          <option value="archived">Archived</option>
        </select>
        <button @click="resetFilters">Reset</button>
      </div>
      <div v-if="error" class="error">{{ error }}</div>
      <table v-if="reports.length" class="reports">
        <thead>
          <tr>
            <th>ID</th>
            <th>Type</th>
            <th>Message</th>
            <th>Page</th>
            <th>Component</th>
            <th>Contact</th>
            <th>Created</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="r in reports" :key="r.id">
            <td>{{ r.id }}</td>
            <td>{{ r.report_type }}</td>
            <td class="message">{{ r.message }}</td>
            <td>{{ r.page }}</td>
            <td>{{ r.component }}</td>
            <td>{{ r.user_contact }}</td>
            <td>{{ formatDate(r.created_at) }}</td>
            <td class="actions">
              <div class="action-buttons">
                <button
                  @click="openEdit(r)"
                  class="btn-icon btn-secondary"
                  title="Edit feedback"
                  aria-label="Edit feedback"
                >
                  <i class="fas fa-edit"></i>
                </button>
                <button
                  @click="archive(r)"
                  class="btn-icon btn-archive"
                  title="Archive feedback"
                  aria-label="Archive feedback"
                >
                  <i class="fas fa-box-archive"></i>
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-else class="empty">No feedback yet.</div>
    </div>

    <!-- Edit modal -->
    <div v-if="editing" class="modal-overlay" @click.self="closeEdit">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h3>Edit Feedback #{{ editItem.id }}</h3>
          <button class="close-btn" @click="closeEdit" aria-label="Close">&times;</button>
        </div>
        <div class="modal-body">
        <h3>Edit Feedback #{{ editItem.id }}</h3>
        <label>Type
          <select v-model="editItem.report_type">
            <option>suggestion</option>
            <option>other</option>
          </select>
        </label>
        <label>Component <input v-model="editItem.component" /></label>
        <label>Contact <input v-model="editItem.user_contact" /></label>
        <label>Status <select v-model="editItem.status"><option>new</option><option>in_progress</option><option>resolved</option><option>archived</option></select></label>
        <label>Message <textarea v-model="editItem.message"></textarea></label>
          <div class="modal-actions">
            <button class="btn btn-primary" @click="saveEdit">Save</button>
            <button class="btn btn-secondary" @click="closeEdit">Cancel</button>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
export default {
  name: 'AdminFeedback',
  data() {
    return { loading: false, error: '', reports: [],
      filters: { q: '', type: '', status: '' },
      editing: false, editItem: null
    };
  },
  created() {
    this.load();
  },
  methods: {
    async load() {
      this.loading = true; this.error = ''; this.reports = [];
      try {
        const params = new URLSearchParams();
        if (this.filters.q) params.append('q', this.filters.q);
        if (this.filters.type) params.append('type', this.filters.type);
        if (this.filters.status) params.append('status', this.filters.status);
  const res = await fetch('/api/feedback?' + params.toString());
        if (!res.ok) throw new Error('Failed to load feedback');
  const all = await res.json();
  // Exclude bug reports; those live in the dedicated Bugs page
  this.reports = Array.isArray(all) ? all.filter(r => r?.report_type !== 'bug') : [];
      } catch (e) {
        this.error = e.message || 'Error loading feedback';
      } finally {
        this.loading = false;
      }
    },
    resetFilters() {
      this.filters = { q: '', type: '', status: '' };
      this.load();
    },
    openEdit(item) {
      this.editing = true;
      // shallow copy to avoid mutating list until saved
      this.editItem = Object.assign({}, item);
    },
    closeEdit() { this.editing = false; this.editItem = null; },
    async saveEdit() {
      try {
        let res = await fetch('/api/feedback/' + this.editItem.id, {
          method: 'PATCH', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(this.editItem)
        });
        if (res.status === 405) {
          // fallback to POST update
          res = await fetch('/api/feedback/' + this.editItem.id + '/update', {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(this.editItem)
          });
        }
        if (!res.ok) throw new Error('Failed to save');
        const updated = await res.json();
        // update list
        const idx = this.reports.findIndex(r => r.id === updated.id);
        if (idx !== -1) this.reports.splice(idx, 1, updated);
        this.closeEdit();
      } catch (e) {
        this.error = e.message || 'Error saving feedback';
      }
    },
    async archive(item) {
      if (!confirm('Archive this feedback?')) return;
      try {
        let res = await fetch('/api/feedback/' + item.id, { method: 'DELETE' });
        if (res.status === 405) {
          res = await fetch('/api/feedback/' + item.id + '/archive', { method: 'POST' });
        }
        if (!res.ok) throw new Error('Failed to archive');
        // remove from list
        this.reports = this.reports.filter(r => r.id !== item.id);
      } catch (e) {
        this.error = e.message || 'Error archiving';
      }
    },
    formatDate(iso) {
      if (!iso) return '';
      try { return new Date(iso).toLocaleString(); } catch { return iso; }
    }
  }
}
</script>

<style scoped>
.admin-page { padding: 1rem; }
.subtitle { margin-bottom: 1rem; }
.loading { color: #205493; }
.error { color: #b00020; margin: 1rem 0; }
.reports { width: 100%; border-collapse: collapse; font-size: 0.95rem; }
.reports th, .reports td { border: 1px solid #e9ecef; padding: 0.5rem 0.6rem; vertical-align: middle; }
.reports th { background: #f8f9fa; text-align: left; }
.reports .message { max-width: 520px; white-space: pre-wrap; }
.empty { color: #6c757d; }

.controls { display:flex; gap:0.5rem; align-items:center; margin-bottom:0.75rem; }
.controls input {
  padding:0.35rem;
  flex:1;
  min-width: 200px;
}
.controls select { padding:0.35rem; }
  .reports td.actions { text-align: center; vertical-align: middle; white-space: nowrap; }
  .actions .action-buttons { display: inline-flex; gap: 0.5rem; align-items: center; justify-content: center; }
  /* Match User Management action icon sizes */
  .btn-icon {
    width: 32px;
    height: 32px;
    padding: 0;
    border-radius: 4px;
    border: 1px solid transparent;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
    cursor: pointer;
    transition: all 0.2s ease;
  }
  .btn-icon:hover:not(:disabled) { transform: translateY(-1px); box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
  .btn-icon:disabled { opacity: 0.5; cursor: not-allowed; }
  /* Modal content element spacing */
  .modal-body label { display:block; margin:0.5rem 0; }
  .modal-body textarea { width:100%; min-height:100px; }
</style>
