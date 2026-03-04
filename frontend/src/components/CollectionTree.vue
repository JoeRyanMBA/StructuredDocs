<template>
  <div>
    <draggable
    :list="localTree"
    item-key="id"
    group="collections"
    @change="onDrag"
  >
    <template #item="{ element }">
      <div class="node">
        {{ element.name }}

        <!-- Render topics under this collection as a draggable list -->
        <div class="topics-container">
          <draggable
            :list="element.topics"
            group="topics"
            item-key="id"
            @change="onDrag"
          >
            <template #item="{ element: topic }">
              <div class="topic-wrapper">
                <TopicItem :topic="topic" />
              </div>
            </template>
          </draggable>
        </div>
        
        <!-- Conditionally show Publish for this collection -->
        <div v-if="element.topics && element.topics.length" class="publish-buttons">
          <button
            @click="openVariableConfigurator(element.id, $event)"
            class="publish-btn configure-vars"
            title="Configure variables before publishing"
          >
            ⚙️ Configure Variables
          </button>
          <button
            @click="goPublishHtml(element.id, $event)"
            class="publish-btn publish-html"
          >
            🔗 Save & Export HTML
          </button>
          <button
            @click="goPublishPdf(element.id, $event)"
            class="publish-btn publish-pdf"
          >
            📋 Save & Export PDF
          </button>
        </div>
        <div v-else-if="!element.topics || element.topics.length === 0" class="empty-collection">
          <em>No topics in this collection</em>
          <div class="publish-buttons">
            <button
              @click="goPublishHtml(element.id, $event)"
              class="publish-btn-disabled"
              title="This will create an empty HTML publication"
            >
              🔗 Save & Export Empty HTML
            </button>
            <button
              @click="goPublishPdf(element.id, $event)"
              class="publish-btn-disabled"
              title="This will create an empty PDF publication"
            >
              📋 Save & Export Empty PDF
            </button>
          </div>
        </div>

        <!-- Recurse into nested collections -->
        <collection-tree
          v-if="element.children && element.children.length"
          :tree="element.children || []"
          @update="children => onChildUpdate(element.id, children)"
        />
      </div>
    </template>
  </draggable>
  
  <!-- Variable Selection Modal -->
  <VariableSelectionModal
    :show="showVariableModal"
    :collection-id="variableModalData?.collectionId"
    :variables-info="variableModalData?.variablesInfo"
    :unresolved-variables="variableModalData?.unresolvedVariables"
    @close="closeVariableModal"
    @variables-configured="onVariablesConfigured"
  />
  </div>
</template>

<script>
import TopicItem from '@/components/TopicItem.vue'
import draggable from 'vuedraggable'
import { getCollections, getDocuments } from '@/api/collections.js'
import { toast } from '@/composables/useToast'
import VariableSelectionModal from './VariableSelectionModal.vue'

