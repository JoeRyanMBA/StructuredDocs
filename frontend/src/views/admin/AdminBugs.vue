<template>
  <section class="admin-page">
    <h1>Bugs</h1>
    <p class="muted">User-submitted bugs from the floating widget.</p>

    <div v-if="loading" class="loading">Loading…</div>
    <div v-else>
      <div class="controls">
        <input v-model="filters.q" placeholder="Search message..." @input="load" />
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
              <button @click="openEdit(r)">Edit</button>
              <button @click="archive(r)">Archive</button>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-else class="empty">No bugs reported yet.</div>
    </div>

    <!-- Edit modal -->
    <div v-if="editing" class="modal">
      <div class="modal-body">
        <h3>Edit Bug #{{ editItem.id }}</h3>
        <label>Component <input v-model="editItem.component" /></label>
        <label>Contact <input v-model="editItem.user_contact" /></label>
        <label>Status <select v-model="editItem.status"><option>new</option><option>in_progress</option><option>resolved</option><option>archived</option></select></label>
        <label>Message <textarea v-model="editItem.message"></textarea></label>
        <div class="modal-actions">
          <button @click="saveEdit">Save</button>
          <button @click="closeEdit">Cancel</button>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
export default {
  name: 'AdminBugs',
  data() {
  return { loading: false, error: '', reports: [], filters: { q: '', status: '' }, editing: false, editItem: null };
  },
  created() {
    this.load();
  },
  methods: {
    async load() {
      this.loading = true; this.error = ''; this.reports = [];
      try {
        const params = new URLSearchParams();
        params.append('type', 'bug');
        if (this.filters.q) params.append('q', this.filters.q);
        if (this.filters.status) params.append('status', this.filters.status);
        const res = await fetch('/api/feedback?' + params.toString());
        if (!res.ok) throw new Error('Failed to load bug reports');
        this.reports = await res.json();
      } catch (e) {
        this.error = e.message || 'Error loading bugs';
      } finally {
        this.loading = false;
      }
    },
    resetFilters() { this.filters = { q: '', status: '' }; this.load(); },
    openEdit(item) { this.editing = true; this.editItem = Object.assign({}, item); },
    closeEdit() { this.editing = false; this.editItem = null; },
    async saveEdit() {
      try {
        let res = await fetch('/api/feedback/' + this.editItem.id, {
          method: 'PATCH', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(this.editItem)
        });
        if (res.status === 405) {
          res = await fetch('/api/feedback/' + this.editItem.id + '/update', {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(this.editItem)
          });
        }
        if (!res.ok) throw new Error('Failed to save');
        const updated = await res.json();
        const idx = this.reports.findIndex(r => r.id === updated.id);
        if (idx !== -1) this.reports.splice(idx, 1, updated);
        this.closeEdit();
      } catch (e) { this.error = e.message || 'Error saving bug'; }
    },
    async archive(item) {
      if (!confirm('Archive this bug report?')) return;
      try {
        let res = await fetch('/api/feedback/' + item.id, { method: 'DELETE' });
        if (res.status === 405) {
          res = await fetch('/api/feedback/' + item.id + '/archive', { method: 'POST' });
        }
        if (!res.ok) throw new Error('Failed to archive');
        this.reports = this.reports.filter(r => r.id !== item.id);
      } catch (e) { this.error = e.message || 'Error archiving'; }
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
.muted { color: #6c757d; margin-bottom: 1rem; }
.loading { color: #205493; }
.error { color: #b00020; margin: 1rem 0; }
.reports { width: 100%; border-collapse: collapse; font-size: 0.95rem; }
.reports th, .reports td { border: 1px solid #e9ecef; padding: 0.5rem 0.6rem; vertical-align: top; }
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
.actions button { margin-right:0.4rem; }
.modal { position:fixed; inset:0; background:rgba(0,0,0,0.4); display:flex; align-items:center; justify-content:center; }
.modal-body { background:white; padding:1rem; width:640px; max-width:95%; border-radius:6px; }
.modal-body label { display:block; margin:0.5rem 0; }
.modal-body textarea { width:100%; min-height:100px; }
.modal-actions { display:flex; gap:0.5rem; justify-content:flex-end; margin-top:0.5rem; }
</style>
