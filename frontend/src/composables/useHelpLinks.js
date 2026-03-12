// src/composables/useHelpLinks.js
import { reactive, readonly } from 'vue'
import { getHelpLinksMap } from '@/api/helpLinks'

const state = reactive({
  map: {},  // { [feature_key]: HelpLink }
})

// Deduplicates parallel calls from multiple HelpIcon components on the same page,
// but does NOT cache across page navigations so admins see changes immediately.
let inflightPromise = null

async function ensureLoaded() {
  if (inflightPromise) return inflightPromise
  inflightPromise = getHelpLinksMap()
    .then(map => { state.map = map })
    .catch(e => console.warn('[useHelpLinks] Failed to load help links:', e))
    .finally(() => { inflightPromise = null })
  return inflightPromise
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
