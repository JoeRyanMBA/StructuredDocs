// Reviews API service
import { apiGet, apiPost, apiRequest } from './base.js'

async function throwApiError(res, fallbackMessage = 'Request failed') {
  const payload = await res.json().catch(() => null)
  throw new Error(payload?.error || payload?.message || res.statusText || fallbackMessage)
}

export async function getReviews() {
  return apiGet('/api/reviews/')
}

export async function getReviewers() {
  return apiGet('/api/reviews/reviewers')
}

export async function requestReview(reviewData) {
  return apiPost('/api/reviews/request', reviewData)
}

export async function startReview(reviewId) {
  return apiPost(`/api/reviews/${reviewId}/start`, {})
}

export async function submitReview(reviewId, reviewData) {
  return apiPost(`/api/reviews/${reviewId}/submit`, reviewData)
}

export async function getPendingReviews(reviewerId = null) {
  const url = reviewerId
    ? `/api/reviews/pending?reviewer_id=${reviewerId}`
    : '/api/reviews/pending'
  // /pending has no @jwt_required — use plain fetch
  const res = await fetch(url)
  if (!res.ok) await throwApiError(res, 'Failed to load pending reviews')
  return res.json()
}

export async function getMyReviews(requesterId) {
  return apiGet(`/api/reviews/my-reviews?requester_id=${requesterId}`)
}

export async function getTopicReviews(topicId) {
  return apiGet(`/api/reviews/topic/${topicId}/reviews`)
}

export async function getReviewStats() {
  return apiGet('/api/reviews/stats')
}

export async function sendFollowUpReminder(reviewId) {
  return apiPost(`/api/reviews/${reviewId}/follow-up`, {})
}

// --- Bulk Review (token-based, no JWT needed) ---

export async function requestBulkReview(data) {
  return apiPost('/api/reviews/bulk-request', data)
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
