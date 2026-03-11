<template>
  <div class="rde-root">
    <div v-if="!hasChanges" class="rde-no-changes">
      <i class="bi bi-check-circle-fill me-2"></i>
      No direct content edits were made by this reviewer.
    </div>

    <div v-else>
      <div class="rde-toolbar">
        <button class="btn btn-sm btn-success me-2" @click="acceptAll">
          <i class="bi bi-check-all me-1"></i>Accept All
        </button>
        <button class="btn btn-sm btn-outline-danger me-2" @click="rejectAll">
          <i class="bi bi-x-circle me-1"></i>Reject All
        </button>
        <div class="rde-stats ms-auto">
          <span class="badge bg-success me-1">{{ acceptedCount }} accepted</span>
          <span class="badge bg-danger">{{ rejectedCount }} rejected</span>
          <span class="text-muted ms-2" style="font-size:0.78rem">(click any change to toggle)</span>
        </div>
      </div>

      <div class="rde-content">
        <template v-for="seg in rawSegments" :key="seg.index">
          <!-- Unchanged text — render as HTML so formatting shows correctly -->
          <span v-if="seg.type === 'equal'" v-html="seg.value"></span>

          <!-- A change unit: click to accept/reject -->
          <span
            v-else
            class="rde-change"
            :class="acceptedMap[seg.changeId] ? 'rde-accepted' : 'rde-rejected'"
            :title="acceptedMap[seg.changeId] ? 'Click to reject this change' : 'Click to accept this change'"
            @click="toggle(seg.changeId)"
          >
            <span v-if="seg.removedHtml" class="rde-removed" v-html="seg.removedHtml"></span>
            <span v-if="seg.addedHtml"   class="rde-added"   v-html="seg.addedHtml"></span>
            <span class="rde-badge">{{ acceptedMap[seg.changeId] ? '✓' : '✗' }}</span>
          </span>
        </template>
      </div>
    </div>
  </div>
</template>

<script>
import { diffWords } from 'diff'

export default {
  name: 'ReviewDiffEditor',
  props: {
    originalHtml: { type: String, default: '' },
    editedHtml:   { type: String, default: '' },
  },
  emits: ['update:finalHtml'],

  data() {
    return {
      // { [changeId]: boolean }  true = accept reviewer's version
      acceptedMap: {}
    }
  },

  computed: {
    rawSegments() {
      const parts = diffWords(this.originalHtml || '', this.editedHtml || '')
      const segments = []
      let changeId = 0
      let i = 0

      while (i < parts.length) {
        const p = parts[i]
        if (!p.added && !p.removed) {
          segments.push({ type: 'equal', value: p.value, index: segments.length })
          i++
        } else {
          let removedHtml = '', addedHtml = ''
          while (i < parts.length && (parts[i].added || parts[i].removed)) {
            if (parts[i].removed) removedHtml += parts[i].value
            if (parts[i].added)   addedHtml   += parts[i].value
            i++
          }
          segments.push({
            type: 'change',
            changeId: changeId++,
            removedHtml,
            addedHtml,
            index: segments.length
          })
        }
      }
      return segments
    },

    changeCount()   { return this.rawSegments.filter(s => s.type === 'change').length },
    hasChanges()    { return this.changeCount > 0 },
    acceptedCount() { return Object.values(this.acceptedMap).filter(Boolean).length },
    rejectedCount() { return this.changeCount - this.acceptedCount },

    finalHtml() {
      return this.rawSegments.map(seg => {
        if (seg.type === 'equal') return seg.value
        return this.acceptedMap[seg.changeId] ? seg.addedHtml : seg.removedHtml
      }).join('')
    }
  },

  watch: {
    rawSegments: {
      immediate: true,
      handler(segs) {
        // Default: all changes accepted
        const map = {}
        segs.forEach(s => { if (s.type === 'change') map[s.changeId] = true })
        this.acceptedMap = map
        this.$nextTick(() => this.$emit('update:finalHtml', this.finalHtml))
      }
    },
    finalHtml(val) {
      this.$emit('update:finalHtml', val)
    }
  },

  methods: {
    toggle(changeId) {
      this.acceptedMap = { ...this.acceptedMap, [changeId]: !this.acceptedMap[changeId] }
    },
    acceptAll() {
      const map = {}
      this.rawSegments.forEach(s => { if (s.type === 'change') map[s.changeId] = true })
      this.acceptedMap = map
    },
    rejectAll() {
      const map = {}
      this.rawSegments.forEach(s => { if (s.type === 'change') map[s.changeId] = false })
      this.acceptedMap = map
    }
  }
}
</script>

<style scoped>
.rde-root { font-size: 0.92rem; }

.rde-no-changes {
  padding: 0.85rem 1rem;
  background: #d1e7dd;
  border-radius: 6px;
  color: #0a3622;
  font-size: 0.9rem;
}

.rde-toolbar {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.35rem;
  margin-bottom: 0.65rem;
  padding: 0.5rem 0.75rem;
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 6px 6px 0 0;
}

.rde-stats { display: flex; align-items: center; gap: 0.25rem; }

.rde-content {
  line-height: 1.85;
  padding: 1rem 1.25rem;
  background: #fff;
  border: 1px solid #dee2e6;
  border-top: none;
  border-radius: 0 0 6px 6px;
  word-wrap: break-word;
  min-height: 80px;
}

/* A change unit */
.rde-change {
  display: inline;
  cursor: pointer;
  border-radius: 3px;
  padding: 1px 2px;
  outline: 1px solid transparent;
  transition: outline-color 0.1s;
}
.rde-change:hover { outline-color: #0d6efd; }

.rde-removed, .rde-added { display: inline; }

/* Accepted: reviewer's word is green underline, original is red strikethrough */
.rde-accepted .rde-removed {
  text-decoration: line-through;
  color: #842029;
  background: #f8d7da;
  opacity: 0.75;
  border-radius: 2px;
}
.rde-accepted .rde-added {
  color: #0a3622;
  background: #d1e7dd;
  text-decoration: underline;
  border-radius: 2px;
}

/* Rejected: original is kept (amber background), reviewer's word is dim strikethrough */
.rde-rejected .rde-removed {
  color: #664d03;
  background: #fff3cd;
  border-radius: 2px;
}
.rde-rejected .rde-added {
  text-decoration: line-through;
  color: #6c757d;
  background: #e9ecef;
  opacity: 0.6;
  border-radius: 2px;
}

/* Small indicator badge */
.rde-badge {
  display: inline-block;
  font-size: 0.65rem;
  font-weight: 800;
  vertical-align: super;
  margin-left: 1px;
  line-height: 1;
}
.rde-accepted .rde-badge { color: #0a3622; }
.rde-rejected .rde-badge { color: #842029; }
</style>
