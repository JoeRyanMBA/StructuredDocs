// src/composables/useHelpLinks.js
import { reactive, readonly } from 'vue'
import { getHelpLinksMap } from '@/api/helpLinks'

// Module-level cache so the map is fetched once per page load
const state = reactive({
  map: {},       // { [feature_key]: HelpLink }
  loaded: false,
  loading: false,
})

async function ensureLoaded() {
  if (state.loaded || state.loading) return
  state.loading = true
  try {
    state.map = await getHelpLinksMap()
    state.loaded = true
  } catch (e) {
    // Non-critical — fail silently so a backend error doesn't break the UI
    console.warn('[useHelpLinks] Failed to load help links:', e)
  } finally {
    state.loading = false
  }
}

/** Returns the HelpLink object for a feature key, or null if absent/disabled. */
function getLink(featureKey) {
  return state.map[featureKey] || null
}

export function useHelpLinks() {
  return {
    ensureLoaded,
    getLink,
    state: readonly(state),
  }
}
