<template>
  <div class="organize-view">
    <Breadcrumbs />
    <div class="organize-header">
      <h1>{{ isEditMode ? '✏️ Edit Collection' : '📋 Organize Collection' }}</h1>
      <p class="guidance-text">
        Add topics to your collection by dragging topics from the Available Topics area to your collection. 
        Use the drag handles to drag topics. You can organize your topics within the collection by reordering them and dragging them onto other topics to create a hierarchy.
        <br><br>
        <strong>Multi-select:</strong> Click to select a topic, Ctrl+click to select multiple individual topics, Shift+click to select a range of topics (e.g., topics 2-12).
      </p>
    </div>
    
    <div class="organize-layout">
      <div class="collections-panel">
        <h2>{{ currentCollection?.name || 'Collection' }}</h2>
        
        <!-- Collection Properties Edit Panel (only in edit mode) -->
        <div v-if="isEditMode && currentCollection" class="collection-edit-panel">
          <h3>Collection Properties</h3>
          <div class="edit-form">
            <div class="form-group">
              <label>Collection Name:</label>
              <input 
                v-model="currentCollection.name" 
                @blur="saveCollectionProperty('name')"
                class="edit-input"
              />
            </div>
            <div class="form-group">
              <label>Form Number:</label>
              <input 
                v-model="currentCollection.form_number" 
                @blur="saveCollectionProperty('form_number')"
                class="edit-input"
                placeholder="e.g., FORM-001"
              />
            </div>
            <div class="form-group">
              <label>Project:</label>
              <select v-model="currentCollection.projectId" @change="saveCollectionProperty('projectId')" class="edit-input">
                <option value="">Select Project...</option>
                <option v-for="project in projects" :key="project.id" :value="project.id">{{ project.name }}</option>
              </select>
            </div>
          </div>
        </div>
        
        <div v-if="currentCollection" class="current-collection">
          <div class="node">
            {{ currentCollection.name }}
            
            <!-- Multi-select controls -->
            <div v-if="selectedTopics.size > 0" class="multi-select-controls">
              <span class="selected-count">{{ selectedTopics.size }} topic(s) selected</span>
              <button @click="clearSelection" class="clear-btn">Clear Selection</button>
              <button @click="moveSelectedToTop" class="move-btn">Move to Top</button>
              <button @click="moveSelectedToBottom" class="move-btn">Move to Bottom</button>
              <select v-model="moveTargetId" class="move-target-select">
                <option value="">Select target topic...</option>
                <option 
                  v-for="topic in currentCollection.topics" 
                  :key="topic.id" 
                  :value="topic.id"
                  :disabled="selectedTopics.has(topic.id)"
                >
                  {{ topic.title }}
                </option>
              </select>
              <button @click="moveSelectedUnderTarget" :disabled="!moveTargetId" class="move-btn">
                Move Under Target
              </button>
            </div>

            <!-- Expand/Collapse controls -->
            <div class="expand-controls">
              <button @click="expandAll" class="expand-btn">Expand All</button>
              <button @click="collapseAll" class="expand-btn">Collapse All</button>
            </div>
            
            <!-- Render topics under this collection as a draggable list -->
            <div class="topics-container">
              <draggable
                :list="currentCollection.topics"
                group="topics"
                item-key="id"
                @change="onTopicDrop"
                @start="onDragStart"
                @end="onDragEnd"
                class="collection-topics-list"
                :fallback-tolerance="5"
                :force-fallback="true"
                :animation="200"
                :ghost-class="'sortable-ghost'"
                :chosen-class="'sortable-chosen'"
                :drag-class="'sortable-drag'"
                handle=".drag-handle"
    :move="customMove"
  >
    <template #item="{ element: topic, index }">
                  <div 
                    class="topic-wrapper"
                    @dragover="handleDragOver(topic, $event)"
                    @dragleave="handleDragLeave(topic, $event)"
                  >
                    <div 
                      class="collection-topic-item"
                      :class="{ 
                        'selected': selectedTopics.has(topic.id),
                        'drop-target': dropTarget === topic.id
                      }"
                      :data-topic-id="topic.id"
                      @click="handleTopicClick(topic, index, $event)"
                      @contextmenu="handleTopicRightClick(topic, index, $event)"
                      @drop="handleDrop(topic, $event)"
                    >
                      <div class="collection-topic-item-row" style="display: flex; align-items: center; width: 100%;">
                        <div v-if="topic.children && topic.children.length > 0" class="expand-toggle" @click.stop="toggleExpansion(topic.id)">
                          <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                            <path v-if="expandedTopics.has(topic.id)" d="M3 4.5L6 7.5L9 4.5" stroke="#666" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                            <path v-else d="M4.5 3L7.5 6L4.5 9" stroke="#666" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                          </svg>
                        </div>
                        <div v-else class="expand-spacer"></div>
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
                        <div class="topic-content-row" style="display: flex; align-items: center; flex: 1; min-width: 0;">
                          <span class="topic-title">{{ topic.title }}</span>
                          <span v-if="topic.children && topic.children.length > 0" class="child-count">
                            ({{ topic.children.length }})
                          </span>
                          <div class="topic-actions" style="margin-left: auto;">
                            <button class="topic-btn up" @click.stop="moveTopicUp(topic)">▲</button>
                            <button class="topic-btn down" @click.stop="moveTopicDown(topic)">▼</button>
                            <button class="topic-btn right" @click.stop="indentTopic(topic)">▶</button>
                            <button class="topic-btn left" @click.stop="outdentTopic(topic)">◀</button>
                          </div>
                        </div>
                      </div>
                    </div> <!-- close .collection-topic-item-row -->
                    <!-- Render child topics if they exist and topic is expanded -->
                    <div 
                      v-if="topic.children && topic.children.length > 0 && expandedTopics.has(topic.id)" 
                      class="child-topics"
                    >
                      <draggable
                        :list="topic.children"
                        group="topics"
                        item-key="id"
                        @change="onTopicDrop"
                        class="child-topics-list"
                        :fallback-tolerance="5"
                        :force-fallback="true"
                        handle=".drag-handle"
                      >
                        <template #item="{ element: childTopic, index: childIndex }">
                          <div 
                            class="collection-topic-item child-topic"
                            :class="{ 'selected': selectedTopics.has(childTopic.id) }"
                            @click="handleChildTopicClick(childTopic, topic, childIndex, $event)"
                            @contextmenu="handleTopicRightClick(childTopic, childIndex, $event)"
                          >
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
                            <span class="topic-title">{{ childTopic.title }}</span>
                            <div class="topic-actions">
                              <button class="topic-btn up" @click.stop="moveTopicUp(childTopic)">▲</button>
                              <button class="topic-btn down" @click.stop="moveTopicDown(childTopic)">▼</button>
                              <button class="topic-btn right" @click.stop="indentTopic(childTopic)">▶</button>
                              <button class="topic-btn left" @click.stop="outdentTopic(childTopic)">◀</button>
                            </div>
                          </div>
                        </template>
                      </draggable>
                    </div>
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
        <h2>Available Topics</h2>
        <draggable
          :list="unassignedTopics"
          group="topics"
          item-key="id"
          @change="onTopicDrop"
          class="unassigned-list"
          handle=".drag-handle"
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
              <div style="margin-left: auto; display: flex; align-items: center;">
                <button class="preview-icon-btn" @click.stop="previewTopic(element)" title="Preview this topic">
                  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 20 20" fill="none">
                    <path d="M10 4C5 4 1.73 8.11 1.08 9.01a1.5 1.5 0 0 0 0 1.98C1.73 11.89 5 16 10 16s8.27-4.11 8.92-5.01a1.5 1.5 0 0 0 0-1.98C18.27 8.11 15 4 10 4Zm0 10c-3.87 0-6.82-3.13-7.7-4C3.18 9.13 6.13 6 10 6s6.82 3.13 7.7 4c-.88.87-3.83 4-7.7 4Zm0-7a3 3 0 1 0 0 6 3 3 0 0 0 0-6Zm0 5a2 2 0 1 1 0-4 2 2 0 0 1 0 4Z" fill="#007acc"/>
                  </svg>
                </button>
              </div>
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
    
    <!-- Context Menu -->
    <div 
      v-if="contextMenu.show" 
      class="context-menu"
      :style="{ top: contextMenu.y + 'px', left: contextMenu.x + 'px' }"
      @click.stop
    >
      <div class="context-menu-item" @click="selectAllTopics">
        Select All Topics
      </div>
      <div class="context-menu-item" @click="invertSelection">
        Invert Selection
      </div>
      <div v-if="selectedTopics.size > 0" class="context-menu-divider"></div>
      <div v-if="selectedTopics.size > 0" class="context-menu-item" @click="duplicateSelectedTopics">
        Duplicate Selected ({{ selectedTopics.size }})
      </div>
      <div v-if="selectedTopics.size > 0" class="context-menu-item danger" @click="removeSelectedTopics">
        Remove Selected ({{ selectedTopics.size }})
      </div>
    </div>
    
    <!-- Click outside to close context menu -->
    <div 
      v-if="contextMenu.show" 
      class="context-menu-overlay"
      @click="closeContextMenu"
    ></div>

    <div v-if="previewModal.show" class="modal-overlay" @click.self="closePreviewModal">
      <div class="modal-content preview-modal" @click.stop>
        <div class="modal-header">
          <h3>👁️ Topic Preview</h3>
          <button class="btn-close" @click="closePreviewModal">✕</button>
        </div>
        <div class="modal-body">
          <div v-if="previewModal.loading">Loading…</div>
          <div v-else-if="previewModal.error" class="error">{{ previewModal.error }}</div>
          <div v-else>
            <TopicEditor
              :topicId="previewModal.topic.id"
              :initialTitle="previewModal.title"
              :initialContent="previewModal.content"
              :initialFrontmatter="previewModal.frontmatter"
              :readOnly="true"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Breadcrumbs from '@/components/Breadcrumbs.vue'
