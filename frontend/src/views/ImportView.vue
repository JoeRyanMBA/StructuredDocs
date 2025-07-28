<template>
  <div class="import-view">
    <Breadcrumbs />
    <h2>Import Topics</h2>
    
    <p class="guidance-text">
      Use this tool to import content from outside this app. You can import Markdown (.md) documents (preferred) or Word (.docx) documents.
    </p>

    <label>
      Format
      <select v-model="source">
        <option value="markdown">Markdown</option>
        <option value="word">Word (.docx)</option>
      </select>
    </label>

    <input
      ref="fileInput"
      type="file"
      @change="onFileSelected"
      :accept="acceptedTypes"
    />

    <div v-if="error" class="error">{{ error }}</div>
  </div>
</template>

<script>
import Breadcrumbs from '@/components/Breadcrumbs.vue'

export default {
  name: 'ImportView',
  components: { Breadcrumbs },

  data() {
    return {
      source: 'markdown',
      error: null
    }
  },

  computed: {
    acceptedTypes() {
      return this.source === 'word' ? '.docx' : '.md,.markdown'
    }
  },

  methods: {
    async onFileSelected(event) {
      this.error = null
      const file = event.target.files[0]
      if (!file) return

      const form = new FormData()
      form.append('file', file)
      form.append('source', this.source)

      try {
        const res = await fetch('/api/import/upload', {
          method: 'POST',
          body: form
        })

        // Always read text first
        const text = await res.text()

        // Try parse JSON if appropriate
        let importDoc = null
        const ct = res.headers.get('content-type') || ''
        if (ct.includes('application/json')) {
          importDoc = JSON.parse(text)
        }

        // On error status, throw with message from payload or raw text
        if (!res.ok) {
          const msg = importDoc?.error || text || `HTTP ${res.status}`
          throw new Error(msg)
        }

        // Ensure we got an ID
        if (!importDoc || typeof importDoc.id !== 'number') {
          throw new Error('Invalid response from import endpoint')
        }

        console.log('Upload successful, import doc:', importDoc) // Debug log

        // Navigate to review, passing ID as param
        this.$router.push({
          name: 'ImportReview',
          params: { id: importDoc.id }
        })

      } catch (err) {
        console.error('Import failed:', err)
        this.error = `Import failed: ${err.message}`
      } finally {
        // Clear the file input so the same file can be re‐selected
        this.$refs.fileInput.value = null
      }
    }
  }
}
</script>

<style scoped>
.import-view {
  padding-top: 70px; /* Top padding to account for fixed header */
  padding-left: 2rem;
  padding-right: 2rem;
  padding-bottom: 2rem;
}

.guidance-text {
  background: #f8f9fa;
  border-left: 4px solid #007acc;
  padding: 1rem;
  margin-bottom: 1.5rem;
  color: #495057;
  font-size: 0.95rem;
  line-height: 1.5;
}

label {
  display: block;
  margin-bottom: 1rem;
}

input[type="file"] {
  display: block;
  margin-bottom: 1rem;
}

.error {
  color: #c00;
  font-weight: bold;
  margin-top: 1rem;
}
</style>