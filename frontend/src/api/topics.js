export async function getTopics() {
  try {
    const res = await fetch('/api/topics')
    if (!res.ok) throw new Error(res.statusText)
    return res.json()
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
  const res = await fetch('/api/topics', {
    method: 'POST',
    body: JSON.stringify(data),
    headers: {
      'Content-Type': 'application/json',
    },
  })
  if (!res.ok) throw new Error(res.statusText)
  return res.json()
}

export async function updateTopic(topicId, data) {
  const res = await fetch(`/api/topics/${topicId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function deleteTopic(topicId) {
  const res = await fetch(`/api/topics/${topicId}`, {
    method: 'DELETE'
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}