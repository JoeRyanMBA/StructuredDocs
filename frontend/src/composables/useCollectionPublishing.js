import { ref } from 'vue'
import { apiGet } from '@/api/base'
import { publishCollection as savePublication } from '@/api/collections'
import { downloadMobileKnowledgeBase, downloadPublicationPdf } from '@/api/publications'
import { toast } from '@/composables/useToast'

export function useCollectionPublishing() {
  const publishing = ref(false)
  const showVariableModal = ref(false)
  const variableModalData = ref(null)
  const pendingPublishAction = ref(null)

  function closeVariableModal() {
    showVariableModal.value = false
    variableModalData.value = null
    pendingPublishAction.value = null
  }

  async function publishCollection(collectionId, type, options = {}) {
    if (publishing.value) return
    publishing.value = true
    let publicationId
    try {
      if (options.beforePublish && !await options.beforePublish()) return
      const result = await savePublication(collectionId)
      publicationId = result.publication_id
      if (!Number.isInteger(publicationId) || publicationId <= 0) {
        throw new Error('The server did not return a valid publication ID.')
      }
      const filename = options.filename || 'publication'
      const tagIds = options.tagIds || []
      if (type === 'html') {
        await downloadMobileKnowledgeBase(publicationId, `${filename}_mobile_kb.html`, tagIds)
      } else {
        await downloadPublicationPdf(publicationId, `${filename}.pdf`, tagIds)
      }
      toast.success(`${type === 'html' ? 'Knowledge base' : 'PDF'} download started.`)
    } catch (error) {
      const errorData = error?.response?.data
      if (!publicationId && error?.response?.status === 400 && errorData?.requires_variable_selection) {
        pendingPublishAction.value = { type, collectionId, options }
        variableModalData.value = {
          collectionId,
          variablesInfo: errorData.variables_info,
          unresolvedVariables: errorData.unresolved_variables,
        }
        showVariableModal.value = true
        return
      }
      console.error('Collection publishing failed:', error)
      const message = errorData?.message || errorData?.error || error.message
      toast.error(`${publicationId ? 'Publication saved, but export failed' : 'Unable to publish collection'}: ${message}`)
    } finally {
      publishing.value = false
    }
  }

  async function openVariableConfigurator(collectionId) {
    if (publishing.value) return
    publishing.value = true
    try {
      const data = await apiGet(`/api/variables/collections/${collectionId}/publish-setup`)
      const variablesInfo = data.variables_in_content || []
      if (!variablesInfo.length) {
        toast.success('No variables required for this collection')
        return
      }
      pendingPublishAction.value = { type: 'configure-only', collectionId }
      variableModalData.value = {
        collectionId,
        variablesInfo,
        unresolvedVariables: variablesInfo.filter(variable => !variable.is_resolved).map(variable => variable.slug),
      }
      showVariableModal.value = true
    } catch (error) {
      console.error('Unable to load collection variables:', error)
      toast.error(error.message)
    } finally {
      publishing.value = false
    }
  }

  async function completeCollectionPublish() {
    const action = pendingPublishAction.value
    // The modal emits close immediately after variables-configured.
    closeVariableModal()
    if (!action) return
    if (action.type === 'configure-only') {
      toast.success('Variables configured. You can now publish a knowledge base or PDF.')
      return
    }
    await publishCollection(action.collectionId, action.type, action.options)
  }

  return {
    publishing,
    showVariableModal,
    variableModalData,
    pendingPublishAction,
    publishCollection,
    openVariableConfigurator,
    closeVariableModal,
    completeCollectionPublish,
  }
}