export default {
  name: 'CollectionTree',
  components: {
    draggable,
    TopicItem,
    VariableSelectionModal
  },
  props: {
    tree: { type: Array, required: false, default: () => [] },
  },
  emits: ['update'],

  data(){
    return {
      localTree: JSON.parse(JSON.stringify(this.tree ?? [])),
      recentCols: [],
      recentDocs: [],
      showVariableModal: false,
      variableModalData: null,
      pendingPublishAction: null
    }
  },
  watch: {
    tree(newT) { this.localTree = JSON.parse(JSON.stringify(newT)) }
  },

  created() {
    this.fetchCollections()
    this.fetchDocuments()
  },

  methods: {
    async openVariableConfigurator(collectionId, event) {
      const btn = event?.target
      if (btn) { btn.disabled = true; btn.textContent = 'Loading…' }
      try {
        const resp = await fetch(`/api/variables/collections/${collectionId}/publish-setup`)
        const data = await resp.json().catch(()=>({}))
        if (!resp.ok) throw new Error(data.error || 'Failed to load variable setup')
        // Translate variables_in_content to modal expected shape (variablesInfo)
        const variablesInfo = (data.variables_in_content||[]).map(v => ({
          id: v.id, slug: v.slug, name: v.name, description: v.description, values: v.values, current_selection: v.current_selection
        }))
        // Always open the modal for consistency; still inform when none
        if (!variablesInfo.length) {
          toast.success('No variables required for this collection')
        }
        this.pendingPublishAction = { type: 'configure-only', collectionId, button: btn }
        this.variableModalData = { collectionId, variablesInfo, unresolvedVariables: (data.variables_in_content||[]).filter(v=>!v.is_resolved).map(v=>v.slug) }
        this.showVariableModal = true
      } catch(e) {
        console.error(e)
        toast.error(e.message)
      } finally {
        if (btn) { btn.disabled = false; btn.textContent = '⚙️ Configure Variables' }
      }
    },
    onDrag() {
      this.$emit('update', this.localTree)
    },

    onChildUpdate(parentId, children) {
      const parent = this.findNodeById(this.localTree, parentId)
      if (parent) {
        parent.children = children
        this.$emit('update', this.localTree)
      }
    },

    findNodeById(tree, id) {
      for (const node of tree) {
        if (node.id === id) return node
        if (node.children) {
          const found = this.findNodeById(node.children, id)
          if (found) return found
        }
      }
      return null
    },

    async fetchCollections() {
      try {
        this.recentCols = await getCollections()
      } catch (err) {
        console.error('Failed to fetch collections:', err)
      }
    },

    async fetchDocuments() {
      try {
        this.recentDocs = await getDocuments()
      } catch (err) {
        console.error('Failed to fetch documents:', err)
      }
    },

    async goPublishHtml(collectionId, event) {
      const button = event?.target
      if (button) {
        button.disabled = true
        button.textContent = 'Publishing...'
      }

      try {
        console.log(`Publishing HTML for collection ${collectionId}`)
        
        // First, publish the collection to create a publication
        const response = await fetch(`/api/collections/${collectionId}/publish`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' }
        })
        
        if (response.ok) {
          const result = await response.json()
          console.log('Publication created:', result)
          
          // Navigate to the Mobile KB page to show available publications
          this.$router.push({ name: 'PublishMobileKB' })
        } else if (response.status === 400) {
          // Handle variable configuration requirement
          const errorData = await response.json()
          if (errorData.requires_variable_selection) {
            this.pendingPublishAction = { type: 'html', collectionId, button }
            this.showVariableModal = true
            this.variableModalData = {
              collectionId,
              variablesInfo: errorData.variables_info,
              unresolvedVariables: errorData.unresolved_variables
            }
            return
          } else {
            throw new Error(errorData.error || `Failed to publish collection: ${response.status}`)
          }
        } else {
          throw new Error(`Failed to publish collection: ${response.status}`)
        }
        
      } catch (error) {
        console.error('Error publishing collection:', error)
        toast.error(`Error publishing collection: ${error.message}`)
        
        // Reset button state
        if (button) {
          button.disabled = false
          button.textContent = button.classList.contains('publish-btn-disabled') 
            ? '🔗 Publish Empty HTML' 
            : '🔗 Publish HTML'
        }
      }
    },

    async goPublishPdf(collectionId, event) {
      const button = event?.target
      if (button) {
        button.disabled = true
        button.textContent = 'Publishing...'
      }

      try {
        console.log(`Publishing PDF for collection ${collectionId}`)
        
        // First, publish the collection to create a publication
        const response = await fetch(`/api/collections/${collectionId}/publish`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' }
        })
        
        if (response.ok) {
          const result = await response.json()
          console.log('Publication created:', result)
          
          // Navigate to the PDF page to show available publications
          this.$router.push({ name: 'PublishPDF' })
        } else if (response.status === 400) {
          // Handle variable configuration requirement
          const errorData = await response.json()
          if (errorData.requires_variable_selection) {
            this.pendingPublishAction = { type: 'pdf', collectionId, button }
            this.showVariableModal = true
            this.variableModalData = {
              collectionId,
              variablesInfo: errorData.variables_info,
              unresolvedVariables: errorData.unresolved_variables
            }
            return
          } else {
            throw new Error(errorData.error || `Failed to publish collection: ${response.status}`)
          }
        } else {
          throw new Error(`Failed to publish collection: ${response.status}`)
        }
        
      } catch (error) {
        console.error('Error publishing collection:', error)
        toast.error(`Error publishing collection: ${error.message}`)
        
        // Reset button state
        if (button) {
          button.disabled = false
          button.textContent = button.classList.contains('publish-btn-disabled') 
            ? '📋 Publish Empty PDF' 
            : '📋 Publish PDF'
        }
      }
    },
    
    closeVariableModal() {
      this.showVariableModal = false
      this.variableModalData = null
      
      // Reset button state for pending action
      if (this.pendingPublishAction && this.pendingPublishAction.button) {
        const button = this.pendingPublishAction.button
        button.disabled = false
        button.textContent = this.pendingPublishAction.type === 'html' 
          ? (button.classList.contains('publish-btn-disabled') ? '🔗 Publish Empty HTML' : '🔗 Publish HTML')
          : (button.classList.contains('publish-btn-disabled') ? '📋 Publish Empty PDF' : '📋 Publish PDF')
      }
      
      this.pendingPublishAction = null
    },
    
    async onVariablesConfigured(data) {
      if (!this.pendingPublishAction) return
      
      const { type, collectionId } = this.pendingPublishAction
      
      try {
        if (type === 'configure-only') {
          toast.success('Variables configured. You can now publish HTML or PDF.')
          return
        }
        // Now try to publish again
        const response = await fetch(`/api/collections/${collectionId}/publish`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' }
        })
        
        if (!response.ok) {
          const errorData = await response.json()
          throw new Error(errorData.error || `Failed to publish collection: ${response.status}`)
        }
        
        const result = await response.json()
        console.log('Publication created after variable configuration:', result)
        
        // Navigate to appropriate page
        if (type === 'html') {
          this.$router.push({ name: 'PublishMobileKB' })
        } else {
          this.$router.push({ name: 'PublishPDF' })
        }
        
        toast.success('Collection published successfully!')
        
      } catch (error) {
        console.error('Error publishing after variable configuration:', error)
        toast.error(`Error publishing collection: ${error.message}`)
        
        // Reset button state
        if (this.pendingPublishAction.button) {
          const button = this.pendingPublishAction.button
          button.disabled = false
          button.textContent = type === 'html' 
            ? (button.classList.contains('publish-btn-disabled') ? '🔗 Publish Empty HTML' : '🔗 Publish HTML')
            : (button.classList.contains('publish-btn-disabled') ? '📋 Publish Empty PDF' : '📋 Publish PDF')
        }
      }
      
      this.pendingPublishAction = null
    }
  }
}
</script>

