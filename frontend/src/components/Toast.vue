<template>
  <div
    class="toast-item"
    :class="type"
    :role="type === 'error' ? 'alert' : 'status'"
    :aria-live="type === 'error' ? 'assertive' : 'polite'"
  >
    <span class="toast-message">{{ message }}</span>
    <button class="toast-close" @click="$emit('close', id)" aria-label="Close">×</button>
  </div>
  
</template>

<script>
export default {
  name: 'Toast',
  props: {
    id: { type: [String, Number], required: true },
    type: { type: String, default: 'success' }, // success | error | info | warn
    message: { type: String, required: true }
  }
}
</script>

<style scoped>
.toast-item {
  min-width: 280px;
  max-width: 420px;
  padding: 12px 14px;
  border-radius: 6px;
  color: #fff;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  display: flex;
  align-items: center;
  gap: 10px;
}

.toast-item.success { background: var(--success-dark-green); }
.toast-item.error { background: var(--error-coral-red); }
.toast-item.info { background: var(--primary-dark-blue); }
.toast-item.warn { background: var(--warning-amber); color: #1b1b1b; }

.toast-message { flex: 1; }
.toast-close {
  background: none;
  border: none;
  color: inherit;
  font-size: 18px;
  cursor: pointer;
  opacity: 0.9;
}
.toast-close:focus-visible { outline: 2px solid var(--primary-light-teal); outline-offset: 2px; }
</style>
