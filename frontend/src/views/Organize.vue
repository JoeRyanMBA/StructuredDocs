<template>
  <div class="organize-view">
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
                :animation="200"
                :fallback-tolerance="5"
                :force-fallback="true"
                handle=".drag-handle"
              >
    <template #item="{ element: topic, index }">
                  <div 
                    class="topic-wrapper"
                    :data-topic-id="topic.id"
                  >
                    <div 
                      class="collection-topic-item"
                      :class="{ 
                        'selected': selectedTopics.has(topic.id),
                        'drop-target': dropTarget === topic.id
                      }"
                      
                      @click="handleTopicClick(topic, index, $event)"
                      @contextmenu="handleTopicRightClick(topic, index, $event)"
                      
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
        
        <!-- Multi-select controls for Available Topics -->
        <div v-if="selectedAvailableTopics.size > 0" class="multi-select-controls">
          <span class="selected-count">{{ selectedAvailableTopics.size }} topic(s) selected</span>
          <button @click="clearAvailableSelection" class="clear-btn">Clear Selection</button>
          <button @click="addSelectedToCollection" class="move-btn">Add to Collection</button>
        </div>
        
        <draggable
          :list="unassignedTopics"
          group="topics"
          item-key="id"
          @change="onTopicDrop"
          class="unassigned-list"
          handle=".drag-handle"
        >
          <template #item="{ element, index }">
            <div 
              class="unassigned-topic-item"
              :class="{ 'selected': selectedAvailableTopics.has(element.id) }"
              @click="handleAvailableTopicClick(element, index, $event)"
              @contextmenu="handleAvailableTopicRightClick(element, index, $event)"
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
              <span class="topic-title">{{ element.title }}</span>
              <div style="margin-left: auto; display: flex; align-items: center;">
                <button class="preview-icon-btn" @click.stop="previewTopic(element)" title="Preview this topic">
                  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 20 20" fill="none">
                    <path d="M10 4C5 4 1.73 8.11 1.08 9.01a1.5 1.5 0 0 0 0 1.98C1.73 11.89 5 16 10 16s8.27-4.11 8.92-5.01a1.5 1.5 0 0 0 0-1.98C18.27 8.11 15 4 10 4Zm0 10c-3.87 0-6.82-3.13-7.7-4C3.18 9.13 6.13 6 10 6s6.82 3.13 7.7 4c-.88.87-3.83 4-7.7 4Zm0-7a3 3 0 1 0 0 6 3 3 0 0 0 0-6Zm0 5a2 2 0 1 1 0-4 2 2 0 0 1 0 4Z" fill="#205493"/>
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
  components: { CollectionTree, TopicItem, draggable, TopicEditor },
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
      selectedAvailableTopics: new Set(), // Track selected available topic IDs
      lastSelectedIndex: -1, // Track last selected index for shift+click
      lastSelectedAvailableIndex: -1, // Track last selected index for shift+click in available topics
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
    
    try {
      // Load collections and topics (critical)
      const [collections, topics] = await Promise.all([
        getCollections(),
        getTopics()
      ])
      this.allCollections = collections
      this.topics = topics
      
      // Load projects separately with error handling (non-critical for viewing)
      try {
        const projects = await getProjects()
        this.projects = projects
      } catch (projectError) {
        console.warn('Failed to load projects, but continuing with collection view:', projectError)
        this.projects = [] // Default to empty array
      }
    } catch (error) {
      console.error('Failed to load critical data:', error)
      return
    }
    
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
      // Always allow moves - let vuedraggable handle everything
      // The custom drop handlers will only trigger for specific hierarchy creation
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

    clearAvailableSelection() {
      this.selectedAvailableTopics.clear()
      this.lastSelectedAvailableIndex = -1
    },

    // Available Topics selection methods
    handleAvailableTopicClick(topic, index, event) {
      event.preventDefault()
      event.stopPropagation()
      
      if (event.shiftKey && this.lastSelectedAvailableIndex !== -1) {
        // Shift+click: select range
        this.selectAvailableRange(this.lastSelectedAvailableIndex, index)
      } else if (event.ctrlKey || event.metaKey) {
        // Ctrl+click: toggle individual selection
        this.toggleAvailableTopicSelection(topic.id)
      } else {
        // Regular click: select only this topic
        this.clearAvailableSelection()
        this.selectAvailableTopic(topic.id)
        this.lastSelectedAvailableIndex = index
      }
    },

    handleAvailableTopicRightClick(topic, index, event) {
      event.preventDefault()
      
      // If right-clicking on unselected topic, select it
      if (!this.selectedAvailableTopics.has(topic.id)) {
        this.clearAvailableSelection()
        this.selectAvailableTopic(topic.id)
        this.lastSelectedAvailableIndex = index
      }
      
      // You can add context menu functionality here if needed
    },

    selectAvailableTopic(topicId) {
      this.selectedAvailableTopics.add(topicId)
    },

    toggleAvailableTopicSelection(topicId) {
      if (this.selectedAvailableTopics.has(topicId)) {
        this.selectedAvailableTopics.delete(topicId)
      } else {
        this.selectedAvailableTopics.add(topicId)
      }
    },

    selectAvailableRange(startIndex, endIndex) {
      const start = Math.min(startIndex, endIndex)
      const end = Math.max(startIndex, endIndex)
      
      for (let i = start; i <= end && i < this.unassignedTopics.length; i++) {
        this.selectedAvailableTopics.add(this.unassignedTopics[i].id)
      }
    },

    async addSelectedToCollection() {
      if (this.selectedAvailableTopics.size === 0) return
      
      const selectedTopicsToAdd = this.unassignedTopics.filter(topic => 
        this.selectedAvailableTopics.has(topic.id)
      )
      
      // Add selected topics to the collection
      this.currentCollection.topics.push(...selectedTopicsToAdd)
      
      // Clear selection
      this.clearAvailableSelection()
      
      // Save changes and refresh
      await this.saveChanges()
      this.unassignedTopics = this.getUnassignedTopics()
      
      this.confirmation = `Added ${selectedTopicsToAdd.length} topic(s) to collection!`
      setTimeout(() => { this.confirmation = '' }, 1500)
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
      // Only handle dragover for hierarchy creation (when dropping onto topics)
      // Don't interfere with vuedraggable's normal operations
      if (!this.draggedTopics.length && !this.selectedTopics.size) {
        return; // No topics being dragged, let vuedraggable handle it
      }
      
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
  padding: 2rem;
  background-color: var(--bg-light-mist-gray);
}

