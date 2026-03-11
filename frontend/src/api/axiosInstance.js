/**
 * Axios instance with automatic JWT token refresh.
 *
 * When a request fails with 401, this module will:
 * 1. Attempt to call POST /api/users/refresh with the stored refresh token.
 * 2. If successful, update the stored access token and retry the original request.
 * 3. If the refresh fails, clear all tokens and redirect to /login.
 */
import axios from 'axios';

const axiosInstance = axios.create();

let isRefreshing = false;
let failedQueue = [];

function processQueue(error, token = null) {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
}

axiosInstance.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`;
  }
  return config;
});

axiosInstance.interceptors.response.use(
  response => response,
  async error => {
    const originalRequest = error.config;

    // Only attempt refresh for 401 errors that haven't been retried yet,
    // and don't retry the refresh endpoint itself.
    if (
      error.response?.status === 401 &&
      !originalRequest._retry &&
      !originalRequest.url?.includes('/api/users/refresh')
    ) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        }).then(token => {
          originalRequest.headers['Authorization'] = `Bearer ${token}`;
          return axiosInstance(originalRequest);
        }).catch(err => Promise.reject(err));
      }

      originalRequest._retry = true;
      isRefreshing = true;

      const refreshToken = localStorage.getItem('refresh_token');
      if (!refreshToken) {
        isRefreshing = false;
        clearAuthAndRedirect();
        return Promise.reject(error);
      }

      try {
        const resp = await axios.post('/api/users/refresh', {}, {
          headers: { 'Authorization': `Bearer ${refreshToken}` }
        });
        const newToken = resp.data.access_token;
        localStorage.setItem('access_token', newToken);
        axiosInstance.defaults.headers.common['Authorization'] = `Bearer ${newToken}`;
        axios.defaults.headers.common['Authorization'] = `Bearer ${newToken}`;
        processQueue(null, newToken);
        originalRequest.headers['Authorization'] = `Bearer ${newToken}`;
        return axiosInstance(originalRequest);
      } catch (refreshError) {
        processQueue(refreshError, null);
        clearAuthAndRedirect();
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);

function clearAuthAndRedirect() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('isAuthenticated');
  delete axios.defaults.headers.common['Authorization'];
  // Dispatch event so useSessionTimeout shows the modal instead of a raw page reload
  window.dispatchEvent(new CustomEvent('auth:logout'));
}

export default axiosInstance;
