<template>
  <div class="organize-view">
    <Breadcrumbs />
    <div class="organize-header">
      <h1>📋 Organize Collection</h1>
      <p class="guidance-text">
        Add topics to your collection by dragging topics from the Unassigned Topics area to your collection. 
        Use the drag handles to drag topics. You can organize your topics within the collection by reordering them and dragging them onto other topics to create a hierarchy.
      </p>
    </div>
    
    <div class="organize-layout">
      <div class="collections-panel">
        <h2>{{ currentCollection?.name || 'Collection' }}</h2>
        <div v-if="currentCollection" class="current-collection">
          <div class="node">
            {{ currentCollection.name }}
            
            <!-- Render topics under this collection as a draggable list -->
            <div class="topics-container">
              <draggable
                :list="currentCollection.topics"
                group="topics"
                item-key="id"
                @change="onTopicDrop"
                class="collection-topics-list"
              >
                <template #item="{ element: topic }">
                  <div class="topic-wrapper">
                    <TopicItem :topic="topic" />
                  </div>
                </template>
              </draggable>
            </div>
            
            <!-- Show publish buttons for the current collection -->
            <div v-if="currentCollection.topics && currentCollection.topics.length" class="publish-buttons">
              <button
                @click="goPublishHtml(currentCollection.id, $event)"
                class="publish-btn publish-html"
              >
                🔗 Publish HTML
              </button>
              <button
                @click="goPublishPdf(currentCollection.id, $event)"
                class="publish-btn publish-pdf"
              >
                📋 Publish PDF
              </button>
            </div>
            <div v-else class="empty-collection">
              <em>No topics in this collection</em>
              <div class="publish-buttons">
                <button
                  @click="goPublishHtml(currentCollection.id, $event)"
                  class="publish-btn-disabled"
                  title="This will create an empty HTML publication"
                >
                  🔗 Publish Empty HTML
                </button>
                <button
                  @click="goPublishPdf(currentCollection.id, $event)"
                  class="publish-btn-disabled"
                  title="This will create an empty PDF publication"
                >
                  📋 Publish Empty PDF
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="topics-panel">
        <h2>Unassigned Topics</h2>
        <draggable
          :list="unassignedTopics"
          group="topics"
          item-key="id"
          @change="onTopicDrop"
          class="unassigned-list"
        >
          <template #item="{ element }">
            <div class="unassigned-topic-item">
              <div class="drag-handle">
                <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                  <circle cx="2" cy="2" r="1" fill="#999"/>
                  <circle cx="6" cy="2" r="1" fill="#999"/>
                  <circle cx="10" cy="2" r="1" fill="#999"/>
                  <circle cx="2" cy="6" r="1" fill="#999"/>
                  <circle cx="6" cy="6" r="1" fill="#999"/>
                  <circle cx="10" cy="6" r="1" fill="#999"/>
                  <circle cx="2" cy="10" r="1" fill="#999"/>
                  <circle cx="6" cy="10" r="1" fill="#999"/>
                  <circle cx="10" cy="10" r="1" fill="#999"/>
                </svg>
              </div>
              <span class="topic-title">{{ element.title }}</span>
            </div>
          </template>
        </draggable>
      </div>
    </div>
    
    <div class="organize-actions">
      <button @click="saveChanges">Save</button>
      <button @click="onTopicDrop">Refresh Topics</button>
      <span v-if="confirmation" class="confirmation">{{ confirmation }}</span>
    </div>
  </div>
</template>

<script>
import Breadcrumbs from '@/components/Breadcrumbs.vue'
import CollectionTree from '@/components/CollectionTree.vue'
import TopicItem from '@/components/TopicItem.vue'
import draggable from 'vuedraggable'
import { getCollections, saveCollections } from '@/api/collections.js'
import { getTopics } from '@/api/topics.js' // You may need to implement this

