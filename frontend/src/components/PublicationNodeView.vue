<template>
  <ul class="publication-tree" v-if="nodes && nodes.length">
    <li v-for="node in nodes" :key="node.id" class="tree-item">
      <span class="topic-title">{{ node.topic.title }}</span>
      
      <!-- Recurse into children if present -->
      <PublicationNodeView
        v-if="node.children && node.children.length"
        :nodes="node.children"
      />
    </li>
  </ul>
</template>

<script>
export default {
  name: 'PublicationNodeView',
  props: {
    nodes: {
      type: Array,
      required: true
    }
  }
}
</script>

<style>
.publication-tree {
  list-style: none;
  padding-left: 0;
  margin: 0;
}

.tree-item {
  margin: 0.25rem 0;
  padding: 0.25rem 0;
}

.topic-title {
  color: #333;
  font-size: 0.95rem;
  line-height: 1.4;
}

/* Indent nested levels */
.publication-tree .publication-tree {
  padding-left: 1.5rem;
  margin-top: 0.5rem;
  border-left: 2px solid #e1e5e9;
}

/* Different styling for different nesting levels */
.publication-tree .publication-tree .topic-title {
  color: #666;
  font-size: 0.9rem;
}

.publication-tree .publication-tree .publication-tree .topic-title {
  color: #888;
  font-size: 0.85rem;
}
</style>
