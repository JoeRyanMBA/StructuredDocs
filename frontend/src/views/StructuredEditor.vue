<template>
  <div>
    <h2>Organize Collections & Topics</h2>
    <collection-tree
      :tree="treeData"
      @update="treeData = $event"
    />
    <button @click="saveTree">Save Structure</button>
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