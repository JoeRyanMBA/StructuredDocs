<template>
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
            @click="goPublishHtml(element.id, $event)"
            class="publish-btn publish-html"
          >
            🔗 Publish HTML
          </button>
          <button
            @click="goPublishPdf(element.id, $event)"
            class="publish-btn publish-pdf"
          >
            📋 Publish PDF
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
              🔗 Publish Empty HTML
            </button>
            <button
              @click="goPublishPdf(element.id, $event)"
              class="publish-btn-disabled"
              title="This will create an empty PDF publication"
            >
              📋 Publish Empty PDF
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
</template>

<script>
import TopicItem from '@/components/TopicItem.vue'
import draggable from 'vuedraggable'
import { getCollections, getDocuments } from '@/api/collections.js'

export default {
  name: 'CollectionTree',
  components: {
    draggable,
    TopicItem
  },
  props: {
    tree: { type: Array, required: false, default: () => [] },
  },
  emits: ['update'],

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
    },

    async goPublishHtml(collectionId, event) {
      const button = event?.target
      if (button) {
        button.disabled = true
        button.textContent = 'Processing...'
      }

      try {
        console.log(`Publishing HTML for collection ${collectionId}`)
        this.$router.push({
          name: 'ExportHtml',
          params: { collectionId }
        })
      } catch (error) {
        console.error('Error navigating to HTML export:', error)
        
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
        button.textContent = 'Processing...'
      }

      try {
        console.log(`Publishing PDF for collection ${collectionId}`)
        this.$router.push({
          name: 'ExportPdf',
          params: { collectionId }
        })
      } catch (error) {
        console.error('Error navigating to PDF export:', error)
        
        // Reset button state
        if (button) {
          button.disabled = false
          button.textContent = button.classList.contains('publish-btn-disabled') 
            ? '📋 Publish Empty PDF' 
            : '📋 Publish PDF'
        }
      }
    }
  }
}
</script>

<style scoped>
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
