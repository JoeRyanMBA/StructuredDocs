<template>
  <div class="toast-container" aria-live="polite" aria-atomic="true">
    <Toast v-for="t in toasts" :key="t.id" :id="t.id" :type="t.type" :message="t.message" @close="remove" />
  </div>
</template>

<script>
import { computed } from 'vue'
import { toast } from '@/composables/useToast'
import Toast from './Toast.vue'

export default {
  name: 'ToastContainer',
  components: { Toast },
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

</style>
