<template>
  <div class="find-replace-page">
    <div class="page-header">
      <h1>🔍 Find &amp; Replace</h1>
      <p class="subtitle">Search and replace text across all user-editable content in the database.</p>
    </div>

    <!-- ── Search Form ─────────────────────────────────────────────────── -->
    <div class="card search-card">
      <div class="form-row">
        <div class="form-col">
          <label class="form-label">Find (regex)</label>
          <input
            v-model="pattern"
            class="form-input"
            placeholder="e.g. \bfoo\b or plain text"
            @keydown.enter="runSearch"
            :class="{ 'input-error': patternError }"
          />
          <span v-if="patternError" class="error-msg">{{ patternError }}</span>
        </div>
        <div class="form-col">
          <label class="form-label">Replace with</label>
          <input
            v-model="replacement"
            class="form-input"
            placeholder="Replacement text (supports $1, $2 groups)"
          />
        </div>
      </div>

      <!-- Flags -->
      <div class="flags-row">
        <label class="flag-toggle">
          <input type="checkbox" v-model="flags.ignoreCase" />
          <span>Case-insensitive</span>
        </label>
        <label class="flag-toggle">
          <input type="checkbox" v-model="flags.multiline" />
          <span>Multiline (^ $ match line boundaries)</span>
        </label>
        <label class="flag-toggle">
          <input type="checkbox" v-model="flags.dotall" />
          <span>Dot matches newline</span>
        </label>
      </div>

      <!-- Scope -->
      <div class="scope-section">
        <div class="scope-header">
          <span class="scope-label">Search in:</span>
          <button class="link-btn" @click="selectAllScope">All</button>
          <span class="scope-sep">·</span>
          <button class="link-btn" @click="clearScope">None</button>
        </div>
        <div class="scope-grid">
          <label v-for="grp in MODEL_GROUPS" :key="grp.label" class="scope-item">
            <input type="checkbox" :value="grp.models" v-model="selectedGroupModels" @change="syncScope(grp)" />
            <span>{{ grp.label }}</span>
          </label>
        </div>
      </div>

      <div class="search-actions">
        <button class="primary-btn" :disabled="searching || !pattern.trim()" @click="runSearch">
          <span v-if="searching">Searching…</span>
          <span v-else>Search</span>
        </button>
        <button v-if="hits.length" class="secondary-btn" @click="resetAll">Clear</button>
      </div>
    </div>

    <!-- ── Results ─────────────────────────────────────────────────────── -->
    <div v-if="searchDone" class="results-section">

      <div v-if="!hits.length" class="no-results">
        No matches found.
      </div>

      <template v-else>
        <div class="results-summary-bar">
          <span class="results-count">
            {{ hits.length }} match{{ hits.length !== 1 ? 'es' : '' }} found
            <span v-if="truncated" class="truncated-warning"> (showing first {{ hits.length }} — refine your pattern to see more)</span>
          </span>
          <div class="results-actions">
            <button class="link-btn" @click="selectAllHits">Select all</button>
            <span class="scope-sep">·</span>
            <button class="link-btn" @click="deselectAllHits">Deselect all</button>
          </div>
        </div>

        <!-- HTML content warning -->
        <div v-if="hasHtmlHits" class="html-warning">
          ⚠️ Some matches are in HTML content fields (e.g. Topic content). Replacement will be applied to the raw HTML — avoid patterns that match inside tag names or attributes.
        </div>

        <!-- Groups -->
        <div v-for="group in groupedHits" :key="group.model" class="result-group">
          <div class="group-header" @click="toggleGroup(group.model)">
            <span class="group-chevron">{{ collapsedGroups.has(group.model) ? '▶' : '▼' }}</span>
            <span class="group-model">{{ friendlyModel(group.model) }}</span>
            <span class="group-count">{{ group.hits.length }} match{{ group.hits.length !== 1 ? 'es' : '' }}</span>
            <div class="group-sel-actions" @click.stop>
              <button class="link-btn small" @click="selectGroup(group.model)">Select all</button>
              <span class="scope-sep">·</span>
              <button class="link-btn small" @click="deselectGroup(group.model)">Deselect</button>
            </div>
          </div>

          <div v-if="!collapsedGroups.has(group.model)" class="group-hits">
            <div
              v-for="hit in group.hits"
              :key="hitKey(hit)"
              class="hit-row"
              :class="{ 'hit-selected': isSelected(hit) }"
            >
              <label class="hit-checkbox">
                <input type="checkbox" :checked="isSelected(hit)" @change="toggleHit(hit)" />
              </label>
              <div class="hit-meta">
                <span class="hit-record-title">{{ hit.record_title }}</span>
                <span class="hit-field-label">{{ hit.field_label }}</span>
                <span v-if="hit.is_html" class="hit-html-badge">HTML</span>
              </div>
              <div class="hit-context">
                <span class="ctx-before">{{ hit.context_before }}</span><span
                  class="ctx-match">{{ hit.match_text }}</span><span
                  class="ctx-after">{{ hit.context_after }}</span>
              </div>
            </div>
          </div>
        </div>
      </template>
    </div>

    <!-- ── Sticky Replace Bar ──────────────────────────────────────────── -->
    <div v-if="selectedHits.size > 0" class="replace-bar">
      <span class="replace-bar-label">{{ selectedHits.size }} match{{ selectedHits.size !== 1 ? 'es' : '' }} selected</span>
      <div class="replace-bar-input">
        <label>Replace with:</label>
        <input v-model="replacement" class="form-input inline-input" placeholder="Replacement text" />
      </div>
      <button class="danger-btn" :disabled="replacing" @click="showConfirm = true">
        {{ replacing ? 'Replacing…' : `Replace ${selectedHits.size} selected` }}
      </button>
    </div>

    <!-- ── Confirm Modal ───────────────────────────────────────────────── -->
    <div v-if="showConfirm" class="modal-overlay" @click.self="showConfirm = false">
      <div class="modal-box">
        <h2>⚠️ Confirm Replace</h2>
        <p>
          You are about to replace <strong>{{ selectedHits.size }}</strong> field value{{ selectedHits.size !== 1 ? 's' : '' }}
          across the database. <strong>This cannot be undone.</strong>
        </p>
        <p>
          Pattern: <code>{{ pattern }}</code><br />
          Replace with: <code>{{ replacement || '(empty string)' }}</code>
        </p>
        <div class="modal-actions">
          <button class="secondary-btn" @click="showConfirm = false">Cancel</button>
          <button class="danger-btn" @click="runReplace">Yes, replace</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { findReplaceSearch, findReplaceExecute } from '@/api/findReplace'
