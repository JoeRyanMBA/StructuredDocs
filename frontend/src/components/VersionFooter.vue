<template>
  <div class="version-footer" v-if="metaLoaded">
    <small>
      <span v-if="version">v{{ version }}</span>
      <span v-if="commit"> ({{ commit }})</span>
      <span v-if="buildTime"> • built {{ relativeBuildTime }}</span>
    </small>
  </div>
</template>

<script>
import { apiGet } from '@/api/base'

export default {
  name: 'VersionFooter',
  data() {
    return { meta: {}, metaLoaded: false }
  },
  computed: {
    version() { return this.meta.version },
    commit() { return this.meta.commit },
    buildTime() { return this.meta.build_time },
    relativeBuildTime() {
      if(!this.buildTime) return ''
      try {
        const dt = new Date(this.buildTime)
        const diffMs = Date.now() - dt.getTime()
        const diffMins = Math.floor(diffMs / 60000)
        if (diffMins < 60) return `${diffMins}m ago`
        const diffH = Math.floor(diffMins / 60)
        if (diffH < 24) return `${diffH}h ago`
        const diffD = Math.floor(diffH / 24)
        return `${diffD}d ago`
      } catch { return '' }
    }
  },
  mounted() {
    apiGet('/api/version')
      .then(data => {
        if (data) this.meta = data
      })
      .catch(() => {})
      .finally(() => {
        this.metaLoaded = true
      })
  }
}
</script>

<style scoped>
.version-footer {
  text-align: center;
  padding: 0.5rem 0;
  color: #6c757d;
  font-size: 0.75rem;
  letter-spacing: 0.5px;
}
</style>
