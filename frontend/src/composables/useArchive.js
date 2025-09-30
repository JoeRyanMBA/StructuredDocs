import { ref } from 'vue'
import { fetchArchived, toggleArchive, isEntityArchived } from '@/services/archiveService'
import { toast } from '@/composables/useToast'

/**
 * useArchive composable
 * Provides reactive helpers to load archived entities and toggle archive state.
 * @param {('projects'|'collections'|'feedback'|'bugs')} entityType
 */
export function useArchive(entityType) {
  const loading = ref(false)
  const error = ref('')
  const items = ref([])

  async function load() {
    loading.value = true
    error.value = ''
    try {
      items.value = await fetchArchived(entityType)
    } catch (e) {
      error.value = e.message || 'Failed to load archived items'
      toast.error(error.value)
    } finally {
      loading.value = false
    }
  }

  async function restore(entity) {
    const label = entityType.slice(0, -1) // crude singularization
    try {
      await toggleArchive(entityType, entity.id, false)
      items.value = items.value.filter(i => i.id !== entity.id)
      toast.success(`${label.charAt(0).toUpperCase() + label.slice(1)} restored`)
    } catch (e) {
      toast.error(e.message || 'Failed to restore')
    }
  }

  async function archive(entity) {
    try {
      await toggleArchive(entityType, entity.id, true)
      toast.success('Archived successfully')
    } catch (e) {
      toast.error(e.message || 'Failed to archive')
    }
  }

  return { loading, error, items, load, restore, archive, isEntityArchived }
}
