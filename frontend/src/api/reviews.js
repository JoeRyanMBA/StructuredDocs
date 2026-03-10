// Reviews API service
async function throwApiError(res, fallbackMessage = 'Request failed') {
  const payload = await res.json().catch(() => null)
  throw new Error(payload?.error || payload?.message || res.statusText || fallbackMessage)
}

export async function getReviews() {
  const res = await fetch('/api/reviews/')
  if (!res.ok) await throwApiError(res, 'Failed to load reviews')
  return res.json()
}

export async function getReviewers() {
  const res = await fetch('/api/reviews/reviewers')
  if (!res.ok) await throwApiError(res, 'Failed to load reviewers')
  return res.json()
}

export async function requestReview(reviewData) {
  const res = await fetch('/api/reviews/request', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(reviewData)
  })
  if (!res.ok) await throwApiError(res, 'Failed to request review')
  return res.json()
}

export async function startReview(reviewId) {
  const res = await fetch(`/api/reviews/${reviewId}/start`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' }
  })
  if (!res.ok) await throwApiError(res, 'Failed to start review')
  return res.json()
}

export async function submitReview(reviewId, reviewData) {
  const res = await fetch(`/api/reviews/${reviewId}/submit`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(reviewData)
  })
  if (!res.ok) await throwApiError(res, 'Failed to submit review')
  return res.json()
}

export async function getPendingReviews(reviewerId = null) {
  const url = reviewerId 
    ? `/api/reviews/pending?reviewer_id=${reviewerId}`
    : '/api/reviews/pending'
  
  const res = await fetch(url)
  if (!res.ok) await throwApiError(res, 'Failed to load pending reviews')
  return res.json()
}

export async function getMyReviews(requesterId) {
  const res = await fetch(`/api/reviews/my-reviews?requester_id=${requesterId}`)
  if (!res.ok) await throwApiError(res, 'Failed to load my reviews')
  return res.json()
}

export async function getTopicReviews(topicId) {
  const res = await fetch(`/api/reviews/topic/${topicId}/reviews`)
  if (!res.ok) await throwApiError(res, 'Failed to load topic reviews')
  return res.json()
}

export async function getReviewStats() {
  const res = await fetch('/api/reviews/stats')
  if (!res.ok) await throwApiError(res, 'Failed to load review stats')
  return res.json()
}

export async function sendFollowUpReminder(reviewId) {
  const res = await fetch(`/api/reviews/${reviewId}/follow-up`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    }
  })
  if (!res.ok) await throwApiError(res, 'Failed to send follow-up reminder')
  return res.json()
}

// --- Bulk Review ---

export async function requestBulkReview(data) {
  const res = await fetch('/api/reviews/bulk-request', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  })
  if (!res.ok) await throwApiError(res, 'Failed to create bulk review')
  return res.json()
}

export async function getBulkReview(token) {
  const res = await fetch(`/api/bulk-review/${token}`)
  if (!res.ok) await throwApiError(res, 'Failed to load bulk review')
  return res.json()
}

export async function submitBulkTopicFeedback(token, reviewId, feedbackData) {
  const res = await fetch(`/api/bulk-review/${token}/review/${reviewId}/feedback`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(feedbackData)
  })
  if (!res.ok) await throwApiError(res, 'Failed to submit feedback')
  return res.json()
}

export async function getBulkReviewStatus(token) {
  const res = await fetch(`/api/bulk-review/${token}/status`)
  if (!res.ok) await throwApiError(res, 'Failed to load bulk review status')
  return res.json()
}
