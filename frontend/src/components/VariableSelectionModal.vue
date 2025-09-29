<template>
  <div v-if="show" class="modal-overlay" @click="closeModal">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h3>Configure Variables for Publishing</h3>
        <button class="btn-close" @click="closeModal">&times;</button>
      </div>
      
      <div class="modal-body">
        <p class="modal-description">
          This collection contains variables that need to be configured before publishing.
          Please select values for each variable below:
        </p>
        
        <div v-if="loading" class="loading-state">
          <p>Loading variable configuration...</p>
        </div>
        
        <div v-else-if="variablesInfo && variablesInfo.length > 0" class="variables-list">
          <div class="variables-toolbar">
            <button class="btn btn-tertiary btn-xs" @click="resetToDefaults" :disabled="saving || previewing">Reset Defaults</button>
            <button class="btn btn-tertiary btn-xs" @click="toggleShowResolved">{{ showResolved ? 'Hide Resolved' : 'Show Resolved' }}</button>
            <button class="btn btn-tertiary btn-xs" @click="toggleFullPreview" :disabled="previewing || (!previewResult)">
              {{ fullPreview ? 'Compact Preview' : 'Full Topic Preview' }}
            </button>
          </div>
          <div v-for="variable in filteredVariables" :key="variable.id" class="variable-item">
            <div class="variable-header">
              <h4>{{ variable.name }}</h4>
            <span class="variable-slug">{{ variable.slug }}</span>
            <span class="badge" :class="variable.is_resolved ? 'badge-resolved':'badge-unresolved'">{{ variable.is_resolved ? 'Resolved':'Unresolved' }}</span>
            </div>
            
            <p v-if="variable.description" class="variable-description">
              {{ variable.description }}
            </p>
            
            <div class="variable-values">
              <label class="values-label">Select value:</label>
              <select 
                v-model="selections[variable.id]" 
                :class="{ 'has-error': !selections[variable.id] }"
                class="value-select">
                <option value="">Choose a value...</option>
                <option 
                  v-for="value in variable.values" 
                  :key="value.id" 
                  :value="value.id">
                  {{ value.value }}{{ value.is_default ? ' (default)' : '' }}
                </option>
              </select>
            </div>
          </div>
        </div>
        
        <div v-else class="no-variables">
          <p>No variables found to configure.</p>
        </div>

        <!-- Inline Preview Panel -->
        <div v-if="previewResult" class="preview-panel" :class="{ open: showPreviewPanel }">
          <div class="preview-header" @click="togglePreviewPanel()">
            <h4 class="preview-title">
              <span v-if="!showPreviewPanel">▶</span>
              <span v-else>▼</span>
              Preview ({{ previewResult.topics?.length || 0 }} topic{{ (previewResult.topics?.length||0)===1?'':'s' }})
            </h4>
            <div class="preview-actions">
              <button class="btn btn-tertiary btn-xs" @click.stop="clearPreview">Clear</button>
              <button class="btn btn-tertiary btn-xs" v-if="showPreviewPanel" @click.stop="expandPreviewLimit" :disabled="previewTopicLimit >= (previewResult.topics?.length||0)">
                Show More
              </button>
            </div>
          </div>
          <transition name="fade">
            <div v-show="showPreviewPanel" class="preview-body">
              <div v-if="previewError" class="preview-error">{{ previewError }}</div>
              <div class="mapping-summary" v-if="previewResult.mapping">
                <h5>Variable Mapping</h5>
                <ul>
                  <li v-for="(val, slug) in previewResult.mapping" :key="slug">
                    <code>{{ slug }}</code>: <strong>{{ val }}</strong>
                  </li>
                </ul>
              </div>
              <div class="preview-topics" v-if="previewResult.topics && previewResult.topics.length">
                <div
                  v-for="t in previewResult.topics.slice(0, previewTopicLimit)"
                  :key="t.id"
                  class="preview-topic"
                >
                  <h5 class="preview-topic-title">{{ t.title }}</h5>
                  <div class="preview-content" v-html="renderSnippet(t.content)"></div>
                </div>
                <div v-if="previewResult.topics.length > previewTopicLimit" class="preview-more">
                  Showing first {{ previewTopicLimit }} topics of {{ previewResult.topics.length }}.
                </div>
              </div>
              <div v-else class="preview-empty">No topics returned in preview.</div>
            </div>
          </transition>
        </div>
      </div>
      
      <div class="modal-footer">
        <div class="left-actions">
          <button class="btn btn-secondary" @click="closeModal" :disabled="saving">Cancel</button>
          <button class="btn btn-tertiary" @click="saveOnly" :disabled="!canPublish || saving">
            {{ saving && saveMode==='save' ? 'Saving...' : 'Save Only' }}
          </button>
          <button class="btn btn-tertiary" @click="previewVariables" :disabled="!canPublish || previewing || saving">
            {{ previewing ? 'Previewing...' : 'Preview' }}
          </button>
        </div>
        <div class="right-actions">
          <button 
            class="btn btn-primary" 
            @click="saveAndPublish" 
            :disabled="!canPublish || saving">
            {{ saving && saveMode==='publish' ? 'Configuring...' : 'Configure & Publish' }}
          </button>
        </div>
      </div>
      <div class="batch-apply-bar" v-if="canPublish">
        <label class="batch-label">Batch apply to collection IDs (comma-separated)</label>
        <div class="batch-row">
          <input v-model="batchApplyTargetIds" class="batch-input" placeholder="e.g., 12,15,27" />
          <button class="btn btn-tertiary" @click="batchApply" :disabled="batchApplying">{{ batchApplying ? 'Applying...' : 'Batch Apply' }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { toast } from '../composables/useToast.js'

export default {
  name: 'VariableSelectionModal',
  props: {
    show: {
      type: Boolean,
      default: false
    },
    collectionId: {
      type: Number,
      required: true
    },
    variablesInfo: {
      type: Array,
      default: () => []
    },
    unresolvedVariables: {
      type: Array,
      default: () => []
    }
  },
  
  data() {
    return {
      loading: false,
      saving: false,
      selections: {},
      previewing: false,
      previewResult: null,
      previewError: null,
      saveMode: null,
      showPreviewPanel: true,
      previewTopicLimit: 5,
      fullPreview: false,
      showResolved: true,
      batchApplyTargetIds: '',
      batchApplying: false
    }
  },
  
  computed: {
    canPublish() {
      // Check if all required variables have selections
      return this.variablesInfo && this.variablesInfo.length > 0 && 
             this.variablesInfo.every(variable => this.selections[variable.id])
    },
    filteredVariables() {
      if (!this.variablesInfo) return []
      if (this.showResolved) return this.variablesInfo
      return this.variablesInfo.filter(v => !v.is_resolved)
    }
  },
  
  watch: {
    show(newValue) {
      if (newValue) {
        this.initializeSelections()
      }
    },
    
    variablesInfo: {
      handler(newValue) {
        if (newValue && newValue.length > 0) {
          this.initializeSelections()
        }
      },
      immediate: true
    }
  },
  
  methods: {
    initializeSelections() {
      const selections = {}
      
      // Initialize with current selections or defaults
      if (this.variablesInfo) {
        this.variablesInfo.forEach(variable => {
          if (variable.current_selection) {
            selections[variable.id] = variable.current_selection.id
          } else {
            // Try to find default value
            const defaultValue = variable.values.find(v => v.is_default)
            if (defaultValue) {
              selections[variable.id] = defaultValue.id
            }
          }
        })
      }
      
      this.selections = selections
    },
    
    async saveAndPublish() {
      this.saveMode = 'publish'
      if (!this.canPublish) {
        toast.error('Please select values for all variables')
        return
      }
      
      this.saving = true
      
      try {
        // Prepare variable selections for API
        const variableSelections = Object.entries(this.selections).map(([variableId, valueId]) => ({
          variable_id: parseInt(variableId),
          variable_value_id: parseInt(valueId)
        }))
        
        // Configure variables for the collection
        const configResponse = await fetch(`/api/variables/collections/${this.collectionId}/configure-for-publish`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            variable_selections: variableSelections
          })
        })
        
        if (!configResponse.ok) {
          const errorData = await configResponse.json()
          throw new Error(errorData.error || 'Failed to configure variables')
        }
        
        const configResult = await configResponse.json()
        console.log('Variables configured:', configResult)
        
        if (!configResult.ready_to_publish) {
          throw new Error('Variables configuration incomplete')
        }
        
        toast.success('Variables configured successfully!')
        
        // Emit success event so parent can proceed with publishing
        this.$emit('variables-configured', {
          success: true,
          variableSelections: variableSelections
        })
        
        this.closeModal()
        
      } catch (error) {
        console.error('Error configuring variables:', error)
        toast.error(`Error configuring variables: ${error.message}`)
      } finally {
        this.saving = false
      }
    },
    async saveOnly() {
      this.saveMode = 'save'
      if (!this.canPublish) return
      this.saving = true
      try {
        const variableSelections = Object.entries(this.selections).map(([variableId, valueId]) => ({
          variable_id: parseInt(variableId),
          variable_value_id: parseInt(valueId)
        }))
        const configResponse = await fetch(`/api/variables/collections/${this.collectionId}/configure-for-publish`, {
          method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ variable_selections: variableSelections })
        })
        const data = await configResponse.json()
        if (!configResponse.ok) throw new Error(data.error || 'Failed to save')
        toast.success('Variables saved')
      } catch(e) {
        toast.error(e.message)
      } finally {
        this.saving = false
        this.saveMode = null
      }
    },
    async previewVariables() {
      if (!this.canPublish) return
      this.previewing = true
      this.previewError = null
      try {
        // Build a slug:value map for preview
        const slugMap = {}
        this.variablesInfo.forEach(v => {
          const sel = this.selections[v.id]
          if (sel) {
            const valObj = v.values.find(val => val.id === sel)
            if (valObj) slugMap[v.slug] = valObj.value
          }
        })
        const resp = await fetch(`/api/variables/collections/${this.collectionId}/preview`, {
          method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ map: slugMap })
        })
        const data = await resp.json()
        if (!resp.ok) throw new Error(data.error || 'Preview failed')
        this.previewResult = data
        this.showPreviewPanel = true
        toast.success('Preview generated')
      } catch(e) {
        this.previewError = e.message
        toast.error(e.message)
      } finally {
        this.previewing = false
      }
    },
    togglePreviewPanel() { this.showPreviewPanel = !this.showPreviewPanel },
    clearPreview() { this.previewResult = null; this.previewError = null },
    expandPreviewLimit() { this.previewTopicLimit = Math.min(this.previewTopicLimit + 5, (this.previewResult?.topics?.length||0)) },
    renderSnippet(html) {
      if (!html) return '<em>(empty)</em>'
      // Basic sanitization & truncation (no external lib)
      const div = document.createElement('div')
      div.innerHTML = html
      let text = div.textContent || div.innerText || ''
      if (text.length > 400) text = text.slice(0, 400) + '…'
      // Re-escape for safe HTML insertion (very naive)
      const esc = text.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
      return esc.replace(/\n/g,'<br>')
    },
    toggleFullPreview() {
      this.fullPreview = !this.fullPreview
      if (this.fullPreview && this.previewResult) {
        this.previewTopicLimit = this.previewResult.topics?.length || 0
      } else if (!this.fullPreview) {
        this.previewTopicLimit = 5
      }
    },
    resetToDefaults() {
      this.variablesInfo.forEach(v => {
        const def = v.values.find(val => val.is_default)
        if (def) this.selections[v.id] = def.id
      })
    },
    toggleShowResolved() { this.showResolved = !this.showResolved },
    async batchApply() {
      if (!this.canPublish) return
      const ids = this.batchApplyTargetIds.split(',').map(s=>parseInt(s.trim())).filter(n=>!isNaN(n))
      if (!ids.length) { toast.error('Enter collection IDs first'); return }
      this.batchApplying = true
      try {
        const variableSelections = Object.entries(this.selections).map(([variableId, valueId]) => ({ variable_id: parseInt(variableId), variable_value_id: parseInt(valueId) }))
        const resp = await fetch('/api/variables/collections/batch-configure', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ collection_ids: ids, variable_selections: variableSelections }) })
        const data = await resp.json()
        if (!resp.ok) throw new Error(data.error || 'Batch apply failed')
        toast.success(`Applied to ${data.collections.length} collections`)
      } catch(e) {
        toast.error(e.message)
      } finally { this.batchApplying = false }
    },
    
    closeModal() {
      this.$emit('close')
    }
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 600px;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h3 {
  margin: 0;
  color: #1f2937;
  font-size: 1.25rem;
  font-weight: 600;
}