export default {
  name: 'OrganizeView',
  props: {
    id: {
      type: [String, Number],
      required: true
    }
  },
  components: { Breadcrumbs, CollectionTree, TopicItem, draggable },
  data() {
    return {
      currentCollection: null, // The specific collection being organized
      allCollections: [], // All collections (for saving purposes)
      topics: [],
      unassignedTopics: [],
      confirmation: ''
    }
  },
  async created() {
    this.allCollections = await getCollections()
    this.topics = await getTopics()
    
    // Find the specific collection being organized
    this.currentCollection = this.findCollectionById(this.allCollections, parseInt(this.id))
    if (!this.currentCollection) {
      console.error(`Collection with ID ${this.id} not found`)
      this.$router.push({ name: 'Collections' })
      return
    }
    
    this.unassignedTopics = this.getUnassignedTopics()
  },
  methods: {
    findCollectionById(collections, id) {
      for (const collection of collections) {
        if (collection.id === id) return collection
        if (collection.children) {
          const found = this.findCollectionById(collection.children, id)
          if (found) return found
        }
      }
      return null
    },

    getUnassignedTopics() {
      // Get topics that are NOT in the current collection being organized
      const currentCollectionTopicIds = new Set()
      
      if (this.currentCollection?.topics) {
        this.walkTopics(this.currentCollection.topics, currentCollectionTopicIds)
      }
      
      // Return all topics that are NOT in the current collection
      // This allows topics to be reused across different collections
      return this.topics.filter(topic => !currentCollectionTopicIds.has(topic.id))
    },
    
    walkTopics(topics, topicIds) {
      topics.forEach(topic => {
        topicIds.add(topic.id)
        if (topic.children && topic.children.length > 0) {
          this.walkTopics(topic.children, topicIds)
        }
      })
    },

    async onTreeUpdate(newTree) {
      // Update the current collection in the global collections array
      const collectionToUpdate = this.findCollectionById(this.allCollections, parseInt(this.id))
      if (collectionToUpdate) {
        Object.assign(collectionToUpdate, this.currentCollection)
      }
      
      console.log('Updated current collection:', JSON.stringify(this.currentCollection, null, 2))
      await saveCollections(this.allCollections)
      this.unassignedTopics = this.getUnassignedTopics()
    },

    async onTopicDrop() {
      // Refresh unassigned topics list when topics are moved
      this.unassignedTopics = this.getUnassignedTopics()
      
      // Update the collection in the global array and save
      const collectionToUpdate = this.findCollectionById(this.allCollections, parseInt(this.id))
      if (collectionToUpdate) {
        Object.assign(collectionToUpdate, this.currentCollection)
      }
      
      await saveCollections(this.allCollections)
      this.confirmation = 'Topics updated!'
      setTimeout(() => { this.confirmation = '' }, 1500)
    },

    async saveChanges() {
      // Update the collection in the global array and save
      const collectionToUpdate = this.findCollectionById(this.allCollections, parseInt(this.id))
      if (collectionToUpdate) {
        Object.assign(collectionToUpdate, this.currentCollection)
      }
      
      await saveCollections(this.allCollections)
      this.confirmation = 'Collection saved!'
      setTimeout(() => { this.confirmation = '' }, 1500)
    },

    // Add publish methods from CollectionTree
    async goPublishHtml(collectionId, event) {
      const button = event?.target
      if (button) {
        button.disabled = true
        button.textContent = 'Publishing...'
      }

      try {
        console.log(`Publishing HTML for collection ${collectionId}`)
        
        const response = await fetch(`/api/collections/${collectionId}/publish`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' }
        })
        
        if (!response.ok) {
          throw new Error(`Failed to publish collection: ${response.status}`)
        }
        
        const result = await response.json()
        console.log('Publication created:', result)
        
        this.$router.push({ name: 'PublishMobileKB' })
        
      } catch (error) {
        console.error('Error publishing collection:', error)
        alert(`Error publishing collection: ${error.message}`)
        
        if (button) {
          button.disabled = false
          button.textContent = '🔗 Publish HTML'
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
        
        const response = await fetch(`/api/collections/${collectionId}/publish`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' }
        })
        
        if (!response.ok) {
          throw new Error(`Failed to publish collection: ${response.status}`)
        }
        
        const result = await response.json()
        console.log('Publication created:', result)
        
        this.$router.push({ name: 'PublishPDF' })
        
      } catch (error) {
        console.error('Error publishing collection:', error)
        alert(`Error publishing collection: ${error.message}`)
        
        if (button) {
          button.disabled = false
          button.textContent = '📋 Publish PDF'
        }
      }
    }
  }
}
</script>

