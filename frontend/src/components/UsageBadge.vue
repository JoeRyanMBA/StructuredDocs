<template>
  <span class="usage-badge-wrap" ref="wrap">
    <button
      class="usage-badge"
      :class="{ 'is-zero': count === 0, 'is-used': count > 0 }"
      @click.stop="toggle"
      :title="count === 0 ? `Unused — no ${label}s` : `Used in ${count} ${label}${count === 1 ? '' : 's'} (click to see)`"
      type="button"
    >{{ count }}</button>

    <div v-if="open && items.length > 0" class="usage-popover">
      <div class="usage-popover-header">{{ label }}s</div>
      <ul>
        <li v-for="item in items" :key="item.id">{{ item.name }}</li>
      </ul>
    </div>
    <div v-else-if="open && count === 0" class="usage-popover usage-popover--empty">
      Not used in any {{ label }}.
    </div>
  </span>
</template>

<script>
export default {
  name: 'UsageBadge',
  props: {
    count: { type: Number, default: 0 },
    label: { type: String, default: 'collection' },
    items: { type: Array, default: () => [] }   // [{id, name}]
  },
  data() {
    return { open: false }
  },
  mounted() {
    document.addEventListener('click', this.onOutsideClick)
  },
  beforeUnmount() {
    document.removeEventListener('click', this.onOutsideClick)
  },
  methods: {
    toggle() {
      this.open = !this.open
    },
    onOutsideClick(e) {
      if (this.$refs.wrap && !this.$refs.wrap.contains(e.target)) {
        this.open = false
      }
    }
  }
}
</script>

<style scoped>
.usage-badge-wrap {
  position: relative;
  display: inline-block;
}

.usage-badge {
  display: inline-block;
  min-width: 1.6rem;
  padding: 0.15rem 0.45rem;
  border-radius: 999px;
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
  border: none;
  line-height: 1.4;
}

.usage-badge.is-used {
  background: var(--extended-sky-blue, #d0eaf9);
  color: var(--primary-deep-teal, #1a6b6b);
}

.usage-badge.is-zero {
  background: #fde8e8;
  color: #c0392b;
}

.usage-popover {
  position: absolute;
  top: calc(100% + 4px);
  left: 50%;
  transform: translateX(-50%);
  z-index: 200;
  background: #fff;
  border: 1px solid var(--border-gray, #ddd);
  border-radius: 6px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.12);
  min-width: 160px;
  max-width: 280px;
  padding: 0.5rem 0;
  white-space: nowrap;
}

.usage-popover-header {
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-secondary-cool-gray, #6b7280);
  padding: 0.25rem 0.75rem 0.4rem;
  border-bottom: 1px solid var(--border-gray, #ddd);
}

.usage-popover ul {
  list-style: none;
  margin: 0;
  padding: 0.25rem 0;
  max-height: 200px;
  overflow-y: auto;
}

.usage-popover ul li {
  padding: 0.3rem 0.75rem;
  font-size: 0.85rem;
  color: var(--text-primary-dark-navy, #1a1a2e);
  overflow: hidden;
  text-overflow: ellipsis;
}

.usage-popover ul li:hover {
  background: var(--bg-light-gray, #f5f5f5);
}

.usage-popover--empty {
  padding: 0.5rem 0.75rem;
  font-size: 0.85rem;
  color: var(--text-secondary-cool-gray, #6b7280);
  font-style: italic;
}
</style>
