<template>
  <draggable
             <button
              <button
              @click="goPublishHtml(element.id, $event)"
              class="publish-btn-disabled"
              title="This will cr          button.textContent = button.classList.contains('publish-btn-disabled') 
            ? '🔗 Publish Empty HTML' 
            : '🔗 Publish HTML'e an empty HTML publication"
            >
              🔗 Publish Empty HTML
            </button>   @click="goPublishHtml(element.id, $event)"
            class="publish-btn publish-html"
          >
            🔗 Publish HTML
          </button>="localTree"
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
            � Publish HTML
          </button>
          <button
            @click="goPublishPdf(element.id, $event)"
            class="publish-btn publish-pdf"
          >
            � Publish PDF
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
              � Publish Empty HTML
            </button>
            <button
              @click="goPublishPdf(element.id, $event)"
              class="publish-btn-disabled"
              title="This will create an empty PDF publication"
            >
              � Publish Empty PDF
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

  async created() {
    try {
      this.recentCols = await getCollections({ limit: 3 })
      this.recentDocs = await getDocuments({ limit: 3 })
    } catch (err) {
      console.error('Failed to load recent items', err)
    }
  },
  methods: {
    onDrag() {
      console.log('localTree after drag:', JSON.stringify(this.localTree, null, 2));
      this.$emit('update', this.localTree);
    },
    onChildUpdate(parentId, updatedChildren) {
      const recurse = arr => {
        for (const n of arr) {
          if (n.id === parentId) {
            n.children = updatedChildren
            return true
          }
          if (n.children.length && recurse(n.children)) return true
        }
      }
      recurse(this.localTree)
      this.$emit('update', this.localTree)
    },
    async goPublishHtml(collectionId, event) {
      const button = event?.target
      
      try {
        console.log(`🚀 Publishing collection ${collectionId} as HTML...`)
        
        // Show loading state
        if (button) {
          button.disabled = true
          button.textContent = '⏳ Publishing...'
        }
        
        // Make the API request
        console.log('📡 Making fetch request to:', `/api/collections/${collectionId}/publish`)
        const response = await fetch(`/api/collections/${collectionId}/publish`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ format: 'html' })
        })
        
        console.log('📊 Response received. Status:', response.status, 'OK:', response.ok)
        
        if (!response.ok) {
          const errorText = await response.text()
          throw new Error(`HTTP ${response.status}: ${errorText}`)
        }
        
        const responseText = await response.text()
        console.log('📄 Raw response text:', responseText)
        
        let data
        try {
          data = JSON.parse(responseText)
        } catch (parseError) {
          console.error('❌ JSON Parse Error:', parseError)
          throw new Error('Invalid JSON response from server')
        }
        
        console.log('📋 Parsed response data:', data)
        console.log('📋 Available keys in response:', Object.keys(data))
        
        // Extract publication_id with multiple fallbacks
        const publicationId = data.publication_id || data.publicationId || data.id
        console.log('📋 Publication ID extracted:', publicationId, 'Type:', typeof publicationId)
        
        if (!publicationId) {
          console.error('❌ No publication ID found in response')
          console.error('Response data structure:', JSON.stringify(data, null, 2))
          throw new Error('No publication_id returned from server')
        }
        
        // Show success and immediately navigate to Mobile KB export
        console.log('✅ HTML Publication found/created successfully!')
        console.log('🚀 Redirecting to Mobile KB export page...')
        
        alert(`Collection published as HTML successfully!\nPublication ID: ${publicationId}\n\nRedirecting to Mobile Knowledge Base export...`)
        
        // Navigate directly to Mobile KB export page
        this.$router.push({ name: 'PublishMobileKB' })
        
      } catch (error) {
        console.error('❌ Error publishing collection as HTML:', error)
        alert(`Failed to publish collection as HTML: ${error.message}`)
      } finally {
        // Reset button state
        if (button) {
          button.disabled = false
          button.textContent = button.classList.contains('publish-btn-disabled') 
            ? '� Publish Empty HTML' 
            : '📄 Publish HTML'
        }
      }
    },

    async goPublishPdf(collectionId, event) {
      const button = event?.target
      
      try {
        console.log(`🚀 Publishing collection ${collectionId} as PDF...`)
        
        // Show loading state
        if (button) {
          button.disabled = true
          button.textContent = '⏳ Publishing...'
        }
        
        // Make the API request
        console.log('📡 Making fetch request to:', `/api/collections/${collectionId}/publish`)
        const response = await fetch(`/api/collections/${collectionId}/publish`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ format: 'pdf' })
        })
        
        console.log('� Response received. Status:', response.status, 'OK:', response.ok)
        
        if (!response.ok) {
          const errorText = await response.text()
          throw new Error(`HTTP ${response.status}: ${errorText}`)
        }
        
        const responseText = await response.text()
        console.log('📄 Raw response text:', responseText)
        
        let data
        try {
          data = JSON.parse(responseText)
        } catch (parseError) {
          console.error('❌ JSON Parse Error:', parseError)
          throw new Error('Invalid JSON response from server')
        }
        
        console.log('📋 Parsed response data:', data)
        console.log('📋 Available keys in response:', Object.keys(data))
        
        // Extract publication_id with multiple fallbacks
        const publicationId = data.publication_id || data.publicationId || data.id
        console.log('📋 Publication ID extracted:', publicationId, 'Type:', typeof publicationId)
        
        if (!publicationId) {
          console.error('❌ No publication ID found in response')
          console.error('Response data structure:', JSON.stringify(data, null, 2))
          throw new Error('No publication_id returned from server')
        }
        
        // Show success and immediately navigate to PDF export
        console.log('✅ PDF Publication found/created successfully!')
        console.log('🚀 Redirecting to PDF export page...')
        
        alert(`Collection published as PDF successfully!\nPublication ID: ${publicationId}\n\nRedirecting to PDF Documents export...`)
        
        // Navigate directly to PDF export page
        this.$router.push({ name: 'PublishPDF' })
        
      } catch (error) {
        console.error('❌ Error publishing collection as PDF:', error)
        alert(`Failed to publish collection as PDF: ${error.message}`)
      } finally {
        // Reset button state
        if (button) {
          button.disabled = false
          button.textContent = button.classList.contains('publish-btn-disabled') 
            ? '� Publish Empty PDF' 
            : '� Publish PDF'
        }
      }
    }
  }
}
</script>

