<template>
  <div class="tag-editor">
    <!-- Existing tag chips -->
    <div class="tag-chips">
      <span v-for="tag in assignedTags" :key="tag.id" class="tag-chip">
        {{ tag.name }}
        <button type="button" class="chip-remove" @click="removeTag(tag.id)" aria-label="Remove tag">×</button>
      </span>

      <!-- Inline add control -->
      <div class="tag-add-wrap" ref="addWrap">
        <input
          ref="input"
          v-model="query"
          type="text"
          class="tag-input"
          placeholder="Add tag…"
          @focus="open = true"
          @input="open = true"
          @keydown.enter.prevent="selectHighlighted"
          @keydown.escape="close"
          @keydown.down.prevent="moveHighlight(1)"
          @keydown.up.prevent="moveHighlight(-1)"
        />
        <ul v-if="open && filtered.length" class="tag-dropdown">
          <li
            v-for="(tag, i) in filtered"
            :key="tag.id"
            :class="{ highlighted: i === highlightIndex }"
            @mousedown.prevent="addTag(tag)"
          >
            {{ tag.name }}
          </li>
        </ul>
        <ul v-else-if="open && query.length >= 2 && canCreate" class="tag-dropdown">
          <li class="create-option" @mousedown.prevent="createAndAdd">
            Create "<strong>{{ query }}</strong>"
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script>
import { apiRequest } from '../api/base.js'

export default {
  name: 'TagEditor',
  props: {
    entityType: { type: String, required: true },
    entityId:   { type: Number, required: true },
    canCreate:  { type: Boolean, default: true },
  },
  data() {
    return {
      assignedTags: [],   // [{id, name}]
      allTags: [],        // [{id, name}] — full tag library
      query: '',
      open: false,
      highlightIndex: -1,
      loading: false,
    }
  },
  computed: {
    assignedIds() {
      return new Set(this.assignedTags.map(t => t.id))
    },
    filtered() {
      const q = this.query.toLowerCase()
      return this.allTags.filter(t =>
        !this.assignedIds.has(t.id) &&
        t.name.toLowerCase().includes(q)
      ).slice(0, 10)
    },
  },
  watch: {
    entityId(newVal) {
      if (newVal) this.loadTags()
    },
  },
  async mounted() {
    await Promise.all([this.loadAllTags(), this.loadTags()])
    document.addEventListener('click', this.handleOutsideClick)
  },
  beforeUnmount() {
    document.removeEventListener('click', this.handleOutsideClick)
  },
  methods: {
    async loadTags() {
      if (!this.entityId) return
      try {
        const data = await apiRequest(`/api/tags/entity/${this.entityType}/${this.entityId}`)
        this.assignedTags = Array.isArray(data) ? data : []
      } catch { this.assignedTags = [] }
    },
    async loadAllTags() {
      try {
        const data = await apiRequest('/api/tags/')
        this.allTags = Array.isArray(data) ? data : (data.tags || [])
      } catch { this.allTags = [] }
    },
    async save() {
      await apiRequest(`/api/tags/entity/${this.entityType}/${this.entityId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tag_ids: [...this.assignedIds] }),
      })
      this.$emit('change', this.assignedTags)
    },
    async addTag(tag) {
      if (!this.assignedIds.has(tag.id)) {
        this.assignedTags.push(tag)
        await this.save()
      }
      this.close()
    },
    async removeTag(tagId) {
      this.assignedTags = this.assignedTags.filter(t => t.id !== tagId)
      await this.save()
    },
    async createAndAdd() {
      const name = this.query.trim()
      if (!name) return
      try {
        const tag = await apiRequest('/api/tags/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ name }),
        })
        this.allTags.push(tag)
        await this.addTag(tag)
      } catch (e) {
        console.error('Failed to create tag', e)
      }
    },
    selectHighlighted() {
      if (this.highlightIndex >= 0 && this.filtered[this.highlightIndex]) {
        this.addTag(this.filtered[this.highlightIndex])
      } else if (this.query.length >= 2 && this.canCreate) {
        this.createAndAdd()
      }
    },
    moveHighlight(dir) {
      const max = this.filtered.length - 1
      this.highlightIndex = Math.max(0, Math.min(max, this.highlightIndex + dir))
    },
    close() {
      this.open = false
      this.query = ''
      this.highlightIndex = -1
    },
    handleOutsideClick(e) {
      if (this.$refs.addWrap && !this.$refs.addWrap.contains(e.target)) {
        this.close()
      }
    },
  },
}
</script>

<style scoped>
.tag-editor { display: inline-block; width: 100%; }

.tag-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.375rem;
  align-items: center;
  min-height: 2rem;
}

.tag-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  background: #e3f2fd;
  color: #1565c0;
  border: 1px solid #bbdefb;
  border-radius: 12px;
  padding: 0.125rem 0.5rem;
  font-size: 0.8rem;
  font-weight: 500;
}

.chip-remove {
  background: none;
  border: none;
  color: #1565c0;
  cursor: pointer;
  font-size: 1rem;
  line-height: 1;
  padding: 0;
  opacity: 0.6;
}
.chip-remove:hover { opacity: 1; }

.tag-add-wrap {
  position: relative;
}

.tag-input {
  border: 1px dashed #adb5bd;
  border-radius: 12px;
  padding: 0.125rem 0.625rem;
  font-size: 0.8rem;
  width: 110px;
  outline: none;
  background: #fff;
}
.tag-input:focus { border-color: #1565c0; border-style: solid; }

.tag-dropdown {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  z-index: 1050;
  background: #fff;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.12);
  list-style: none;
  margin: 0;
  padding: 0.25rem 0;
  min-width: 160px;
  max-height: 200px;
  overflow-y: auto;
}

.tag-dropdown li {
  padding: 0.375rem 0.75rem;
  font-size: 0.85rem;
  cursor: pointer;
  color: #333;
}
.tag-dropdown li:hover,
.tag-dropdown li.highlighted { background: #f0f4ff; }

.create-option { color: #1565c0; font-style: italic; }
</style>