.btn-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #6b7280;
  cursor: pointer;
  padding: 0;
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-close:hover {
  color: #374151;
}

.modal-body {
  padding: 1.5rem;
}

.modal-description {
  color: #6b7280;
  margin-bottom: 1.5rem;
  line-height: 1.5;
}

.loading-state {
  text-align: center;
  padding: 2rem;
  color: #6b7280;
}

.variables-list {
  space-y: 1.5rem;
}

.variable-item {
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  padding: 1rem;
  margin-bottom: 1rem;
}

.variable-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.variable-header h4 {
  margin: 0;
  color: #1f2937;
  font-size: 1rem;
  font-weight: 600;
}

.variable-slug {
  background: #f3f4f6;
  color: #6b7280;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-family: monospace;
  font-size: 0.875rem;
}

.variable-description {
  color: #6b7280;
  font-size: 0.875rem;
  margin-bottom: 1rem;
  line-height: 1.4;
}

.variable-values {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.values-label {
  font-weight: 500;
  color: #374151;
  font-size: 0.875rem;
}

.value-select {
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  background: white;
  font-size: 0.875rem;
}

.value-select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.value-select.has-error {
  border-color: #ef4444;
}

.no-variables {
  text-align: center;
  padding: 2rem;
  color: #6b7280;
}

.modal-footer {
  display: flex;
  justify-content: space-between;
  gap: 0.75rem;
  padding: 1.5rem;
  border-top: 1px solid #e5e7eb;
  background: #f9fafb;
}

.left-actions, .right-actions { display: flex; gap: 0.5rem; align-items: center; }

.btn-tertiary {
  background: #eef2f7;
  color: #374151;
}
.btn-tertiary:hover:not(:disabled) { background: #e2e8f0; }

.btn {
  padding: 0.5rem 1rem;
  border-radius: 4px;
  font-weight: 500;
  cursor: pointer;
  border: 1px solid transparent;
  transition: all 0.2s;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-secondary {
  background: white;
  border-color: #d1d5db;
  color: #374151;
}

.btn-secondary:hover:not(:disabled) {
  background: #f9fafb;
}

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #2563eb;
}

/* Preview panel styling */
.preview-panel { margin-top: 1.25rem; border: 1px solid #e5e7eb; border-radius: 6px; background: #fdfdfd; }
.preview-header { display: flex; justify-content: space-between; align-items: center; padding: 0.6rem 0.9rem; cursor: pointer; background:#f3f4f6; border-bottom:1px solid #e5e7eb; }
.preview-title { font-size: 0.95rem; font-weight:600; margin:0; display:flex; gap:0.5rem; align-items:center; }
.preview-actions { display:flex; gap:0.4rem; }
.btn-xs { padding:0.25rem 0.5rem; font-size:0.7rem; }
.preview-body { padding: 0.85rem 0.9rem 1rem; max-height: 300px; overflow-y:auto; }
.preview-topic { border:1px solid #e5e7eb; border-radius:4px; padding:0.5rem 0.6rem; margin-bottom:0.6rem; background:white; }
.preview-topic-title { margin:0 0 0.25rem 0; font-size:0.85rem; font-weight:600; color:#1f2937; }
.preview-content { font-size:0.75rem; line-height:1.3; color:#374151; white-space:normal; word-break:break-word; }
.preview-more { font-size:0.75rem; color:#6b7280; text-align:center; }
.mapping-summary { margin-bottom:0.75rem; }
.mapping-summary h5 { margin:0 0 0.4rem 0; font-size:0.8rem; font-weight:600; }
.mapping-summary ul { list-style:none; padding:0; margin:0; column-count:2; column-gap:1.25rem; }
.mapping-summary li { font-size:0.7rem; margin-bottom:0.25rem; }
.preview-error { color:#b91c1c; font-size:0.75rem; margin-bottom:0.75rem; }
.preview-empty { font-size:0.75rem; color:#6b7280; }
.fade-enter-active, .fade-leave-active { transition: opacity .2s; }
.fade-enter-from, .fade-leave-to { opacity:0; }

/* Enhancements */
.variables-toolbar { display:flex; gap:0.4rem; flex-wrap:wrap; margin-bottom:0.75rem; }
.badge { font-size:0.6rem; padding:0.2rem 0.4rem; border-radius:4px; text-transform:uppercase; letter-spacing:0.5px; }
.badge-resolved { background:#d1fae5; color:#065f46; }
.badge-unresolved { background:#fee2e2; color:#991b1b; }
.batch-apply-bar { border-top:1px solid #e5e7eb; background:#f9fafb; padding:0.75rem 1rem 1rem; }
.batch-label { display:block; font-size:0.65rem; font-weight:600; text-transform:uppercase; margin-bottom:0.25rem; color:#374151; }
.batch-row { display:flex; gap:0.5rem; }
.batch-input { flex:1; padding:0.4rem 0.5rem; border:1px solid #d1d5db; border-radius:4px; font-size:0.75rem; }
</style>