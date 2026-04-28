// src/api/base.js
// Base API configuration for HTTP Basic Auth

function normalizeApiBase(raw) {
  if (!raw) return '';

  // Remove trailing slashes
  raw = raw.replace(/\/+$/, '');

  try {
    // If missing scheme, inherit current page protocol
    if (!/^https?:\/\//i.test(raw)) {
      const proto = typeof window !== 'undefined' ? window.location.protocol : 'https:';
      const hostPref = proto === 'https:' ? 'https://' : 'http://';
      raw = hostPref + raw.replace(/^\/*/, '');
    }
    // If current page is https, force https for API base to prevent mixed content
    if (typeof window !== 'undefined' && window.location.protocol === 'https:' && raw.startsWith('http://')) {
      raw = raw.replace(/^http:\/\//i, 'https://');
    }
  } catch (_) {
    // Fallback: empty base uses same-origin relative requests
    return '';
  }
  return raw;
}

// In production on structureddocs.online, prefer same-origin API calls so a stale
// hosted frontend env var cannot bypass the live /api proxy on the site.
export function computeApiBase() {
  const normalized = normalizeApiBase((import.meta.env.VITE_API_BASE_URL || '').trim());
  if (!normalized) return '';

  if (typeof window !== 'undefined') {
    const currentHost = window.location.hostname;
    if (currentHost === 'structureddocs.online' || currentHost === 'www.structureddocs.online') {
      return '';
    }
  }

  return normalized;
}

export const API_BASE = computeApiBase();

// Accept common list payload shapes so views can tolerate endpoint variants.
export function normalizeListResponse(payload, candidateKeys = ['items', 'results', 'data', 'projects']) {
  if (Array.isArray(payload)) return payload;
  if (!payload || typeof payload !== 'object') return [];

  for (const key of candidateKeys) {
    if (Array.isArray(payload[key])) return payload[key];
  }

  return [];
}

export function isSessionExpiredError(error) {
  const message = String(error?.message || '').toLowerCase();
  const responseMessage = String(error?.response?.data?.error || error?.response?.data?.message || '').toLowerCase();
  const haystack = `${message} ${responseMessage}`;
  return (
    haystack.includes('signature verification failed') ||
    haystack.includes('token has expired') ||
    haystack.includes('jwt') ||
    haystack.includes('unauthorized') ||
    haystack.includes('401')
  );
}

export function toFriendlyAuthError(error, fallback = 'Request failed.') {
  if (isSessionExpiredError(error)) {
    return 'Your session has expired. Please sign in again.';
  }
  return error?.response?.data?.error || error?.response?.data?.message || error?.message || fallback;
}

async function parseResponseBody(response) {
  if (response.status === 204 || response.status === 205) {
    return null;
  }

  const contentType = (response.headers.get('content-type') || '').toLowerCase();
  if (contentType.includes('application/json')) {
    return response.json();
  }

  const text = await response.text();
  if (!text) return null;

  try {
    return JSON.parse(text);
  } catch (_) {
    return text;
  }
}

function isLikelyJwt(token) {
  if (!token || typeof token !== 'string') return false;
  const parts = token.split('.');
  return parts.length === 3 && parts.every(Boolean);
}

function getStoredAccessToken() {
  if (typeof localStorage === 'undefined') return null;
  const token = localStorage.getItem('access_token');
  if (!isLikelyJwt(token)) {
    if (token) {
      localStorage.removeItem('access_token');
    }
    return null;
  }
  return token;
}

async function _doRefresh() {
  const refreshToken = typeof localStorage !== 'undefined' ? localStorage.getItem('refresh_token') : null;
  if (!refreshToken) return null;
  try {
    const resp = await fetch(`${API_BASE}/api/users/refresh`, {
      method: 'POST',
      credentials: 'include',
      headers: { 'Authorization': `Bearer ${refreshToken}`, 'Content-Type': 'application/json' },
    });
    if (!resp.ok) return null;
    const data = await resp.json();
    if (data.access_token) {
      localStorage.setItem('access_token', data.access_token);
      return data.access_token;
    }
  } catch (_) { /* ignore */ }
  return null;
}

function clearStoredAuthState() {
  if (typeof localStorage === 'undefined') return;
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('isAuthenticated');
  localStorage.removeItem('user');
}

async function _requestWithAuth(endpoint, options = {}, _isRetry = false) {
  const url = `${API_BASE}${endpoint}`;

  const token = getStoredAccessToken();
  const defaultOptions = {
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
      ...options.headers,
    },
    ...options,
  };

  const response = await fetch(url, defaultOptions);

  // Attempt silent token refresh on 401 (once)
  if (response.status === 401 && !_isRetry && !endpoint.includes('/api/users/refresh')) {
    const newToken = await _doRefresh();
    if (newToken) {
      return _requestWithAuth(endpoint, options, true);
    }
    // Refresh failed — clear auth and notify app state listeners.
    clearStoredAuthState();
    if (typeof window !== 'undefined') {
      window.dispatchEvent(new CustomEvent('userUpdated'));
      window.dispatchEvent(new CustomEvent('auth:logout'));
    }
  }

  return response;
}

export async function apiRequest(endpoint, options = {}, _isRetry = false) {
  const response = await _requestWithAuth(endpoint, options, _isRetry);

  if (!response.ok) {
    let message = `API Error: ${response.status} ${response.statusText}`;
    try {
      const body = await parseResponseBody(response);
      if (body?.error) message = body.error;
      else if (body?.msg) message = body.msg;
      else if (body?.message) message = body.message;
      else if (typeof body === 'string' && body.trim()) message = body.trim().slice(0, 200);
    } catch (_) { /* body not JSON, keep default message */ }

    throw new Error(message);
  }

  const body = await parseResponseBody(response);
  if (typeof body === 'string') {
    const preview = body.trim().slice(0, 80).toLowerCase();
    if (preview.startsWith('<!doctype') || preview.startsWith('<html')) {
      throw new Error('API returned HTML instead of JSON');
    }
    throw new Error('API returned non-JSON response');
  }

  return body;
}

// Returns raw Response while still applying auth headers and silent refresh behavior.
export async function apiRequestRaw(endpoint, options = {}, _isRetry = false) {
  return _requestWithAuth(endpoint, options, _isRetry);
}

export async function apiGet(endpoint) {
  return apiRequest(endpoint);
}

export async function apiPost(endpoint, data) {
  return apiRequest(endpoint, {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function apiPut(endpoint, data) {
  return apiRequest(endpoint, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

export async function apiDelete(endpoint) {
  return apiRequest(endpoint, {
    method: 'DELETE',
  });
}
