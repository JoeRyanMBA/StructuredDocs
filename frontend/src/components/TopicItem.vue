<!-- filepath: c:\Dev\StructuredDocs\frontend\src\components\TopicItem.vue -->
<template>
  <div class="topic-item" :class="{ 'is-nested': isNested }">
    <div class="topic-content">
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
      <span class="topic-title">{{ topic.title || topic.label }}</span>
    </div>
    
    <!-- Nested topics (if any) -->
    <div v-if="topic.children && topic.children.length" class="nested-topics">
      <draggable
        :list="topic.children"
        group="topics"
        item-key="id"
        @change="onNestedChange"
        class="nested-draggable"
        :fallback-tolerance="5"
        :force-fallback="true"
      >
        <template #item="{ element: childTopic }">
          <TopicItem :topic="childTopic" :is-nested="true" @update="onNestedUpdate" />
        </template>
      </draggable>
    </div>
    
    <!-- Drop zone for creating nested topics -->
    <div v-else class="drop-zone">
      <draggable
        :list="topic.children || []"
        group="topics"
        item-key="id"
        @change="onNestedChange"
        class="empty-nested-draggable"
        :fallback-tolerance="5"
        :force-fallback="true"
      >
        <template #item="{ element: childTopic }">
          <TopicItem :topic="childTopic" :is-nested="true" @update="onNestedUpdate" />
        </template>
      </draggable>
    </div>
  </div>
</template>

<script>
import draggable from 'vuedraggable'

export default {
  name: 'TopicItem',
  components: { draggable },
  props: {
    topic: {
      type: Object,
      required: true
    },
    isNested: {
      type: Boolean,
      default: false
    }
  },
  emits: ['update'],
  methods: {
    onNestedChange(event) {
      console.log('Nested change detected:', event)
      // Ensure topic has children array
      if (!this.topic.children) {
        this.topic.children = []
      }
      this.$emit('update', this.topic)
    },
    onNestedUpdate(updatedTopic) {
      console.log('Nested topic updated:', updatedTopic)
      this.$emit('update', updatedTopic)
    }
  },
  created() {
    // Ensure topic has children array for drag and drop
    if (!this.topic.children) {
      this.topic.children = []
    }
  }
}
</script>

<style>
.topic-item {
  background: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  margin-bottom: 4px;
  transition: all 0.2s ease;
}

.topic-item:hover {
  border-color: #205493;
  box-shadow: 0 2px 4px rgba(0, 122, 204, 0.1);
}

.topic-item.is-nested {
  margin-left: 20px;
  border-left: 3px solid #205493;
  background: #f8fafe;
}

.topic-content {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  cursor: grab;
}

.topic-content:active {
  cursor: grabbing;
}

.drag-handle {
  margin-right: 8px;
  cursor: grab;
  opacity: 0.6;
  transition: opacity 0.2s ease;
  flex-shrink: 0;
}

.topic-content:hover .drag-handle {
  opacity: 1;
}

.topic-title {
  flex: 1;
  font-size: 14px;
  color: #333;
  line-height: 1.4;
}

.nested-topics {
  padding: 4px 8px 8px 8px;
  background: #fafbfc;
  border-top: 1px solid #e8e8e8;
}

.nested-draggable {
  min-height: 20px;
}

.drop-zone {
  min-height: 20px;
  margin-left: 20px;
  border-left: 2px dashed transparent;
  transition: border-color 0.2s ease;
}

.empty-nested-draggable {
  min-height: 20px;
  padding: 4px;
}

/* Enhanced drag feedback */
.topic-item:hover .drop-zone {
  border-left-color: #205493;
}

/* Drag placeholder styling */
.sortable-ghost {
  opacity: 0.5;
  background: #205493 !important;
}

.sortable-chosen {
  background: #e3f2fd;
}

.sortable-drag {
  opacity: 0.8;
  transform: rotate(2deg);
}
</style>