<style scoped>
.node {
  padding: 0.5rem;
  border: 1px solid #ccc;
  margin-bottom: 0.5rem;
  background: #fff;
  border-radius: 4px;
}

.publish-buttons {
  display: flex;
  gap: 10px;
  margin-top: 0.5rem;
}

.publish-btn {
  background: #28a745;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background-color 0.2s ease;
  flex: 1;
}

.publish-btn:hover {
  background: #218838;
}

.publish-btn.publish-html {
  background: #007bff;
}

.publish-btn.publish-html:hover {
  background: #0056b3;
}

.publish-btn.publish-pdf {
  background: #dc3545;
}

.publish-btn.publish-pdf:hover {
  background: #c82333;
}

.publish-btn-disabled {
  background: #6c757d;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background-color 0.2s ease;
  flex: 1;
}

.publish-btn-disabled:hover {
  background: #5a6268;
}

.empty-collection {
  margin-top: 0.5rem;
  padding: 0.5rem;
  background: #f8f9fa;
  border-radius: 4px;
  text-align: center;
}

.empty-collection em {
  color: #6c757d;
  display: block;
  margin-bottom: 0.5rem;
}

.topics-container {
  margin: 0.5rem 0;
  padding: 0;
}

.topic-wrapper {
  margin: 0;
  padding: 0;
}
</style>