// src/api/base.js
// Base API configuration for HTTP Basic Auth

// Normalize and secure the API base URL to avoid mixed content in HTTPS
function computeApiBase() {
  let raw = (import.meta.env.VITE_API_BASE_URL || '').trim();
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

export const API_BASE = computeApiBase();

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

export async function apiRequest(endpoint, options = {}, _isRetry = false) {
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
      return apiRequest(endpoint, options, true);
    }
    // Refresh failed — clear auth and show session modal via event (no raw page reload)
    if (typeof localStorage !== 'undefined') {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('isAuthenticated');
    }
    if (typeof window !== 'undefined') {
      window.dispatchEvent(new CustomEvent('auth:logout'));
    }
  }

  if (!response.ok) {
    let message = `API Error: ${response.status} ${response.statusText}`;
    try {
      const body = await response.json();
      if (body?.error) message = body.error;
      else if (body?.msg) message = body.msg;
      else if (body?.message) message = body.message;
    } catch (_) { /* body not JSON, keep default message */ }

    throw new Error(message);
  }
  
  return response.json();
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