import CollectionTree from '@/components/CollectionTree.vue'
import TopicItem from '@/components/TopicItem.vue'
import draggable from 'vuedraggable'
import { getCollections, saveCollections } from '@/api/collections.js'
import { getProjects } from '@/api/projects.js'
import { getTopics } from '@/api/topics.js' // You may need to implement this
import TopicEditor from '@/components/TopicEditor.vue'

export default {
  name: 'OrganizeView',
  props: {
    id: {
      type: [String, Number],
      required: true
    }
  },
  components: { Breadcrumbs, CollectionTree, TopicItem, draggable, TopicEditor },
  data() {
    return {
      currentCollection: null, // The specific collection being organized
      allCollections: [], // All collections (for saving purposes)
      topics: [],
      unassignedTopics: [],
      projects: [],
      confirmation: '',
      isEditMode: false, // Track if we're in edit mode
      selectedTopics: new Set(), // Track selected topic IDs
      lastSelectedIndex: -1, // Track last selected index for shift+click
      moveTargetId: '', // Track target topic for hierarchy moves
      draggedTopics: [], // Track topics being dragged
      expandedTopics: new Set(), // Track which topics are expanded
      dropTarget: null, // Track which topic is being dragged over
      contextMenu: {
        show: false,
        x: 0,
        y: 0,
        targetTopic: null
      },
      previewModal: {
        show: false,
        topic: null,
        loading: false,
        error: null,
        content: '',
        title: '',
        frontmatter: ''
      }
    }
  },
  async created() {
    // Check if we're in edit mode
    this.isEditMode = this.$route.query.edit === 'true'
    
    const [collections, topics, projects] = await Promise.all([
      getCollections(),
      getTopics(),
      getProjects()
    ])
    this.allCollections = collections
    this.topics = topics
    this.projects = projects
    
    // Find the specific collection being organized
    this.currentCollection = this.findCollectionById(this.allCollections, parseInt(this.id))
    if (!this.currentCollection) {
      console.error(`Collection with ID ${this.id} not found`)
      this.$router.push({ name: 'Collections' })
      return
    }
    
    // Ensure all topics have proper structure for nesting
    if (this.currentCollection.topics) {
      this.currentCollection.topics = this.currentCollection.topics.map(topic => this.ensureTopicStructure(topic))
    }
    
    this.unassignedTopics = this.getUnassignedTopics()
  },
  methods: {
    // Move topic up in its current list
    moveTopicUp(topic) {
      // Find the parent and index of this topic in the tree
      function findParentAndIndex(topics, childId, parent = null) {
        for (let i = 0; i < topics.length; i++) {
          const t = topics[i];
          if (t.id === childId) {
            return { parent, topics, index: i };
          }
          if (t.children && t.children.length > 0) {
            const found = findParentAndIndex(t.children, childId, t);
            if (found) return found;
          }
        }
        return null;
      }
      const result = findParentAndIndex(this.currentCollection.topics, topic.id);
      if (result && result.index > 0) {
        // Swap with previous
        const temp = result.topics[result.index - 1];
        result.topics[result.index - 1] = result.topics[result.index];
        result.topics[result.index] = temp;
        this.saveChanges();
      }
    },

    // Move topic down in its current list
    moveTopicDown(topic) {
      // Find the parent and index of this topic in the tree
      function findParentAndIndex(topics, childId, parent = null) {
        for (let i = 0; i < topics.length; i++) {
          const t = topics[i];
          if (t.id === childId) {
            return { parent, topics, index: i };
          }
          if (t.children && t.children.length > 0) {
            const found = findParentAndIndex(t.children, childId, t);
            if (found) return found;
          }
        }
        return null;
      }
      const result = findParentAndIndex(this.currentCollection.topics, topic.id);
      if (result && result.index < result.topics.length - 1) {
        // Swap with next
        const temp = result.topics[result.index + 1];
        result.topics[result.index + 1] = result.topics[result.index];
        result.topics[result.index] = temp;
        this.saveChanges();
      }
    },
    customMove(evt, originalEvent) {
      // Prevent vuedraggable from handling drop if dropping onto a topic row (for subtopic)
      // Only allow sorting if not dropping onto a topic row
      if (originalEvent && originalEvent.target && originalEvent.target.classList.contains('collection-topic-item')) {
        // Let the custom @drop handler handle this
        return false;
      }
      return true;
    },
    // Multi-select methods
    handleTopicClick(topic, index, event) {
      event.preventDefault()
      event.stopPropagation()
      
      if (event.shiftKey && this.lastSelectedIndex !== -1) {
        // Shift+click: select range
        this.selectRange(this.lastSelectedIndex, index)
      } else if (event.ctrlKey || event.metaKey) {
        // Ctrl+click: toggle individual selection
        this.toggleTopicSelection(topic.id)
      } else {
        // Regular click: select only this topic
        this.clearSelection()
        this.selectTopic(topic.id)
        this.lastSelectedIndex = index
      }
    },

    selectTopic(topicId) {
      this.selectedTopics.add(topicId)
    },

    toggleTopicSelection(topicId) {
      if (this.selectedTopics.has(topicId)) {
        this.selectedTopics.delete(topicId)
      } else {
        this.selectedTopics.add(topicId)
      }
    },

    handleChildTopicClick(childTopic, parentTopic, childIndex, event) {
      event.preventDefault()
      event.stopPropagation()
      
      if (event.ctrlKey || event.metaKey) {
        // Ctrl+click: toggle individual selection
        this.toggleTopicSelection(childTopic.id)
      } else {
        // Regular click: select only this topic
        this.clearSelection()
        this.selectTopic(childTopic.id)
      }
    },

    selectRange(startIndex, endIndex) {
      const start = Math.min(startIndex, endIndex)
      const end = Math.max(startIndex, endIndex)
      
      for (let i = start; i <= end; i++) {
        if (this.currentCollection.topics[i]) {
          this.selectedTopics.add(this.currentCollection.topics[i].id)
        }
      }
    },

    // Expand/Collapse methods
    toggleExpansion(topicId) {
      if (this.expandedTopics.has(topicId)) {
        this.expandedTopics.delete(topicId)
      } else {
        this.expandedTopics.add(topicId)
      }
    },

    expandAll() {
      const allTopicsWithChildren = this.getAllTopicsWithChildren(this.currentCollection.topics)
      allTopicsWithChildren.forEach(topicId => {
        this.expandedTopics.add(topicId)
      })
    },

    collapseAll() {
      this.expandedTopics.clear()
    },

    getAllTopicsWithChildren(topics) {
      let topicsWithChildren = []
      topics.forEach(topic => {
        if (topic.children && topic.children.length > 0) {
          topicsWithChildren.push(topic.id)
          topicsWithChildren = topicsWithChildren.concat(this.getAllTopicsWithChildren(topic.children))
        }
      })
      return topicsWithChildren
    },

    clearSelection() {
      this.selectedTopics.clear()
      this.lastSelectedIndex = -1
      this.moveTargetId = ''
    },

    // Enhanced move methods
    async moveSelectedToTop() {
      if (this.selectedTopics.size === 0) return
      
      const selectedTopicObjects = this.getSelectedTopicObjects()
      this.removeSelectedTopicsFromCollection()
      
      // Add them to the top
      this.currentCollection.topics.unshift(...selectedTopicObjects)
      
      this.clearSelection()
      await this.saveChanges()
      this.confirmation = `Moved ${selectedTopicObjects.length} topic(s) to top!`
      setTimeout(() => { this.confirmation = '' }, 1500)
    },

    async moveSelectedToBottom() {
      if (this.selectedTopics.size === 0) return
      
      const selectedTopicObjects = this.getSelectedTopicObjects()
      this.removeSelectedTopicsFromCollection()
      
      // Add them to the bottom
      this.currentCollection.topics.push(...selectedTopicObjects)
      
      this.clearSelection()
      await this.saveChanges()
      this.confirmation = `Moved ${selectedTopicObjects.length} topic(s) to bottom!`
      setTimeout(() => { this.confirmation = '' }, 1500)
    },

    async moveSelectedUnderTarget() {
      if (this.selectedTopics.size === 0 || !this.moveTargetId) return
      
      const selectedTopicObjects = this.getSelectedTopicObjects()
      const targetTopic = this.findTopicById(this.currentCollection.topics, parseInt(this.moveTargetId))
      
      if (!targetTopic) {
        alert('Target topic not found')
        return
      }
      
      this.removeSelectedTopicsFromCollection()
      
      // Ensure target topic has children array
      if (!targetTopic.children) {
        targetTopic.children = []
      }
      
      // Add selected topics as children of target
      targetTopic.children.push(...selectedTopicObjects)
      
      // Auto-expand the target topic to show the newly added children
      this.expandedTopics.add(targetTopic.id)
      
      this.clearSelection()
      await this.saveChanges()
      this.confirmation = `Moved ${selectedTopicObjects.length} topic(s) under "${targetTopic.title}"!`
      setTimeout(() => { this.confirmation = '' }, 1500)
    },

    getSelectedTopicObjects() {
      const allTopics = this.getAllTopicsFlat(this.currentCollection.topics)
      return allTopics.filter(topic => this.selectedTopics.has(topic.id))
    },

    getAllTopicsFlat(topics) {
      let flat = []
      topics.forEach(topic => {
        flat.push(topic)
        if (topic.children && topic.children.length > 0) {
          flat = flat.concat(this.getAllTopicsFlat(topic.children))
        }
      })
      return flat
    },

    removeSelectedTopicsFromCollection() {
      this.removeSelectedFromTopicsList(this.currentCollection.topics)
    },

    removeSelectedFromTopicsList(topics) {
      for (let i = topics.length - 1; i >= 0; i--) {
        const topic = topics[i]
        if (this.selectedTopics.has(topic.id)) {
          topics.splice(i, 1)
        } else if (topic.children && topic.children.length > 0) {
          this.removeSelectedFromTopicsList(topic.children)
        }
      }
    },

    findTopicById(topics, id) {
      for (const topic of topics) {
        if (topic.id === id) return topic
        if (topic.children) {
          const found = this.findTopicById(topic.children, id)
          if (found) return found
        }
      }
      return null
    },

    // Enhanced drag and drop handlers
    onDragStart(event) {
      console.log('Drag start event:', event)
      console.log('Event properties:', Object.keys(event))
      console.log('Old index:', event.oldIndex)
      console.log('Collection topics:', this.currentCollection.topics)
      
      // For vuedraggable, the event object contains oldIndex
      let draggedTopic = null
      
      // Try to get the topic from the oldIndex
      if (event.oldIndex !== undefined && this.currentCollection.topics && this.currentCollection.topics[event.oldIndex]) {
        draggedTopic = this.currentCollection.topics[event.oldIndex]
        console.log('Found dragged topic from oldIndex:', draggedTopic)
      }
      
      // Fallback: try to get from the item property (some versions of vueddraggable)
      if (!draggedTopic && event.item && event.item.dataset) {
        const topicId = parseInt(event.item.dataset.topicId)
        if (topicId) {
          draggedTopic = this.currentCollection.topics.find(t => t.id === topicId)
          console.log('Found dragged topic from dataset:', draggedTopic)
        }
      }
      
      console.log('Final dragged topic:', draggedTopic)
      
      if (draggedTopic) {
        // If dragging a selected topic, include all selected topics
        if (this.selectedTopics.has(draggedTopic.id)) {
          this.draggedTopics = this.getSelectedTopicObjects()
          console.log('Dragging selected topics:', this.draggedTopics.map(t => t.title))
        } else {
          this.draggedTopics = [draggedTopic]
          console.log('Dragging single topic:', draggedTopic.title)
        }
      } else {
        console.warn('Could not identify dragged topic')
        this.draggedTopics = []
      }
    },

    onDragEnd(event) {
      this.draggedTopics = []
      this.dropTarget = null
      this.clearSelection()
    },

    // Topic drop zone handlers
    handleDragOver(targetTopic, event) {
      event.preventDefault()
      event.stopPropagation()
      
      // Don't allow dropping on self or selected topics
      if (this.selectedTopics.has(targetTopic.id)) {
        return
      }
      
      // Set visual feedback
      this.dropTarget = targetTopic.id
      event.dataTransfer.dropEffect = 'move'
    },

    handleDragLeave(targetTopic, event) {
      event.preventDefault()
      event.stopPropagation()
      
      // Clear visual feedback when leaving the drop zone
      if (this.dropTarget === targetTopic.id) {
        this.dropTarget = null
      }
    },

    async handleDrop(targetTopic, event) {
      event.preventDefault()
      event.stopPropagation()
      
      // Clear visual feedback
      this.dropTarget = null
      
      // Don't allow dropping on self or selected topics
      if (this.selectedTopics.has(targetTopic.id)) {
        return
      }
      
      console.log('Dropping onto topic:', targetTopic.title)
      
      // Get the topics being dragged
      let topicsToMove = []
      if (this.draggedTopics.length > 0) {
        topicsToMove = this.draggedTopics
      } else if (this.selectedTopics.size > 0) {
        topicsToMove = this.getSelectedTopicObjects()
      }
      
      if (topicsToMove.length === 0) {
        console.log('No topics to move')
        return
      }
      
      console.log('Moving topics:', topicsToMove.map(t => t.title))
      
      // Remove the dragged topics from their current locations
      this.removeTopicsFromCollection(topicsToMove.map(t => t.id))
      
      // Ensure target topic has children array
      if (!targetTopic.children) {
        targetTopic.children = []
      }
      
      // Add the dragged topics as children of the target topic
      targetTopic.children.push(...topicsToMove)
      
      // Auto-expand the target topic to show the newly added children
      this.expandedTopics.add(targetTopic.id)
      
      // Clear selection and save
      this.clearSelection()
      await this.saveChanges()
      
      this.confirmation = `Moved ${topicsToMove.length} topic(s) under "${targetTopic.title}"!`
      setTimeout(() => { this.confirmation = '' }, 1500)
    },

    removeTopicsFromCollection(topicIds) {
      this.removeTopicsFromList(this.currentCollection.topics, topicIds)
    },

    removeTopicsFromList(topics, topicIds) {
      for (let i = topics.length - 1; i >= 0; i--) {
        const topic = topics[i]
        if (topicIds.includes(topic.id)) {
          topics.splice(i, 1)
        } else if (topic.children && topic.children.length > 0) {
          this.removeTopicsFromList(topic.children, topicIds)
        }
      }
    },

    async moveSelectedTopics() {
      if (this.selectedTopics.size === 0) return
      
      // For now, let's implement a simple "move to top" functionality
      // You can enhance this to allow dropping on specific topics
      const selectedTopicObjects = this.currentCollection.topics.filter(
        topic => this.selectedTopics.has(topic.id)
      )
      
      // Remove selected topics from their current positions
      this.currentCollection.topics = this.currentCollection.topics.filter(
        topic => !this.selectedTopics.has(topic.id)
      )
      
      // Add them to the top (you could modify this to insert at a specific position)
      this.currentCollection.topics.unshift(...selectedTopicObjects)
      
      this.clearSelection()
      await this.saveChanges()
      this.confirmation = `Moved ${selectedTopicObjects.length} topic(s)!`
      setTimeout(() => { this.confirmation = '' }, 1500)
    },

    // Context menu methods
    handleTopicRightClick(topic, index, event) {
      event.preventDefault()
      
      // If right-clicking on unselected topic, select it
      if (!this.selectedTopics.has(topic.id)) {
        this.clearSelection()
        this.selectTopic(topic.id)
        this.lastSelectedIndex = index
      }
      
      this.contextMenu = {
        show: true,
        x: event.clientX,
        y: event.clientY,
        targetTopic: topic
      }
    },

    closeContextMenu() {
      this.contextMenu.show = false
    },

    selectAllTopics() {
      const allTopics = this.getAllTopicsFlat(this.currentCollection.topics)
      allTopics.forEach(topic => {
        this.selectedTopics.add(topic.id)
      })
      this.closeContextMenu()
    },

    invertSelection() {
      const allTopics = this.getAllTopicsFlat(this.currentCollection.topics)
      const newSelection = new Set()
      allTopics.forEach(topic => {
        if (!this.selectedTopics.has(topic.id)) {
          newSelection.add(topic.id)
        }
      })
      this.selectedTopics = newSelection
      this.closeContextMenu()
    },

    async duplicateSelectedTopics() {
      if (this.selectedTopics.size === 0) return
      
      const selectedTopicObjects = this.getSelectedTopicObjects()
      const duplicatedTopics = selectedTopicObjects.map(topic => ({
        ...topic,
        id: Date.now() + Math.random(), // Generate temporary ID
        title: `${topic.title} (Copy)`,
        children: topic.children ? [...topic.children] : []
      }))
      
      // Add duplicated topics after the last selected topic
      const lastSelectedIndex = this.currentCollection.topics.findIndex(
        topic => this.selectedTopics.has(topic.id)
      )
      
      this.currentCollection.topics.splice(lastSelectedIndex + 1, 0, ...duplicatedTopics)
      
      this.closeContextMenu()
      this.clearSelection()
      await this.saveChanges()
      this.confirmation = `Duplicated ${duplicatedTopics.length} topic(s)!`
      setTimeout(() => { this.confirmation = '' }, 1500)
    },

    async removeSelectedTopics() {
      if (this.selectedTopics.size === 0) return
      
      const count = this.selectedTopics.size
      this.removeSelectedTopicsFromCollection()
      
      this.closeContextMenu()
      this.clearSelection()
      await this.saveChanges()
      this.confirmation = `Removed ${count} topic(s)!`
      setTimeout(() => { this.confirmation = '' }, 1500)
    },

    async saveCollectionProperty(propertyName) {
      if (!this.currentCollection) return
      try {
        let payload = {};
        if (propertyName === 'projectId') {
          payload['project_id'] = this.currentCollection.projectId ? Number(this.currentCollection.projectId) : null;
        } else {
          payload[propertyName] = this.currentCollection[propertyName];
        }
        const response = await fetch(`/api/collections/${this.currentCollection.id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        })
        if (response.ok) {
          console.log(`✅ Updated collection ${propertyName}`)
        } else {
          const error = await response.json()
          alert(`Failed to update ${propertyName}: ${error.error || 'Unknown error'}`)
        }
      } catch (error) {
        console.error(`Failed to update collection ${propertyName}:`, error)
        alert(`Failed to update ${propertyName}. Please try again.`)
      }
    },

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
      return this.topics
        .filter(topic => !currentCollectionTopicIds.has(topic.id))
        .map(topic => this.ensureTopicStructure(topic))
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

    async onTopicDrop(event) {
      console.log('Topic drop event:', event)
      console.log('Event keys:', Object.keys(event))
      
      // Handle different types of drag-and-drop events
      if (event.added) {
        // Topic was added to this collection from somewhere else
        const addedTopic = event.added.element
        console.log('Topic added:', addedTopic)
        
        // Ensure the added topic has proper structure
        this.ensureTopicStructure(addedTopic)
        
        // Auto-expand if the added topic has children
        if (addedTopic.children && addedTopic.children.length > 0) {
          this.expandedTopics.add(addedTopic.id)
        }
      }
      
      if (event.moved) {
        // Topic was moved within this collection
        const movedTopic = event.moved.element
        console.log('Topic moved within collection:', movedTopic)
      }
      
      if (event.removed) {
        // Topic was removed from this collection
        const removedTopic = event.removed.element
        console.log('Topic removed from collection:', removedTopic)
      }
      
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

    onTopicUpdate(updatedTopic) {
      // Handle updates to nested topic structure
      console.log('Topic updated:', updatedTopic)
      this.saveChanges()
    },

    ensureTopicStructure(topic) {
      // Ensure each topic has a children array for nesting
      if (!topic.children) {
        topic.children = []
      }
      return topic
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
  },
    // Indent topic (make it a child of the previous sibling)
    indentTopic(topic) {
      // Find the parent and index of this topic in the tree
      function findParentAndIndex(topics, childId, parent = null) {
        for (let i = 0; i < topics.length; i++) {
          const t = topics[i];
          if (t.id === childId) {
            return { parent, topics, index: i };
          }
          if (t.children && t.children.length > 0) {
            const found = findParentAndIndex(t.children, childId, t);
            if (found) return found;
          }
        }
        return null;
      }

      const result = findParentAndIndex(this.currentCollection.topics, topic.id);
      if (!result) return;
      const { topics, index } = result;
      if (index > 0) {
        // Remove topic from its current parent/array
        const [removed] = topics.splice(index, 1);
        // Add as child to previous sibling (regardless of nesting)
        const prevSibling = topics[index - 1];
        if (!prevSibling.children) prevSibling.children = [];
        prevSibling.children.push(removed);
        // Expand the previous sibling to show the new child
        this.expandedTopics.add(prevSibling.id);
        this.saveChanges();
      }
    },

    // Outdent topic (move it up one level in the hierarchy)
    outdentTopic(topic) {
      // Find the parent and index of this topic in the tree
      function findParentAndIndex(topics, childId, parent = null) {
        for (let i = 0; i < topics.length; i++) {
          const t = topics[i];
          if (t.id === childId) {
            return { parent, topics, index: i };
          }
          if (t.children && t.children.length > 0) {
            const found = findParentAndIndex(t.children, childId, t);
            if (found) return found;
          }
        }
        return null;
      }

      const result = findParentAndIndex(this.currentCollection.topics, topic.id);
      if (result && result.parent) {
        // Remove from parent's children
        const [removed] = result.topics.splice(result.index, 1);
        // Insert after the parent in the parent's parent's children (or top-level)
        const parentResult = findParentAndIndex(this.currentCollection.topics, result.parent.id);
        if (parentResult) {
          parentResult.topics.splice(parentResult.index + 1, 0, removed);
        } else {
          // If parent is top-level, insert after it in top-level
          const topIdx = this.currentCollection.topics.findIndex(t => t.id === result.parent.id);
          if (topIdx !== -1) {
            this.currentCollection.topics.splice(topIdx + 1, 0, removed);
          }
        }
        this.saveChanges();
      }
    },
    async previewTopic(topic) {
      this.previewModal.show = true;
      this.previewModal.loading = true;
      this.previewModal.error = null;
      this.previewModal.topic = topic;
      try {
        const res = await fetch(`/api/topics/${topic.id}`);
        if (!res.ok) throw new Error('Failed to load topic');
        const data = await res.json();
        this.previewModal.title = data.title || topic.title;
        this.previewModal.content = data.content || '';
        this.previewModal.frontmatter = data.frontmatter || '';
      } catch (e) {
        this.previewModal.error = e.message;
      } finally {
        this.previewModal.loading = false;
      }
    },
    closePreviewModal() {
      this.previewModal.show = false;
      this.previewModal.topic = null;
      this.previewModal.content = '';
      this.previewModal.title = '';
      this.previewModal.frontmatter = '';
      this.previewModal.error = null;
      this.previewModal.loading = false;
    },
  }
}
</script>

<style scoped>
.organize-view {
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
  border-radius: .75rem;
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
  min-height: 400px;
  align-items: flex-start;
  height: 70vh;
}

.collections-panel {
  flex: 0 0 60%;
  max-width: 60%;
  background: #f8f8f8;
  padding: 1rem;
  border-radius: 8px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.topics-panel {
  flex: 0 0 35%;
  max-width: 35%;
  background: #f8f8f8;
  padding: 1rem;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  height: 100%;
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

.current-collection .node {
  border: 2px solid #007acc;
  border-radius: .5rem;
  padding: 1rem;
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
  flex: 1 1 auto;
  overflow-y: auto;
  max-height: 100%;
  height: 100%;
}

.collection-topic-item.selected {
  background: #e3f2fd;
  border-color: #2196f3;
  box-shadow: 0 0 0 2px rgba(33, 150, 243, 0.2);
}

.collection-topic-item.drop-target {
  background: #fff3cd;
  border-color: #ffc107;
  box-shadow: 0 0 0 2px rgba(255, 193, 7, 0.3);
  transform: scale(1.02);
  transition: all 0.2s ease;
}

.multi-select-controls {
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  padding: 0.75rem;
  margin: 0.5rem 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  flex-wrap: wrap;
}

.selected-count {
  color: #495057;
  font-weight: 500;
  margin-right: 0.5rem;
}

.clear-btn, .move-btn {
  padding: 0.375rem 0.75rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.8rem;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.clear-btn {
  background: #6c757d;
  color: white;
}

.clear-btn:hover {
  background: #5a6268;
}

.move-btn {
  background: #28a745;
  color: white;
}

.move-btn:hover:not(:disabled) {
  background: #218838;
}

.move-btn:disabled {
  background: #6c757d;
  cursor: not-allowed;
  opacity: 0.6;
}

.move-target-select {
  padding: 0.375rem 0.5rem;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 0.8rem;
  background: white;
  cursor: pointer;
  min-width: 150px;
}

.move-target-select:focus {
  outline: none;
  border-color: #007acc;
  box-shadow: 0 0 0 2px rgba(0, 122, 204, 0.1);
}

.expand-controls {
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  padding: 0.5rem;
  margin: 0.5rem 0;
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.expand-btn {
  padding: 0.25rem 0.5rem;
  border: 1px solid #007acc;
  border-radius: 4px;
  background: white;
  color: #007acc;
  cursor: pointer;
  font-size: 0.8rem;
  transition: all 0.2s ease;
}

.expand-btn:hover {
  background: #007acc;
  color: white;
}

.expand-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  margin-right: 4px;
  cursor: pointer;
  border-radius: 3px;
  transition: background-color 0.2s ease;
}

.expand-toggle:hover {
  background: #f0f0f0;
}

.expand-spacer {
  width: 20px;
  margin-right: 4px;
}

.multi-drag-selected {
  background: #e3f2fd !important;
  border-color: #2196f3 !important;
  box-shadow: 0 0 0 2px rgba(33, 150, 243, 0.3) !important;
}

.collection-topic-item {
  display: flex;
  align-items: center;
  background: white;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 8px;
  margin-bottom: 4px;
  font-size: 14px;
  cursor: move;
  transition: all 0.2s ease;
  width: 100%;
  flex-wrap: nowrap;
  box-sizing: border-box;
  max-width: 100%;
}

.collection-topic-item-row {
  display: flex;
  align-items: center;
  width: 100%;
  min-width: 0;
  max-width: 100%;
  box-sizing: border-box;
}

.topic-content-row {
  display: flex;
  align-items: center;
  flex: 1;
  min-width: 0;
  max-width: 100%;
  box-sizing: border-box;
}

.topic-btn {
  width: 28px;
  height: 28px;
  min-width: 28px;
  min-height: 28px;
  max-width: 28px;
  max-height: 28px;
  font-size: 1rem;
  font-family: inherit;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f0f0f0;
  border: 1px solid #ccc;
  border-radius: 4px;
  margin-left: 2px;
  margin-right: 0;
  box-sizing: border-box;
  cursor: pointer;
  transition: background 0.2s, border 0.2s;
}

.collection-topic-item:hover {
  background: #f8f9fa;
  border-color: #007bff;
}

.collection-topic-item .drag-handle {
  margin-right: 8px;
  opacity: 0.5;
  cursor: grab;
}

.collection-topic-item .drag-handle:active {
  cursor: grabbing;
}

.collection-topic-item .topic-title {
  flex: 1 1 auto;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 200px;
}

.child-count {
  color: #6c757d;
  font-size: 12px;
  margin-left: 0.5rem;
  font-weight: 500;
}

.topic-wrapper {
  margin-bottom: 4px;
}

.child-topics {
  margin-left: 20px;
  margin-top: 4px;
}

.child-topics-list {
  min-height: 20px;
  padding: 4px;
  border-left: 2px solid #e9ecef;
  border-radius: 0 0 0 4px;
}

.child-topic {
  background: #f8f9fa !important;
  border-color: #e9ecef !important;
  margin-bottom: 2px !important;
  padding: 6px 8px !important;
  font-size: 13px !important;
}

.child-topic:hover {
  background: #e9ecef !important;
  border-color: #007bff !important;
}

.child-topic.selected {
  background: #d4edda !important;
  border-color: #28a745 !important;
  box-shadow: 0 0 0 1px rgba(40, 167, 69, 0.2) !important;
}

.child-topic .topic-title {
  max-width: 180px;
}

.topics-container {
  min-height: 50px;
  padding: 4px 0;
}

/* Remove the old topic-item styling that was too spacious */
.collection-topics-list .sortable-chosen {
  opacity: 0.5;
}

.collection-topics-list .sortable-ghost {
  opacity: 0.3;
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
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 250px;
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
  content: "No available topics";
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

/* Collection Edit Panel Styles */
.collection-edit-panel {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1rem;
}

.collection-edit-panel h3 {
  margin: 0 0 1rem 0;
  color: #495057;
  font-size: 1.1rem;
}

.edit-form {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group label {
  font-weight: 500;
  margin-bottom: 0.25rem;
  color: #495057;
  font-size: 0.9rem;
}

.edit-input {
  padding: 0.5rem;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 0.9rem;
  transition: border-color 0.15s ease-in-out;
}

.edit-input:focus {
  outline: none;
  border-color: #007acc;
  box-shadow: 0 0 0 2px rgba(0, 122, 204, 0.1);
}

/* Context Menu Styles */
.context-menu {
  position: fixed;
  background: white;
  border: 1px solid #ddd;
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  min-width: 180px;
  padding: 0.25rem 0;
}

.context-menu-item {
  padding: 0.5rem 1rem;
  cursor: pointer;
  font-size: 0.875rem;
  color: #333;
  transition: background-color 0.2s;
}

.context-menu-item:hover {
  background: #f8f9fa;
}

.context-menu-item.danger {
  color: #dc3545;
}

.context-menu-item.danger:hover {
  background: #f8d7da;
}

.context-menu-divider {
  height: 1px;
  background: #e9ecef;
  margin: 0.25rem 0;
}

.context-menu-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 999;
}

.topic-btn {
  width: 28px;
  height: 28px;
  min-width: 28px;
  min-height: 28px;
  max-width: 28px;
  max-height: 28px;
  font-size: 1rem;
  font-family: inherit;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f0f0f0;
  border: 1px solid #ccc;
  border-radius: 4px;
  margin-left: 2px;
  margin-right: 0;
  box-sizing: border-box;
  cursor: pointer;
  transition: background 0.2s, border 0.2s;
}

.topic-actions {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 0.25rem;
  margin-left: auto;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.35);
  z-index: 2000;
  display: flex;
  align-items: center;
  justify-content: center;
}
.modal-content.preview-modal {
  background: #fff;
  border-radius: 10px;
  max-width: 900px;
  width: 90vw;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 8px 32px rgba(0,0,0,0.25);
  padding: 0;
}
.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.5rem 0.5rem 1.5rem;
  border-bottom: 1px solid #eee;
}
.modal-body {
  padding: 1.5rem;
}
.btn-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #888;
  margin-left: 1rem;
}
.error {
  color: #dc3545;
  font-weight: bold;
  margin: 1rem 0;
}

.preview-icon-btn {
  width: 28px;
  height: 28px;
  min-width: 28px;
  min-height: 28px;
  max-width: 28px;
  max-height: 28px;
  margin-left: 2px;
  margin-right: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  font-size: 1rem;
  font-family: inherit;
  background: #f0f0f0;
  border: 1px solid #ccc;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.2s, border 0.2s;
  box-sizing: border-box;
}
.preview-icon-btn:hover {
  background: #e3f2fd;
}
</style>