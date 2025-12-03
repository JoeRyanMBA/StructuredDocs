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

export async function apiRequest(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  
  const defaultOptions = {
    credentials: 'include', // Include HTTP Basic Auth credentials
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  const response = await fetch(url, defaultOptions);
  
  if (!response.ok) {
    throw new Error(`API Error: ${response.status} ${response.statusText}`);
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
