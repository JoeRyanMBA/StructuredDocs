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
        <ul>
          <draggable
            :list="element.topics"
            group="topics"
            item-key="id"
            @change="onDrag"
          >
            <template #item="{ element: topic }">
              <li>
                <TopicItem :topic="topic" />
              </li>
            </template>
          </draggable>
        </ul>
        
        <!-- Conditionally show Publish for this collection -->
        <button
          v-if="element.topics && element.topics.length"
          @click="goPublish(element.id)"
        >
          Publish Document
        </button>

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
    goPublish(collectionId) {
      this.$router.push({ name: 'PublicationView', params: { id: collectionId } })
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
</style>