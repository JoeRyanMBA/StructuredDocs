<template>
  <ul class="publication-tree">
    <li v-for="node in nodes" :key="node.id" class="tree-node-item">
      <div
        class="tree-node"
        :class="{ active: selectedId === node.id }"
        @click="$emit('select', node)"
      >
        <button
          v-if="node.children && node.children.length"
          class="expand-btn"
          @click.stop="toggle(node.id)"
          :aria-label="expanded.has(node.id) ? 'Collapse' : 'Expand'"
        >{{ expanded.has(node.id) ? '▾' : '▸' }}</button>
        <span v-else class="expand-spacer"></span>
        <span class="node-title">{{ node.title }}</span>
      </div>
      <PublicationNodeView
        v-if="node.children && node.children.length && expanded.has(node.id)"
        :nodes="node.children"
        :selected-id="selectedId"
        @select="$emit('select', $event)"
      />
    </li>
  </ul>
</template>

<script>
export default {
  name: 'PublicationNodeView',
  props: {
    nodes:      { type: Array,  required: true },
    selectedId: { type: Number, default: null },
  },
  emits: ['select'],
  data() {
    return { expanded: new Set() }
  },
  created() {
    // Expand all nodes that have children by default
    this.nodes.forEach(n => {
      if (n.children && n.children.length) this.expanded.add(n.id)
    })
  },
  methods: {
    toggle(id) {
      if (this.expanded.has(id)) {
        this.expanded.delete(id)
      } else {
        this.expanded.add(id)
      }
      // Force reactivity on the Set
      this.expanded = new Set(this.expanded)
    }
  }
}
</script>

<style scoped>
.publication-tree {
  list-style: none;
  padding: 0;
  margin: 0;
}

.tree-node-item {
  margin: 0;
}

.tree-node {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.4rem 0.5rem;
  border-radius: 4px;
  cursor: pointer;
  user-select: none;
  transition: background 0.12s;
}

.tree-node:hover {
  background: var(--extended-sky-blue, #dbeafe);
}

.tree-node.active {
  background: var(--primary-deep-teal, #005b6e);
  color: #fff;
}

.tree-node.active .node-title {
  color: #fff;
  font-weight: 600;
}

.expand-btn {
  flex-shrink: 0;
  width: 18px;
  height: 18px;
  background: none;
  border: none;
  padding: 0;
  cursor: pointer;
  font-size: 0.8rem;
  color: inherit;
  display: flex;
  align-items: center;
  justify-content: center;
}

.expand-spacer {
  flex-shrink: 0;
  width: 18px;
}

.node-title {
  flex: 1;
  font-size: 0.88rem;
  line-height: 1.35;
  color: var(--text-primary-charcoal, #2d3748);
  word-break: break-word;
}

/* Indent nested levels */
.publication-tree .publication-tree {
  padding-left: 1.25rem;
  border-left: 2px solid var(--extended-lavender-gray, #e2e8f0);
  margin-left: 0.5rem;
  margin-top: 2px;
}
</style>
