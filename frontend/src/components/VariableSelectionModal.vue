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
          <div v-for="variable in variablesInfo" :key="variable.id" class="variable-item">
            <div class="variable-header">
              <h4>{{ variable.name }}</h4>
            <span class="variable-slug">{{ variable.slug }}</span>
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
      </div>
      
      <div class="modal-footer">
        <button class="btn btn-secondary" @click="closeModal" :disabled="saving">
          Cancel
        </button>
        <button 
          class="btn btn-primary" 
          @click="saveAndPublish" 
          :disabled="!canPublish || saving">
          {{ saving ? 'Configuring...' : 'Configure & Publish' }}
        </button>
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
      selections: {}
    }
  },
  
  computed: {
    canPublish() {
      // Check if all required variables have selections
      return this.variablesInfo && this.variablesInfo.length > 0 && 
             this.variablesInfo.every(variable => this.selections[variable.id])
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
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1.5rem;
  border-top: 1px solid #e5e7eb;
  background: #f9fafb;
}

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
</style>