<template>
  <div class="import-review-view">
    <div v-if="loading" class="loading">Loading…</div>
    <div v-else-if="error" class="error-banner">{{ error }}</div>

    <div v-else>
      <!-- Header -->
      <div class="review-header">
        <div>
          <h2>Review Import <HelpIcon feature="import.review" /></h2>
          <p class="filename">{{ doc.filename }}</p>
        </div>
        <span class="status-badge" :class="doc.review_step">
          {{ stepLabel }}
        </span>
      </div>

      <!-- Already committed -->
      <div v-if="doc.review_step === 'final_approved'" class="completed-banner">
        ✅ This import has been committed successfully.
        <router-link :to="{ name: 'ImportHistory' }">Back to history</router-link>
      </div>

      <template v-else>
        <!-- No items: offer delete -->
        <div v-if="!doc.items || doc.items.length === 0" class="no-items-warning">
          <strong>No content items found.</strong>
          The original file may not have contained recognizable headings, or parsing failed.
          You can delete this import and try uploading again.
          <div class="actions" style="margin-top:1rem">
            <button @click="deleteImport" class="btn-danger">Delete Import</button>
            <router-link :to="{ name: 'ImportHistory' }" class="btn-secondary-link">Cancel</router-link>
          </div>
        </div>

        <template v-else>
          <!-- Collection selector -->
          <div class="collection-selector">
            <label for="collection-select">
              Add topics to a collection <span class="optional">(optional)</span>
            </label>
            <select id="collection-select" v-model="selectedCollectionId" class="collection-select">
              <option value="">— No collection (create as unassigned topics) —</option>
              <optgroup v-for="group in collectionGroups" :key="group.project" :label="group.project">
                <option v-for="col in group.collections" :key="col.id" :value="col.id">
                  {{ col.name }}
                </option>
              </optgroup>
            </select>
          </div>

          <!-- Topics table -->
          <div class="topics-count">{{ doc.items.length }} topic{{ doc.items.length !== 1 ? 's' : '' }} to import</div>

          <table class="items-table">
            <thead>
              <tr><th>#</th><th>Title</th><th>Content preview</th></tr>
            </thead>
            <tbody>
              <tr v-for="(item, idx) in doc.items" :key="item.id">
                <td class="order-cell">{{ idx + 1 }}</td>
                <td><input v-model="item.title" class="title-input" placeholder="Title" /></td>
                <td class="preview-cell">{{ truncate(item.content, 120) }}</td>
              </tr>
            </tbody>
          </table>

          <!-- Actions -->
          <div class="actions">
            <button
              @click="commitImport"
              :disabled="committing"
              class="btn-primary"
            >
              {{ committing ? 'Committing…' : 'Commit Import' }}
            </button>
            <button @click="rejectImport" :disabled="committing" class="btn-danger">Reject</button>
            <button @click="deleteImport" :disabled="committing" class="btn-secondary">Delete</button>
          </div>
        </template>
      </template>
    </div>
  </div>
</template>

<script>
import HelpIcon from '@/components/HelpIcon.vue'

export default {
  name: 'ImportReviewView',
  components: { HelpIcon },

  props: {
    id: { type: [String, Number], required: true }
  },

  data() {
    return {
      doc: null,
      loading: false,
      error: null,
      committing: false,
      collections: [],
      selectedCollectionId: ''
    }
  },

  computed: {
    stepLabel() {
      const labels = { pending: 'Pending Review', sme_approved: 'Approved', final_approved: 'Committed' }
      return labels[this.doc?.review_step] || this.doc?.review_step || ''
    },
    // Group collections by project name for the dropdown
    collectionGroups() {
      const groups = {}
      const flatten = (cols) => {
        for (const col of cols) {
          const project = col.projectName || 'No Project'
          if (!groups[project]) groups[project] = []
          groups[project].push({ id: col.id, name: col.name })
          if (col.children?.length) flatten(col.children)
        }
      }
      flatten(this.collections)
      return Object.entries(groups).map(([project, collections]) => ({ project, collections }))
    }
  },

  created() {
    this.fetchImport()
    this.fetchCollections()
  },

  methods: {
    async fetchImport() {
      this.loading = true
      this.error = null
      try {
        const res = await fetch(`/api/import/staging/${this.id}`)
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        this.doc = await res.json()
      } catch (err) {
        this.error = `Failed to load import: ${err.message}`
      } finally {
        this.loading = false
      }
    },

    async fetchCollections() {
      try {
        const res = await fetch('/api/collections')
        if (res.ok) this.collections = await res.json()
      } catch { /* non-fatal */ }
    },

    truncate(text, len) {
      if (!text) return '(no content)'
      const plain = text.replace(/<[^>]+>/g, ' ').trim()
      return plain.length > len ? plain.slice(0, len) + '…' : plain
    },

    async commitImport() {
      this.committing = true
      this.error = null
      try {
        const res = await fetch(`/api/import/staging/${this.id}/commit`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ collection_id: this.selectedCollectionId || null })
        })
        if (!res.ok) {
          const body = await res.json().catch(() => ({}))
          throw new Error(body.error || `HTTP ${res.status}`)
        }
        const result = await res.json()
        const dest = this.selectedCollectionId
          ? ` into the selected collection`
          : ` as unassigned topics`
        this.$router.push({ name: 'ImportHistory', query: { success: `${result.topics_created} topics committed${dest}` } })
      } catch (err) {
        this.error = `Commit failed: ${err.message}`
      } finally {
        this.committing = false
      }
    },

    async rejectImport() {
      if (!confirm('Reject this import? It will be marked as rejected but not deleted.')) return
      try {
        const res = await fetch(`/api/import/staging/${this.id}/reject`, { method: 'POST' })
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        this.$router.push({ name: 'ImportHistory' })
      } catch (err) {
        this.error = `Reject failed: ${err.message}`
      }
    },

    async deleteImport() {
      if (!confirm('Permanently delete this import document? This cannot be undone.')) return
      try {
        const res = await fetch(`/api/import/staging/${this.id}`, { method: 'DELETE' })
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        this.$router.push({ name: 'ImportHistory' })
      } catch (err) {
        this.error = `Delete failed: ${err.message}`
      }
    }
  }
}
</script>

