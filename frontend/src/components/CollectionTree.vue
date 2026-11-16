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
            @click="openVariableConfigurator(element.id)"
            :disabled="publishing"
            class="publish-btn configure-vars"
            title="Configure variables before publishing"
          >
            ⚙️ Configure Variables
          </button>
          <button
            @click="publishCollection(element.id, 'html', { filename: element.name, tagIds: [...audienceTagIds], beforePublish })"
            :disabled="publishing"
            class="publish-btn publish-html"
          >
            {{ publishing ? 'Publishing...' : '🔗 Publish as knowledge base' }}
          </button>
          <button
            @click="publishCollection(element.id, 'pdf', { filename: element.name, tagIds: [...audienceTagIds], beforePublish })"
            :disabled="publishing"
            class="publish-btn publish-pdf"
          >
            {{ publishing ? 'Publishing...' : '📋 Publish as PDF' }}
          </button>
        </div>
        <div v-else-if="!element.topics || element.topics.length === 0" class="empty-collection">
          <em>No topics in this collection</em>
          <div class="publish-buttons">
            <button
              @click="publishCollection(element.id, 'html', { filename: element.name, tagIds: [...audienceTagIds], beforePublish })"
              :disabled="publishing"
              class="publish-btn-disabled"
              title="Save the collection and download a knowledge base"
            >
              {{ publishing ? 'Publishing...' : '🔗 Publish as knowledge base' }}
            </button>
            <button
              @click="publishCollection(element.id, 'pdf', { filename: element.name, tagIds: [...audienceTagIds], beforePublish })"
              :disabled="publishing"
              class="publish-btn-disabled"
              title="Save the collection and download a PDF"
            >
              {{ publishing ? 'Publishing...' : '📋 Publish as PDF' }}
            </button>
          </div>
        </div>

        <!-- Recurse into nested collections -->
        <collection-tree
          v-if="element.children && element.children.length"
          :tree="element.children || []"
          :audience-tag-ids="audienceTagIds"
          :before-publish="beforePublish"
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
    :publish-on-configure="pendingPublishAction?.type !== 'configure-only'"
    @close="closeVariableModal"
    @variables-configured="completeCollectionPublish"
  />
  </div>
</template>

<script>
import TopicItem from '@/components/TopicItem.vue'
import draggable from 'vuedraggable'
import { getCollections, getDocuments } from '@/api/collections.js'
import { useCollectionPublishing } from '@/composables/useCollectionPublishing'
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
    audienceTagIds: { type: Array, default: () => [] },
    beforePublish: { type: Function, default: null },
  },
  emits: ['update'],

  setup() {
    return useCollectionPublishing()
  },

  data(){
    return {
      localTree: JSON.parse(JSON.stringify(this.tree ?? [])),
      recentCols: [],
      recentDocs: []
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
