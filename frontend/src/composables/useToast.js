import { reactive } from 'vue'

// Simple global toast store and helpers
const state = reactive({
  toasts: [] // { id, type: 'success'|'error'|'info'|'warn', message, timeoutId }
})

let idCounter = 1

function addToast(message, type = 'success', duration = 3000) {
  const id = idCounter++
  const toast = { id, type, message }
  state.toasts.push(toast)

  const timeoutId = setTimeout(() => removeToast(id), duration)
  toast.timeoutId = timeoutId
  return id
}

function removeToast(id) {
  const idx = state.toasts.findIndex(t => t.id === id)
  if (idx !== -1) {
    const t = state.toasts[idx]
    if (t.timeoutId) clearTimeout(t.timeoutId)
    state.toasts.splice(idx, 1)
  }
}

export const toast = {
  success: (message, duration) => addToast(message, 'success', duration),
  error: (message, duration) => addToast(message, 'error', duration),
  info: (message, duration) => addToast(message, 'info', duration),
  warn: (message, duration) => addToast(message, 'warn', duration),
  remove: removeToast,
  _state: state
}

export function useToast() {
  return toast
}