<style scoped>
.import-review-view { padding: 2rem; background: var(--bg-white); }

.review-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.5rem;
}
.review-header h2 { margin: 0 0 0.25rem; color: var(--primary-deep-teal); }
.filename { margin: 0; color: var(--text-secondary-cool-gray); font-size: 0.9rem; }

.status-badge {
  padding: 0.3rem 0.75rem;
  border-radius: 999px;
  font-size: 0.8rem;
  font-weight: 600;
}
.status-badge.pending { background: var(--extended-warm-taupe); color: var(--warning-amber); }
.status-badge.sme_approved { background: var(--extended-cool-mint); color: var(--success-dark-green); }
.status-badge.final_approved { background: var(--extended-sky-blue); color: var(--primary-deep-teal); }

.completed-banner {
  background: var(--extended-cool-mint);
  border-left: 4px solid var(--success-mint-green);
  padding: 1rem 1.5rem;
  border-radius: 4px;
  color: var(--primary-deep-teal);
  font-weight: 500;
  display: flex;
  gap: 1rem;
  align-items: center;
}

.error-banner {
  background: #fff0f0;
  border-left: 4px solid var(--error-coral-red);
  padding: 1rem;
  color: var(--error-coral-red);
  margin-bottom: 1rem;
  border-radius: 4px;
}

.no-items-warning {
  background: var(--extended-warm-taupe);
  border-left: 4px solid var(--warning-amber);
  padding: 1rem 1.5rem;
  border-radius: 4px;
  color: var(--text-primary-dark-navy);
}

.collection-selector {
  margin-bottom: 1.25rem;
}
.collection-selector label {
  display: block;
  font-weight: 600;
  margin-bottom: 0.4rem;
  color: var(--text-primary-dark-navy);
}
.optional { font-weight: 400; color: var(--text-secondary-cool-gray); font-size: 0.85rem; }
.collection-select {
  width: 100%;
  max-width: 480px;
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--border-gray);
  border-radius: 4px;
  font-size: 0.95rem;
}

.topics-count {
  font-size: 0.9rem;
  color: var(--text-secondary-cool-gray);
  margin-bottom: 0.75rem;
}

.items-table { width: 100%; border-collapse: collapse; margin-bottom: 1.5rem; font-size: 0.9rem; }
.items-table th, .items-table td { border: 1px solid var(--border-gray); padding: 0.5rem 0.75rem; }
.items-table th { background: var(--bg-light-gray); font-weight: 600; text-align: left; }
.order-cell { width: 3rem; text-align: center; color: var(--text-secondary-cool-gray); }
.title-input { width: 100%; border: none; padding: 0.2rem; font-size: 0.9rem; background: transparent; }
.title-input:focus { outline: 1px solid var(--primary-deep-teal); border-radius: 2px; }
.preview-cell { color: var(--text-secondary-cool-gray); font-size: 0.85rem; max-width: 400px; }

.actions { display: flex; gap: 0.75rem; align-items: center; flex-wrap: wrap; }
.btn-primary {
  padding: 0.6rem 1.4rem; border: none; background: var(--primary-deep-teal);
  color: #fff; cursor: pointer; border-radius: 4px; font-weight: 600;
}
.btn-primary:hover:not(:disabled) { background: var(--primary-teal-hover, #1a6b6b); }
.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-danger {
  padding: 0.6rem 1.4rem; border: none; background: var(--error-coral-red);
  color: #fff; cursor: pointer; border-radius: 4px;
}
.btn-danger:hover:not(:disabled) { background: #c0392b; }
.btn-danger:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-secondary {
  padding: 0.6rem 1.4rem; border: 1px solid var(--border-gray); background: #fff;
  color: var(--text-primary-dark-navy); cursor: pointer; border-radius: 4px;
}
.btn-secondary:hover:not(:disabled) { background: var(--bg-light-gray); }
.btn-secondary-link {
  padding: 0.6rem 1rem; color: var(--text-secondary-cool-gray); text-decoration: none; font-size: 0.9rem;
}
.loading { font-style: italic; color: var(--text-secondary-cool-gray); }
</style>