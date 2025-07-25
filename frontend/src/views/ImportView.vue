<template>
  <div class="import-view">
    <h2>Import Topics</h2>

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
export default {
  name: 'ImportView',

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
  padding: 2rem;
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