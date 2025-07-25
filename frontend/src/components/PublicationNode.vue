<template>
  <draggable
    :list="localNodes"
    item-key="id"
    group="nodes"
    handle=".drag-handle"
    @change="onDragChange"
  >
    <template #item="{ element }">
      <div class="node">
        <span class="drag-handle">☰</span>
        {{ element.topic.title }}

        <!-- Recurse into children if present -->
        <PublicationNode
          v-if="element.children && element.children.length"
          :nodes="element.children"
          @update="children => updateChildren(element.id, children)"
        />
      </div>
    </template>
  </draggable>
</template>

<script>
import draggable from 'vuedraggable'

export default {
  name: 'PublicationNode',
  components: { draggable },

  props: {
    nodes: {
      type: Array,
      required: true
    }
  },

  emits: ['update'],

  data() {
    return {
      // local copy so we don’t mutate the prop directly
      localNodes: this._cloneNodes(this.nodes)
    }
  },

  watch: {
    // if the parent ever swaps out `nodes`, re‐clone
    nodes: {
      handler(newVal) {
        this.localNodes = this._cloneNodes(newVal)
      },
      deep: true
    }
  },

  methods: {
    // deep‐clone helper
    _cloneNodes(arr) {
      return arr.map(n => ({
        ...n,
        children: n.children ? this._cloneNodes(n.children) : []
      }))
    },

    // Called after drag‐and‐drop reorders `localNodes`
    onDragChange() {
      // Re‐assign positions based on new index
      this.localNodes.forEach((node, idx) => {
        node.position = idx
      })
      this._emitUpdate()
    },

    // Called when a child PublicationNode emits an update
    updateChildren(parentId, updatedChildren) {
      const recurse = list => {
        for (const node of list) {
          if (node.id === parentId) {
            node.children = this._cloneNodes(updatedChildren)
            return true
          }
          if (node.children && recurse(node.children)) {
            return true
          }
        }
        return false
      }
      recurse(this.localNodes)
      this._emitUpdate()
    },

    // Emit a deep copy so parent state stays immutable
    _emitUpdate() {
      const payload = JSON.parse(JSON.stringify(this.localNodes))
      this.$emit('update', payload)
    }
  }
}
</script>

<style scoped>
.node {
  margin: 0.5rem 0;
  padding: 0.5rem;
  border: 1px solid #ddd;
  background: #f9f9f9;
}

.drag-handle {
  cursor: grab;
  margin-right: 0.5rem;
}
</style>