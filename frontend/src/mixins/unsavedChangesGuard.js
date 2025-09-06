// Reusable mixin to prompt user if navigating away with unsaved changes.
// Usage: provide an isDirty() method OR a reactive 'dirtyFlag' boolean.
export default {
  mounted() {
    window.addEventListener('beforeunload', this.__uc_beforeUnload)
  },
  unmounted() {
    window.removeEventListener('beforeunload', this.__uc_beforeUnload)
  },
  methods: {
    __uc_beforeUnload(e) {
      if (this.$options.name === 'RouterLink') return
      try {
        if (typeof this.isDirty === 'function') {
          if (this.isDirty()) { e.preventDefault(); e.returnValue = '' }
        } else if (this.dirtyFlag) {
          if (this.dirtyFlag) { e.preventDefault(); e.returnValue = '' }
        }
      } catch(_) { /* swallow */ }
    }
  },
  beforeRouteLeave(to, from, next) {
    let dirty = false
    try {
      if (typeof this.isDirty === 'function') dirty = this.isDirty()
      else dirty = !!this.dirtyFlag
    } catch(_) { dirty = false }
    if (!dirty) return next()
    const leave = window.confirm('You have unsaved changes. Leave without saving?')
    if (leave) return next()
    next(false)
  }
}