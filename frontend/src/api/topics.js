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