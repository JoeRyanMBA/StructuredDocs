<template>
  <div class="publication-view" v-if="pub">
    <h1>{{ pub.title }}</h1>
    <p>{{ pub.description }}</p>

    <!-- top‐level tree -->
    <PublicationNode
      :nodes="tree"
      @update="tree = $event"
    />

    <div class="actions">
      <button @click="saveTree">Save Structure</button>
      <button @click="downloadPDF">Download PDF</button>
    </div>
  </div>
</template>

<script>
import PublicationNode from '@/components/PublicationNode.vue'

export default {
  name: 'PublicationView',
  components: { PublicationNode },
  props: {
    id: { type: [String, Number], required: true }
  },
  data() {
    return {
      pub: null,
      tree: []
    }
  },
  async created() {
    // now this.id is defined
    const res  = await fetch(`/api/publications/${this.id}`)
    const json = await res.json()
    this.pub  = { title: json.title, description: json.description }
    this.tree = json.tree
  },
  methods: {
    async saveTree() {
      await fetch(`/api/publications/${this.id}/nodes`, {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({ tree: this.tree })
      })
    },
    downloadPDF() {
      window.open(`/api/publications/${this.id}/export/pdf`, '_blank')
    }
  }
}
</script>

<style scoped>
.publication-view { padding:2rem; }
.actions { margin-top:1rem; display:flex; gap:1rem; }
.actions button {
  padding:.5rem 1rem; border:none; background:#005a9c; color:white; border-radius:4px;
}
</style>