.organize-header {
  margin-bottom: 2rem;
}

.organize-header h1 {
  color: var(--primary-deep-teal);
  margin-bottom: 1rem;
}

.guidance-text {
  background: var(--bg-light-mist-gray);
  border-left: 4px solid var(--primary-deep-teal);
  padding: 1rem;
  margin-bottom: 1.5rem;
  color: var(--text-secondary-cool-gray);
  font-size: 0.95rem;
  line-height: 1.5;
}

.organize-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
}

.collections-panel, .topics-panel {
  background-color: white;
  border: 1px solid var(--extended-lavender-gray);
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.collections-panel h2, .topics-panel h2 {
  color: var(--primary-deep-teal);
  margin-top: 0;
  border-bottom: 2px solid var(--bg-light-mist-gray);
  padding-bottom: 0.5rem;
}

.collection-edit-panel {
  background-color: var(--bg-light-mist-gray);
  padding: 1rem;
  border-radius: 6px;
  margin-bottom: 1.5rem;
}

.edit-form .form-group {
  margin-bottom: 1rem;
}

.edit-form label {
  font-weight: 600;
  color: var(--text-primary-charcoal);
}

.edit-input {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid var(--extended-lavender-gray);
  border-radius: 4px;
}

.multi-select-controls {
  background-color: var(--extended-sky-blue);
  padding: 0.75rem;
  border-radius: 6px;
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.selected-count {
  font-weight: 600;
  color: var(--primary-deep-teal);
}

.clear-btn, .move-btn {
  background-color: var(--primary-deep-teal);
  color: white;
  border: none;
  padding: 0.25rem 0.75rem;
  border-radius: 4px;
  cursor: pointer;
}

.move-target-select {
  padding: 0.25rem;
  border-radius: 4px;
}

.expand-controls {
  margin-bottom: 1rem;
  display: inline-flex;
  gap: 0.5rem;
}

.expand-btn {
  background-color: var(--extended-lavender-gray);
  color: var(--text-primary-charcoal);
  border: none;
  padding: 0.25rem 0.75rem;
  border-radius: 4px;
  cursor: pointer;
}

.collection-topics-list, .unassigned-list {
  min-height: 200px;
  border: 1px dashed var(--extended-lavender-gray);
  padding: 0.5rem;
  border-radius: 4px;
}

.topic-wrapper.drop-target {
  background-color: var(--extended-cool-mint);
}

.collection-topic-item, .unassigned-topic-item {
  background-color: white;
  border: 1px solid var(--extended-lavender-gray);
  padding: 0.5rem;
  margin-bottom: 0.5rem;
  border-radius: 4px;
  display: flex;
  align-items: center;
  cursor: pointer;
}

.collection-topic-item.selected, .unassigned-topic-item.selected {
  background-color: var(--extended-sky-blue);
  border-color: var(--primary-deep-teal);
}

.drag-handle {
  cursor: grab;
  margin-right: 0.5rem;
}

.topic-title {
  flex-grow: 1;
}

.child-count {
  color: var(--text-secondary-cool-gray);
  margin-left: 0.5rem;
}

.topic-actions button {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.25rem;
}

.child-topics {
  margin-left: 2rem;
  padding-left: 1rem;
  border-left: 2px solid var(--extended-lavender-gray);
}

.publish-buttons {
  margin-top: 1.5rem;
  display: flex;
  gap: 1rem;
}

.publish-btn, .publish-btn-disabled {
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
}

.publish-html {
  background-color: var(--primary-deep-teal);
  color: white;
}

.publish-pdf {
  background-color: var(--error-coral-red);
  color: white;
}

.publish-btn-disabled {
  background-color: var(--extended-lavender-gray);
  color: var(--text-secondary-cool-gray);
  cursor: not-allowed;
}

.empty-collection {
  text-align: center;
  padding: 2rem;
  color: var(--text-secondary-cool-gray);
}

.organize-actions {
  margin-top: 2rem;
  display: inline-flex;
  gap: 0.75rem;
  align-items: center;
}

.organize-actions button {
  background-color: var(--success-mint-green);
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  cursor: pointer;
}

.confirmation {
  color: var(--success-mint-green);
  margin-left: 1rem;
  font-weight: 600;
}

.context-menu {
  position: fixed;
  background-color: white;
  border: 1px solid var(--extended-lavender-gray);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  border-radius: 6px;
  padding: 0.5rem 0;
  z-index: 1000;
}

.context-menu-item {
  padding: 0.5rem 1rem;
  cursor: pointer;
}

.context-menu-item:hover {
  background-color: var(--bg-light-mist-gray);
}

.context-menu-item.danger {
  color: var(--error-coral-red);
}

.context-menu-divider {
  height: 1px;
  background-color: var(--extended-lavender-gray);
  margin: 0.5rem 0;
}

.context-menu-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 999;
}

/* Using global .modal-overlay and .modal styles from assets/style.css */

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--extended-lavender-gray);
  padding-bottom: 1rem;
  margin-bottom: 1rem;
}

.btn-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
}
</style>