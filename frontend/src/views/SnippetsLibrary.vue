<template>
  <div class="snippets-library">
    <div class="page-header">
      <h1>📎 Snippets Library</h1>
      <p class="subtitle">Manage reusable audience-specific content blocks</p>
    </div>

    <div class="library-layout">
      <!-- List panel -->
      <aside class="snippet-list-panel">
        <div class="panel-toolbar">
          <input v-model="search" type="text" class="search-input" placeholder="Search snippets…" />
          <button class="btn-new" @click="startNew">+ New Snippet</button>
        </div>
        <ul class="snippet-list">
          <li
            v-for="s in filtered"
            :key="s.id"
            class="snippet-list-item"
            :class="{ active: selected && selected.id === s.id }"
            @click="selectSnippet(s)"
          >
            <div class="snippet-name">{{ s.title }}</div>
            <div class="snippet-tag-row">
              <span v-for="tag in s.tags" :key="tag.id" class="tag-badge">{{ tag.name }}</span>
              <span v-if="!s.tags || s.tags.length === 0" class="no-tags">No audience tags</span>
            </div>
          </li>
          <li v-if="filtered.length === 0" class="empty-state">
            {{ search ? 'No snippets match your search.' : 'No snippets yet. Create one!' }}
          </li>
        </ul>
      </aside>

      <!-- Editor panel -->
      <section class="snippet-editor-panel">
        <div v-if="!selected && !creating" class="select-prompt">
          <p>Select a snippet from the list or create a new one.</p>
        </div>

        <form v-else @submit.prevent="save" class="editor-form">
          <div class="form-header">
            <h2>{{ creating ? 'New Snippet' : 'Edit Snippet' }}</h2>
            <div class="form-header-actions">
              <button v-if="!creating" type="button" class="btn-delete" @click="confirmDelete">🗑 Delete</button>
            </div>
          </div>

          <div class="form-group">
            <label>Title <span class="required">*</span></label>
            <input v-model="form.title" type="text" class="form-input" placeholder="Short descriptive name" required />
          </div>

          <div class="form-group">
            <label>Audience Tags</label>
            <TagEditor
              v-if="!creating && selected"
              :entity-type="'snippet'"
              :entity-id="selected.id"
              @change="onTagsChanged"
            />
            <p v-else class="hint">Save the snippet first, then assign audience tags.</p>
          </div>

          <div class="form-group">
            <label>Content</label>
            <div class="wysiwyg-toolbar">
              <button type="button" @click="execCmd('bold')" class="tb-btn" title="Bold">𝐁</button>
              <button type="button" @click="execCmd('italic')" class="tb-btn" title="Italic">𝐼</button>
              <button type="button" @click="execCmd('insertUnorderedList')" class="tb-btn" title="Bullet list">•</button>
              <button type="button" @click="execCmd('insertOrderedList')" class="tb-btn" title="Numbered list">1.</button>
            </div>
            <div
              ref="contentEditor"
              class="content-editor"
              contenteditable="true"
              @input="onContentInput"
              v-html="form.content"
            ></div>
          </div>

          <div class="form-actions">
            <button type="submit" class="btn-save" :disabled="saving">
              {{ saving ? 'Saving…' : (creating ? 'Create Snippet' : 'Save Changes') }}
            </button>
            <button type="button" class="btn-cancel" @click="cancel">Cancel</button>
            <span v-if="saveMsg" class="save-msg">{{ saveMsg }}</span>
          </div>
        </form>
      </section>
    </div>

    <!-- Delete confirmation -->
    <div v-if="showDeleteConfirm" class="modal-overlay" @click.self="showDeleteConfirm = false">
      <div class="confirm-modal">
        <h3>Delete Snippet?</h3>
        <p>This will remove <strong>{{ selected && selected.title }}</strong> and all its placeholder references in topic content will become empty.</p>
        <div class="confirm-actions">
          <button class="btn-delete" @click="doDelete">Yes, Delete</button>
          <button class="btn-cancel" @click="showDeleteConfirm = false">Cancel</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { listSnippets, createSnippet, updateSnippet, deleteSnippet } from '@/api/snippets.js'
import TagEditor from '@/components/TagEditor.vue'

