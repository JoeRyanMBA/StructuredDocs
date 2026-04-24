import { apiDelete, apiGet, apiPost, apiPut } from './base'

export async function getTopicTagsMap() {
  try {
    const data = await apiGet('/api/tags/entity/topic')
    return data && typeof data === 'object' ? data : {} // {topic_id_str: [{id, name}]}
  } catch (error) {
    console.warn('Failed to load topic tags:', error)
    return {}
  }
}


export async function getTopics() {
  try {
    const data = await apiGet('/api/topics')
    return Array.isArray(data) ? data : (data.topics ?? [])
  } catch (error) {
    console.error('Failed to load topics from API:', error)
    console.log('Using fallback mock data for testing')
    // Return mock data when backend is unavailable
    return [
      {
        id: 5,
        title: 'Unassigned Topic 1',
        status: 'draft',
        summary: 'Available topic for testing drag and drop'
      },
      {
        id: 6,
        title: 'Unassigned Topic 2',
        status: 'pending_review',
        summary: 'Another available topic'
      },
      {
        id: 7,
        title: 'Unassigned Topic 3',
        status: 'approved',
        summary: 'Ready to be organized'
      }
    ]
  }
}

// You can add more topic-related API functions here as needed, for example:
export async function createTopic(data) {
  return apiPost('/api/topics', data)
}

export async function updateTopic(topicId, data) {
  return apiPut(`/api/topics/${topicId}`, data)
}

export async function deleteTopic(topicId) {
  return apiDelete(`/api/topics/${topicId}`)
}

export async function searchTopics(query) {
  const qs = query ? `?q=${encodeURIComponent(query)}` : ''
  return apiGet(`/api/topics/search${qs}`) // Array of { id, title, status, collection_ids }
}