<template>
  <section class="admin-page">
    <h1>Bugs</h1>
    <p class="muted">User-submitted bugs from the floating widget.</p>

    <div v-if="loading" class="loading">Loading…</div>
    <div v-else>
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
          </tr>
        </tbody>
      </table>
      <div v-else class="empty">No bugs reported yet.</div>
    </div>
  </section>
</template>

<script>
export default {
  name: 'AdminBugs',
  data() {
    return { loading: false, error: '', reports: [] };
  },
  created() {
    this.load();
  },
  methods: {
    async load() {
      this.loading = true; this.error = ''; this.reports = [];
      try {
        const res = await fetch('/api/feedback');
        if (!res.ok) throw new Error('Failed to load bug reports');
        const all = await res.json();
        // Filter to only bug-type
        this.reports = (Array.isArray(all) ? all : []).filter(r => (r.report_type || '').toLowerCase() === 'bug');
      } catch (e) {
        this.error = e.message || 'Error loading bugs';
      } finally {
        this.loading = false;
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
.muted { color: #6c757d; margin-bottom: 1rem; }
.loading { color: #205493; }
.error { color: #b00020; margin: 1rem 0; }
.reports { width: 100%; border-collapse: collapse; font-size: 0.95rem; }
.reports th, .reports td { border: 1px solid #e9ecef; padding: 0.5rem 0.6rem; vertical-align: top; }
.reports th { background: #f8f9fa; text-align: left; }
.reports .message { max-width: 520px; white-space: pre-wrap; }
.empty { color: #6c757d; }
</style>