import { toast } from '@/composables/useToast'

const MODEL_GROUPS = [
  { label: 'Topics',          models: ['Topic'] },
  { label: 'Collections',     models: ['Collection'] },
  { label: 'Projects',        models: ['Project'] },
  { label: 'Snippets',        models: ['Snippet'] },
  { label: 'Tasks',           models: ['Task'] },
  { label: 'Milestones',      models: ['ProjectMilestone'] },
  { label: 'Stakeholders',    models: ['Stakeholder', 'ProjectStakeholder'] },
  { label: 'Links',           models: ['Link'] },
  { label: 'Tags',            models: ['Tag'] },
  { label: 'Variables',       models: ['Variable'] },
  { label: 'Publications',    models: ['Publication'] },
  { label: 'Reviews',         models: ['Review', 'ReviewFeedback'] },
  { label: 'Review Sequences',models: ['ReviewSequence', 'ReviewSequenceStep'] },
  { label: 'Help Links',      models: ['HelpLink'] },
  { label: 'Notifications',   models: ['Notification'] },
]

const FRIENDLY_NAMES = {
  Topic: 'Topics', Collection: 'Collections', Project: 'Projects',
  Snippet: 'Snippets', Task: 'Tasks', ProjectMilestone: 'Milestones',
  Stakeholder: 'Stakeholders', ProjectStakeholder: 'Stakeholder Notes',
  Link: 'Links', Tag: 'Tags', Variable: 'Variables',
  Publication: 'Publications', Review: 'Reviews',
  ReviewFeedback: 'Review Feedback', ReviewSequence: 'Review Sequences',
  ReviewSequenceStep: 'Sequence Steps', HelpLink: 'Help Links',
  Notification: 'Notifications',
}

