<template>
  <svg :class="svgClass" :style="svgStyle" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" aria-hidden="true" focusable="false" role="img">
    <path d="M11 4c-.552 0-1 .448-1 1v6H4c-.552 0-1 .448-1 1s.448 1 1 1h6v6c0 .552.448 1 1 1s1-.448 1-1v-6h6c.552 0 1-.448 1-1s-.448-1-1-1h-6V5c0-.552-.448-1-1-1z" fill="currentColor"/>
  </svg>
</template>

<script>
export default {
  name: 'IconPlus',
  props: {
    size: {
      type: [Number, String],
      default: 28
    },
    color: {
      type: String,
      default: ''
    },
    className: {
      type: String,
      default: ''
    }
  },
  computed: {
    svgClass() {
      // Allow global sizing via container; fallback to inline size via style
      return this.className || 'icon-plus-svg'
    }
    ,
    svgStyle() {
      const sizeVal = typeof this.size === 'number' ? `${this.size}px` : this.size
      const style = { width: sizeVal, height: sizeVal }
      if (this.color) style.color = this.color
      return style
    }
  }
}
</script>

<style scoped>
svg {
  width: 1em;
  height: 1em;
}
</style>