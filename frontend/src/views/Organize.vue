<template>
  <div class="organize-layout">
    <div class="collections-panel">
      <h2>Collections</h2>
      <CollectionTree :tree="collections" @update="onTreeUpdate" />
    </div>
    <div class="topics-panel">
      <h2>Unassigned Topics</h2>
      <draggable
        :list="unassignedTopics"
        group="topics"
        item-key="id"
        @change="onTopicDrop"
      >
        <template #item="{ element }">
          <div class="topic-item">{{ element.title }}</div>
        </template>
      </draggable>
    </div>
  </div>
      <button @click="saveChanges">Save</button>
    <button @click="onTopicDrop">Refresh Topics</button>
    <span v-if="confirmation" class="confirmation">{{ confirmation }}</span>
</template>

<script>
import CollectionTree from '@/components/CollectionTree.vue'
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
  components: { CollectionTree, draggable },
  data() {
    return {
      collections: [],
      topics: [],
      unassignedTopics: [],
      confirmation: '' // <-- Add this
    }
  },
  async created() {
    this.collections = await getCollections()
    this.topics = await getTopics()
    this.unassignedTopics = this.getUnassignedTopics()
  },
  methods: {
    getUnassignedTopics() {
      // Flatten all topics assigned to collections
      const assignedIds = new Set()
      const walk = nodes => {
        nodes.forEach(col => {
          if (col.topics) col.topics.forEach(t => assignedIds.add(t.id))
          if (col.children) walk(col.children)
        })
      }
      walk(this.collections)
      // Filter out assigned topics
      return this.topics.filter(t => !assignedIds.has(t.id))
    },
    async onTreeUpdate(newTree) {
      this.collections = newTree
      console.log('Updated collections:', JSON.stringify(this.collections, null, 2))
      await saveCollections(newTree)
      this.unassignedTopics = this.getUnassignedTopics()
    },
    async onTopicDrop() {
      this.unassignedTopics = this.getUnassignedTopics()
      await saveCollections(this.collections)
      this.confirmation = 'Topics refreshed!'
      setTimeout(() => { this.confirmation = '' }, 1500)
    },
    async saveChanges() {
      await saveCollections(this.collections)
      this.confirmation = 'Collections saved!'
      setTimeout(() => { this.confirmation = '' }, 1500)
    }
  }
}
</script>

<style scoped>
.organize-layout {
  display: flex;
  gap: 2rem;
}
.collections-panel, .topics-panel {
  flex: 1;
  background: #f8f8f8;
  padding: 1rem;
  border-radius: 8px;
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
</style>