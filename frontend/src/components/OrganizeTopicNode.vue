<template>
  <div class="topic-wrapper" :data-topic-id="topic.id">
    <div
      class="collection-topic-item"
      :class="{
        'selected': organizeView.selectedTopics.has(topic.id),
        'drop-target': organizeView.dropTarget === topic.id
      }"
      @click="handleClick"
      @contextmenu="handleRightClick"
    >
      <div class="collection-topic-item-row" style="display: flex; align-items: center; width: 100%;">
        <div v-if="topic.children && topic.children.length > 0" class="expand-toggle" @click.stop="organizeView.toggleExpansion(topic.id)">
          <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
            <path v-if="organizeView.expandedTopics.has(topic.id)" d="M3 4.5L6 7.5L9 4.5" :stroke="organizeView.arrowColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            <path v-else d="M4.5 3L7.5 6L4.5 9" :stroke="organizeView.arrowColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
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
          <span class="topic-id-badge">#{{ topic.id }}</span>
          <span class="topic-title">{{ topic.title }}</span>
          <span :class="['topic-status-badge', 'status-' + (topic.status || 'draft')]">{{ topic.status || 'draft' }}</span>
          <span v-if="topic.children && topic.children.length > 0" class="child-count">
            ({{ topic.children.length }})
          </span>
          <div class="topic-actions" style="margin-left: auto;">
            <button class="icon-btn" @click.stop="organizeView.previewTopic(topic)" title="Preview this topic" aria-label="Preview topic">
              <i class="bi bi-zoom-in" aria-hidden="true"></i>
            </button>
            <button class="topic-btn up" @click.stop="organizeView.moveTopicUp(topic)">▲</button>
            <button class="topic-btn down" @click.stop="organizeView.moveTopicDown(topic)">▼</button>
            <!-- Hide indent button at max depth (H5 = depth 4) -->
            <button v-if="depth < 4" class="topic-btn right" @click.stop="organizeView.indentTopic(topic)">▶</button>
            <button class="topic-btn left" @click.stop="organizeView.outdentTopic(topic)">◀</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Recursively render children when expanded (supports up to H5 = depth 4) -->
    <div
      v-if="topic.children && topic.children.length > 0 && organizeView.expandedTopics.has(topic.id)"
      class="child-topics"
    >
      <draggable
        :list="topic.children"
        group="topics"
        item-key="id"
        @change="organizeView.onTopicDrop"
        class="child-topics-list"
        :fallback-tolerance="5"
        :force-fallback="true"
        handle=".drag-handle"
      >
        <template #item="{ element: childTopic }">
          <OrganizeTopicNode :topic="childTopic" :depth="depth + 1" />
        </template>
      </draggable>
    </div>
  </div>
</template>

<script>
import draggable from 'vuedraggable'

export default {
  name: 'OrganizeTopicNode',
  components: { draggable },
  inject: ['organizeView'],
  props: {
    topic: {
      type: Object,
      required: true
    },
    depth: {
      type: Number,
      default: 0
    },
    topicIndex: {
      type: Number,
      default: -1
    }
  },
  methods: {
    handleClick(event) {
      event.preventDefault()
      event.stopPropagation()
      if (this.depth === 0 && event.shiftKey && this.organizeView.lastSelectedIndex !== -1) {
        this.organizeView.selectRange(this.organizeView.lastSelectedIndex, this.topicIndex)
      } else if (event.ctrlKey || event.metaKey) {
        this.organizeView.toggleTopicSelection(this.topic.id)
      } else {
        this.organizeView.clearSelection()
        this.organizeView.selectTopic(this.topic.id)
        if (this.depth === 0) {
          this.organizeView.lastSelectedIndex = this.topicIndex
        }
      }
    },
    handleRightClick(event) {
      this.organizeView.handleTopicRightClick(this.topic, this.topicIndex, event)
    }
  }
}
</script>
