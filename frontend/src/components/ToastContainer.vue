<template>
  <div class="toast-container" aria-live="polite" aria-atomic="true">
    <div v-for="t in toasts" :key="t.id" class="toast-item" :class="t.type" role="status">
      <span class="toast-message">{{ t.message }}</span>
      <button class="toast-close" @click="remove(t.id)" aria-label="Close">×</button>
    </div>
  </div>
</template>

<script>
import { computed } from 'vue'
import { toast } from '@/composables/useToast'

export default {
  name: 'ToastContainer',
  setup() {
    const toasts = computed(() => toast._state.toasts)
    const remove = (id) => toast.remove(id)
    return { toasts, remove }
  }
}
</script>

<style scoped>
.toast-container {
  position: fixed;
  top: 80px;
  right: 20px;
  z-index: 4000;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

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