export default {
  name: 'SnippetsLibrary',
  components: { TagEditor },
  data() {
    return {
      snippets: [],
      search: '',
      selected: null,
      creating: false,
      form: { title: '', content: '' },
      saving: false,
      saveMsg: '',
      showDeleteConfirm: false,
    }
  },
  computed: {
    filtered() {
      const q = this.search.toLowerCase()
      return this.snippets.filter(s => s.title.toLowerCase().includes(q))
    },
  },
  async mounted() {
    await this.loadSnippets()
  },
  methods: {
    async loadSnippets() {
      try {
        this.snippets = await listSnippets()
      } catch (e) {
        console.error('Failed to load snippets', e)
      }
    },
    selectSnippet(s) {
      this.creating = false
      this.selected = s
      this.form = { title: s.title, content: s.content || '' }
      this.$nextTick(() => {
        if (this.$refs.contentEditor) {
          this.$refs.contentEditor.innerHTML = this.form.content
        }
      })
    },
    startNew() {
      this.creating = true
      this.selected = null
      this.form = { title: '', content: '' }
      this.$nextTick(() => {
        if (this.$refs.contentEditor) this.$refs.contentEditor.innerHTML = ''
      })
    },
    cancel() {
      this.creating = false
      this.selected = null
      this.form = { title: '', content: '' }
    },
    onContentInput() {
      if (this.$refs.contentEditor) {
        this.form.content = this.$refs.contentEditor.innerHTML
      }
    },
    execCmd(cmd) {
      document.execCommand(cmd, false, null)
      this.onContentInput()
    },
    async save() {
      if (!this.form.title.trim()) return
      this.saving = true
      this.saveMsg = ''
      try {
        if (this.creating) {
          const created = await createSnippet({ title: this.form.title, content: this.form.content })
          this.snippets.unshift(created)
          this.creating = false
          this.selected = created
        } else {
          const updated = await updateSnippet(this.selected.id, { title: this.form.title, content: this.form.content })
          const idx = this.snippets.findIndex(s => s.id === this.selected.id)
          if (idx !== -1) this.snippets.splice(idx, 1, updated)
          this.selected = updated
        }
        this.saveMsg = '✓ Saved'
        setTimeout(() => { this.saveMsg = '' }, 2000)
      } catch (e) {
        this.saveMsg = 'Error saving'
        console.error(e)
      } finally {
        this.saving = false
      }
    },
    confirmDelete() {
      this.showDeleteConfirm = true
    },
    async doDelete() {
      try {
        await deleteSnippet(this.selected.id)
        this.snippets = this.snippets.filter(s => s.id !== this.selected.id)
        this.selected = null
        this.creating = false
      } catch (e) {
        console.error('Delete failed', e)
      } finally {
        this.showDeleteConfirm = false
      }
    },
    onTagsChanged(tags) {
      if (this.selected) {
        this.selected = { ...this.selected, tags }
        const idx = this.snippets.findIndex(s => s.id === this.selected.id)
        if (idx !== -1) this.snippets.splice(idx, 1, this.selected)
      }
    },
  },
}
</script>

