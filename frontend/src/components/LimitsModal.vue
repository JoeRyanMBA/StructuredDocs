<template>
  <teleport to="body">
    <div v-if="show" class="modal-backdrop" @click.self="$emit('close')">
      <div class="limits-modal" role="dialog" aria-modal="true" aria-labelledby="limits-title">
        <div class="limits-modal-header">
          <h5 id="limits-title"><i class="bi bi-sliders me-2"></i>System Limits</h5>
          <button class="btn-close" @click="$emit('close')" aria-label="Close"></button>
        </div>

        <div class="limits-modal-body">
          <p class="text-muted small mb-3">
            Changes take effect immediately — no restart required.
          </p>

          <div v-if="loadError" class="alert alert-danger py-2 small">{{ loadError }}</div>
          <div v-if="saveSuccess" class="alert alert-success py-2 small">Settings saved successfully.</div>
          <div v-if="saveError" class="alert alert-danger py-2 small">{{ saveError }}</div>

          <div v-if="loading" class="text-center py-3">
            <div class="spinner-border spinner-border-sm" role="status"></div>
          </div>

          <table v-else class="table table-sm limits-table">
            <thead>
              <tr>
                <th>Setting</th>
                <th style="width:170px">Value</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="s in settings" :key="s.key">
                <td>
                  <div class="fw-semibold small">{{ labelFor(s.key) }}</div>
                  <div class="text-muted" style="font-size:0.78rem">{{ s.description }}</div>
                  <div v-if="s.updated_at" class="text-muted" style="font-size:0.72rem">
                    Last changed: {{ formatDate(s.updated_at) }}
                  </div>
                </td>
                <td>
                  <input
                    v-model="edits[s.key]"
                    type="text"
                    class="form-control form-control-sm"
                    :placeholder="s.value"
                    :aria-label="s.description"
                  />
                  <div v-if="hints[s.key]" class="text-muted mt-1" style="font-size:0.72rem">{{ hints[s.key] }}</div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="limits-modal-footer">
          <button class="btn btn-sm btn-outline-secondary" @click="$emit('close')">Cancel</button>
          <button class="btn btn-sm btn-primary ms-2" :disabled="saving || loading" @click="save">
            <span v-if="saving"><span class="spinner-border spinner-border-sm me-1"></span>Saving…</span>
            <span v-else>Save changes</span>
          </button>
        </div>
      </div>
    </div>
  </teleport>
</template>

<script>
import axios from 'axios';

const LABELS = {
  max_upload_size_mb:         'Max upload size (MB)',
  import_rate_limit:          'Import rate limit',
  review_token_rate_limit:    'Review token generation limit',
  review_feedback_rate_limit: 'Review feedback submission limit',
};

const HINTS = {
  max_upload_size_mb:         'Integer, e.g. 20  (applies to Word / HTML file uploads)',
  import_rate_limit:          'Flask-Limiter format, e.g. "20 per hour" or "5 per minute"',
  review_token_rate_limit:    'e.g. "10 per hour"',
  review_feedback_rate_limit: 'e.g. "30 per hour"',
};

export default {
  name: 'LimitsModal',
  props: {
    show: { type: Boolean, default: false },
  },
  emits: ['close'],
  data() {
    return {
      settings: [],
      edits: {},
      loading: false,
      saving: false,
      loadError: null,
      saveError: null,
      saveSuccess: false,
    };
  },
  computed: {
    hints() { return HINTS; },
  },
  watch: {
    show(val) {
      if (val) this.load();
    },
  },
  methods: {
    labelFor(key) { return LABELS[key] || key; },
    formatDate(iso) {
      if (!iso) return '';
      return new Date(iso).toLocaleString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
    },
    async load() {
      this.loading = true;
      this.loadError = null;
      this.saveSuccess = false;
      this.saveError = null;
      try {
        const { data } = await axios.get('/api/admin/settings');
        this.settings = data;
        this.edits = Object.fromEntries(data.map(s => [s.key, s.value]));
      } catch (err) {
        this.loadError = err.response?.data?.error || 'Failed to load settings.';
      } finally {
        this.loading = false;
      }
    },
    async save() {
      this.saving = true;
      this.saveError = null;
      this.saveSuccess = false;
      try {
        const payload = Object.entries(this.edits).map(([key, value]) => ({ key, value }));
        const { data } = await axios.put('/api/admin/settings', payload);
        if (data.errors?.length) {
          this.saveError = data.errors.join('; ');
        } else {
          this.saveSuccess = true;
          // Refresh to pick up server-formatted values
          await this.load();
        }
      } catch (err) {
        this.saveError = err.response?.data?.error || 'Failed to save settings.';
      } finally {
        this.saving = false;
      }
    },
  },
};
</script>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  z-index: 1050;
  display: flex;
  align-items: center;
  justify-content: center;
}
.limits-modal {
  background: #fff;
  border-radius: 8px;
  width: 600px;
  max-width: 95vw;
  max-height: 85vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.18);
}
.limits-modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem 0.75rem;
  border-bottom: 1px solid #e5e7eb;
}
.limits-modal-header h5 {
  margin: 0;
  font-size: 1.05rem;
}
.limits-modal-body {
  padding: 1rem 1.25rem;
  overflow-y: auto;
  flex: 1;
}
.limits-table th {
  font-size: 0.8rem;
  color: #6b7280;
  font-weight: 600;
}
.limits-modal-footer {
  padding: 0.75rem 1.25rem;
  border-top: 1px solid #e5e7eb;
  display: flex;
  justify-content: flex-end;
}
</style>
