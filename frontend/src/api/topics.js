export async function getTopics() {
  const res = await fetch('/api/topics')
  if (!res.ok) throw new Error(res.statusText)
  return res.json()
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