<style>
.node {
  border: 1px solid #ddd;
  padding: 8px;
  margin: 4px 0;
  background: #f9f9f9;
  border-radius: 4px;
}

.topics-container {
  margin-left: 1rem;
  margin-top: 0.5rem;
}

.topic-wrapper {
  margin: 0.25rem 0;
}

.publish-buttons {
  margin-top: 0.5rem;
  display: flex;
  gap: 0.5rem;
}

.publish-btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.875rem;
  transition: background-color 0.2s;
}

.publish-btn.publish-html {
  background-color: #205493;
  color: white;
}

.publish-btn.publish-html:hover {
  background-color: #205493;
}

.publish-btn.publish-pdf {
  background-color: #dc3545;
  color: white;
}

.publish-btn.configure-vars {
  background-color: #6b7280;
  color: #fff;
}

.publish-btn.configure-vars:hover { background-color:#4b5563; }

.publish-btn.publish-pdf:hover {
  background-color: #c82333;
}

.publish-btn-disabled {
  padding: 0.5rem 1rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  background-color: #f8f9fa;
  color: #6c757d;
  cursor: not-allowed;
  font-size: 0.875rem;
}

.empty-collection {
  margin-top: 0.5rem;
  color: #6c757d;
  font-style: italic;
}

.empty-collection em {
  display: block;
  margin-bottom: 0.5rem;
}

/* Draggable styling */
.sortable-ghost {
  opacity: 0.5;
}

.sortable-chosen {
  background-color: #e3f2fd;
}
</style>
