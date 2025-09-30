<template>
  <button
    :class="buttonClass"
    @click.stop="onClick"
    :title="computedTitle"
    :aria-label="computedAria"
    :disabled="disabled || loading"
  >
    <span v-if="loading" class="spinner" aria-hidden="true"></span>
    <i v-else :class="iconClass" aria-hidden="true"></i>
  </button>
</template>

<script>
export default {
  name: 'ArchiveToggleButton',
  props: {
    archived: { type: Boolean, required: true },
    size: { type: String, default: 'sm' },
    disabled: { type: Boolean, default: false },
    loading: { type: Boolean, default: false },
    entityLabel: { type: String, default: 'item' }
  },
  emits: ['toggle'],
  computed: {
    buttonClass() {
      return [
        'btn-icon',
        this.archived ? 'btn-warning' : 'btn-secondary',
        this.size === 'sm' ? 'btn-icon-sm' : 'btn-icon-md'
      ]
    },
    iconClass() {
      return this.archived ? 'bi bi-box-arrow-in-down' : 'bi bi-archive'
    },
    computedTitle() {
      return this.archived ? `Restore ${this.entityLabel}` : `Archive ${this.entityLabel}`
    },
    computedAria() {
      return this.computedTitle
    }
  },
  methods: {
    onClick() {
      if (this.disabled || this.loading) return
      this.$emit('toggle', !this.archived)
    }
  }
}
</script>

<style scoped>
.btn-icon {
  width: 32px;
  height: 32px;
  padding: 0;
  border-radius: 4px;
  border: 1px solid transparent;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
}
.btn-icon-sm { width: 32px; height: 32px; }
.btn-icon-md { width: 40px; height: 40px; }
.btn-icon:hover:not(:disabled) { transform: translateY(-1px); box-shadow: 0 2px 4px rgba(0,0,0,0.12); }
.btn-icon:disabled { opacity: 0.55; cursor: not-allowed; }
.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(0,0,0,0.15);
  border-top-color: currentColor;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
</style>