export default {
  name: 'AdminFindReplace',
  data() {
    return {
      MODEL_GROUPS,
      pattern: '',
      replacement: '',
      flags: { ignoreCase: true, multiline: false, dotall: false },
      scope: MODEL_GROUPS.flatMap(g => g.models),
      selectedGroupModels: MODEL_GROUPS.map(g => g.models),

      searching: false,
      searchDone: false,
      hits: [],
      truncated: false,
      patternError: '',

      selectedHits: new Set(),
      collapsedGroups: new Set(),

      replacing: false,
      showConfirm: false,
    }
  },
  computed: {
    groupedHits() {
      const map = {}
      for (const h of this.hits) {
        if (!map[h.model]) map[h.model] = { model: h.model, hits: [] }
        map[h.model].hits.push(h)
      }
      return Object.values(map)
    },
    hasHtmlHits() {
      return this.hits.some(h => h.is_html)
    },
  },
  methods: {
    hitKey(hit) {
      return `${hit.model}:${hit.record_id}:${hit.field}`
    },
    isSelected(hit) {
      return this.selectedHits.has(this.hitKey(hit))
    },
    toggleHit(hit) {
      const key = this.hitKey(hit)
      const next = new Set(this.selectedHits)
      next.has(key) ? next.delete(key) : next.add(key)
      this.selectedHits = next
    },
    selectAllHits() {
      this.selectedHits = new Set(this.hits.map(this.hitKey))
    },
    deselectAllHits() {
      this.selectedHits = new Set()
    },
    selectGroup(model) {
      const next = new Set(this.selectedHits)
      this.hits.filter(h => h.model === model).forEach(h => next.add(this.hitKey(h)))
      this.selectedHits = next
    },
    deselectGroup(model) {
      const next = new Set(this.selectedHits)
      this.hits.filter(h => h.model === model).forEach(h => next.delete(this.hitKey(h)))
      this.selectedHits = next
    },
    toggleGroup(model) {
      const next = new Set(this.collapsedGroups)
      next.has(model) ? next.delete(model) : next.add(model)
      this.collapsedGroups = next
    },
    selectAllScope() {
      this.selectedGroupModels = MODEL_GROUPS.map(g => g.models)
      this.scope = MODEL_GROUPS.flatMap(g => g.models)
    },
    clearScope() {
      this.selectedGroupModels = []
      this.scope = []
    },
    syncScope() {
      this.scope = this.selectedGroupModels.flat()
    },
    friendlyModel(m) {
      return FRIENDLY_NAMES[m] || m
    },
    resetAll() {
      this.hits = []
      this.selectedHits = new Set()
      this.searchDone = false
      this.patternError = ''
      this.truncated = false
    },
    async runSearch() {
      if (!this.pattern.trim()) return
      this.patternError = ''
      this.searching = true
      this.hits = []
      this.selectedHits = new Set()
      this.searchDone = false
      try {
        const res = await findReplaceSearch(
          this.pattern,
          this.replacement,
          this.flags,
          this.scope,
        )
        this.hits = res.hits || []
        this.truncated = res.truncated || false
        this.searchDone = true
      } catch (err) {
        const msg = err?.response?.data?.error || 'Search failed'
        this.patternError = msg
      } finally {
        this.searching = false
      }
    },
    async runReplace() {
      this.showConfirm = false
      this.replacing = true
      const selectedList = this.hits.filter(h => this.selectedHits.has(this.hitKey(h)))
        .map(h => ({ model: h.model, record_id: h.record_id, field: h.field }))
      try {
        const res = await findReplaceExecute(
          this.pattern,
          this.replacement,
          this.flags,
          selectedList,
        )
        const count = res.replaced_count || 0
        const errs = res.errors || []
        if (errs.length) {
          alert(`Replaced ${count} field(s). Errors:\n${errs.join('\n')}`)
        } else {
          toast.success(`Replaced ${count} field value${count !== 1 ? 's' : ''}`)
        }
        // Re-run search to refresh results
        await this.runSearch()
      } catch (err) {
        alert(err?.response?.data?.error || 'Replace failed')
      } finally {
        this.replacing = false
      }
    },
  },
}
</script>