<style scoped>
.organize-view {
  padding-top: 70px; /* Top padding to account for fixed header */
  padding-left: 2rem;
  padding-right: 2rem;
  padding-bottom: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.organize-header {
  margin-bottom: 2rem;
  text-align: left; /* Left-aligned instead of centered */
}

.organize-header h1 {
  color: #2c3e50;
  margin-bottom: 1rem;
  font-size: 2rem;
}

.guidance-text {
  background: #f8f9fa;
  border-left: 4px solid #007acc;
  padding: 1rem;
  margin-bottom: 1.5rem;
  color: #495057;
  font-size: 0.95rem;
  line-height: 1.5;
  text-align: left; /* Left-aligned text */
}

.organize-layout {
  display: flex;
  gap: 2rem;
  margin-bottom: 2rem;
}

.organize-actions {
  text-align: center;
  margin-top: 1rem;
}

.organize-actions button {
  margin: 0 0.5rem;
  padding: 0.75rem 1.5rem;
  background: #2196f3;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1rem;
}

.organize-actions button:hover {
  background: #1976d2;
}

.collections-panel, .topics-panel {
  flex: 1;
  background: #f8f8f8;
  padding: 1rem;
  border-radius: 8px;
}

.current-collection .node {
  border: 2px solid #007acc;
  background: #f0f8ff;
}

.collection-topics-list {
  min-height: 100px;
  padding: 8px;
  border: 1px dashed #007acc;
  border-radius: 4px;
  background: #fafbfc;
}

.collection-topics-list:empty::after {
  content: "Drag topics here to add them to this collection";
  color: #007acc;
  font-style: italic;
  text-align: center;
  display: block;
  padding: 2rem;
}

.unassigned-list {
  min-height: 100px;
  padding: 8px;
}

.unassigned-topic-item {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  border: 1px solid #e0e0e0;
  margin-bottom: 4px;
  background: #fff;
  border-radius: 4px;
  cursor: grab;
  transition: all 0.2s ease;
}

.unassigned-topic-item:hover {
  border-color: #007acc;
  box-shadow: 0 2px 4px rgba(0, 122, 204, 0.1);
}

.unassigned-topic-item:active {
  cursor: grabbing;
}

.drag-handle {
  margin-right: 8px;
  cursor: grab;
  opacity: 0.6;
  transition: opacity 0.2s ease;
  flex-shrink: 0;
}

.unassigned-topic-item:hover .drag-handle {
  opacity: 1;
}

.topic-title {
  flex: 1;
  font-size: 14px;
  color: #333;
  line-height: 1.4;
}

.topic-item {
  padding: 0.5rem;
  border: 1px solid #ccc;
  margin-bottom: 0.5rem;
  background: #fff;
  border-radius: 4px;
}
.confirmation {
  margin-left: 1rem;
  color: green;
  font-weight: bold;
}

/* Drag and drop visual feedback */
.sortable-ghost {
  opacity: 0.5;
  background: #007acc !important;
  color: white !important;
}

.sortable-chosen {
  background: #e3f2fd !important;
  border-color: #007acc !important;
}

.sortable-drag {
  opacity: 0.8;
  transform: rotate(2deg);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

/* Empty state styling */
.unassigned-list:empty::after {
  content: "No unassigned topics";
  color: #999;
  font-style: italic;
  text-align: center;
  display: block;
  padding: 2rem;
}

/* Publish button styles */
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
  background-color: #007acc;
  color: white;
}

.publish-btn.publish-html:hover {
  background-color: #005a9c;
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
</style>