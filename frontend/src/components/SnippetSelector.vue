<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h3>📎 Insert Snippet</h3>
        <button class="close-btn" @click="$emit('close')" aria-label="Close">×</button>
      </div>
      <div class="modal-body">
        <input
          v-model="search"
          type="text"
          class="search-input"
          placeholder="Search snippets…"
          autofocus
        />
        <div v-if="loading" class="state-msg">Loading snippets…</div>
        <div v-else-if="filtered.length === 0" class="state-msg">No snippets found.</div>
        <ul v-else class="snippet-list">
          <li
            v-for="snippet in filtered"
            :key="snippet.id"
            class="snippet-item"
            @click="select(snippet)"
          >
            <div class="snippet-title">{{ snippet.title }}</div>
            <div class="snippet-tags">
              <span v-for="tag in snippet.tags" :key="tag.id" class="tag-badge">{{ tag.name }}</span>
              <span v-if="!snippet.tags || snippet.tags.length === 0" class="no-tags">No tags</span>
            </div>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script>
import { listSnippets } from '@/api/snippets.js'

export default {
  name: 'SnippetSelector',
  emits: ['select', 'close'],
  data() {
    return {
      snippets: [],
      search: '',
      loading: true,
    }
  },
  computed: {
    filtered() {
      const q = this.search.toLowerCase()
      return this.snippets.filter(s => s.title.toLowerCase().includes(q))
    },
  },
  async mounted() {
    try {
      this.snippets = await listSnippets()
    } catch (e) {
      console.error('Failed to load snippets', e)
    } finally {
      this.loading = false
    }
  },
  methods: {
    select(snippet) {
      this.$emit('select', snippet)
    },
  },
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}
.modal-content {
  background: #fff;
  border-radius: 8px;
  width: 480px;
  max-width: 95vw;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 8px 32px rgba(0,0,0,0.18);
}
.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem 0.75rem;
  border-bottom: 1px solid #e9ecef;
}
.modal-header h3 { margin: 0; font-size: 1.05rem; }
.close-btn {
  background: none;
  border: none;
  font-size: 1.4rem;
  cursor: pointer;
  color: #6c757d;
  line-height: 1;
  padding: 0;
}
.close-btn:hover { color: #333; }
.modal-body {
  padding: 1rem 1.25rem;
  overflow-y: auto;
  flex: 1;
}
.search-input {
  width: 100%;
  padding: 0.5rem 0.75rem;
  border: 1px solid #ced4da;
  border-radius: 6px;
  font-size: 0.9rem;
  margin-bottom: 0.75rem;
  box-sizing: border-box;
}
.search-input:focus { outline: none; border-color: #205493; }
.state-msg { color: #6c757d; font-size: 0.9rem; text-align: center; padding: 1rem 0; }
.snippet-list { list-style: none; margin: 0; padding: 0; }
.snippet-item {
  padding: 0.65rem 0.75rem;
  border-radius: 6px;
  cursor: pointer;
  border: 1px solid transparent;
  margin-bottom: 0.35rem;
  transition: background 0.15s;
}
.snippet-item:hover { background: #f0f4ff; border-color: #c5d3f0; }
.snippet-title { font-weight: 500; font-size: 0.9rem; color: #212529; }
.snippet-tags { margin-top: 0.3rem; display: flex; flex-wrap: wrap; gap: 0.25rem; }
.tag-badge {
  background: #e3f2fd;
  color: #1565c0;
  border: 1px solid #bbdefb;
  border-radius: 10px;
  padding: 0.1rem 0.45rem;
  font-size: 0.75rem;
}
.no-tags { color: #adb5bd; font-size: 0.75rem; font-style: italic; }
</style>