<style scoped>
.find-replace-page { padding: 1.5rem; max-width: 1100px; }

.page-header { margin-bottom: 1.5rem; }
.page-header h1 { font-size: 2.5rem; font-weight: 300; color: var(--primary-deep-teal); margin: 0 0 0.25rem; }
.subtitle { color: #6c757d; margin: 0; }

/* Card */
.card { background: #fff; border: 1px solid #dee2e6; border-radius: 8px; padding: 1.5rem; margin-bottom: 1.5rem; }
.search-card { }

/* Form */
.form-row { display: flex; gap: 1rem; margin-bottom: 1rem; }
.form-col { flex: 1; display: flex; flex-direction: column; gap: 0.35rem; }
.form-label { font-size: 0.85rem; font-weight: 600; color: #495057; }
.form-input { border: 1px solid #ced4da; border-radius: 6px; padding: 0.5rem 0.75rem; font-size: 0.95rem; }
.form-input:focus { outline: none; border-color: var(--primary-deep-teal, #1a6b72); box-shadow: 0 0 0 3px rgba(26,107,114,.15); }
.input-error { border-color: #dc3545 !important; }
.error-msg { font-size: 0.8rem; color: #dc3545; }

/* Flags */
.flags-row { display: flex; gap: 1.5rem; margin-bottom: 1rem; flex-wrap: wrap; }
.flag-toggle { display: flex; align-items: center; gap: 0.4rem; font-size: 0.875rem; cursor: pointer; user-select: none; }
.flag-toggle input { accent-color: var(--primary-deep-teal, #1a6b72); }

/* Scope */
.scope-section { margin-bottom: 1.25rem; }
.scope-header { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem; }
.scope-label { font-size: 0.85rem; font-weight: 600; color: #495057; }
.scope-sep { color: #adb5bd; }
.scope-grid { display: flex; flex-wrap: wrap; gap: 0.5rem 1.25rem; }
.scope-item { display: flex; align-items: center; gap: 0.35rem; font-size: 0.875rem; cursor: pointer; }
.scope-item input { accent-color: var(--primary-deep-teal, #1a6b72); }

/* Search actions */
.search-actions { display: flex; gap: 0.75rem; align-items: center; }

/* Buttons */
.primary-btn {
  background: var(--primary-deep-teal, #1a6b72); color: #fff; border: none;
  border-radius: 6px; padding: 0.5rem 1.25rem; font-size: 0.925rem; cursor: pointer; font-weight: 500;
}
.primary-btn:disabled { opacity: .6; cursor: not-allowed; }
.primary-btn:hover:not(:disabled) { background: #15585e; }
.secondary-btn {
  background: #f8f9fa; color: #495057; border: 1px solid #ced4da;
  border-radius: 6px; padding: 0.5rem 1.25rem; font-size: 0.925rem; cursor: pointer;
}
.secondary-btn:hover { background: #e9ecef; }
.danger-btn {
  background: #dc3545; color: #fff; border: none;
  border-radius: 6px; padding: 0.5rem 1.25rem; font-size: 0.925rem; cursor: pointer; font-weight: 500;
}
.danger-btn:disabled { opacity: .6; cursor: not-allowed; }
.danger-btn:hover:not(:disabled) { background: #b02a37; }
.link-btn { background: none; border: none; color: var(--primary-deep-teal, #1a6b72); font-size: 0.85rem; cursor: pointer; padding: 0; }
.link-btn:hover { text-decoration: underline; }
.link-btn.small { font-size: 0.8rem; }

/* Results */
.results-section { margin-bottom: 5rem; }
.no-results { text-align: center; color: #6c757d; padding: 2rem; }

.results-summary-bar {
  display: flex; align-items: center; justify-content: space-between;
  padding: 0.6rem 0.75rem; background: #f8f9fa; border: 1px solid #dee2e6;
  border-radius: 6px; margin-bottom: 0.75rem; font-size: 0.9rem;
}
.results-count { font-weight: 500; }
.results-actions { display: flex; align-items: center; gap: 0.5rem; }
.truncated-warning { color: #856404; font-size: 0.85rem; }

.html-warning {
  background: #fff3cd; border: 1px solid #ffc107; border-radius: 6px;
  padding: 0.6rem 0.9rem; font-size: 0.875rem; color: #664d03; margin-bottom: 0.75rem;
}

/* Result groups */
.result-group { border: 1px solid #dee2e6; border-radius: 8px; margin-bottom: 0.75rem; overflow: hidden; }

.group-header {
  display: flex; align-items: center; gap: 0.75rem;
  padding: 0.6rem 1rem; background: #f8f9fa;
  cursor: pointer; user-select: none;
}
.group-header:hover { background: #e9ecef; }
.group-chevron { font-size: 0.75rem; color: #6c757d; }
.group-model { font-weight: 600; font-size: 0.9rem; }
.group-count { color: #6c757d; font-size: 0.85rem; }
.group-sel-actions { margin-left: auto; display: flex; align-items: center; gap: 0.35rem; }

.group-hits { }
.hit-row {
  display: flex; align-items: flex-start; gap: 0.75rem;
  padding: 0.6rem 1rem; border-top: 1px solid #f0f0f0;
  transition: background 0.1s;
}
.hit-row:hover { background: #fafafa; }
.hit-selected { background: #e8f4f5 !important; }

.hit-checkbox { padding-top: 0.15rem; flex-shrink: 0; }
.hit-checkbox input { accent-color: var(--primary-deep-teal, #1a6b72); width: 15px; height: 15px; }

.hit-meta {
  display: flex; flex-direction: column; gap: 0.1rem; width: 200px; flex-shrink: 0;
}
.hit-record-title { font-size: 0.85rem; font-weight: 500; color: #212529; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 190px; }
.hit-field-label { font-size: 0.78rem; color: #6c757d; }
.hit-html-badge { display: inline-block; font-size: 0.7rem; background: #e3f2fd; color: #1565c0; border-radius: 3px; padding: 0 4px; align-self: flex-start; }

.hit-context { flex: 1; font-size: 0.875rem; line-height: 1.5; color: #495057; word-break: break-word; }
.ctx-before { color: #6c757d; }
.ctx-match { background: #fff3cd; color: #212529; font-weight: 600; border-radius: 2px; padding: 0 2px; }
.ctx-after { color: #6c757d; }

/* Replace bar */
.replace-bar {
  position: fixed; bottom: 0; left: 0; right: 0; z-index: 100;
  background: #212529; color: #fff;
  display: flex; align-items: center; gap: 1rem; padding: 0.75rem 2rem;
  padding-right: 280px;
  box-shadow: 0 -2px 12px rgba(0,0,0,.25);
}
.replace-bar-label { font-weight: 500; white-space: nowrap; }
.replace-bar-input { display: flex; align-items: center; gap: 0.5rem; flex: 1; font-size: 0.9rem; }
.inline-input { background: #343a40; color: #fff; border: 1px solid #495057; flex: 1; }
.inline-input::placeholder { color: #adb5bd; }
.inline-input:focus { border-color: #80bdff; outline: none; }

/* Confirm modal */
.modal-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,.5); z-index: 200;
  display: flex; align-items: center; justify-content: center;
}
.modal-box {
  background: #fff; border-radius: 10px; padding: 2rem; max-width: 480px; width: 90%;
  box-shadow: 0 8px 32px rgba(0,0,0,.25);
}
.modal-box h2 { margin: 0 0 1rem; font-size: 1.25rem; }
.modal-box p { font-size: 0.925rem; color: #495057; margin-bottom: 0.75rem; }
.modal-box code { background: #f1f3f5; border-radius: 4px; padding: 1px 5px; font-size: 0.875rem; color: #212529; word-break: break-all; }
.modal-actions { display: flex; gap: 0.75rem; justify-content: flex-end; margin-top: 1.5rem; }

@media (max-width: 640px) {
  .form-row { flex-direction: column; }
  .replace-bar { flex-direction: column; align-items: stretch; gap: 0.5rem; padding-right: 2rem; }
  .hit-meta { width: 140px; }
}
</style>