<style scoped>
.snippets-library { padding: 1.5rem; max-width: 1100px; }
.page-header { margin-bottom: 1.5rem; }
.page-header h1 { margin: 0 0 0.25rem; font-size: 1.5rem; }
.subtitle { color: #6c757d; margin: 0; font-size: 0.95rem; }

.library-layout {
  display: flex;
  gap: 1.5rem;
  align-items: flex-start;
}

.snippet-list-panel {
  width: 280px;
  flex-shrink: 0;
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  overflow: hidden;
}
.panel-toolbar {
  padding: 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  border-bottom: 1px solid #dee2e6;
}
.search-input {
  width: 100%;
  padding: 0.4rem 0.65rem;
  border: 1px solid #ced4da;
  border-radius: 6px;
  font-size: 0.85rem;
  box-sizing: border-box;
}
.btn-new {
  background: #205493;
  color: #fff;
  border: none;
  border-radius: 6px;
  padding: 0.4rem 0.75rem;
  font-size: 0.85rem;
  cursor: pointer;
  text-align: center;
}
.btn-new:hover { background: #1a4376; }

.snippet-list { list-style: none; margin: 0; padding: 0.25rem 0; max-height: 60vh; overflow-y: auto; }
.snippet-list-item {
  padding: 0.6rem 0.75rem;
  cursor: pointer;
  border-left: 3px solid transparent;
  transition: background 0.15s;
}
.snippet-list-item:hover { background: #e9ecef; }
.snippet-list-item.active { background: #e8eef7; border-left-color: #205493; }
.snippet-name { font-size: 0.88rem; font-weight: 500; color: #212529; }
.snippet-tag-row { margin-top: 0.2rem; display: flex; flex-wrap: wrap; gap: 0.2rem; }
.tag-badge {
  background: #e3f2fd; color: #1565c0; border: 1px solid #bbdefb;
  border-radius: 10px; padding: 0.05rem 0.4rem; font-size: 0.72rem;
}
.no-tags { color: #adb5bd; font-size: 0.72rem; font-style: italic; }
.empty-state { padding: 1rem; color: #6c757d; font-size: 0.85rem; text-align: center; }

.snippet-editor-panel {
  flex: 1;
  background: #fff;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  padding: 1.25rem;
  min-height: 400px;
}
.select-prompt { color: #6c757d; text-align: center; padding: 3rem 1rem; }

.editor-form { display: flex; flex-direction: column; gap: 1rem; }
.form-header { display: flex; align-items: center; justify-content: space-between; }
.form-header h2 { margin: 0; font-size: 1.1rem; }

.form-group { display: flex; flex-direction: column; gap: 0.35rem; }
.form-group label { font-size: 0.85rem; font-weight: 600; color: #495057; }
.form-input {
  padding: 0.5rem 0.75rem;
  border: 1px solid #ced4da;
  border-radius: 6px;
  font-size: 0.9rem;
}
.form-input:focus { outline: none; border-color: #205493; }
.hint { color: #6c757d; font-size: 0.82rem; margin: 0; }
.required { color: #dc3545; }

.wysiwyg-toolbar {
  display: flex;
  gap: 0.25rem;
  padding: 0.35rem;
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-bottom: none;
  border-radius: 6px 6px 0 0;
}
.tb-btn {
  background: none;
  border: 1px solid transparent;
  border-radius: 4px;
  padding: 0.2rem 0.45rem;
  cursor: pointer;
  font-size: 0.9rem;
}
.tb-btn:hover { background: #e9ecef; border-color: #ced4da; }

.content-editor {
  min-height: 200px;
  border: 1px solid #dee2e6;
  border-radius: 0 0 6px 6px;
  padding: 0.75rem;
  font-size: 0.9rem;
  outline: none;
  line-height: 1.6;
}
.content-editor:focus { border-color: #205493; }

.form-actions { display: flex; align-items: center; gap: 0.75rem; flex-wrap: wrap; }
.btn-save {
  background: #205493; color: #fff; border: none;
  border-radius: 6px; padding: 0.5rem 1.25rem; font-size: 0.9rem; cursor: pointer;
}
.btn-save:hover:not(:disabled) { background: #1a4376; }
.btn-save:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-cancel {
  background: none; border: 1px solid #ced4da;
  border-radius: 6px; padding: 0.5rem 1rem; font-size: 0.9rem; cursor: pointer; color: #495057;
}
.btn-cancel:hover { background: #f8f9fa; }
.btn-delete {
  background: #dc3545; color: #fff; border: none;
  border-radius: 6px; padding: 0.4rem 0.75rem; font-size: 0.85rem; cursor: pointer;
}
.btn-delete:hover { background: #b02a37; }
.save-msg { color: #198754; font-size: 0.85rem; }
.form-header-actions { display: flex; gap: 0.5rem; }

/* Delete confirm modal */
.modal-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.4);
  display: flex; align-items: center; justify-content: center; z-index: 2000;
}
.confirm-modal {
  background: #fff; border-radius: 8px; padding: 1.5rem;
  max-width: 400px; width: 90%;
  box-shadow: 0 8px 32px rgba(0,0,0,0.15);
}
.confirm-modal h3 { margin: 0 0 0.5rem; }
.confirm-modal p { margin: 0 0 1rem; font-size: 0.9rem; color: #495057; }
.confirm-actions { display: flex; gap: 0.75rem; }
</style>
