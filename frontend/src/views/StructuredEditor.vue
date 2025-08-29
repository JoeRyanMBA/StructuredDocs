<template>
  <div class="structured-editor-view">
    <h2>Organize Collections & Topics</h2>
    <collection-tree
      :tree="treeData"
      @update="treeData = $event"
    />
    <button @click="saveTree" class="btn btn-primary">Save Structure</button>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { getCollections, saveCollections } from '@/api/collections'
import CollectionTree from '@/components/CollectionTree.vue'

export default {
  components: { CollectionTree },
  setup() {
    const treeData = ref([])

    const load = async () => {
      treeData.value = await getCollections()
    }
    onMounted(load)

    const saveTree = async () => {
      try {
        await saveCollections(treeData.value)
        alert('Structure saved!')
      } catch (e) {
        console.error(e)
        alert('Failed to save structure')
      }
    }

    return { treeData, saveTree }
  }
}
</script>

<style scoped>
.structured-editor-view {
  padding: 2rem;
  background-color: var(--bg-light-gray);
}

h2 {
  color: var(--text-dark-gray);
  margin-bottom: 1.5rem;
}

.btn {
  margin-top: 1.5rem;
  padding: 0.75rem 1.5rem;
  border-radius: var(--border-radius-md);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid transparent;
}

.btn-primary {
  background-color: var(--primary-deep-teal);
  color: var(--bg-white);
}

.btn-primary:hover {
  background-color: var(--primary-dark-blue);
}
</style>