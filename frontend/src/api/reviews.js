// Reviews API service
export async function getReviews() {
  const res = await fetch('/api/reviews/')
  if (!res.ok) throw new Error(res.statusText)
  return res.json()
}

export async function getReviewers() {
  const res = await fetch('/api/reviews/reviewers')
  if (!res.ok) throw new Error(res.statusText)
  return res.json()
}

export async function requestReview(reviewData) {
  const res = await fetch('/api/reviews/request', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(reviewData)
  })
  if (!res.ok) throw new Error(res.statusText)
  return res.json()
}

export async function startReview(reviewId) {
  const res = await fetch(`/api/reviews/${reviewId}/start`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' }
  })
  if (!res.ok) throw new Error(res.statusText)
  return res.json()
}

export async function submitReview(reviewId, reviewData) {
  const res = await fetch(`/api/reviews/${reviewId}/submit`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(reviewData)
  })
  if (!res.ok) throw new Error(res.statusText)
  return res.json()
}

export async function getPendingReviews(reviewerId = null) {
  const url = reviewerId 
    ? `/api/reviews/pending?reviewer_id=${reviewerId}`
    : '/api/reviews/pending'
  
  const res = await fetch(url)
  if (!res.ok) throw new Error(res.statusText)
  return res.json()
}

export async function getMyReviews(requesterId) {
  const res = await fetch(`/api/reviews/my-reviews?requester_id=${requesterId}`)
  if (!res.ok) throw new Error(res.statusText)
  return res.json()
}

export async function getTopicReviews(topicId) {
  const res = await fetch(`/api/reviews/topic/${topicId}/reviews`)
  if (!res.ok) throw new Error(res.statusText)
  return res.json()
}

export async function getReviewStats() {
  const res = await fetch('/api/reviews/stats')
  if (!res.ok) throw new Error(res.statusText)
  return res.json()
}

export async function sendFollowUpReminder(reviewId) {
  const res = await fetch(`/api/reviews/${reviewId}/follow-up`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    }
  })
  if (!res.ok) {
    const payload = await res.json().catch(() => null)
    throw new Error(payload?.error || res.statusText || 'Failed to send follow-up reminder')
  }
  return res.json()
}
