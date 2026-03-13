<template>
  <div class="audit-log-view">
    <div class="audit-header">
      <h2><i class="bi bi-shield-check me-2"></i>Audit Log <HelpIcon feature="admin.audit" /></h2>
      <p class="text-muted">Immutable record of create / update / delete actions on key resources.</p>
    </div>

    <!-- Filters -->
    <div class="audit-filters card mb-3 p-3">
      <div class="row g-2 align-items-end">
        <div class="col-md-3">
          <label class="form-label small">Resource type</label>
          <select v-model="filters.resource_type" class="form-select form-select-sm" @change="loadLogs(1)">
            <option value="">All</option>
            <option value="topic">Topic</option>
            <option value="collection">Collection</option>
            <option value="project">Project</option>
            <option value="publication">Publication</option>
          </select>
        </div>
        <div class="col-md-3">
          <label class="form-label small">Action</label>
          <select v-model="filters.action" class="form-select form-select-sm" @change="loadLogs(1)">
            <option value="">All</option>
            <option value="create">Create</option>
            <option value="update">Update</option>
            <option value="delete">Delete</option>
          </select>
        </div>
        <div class="col-md-3">
          <label class="form-label small">User ID</label>
          <input v-model.number="filters.user_id" type="number" class="form-control form-control-sm" placeholder="Any"
                 @keyup.enter="loadLogs(1)" @change="loadLogs(1)" />
        </div>
        <div class="col-md-3">
          <button class="btn btn-sm btn-outline-secondary w-100" @click="clearFilters">
            <i class="bi bi-x-circle me-1"></i>Clear filters
          </button>
        </div>
      </div>
    </div>

    <!-- Error / loading state -->
    <div v-if="error" class="alert alert-danger">{{ error }}</div>
    <div v-if="loading && !entries.length" class="text-center py-4">
      <div class="spinner-border spinner-border-sm" role="status"></div>
      <span class="ms-2">Loading…</span>
    </div>

    <!-- Table -->
    <div v-if="entries.length" class="table-responsive">
      <table class="table table-sm table-hover audit-table">
        <thead class="table-dark">
          <tr>
            <th>Timestamp</th>
            <th>Action</th>
            <th>Resource</th>
            <th>ID</th>
            <th>User</th>
            <th>IP</th>
            <th>Details</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="entry in entries" :key="entry.id">
            <td class="text-nowrap small">{{ formatDate(entry.created_at) }}</td>
            <td>
              <span :class="actionBadge(entry.action)" class="badge">{{ entry.action }}</span>
            </td>
            <td class="small">{{ entry.resource_type }}</td>
            <td class="small text-muted">{{ entry.resource_id ?? '—' }}</td>
            <td class="small">{{ entry.user_id ?? 'system' }}</td>
            <td class="small text-muted">{{ entry.ip_address ?? '—' }}</td>
            <td class="small text-muted details-cell">{{ formatDetails(entry.details) }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-else-if="!loading" class="text-center text-muted py-5">No audit log entries found.</div>

    <!-- Pagination -->
    <div v-if="totalPages > 1" class="d-flex justify-content-between align-items-center mt-3">
      <span class="small text-muted">{{ total }} total entries</span>
      <nav>
        <ul class="pagination pagination-sm mb-0">
          <li class="page-item" :class="{ disabled: page <= 1 }">
            <button class="page-link" @click="loadLogs(page - 1)">‹</button>
          </li>
          <li v-for="p in visiblePages" :key="p" class="page-item" :class="{ active: p === page }">
            <button class="page-link" @click="loadLogs(p)">{{ p }}</button>
          </li>
          <li class="page-item" :class="{ disabled: page >= totalPages }">
            <button class="page-link" @click="loadLogs(page + 1)">›</button>
          </li>
        </ul>
      </nav>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import HelpIcon from '@/components/HelpIcon.vue'

export default {
  name: 'AuditLogView',
  components: { HelpIcon },
  data() {
    return {
      entries: [],
      total: 0,
      page: 1,
      limit: 50,
      totalPages: 1,
      loading: false,
      error: null,
      filters: {
        resource_type: '',
        action: '',
        user_id: null,
      },
    };
  },
  computed: {
    visiblePages() {
      const range = [];
      const start = Math.max(1, this.page - 2);
      const end = Math.min(this.totalPages, this.page + 2);
      for (let i = start; i <= end; i++) range.push(i);
      return range;
    },
  },
  created() {
    this.loadLogs(1);
  },
  methods: {
    async loadLogs(p = 1) {
      this.loading = true;
      this.error = null;
      this.page = p;
      try {
        const params = { page: p, limit: this.limit };
        if (this.filters.resource_type) params.resource_type = this.filters.resource_type;
        if (this.filters.action) params.action = this.filters.action;
        if (this.filters.user_id) params.user_id = this.filters.user_id;

        const { data } = await axios.get('/api/admin/audit-logs', { params });
        this.entries = data.items || [];
        this.total = data.total || 0;
        this.totalPages = data.pages || 1;
      } catch (err) {
        this.error = err.response?.data?.error || 'Failed to load audit logs.';
      } finally {
        this.loading = false;
      }
    },
    clearFilters() {
      this.filters = { resource_type: '', action: '', user_id: null };
      this.loadLogs(1);
    },
    formatDate(iso) {
      if (!iso) return '—';
      const d = new Date(iso);
      return d.toLocaleString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit', second: '2-digit' });
    },
    formatDetails(raw) {
      if (!raw) return '';
      try {
        const obj = typeof raw === 'string' ? JSON.parse(raw) : raw;
        return Object.entries(obj).map(([k, v]) => `${k}: ${v}`).join(' · ');
      } catch {
        return raw;
      }
    },
    actionBadge(action) {
      return {
        create: 'bg-success',
        update: 'bg-primary',
        delete: 'bg-danger',
      }[action] || 'bg-secondary';
    },
  },
};
</script>

<style scoped>
.audit-log-view {
  padding: 1.5rem;
  max-width: 1200px;
  margin: 0 auto;
}
.audit-header h2 {
  font-size: 1.4rem;
  margin-bottom: 0.25rem;
}
.audit-table th, .audit-table td {
  vertical-align: middle;
}
.details-cell {
  max-width: 240px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
