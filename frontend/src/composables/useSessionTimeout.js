/**
 * Composable for proactive JWT session expiry handling.
 *
 * - Decodes the stored access_token to read the `exp` claim.
 * - Sets a warning timer (WARNING_BEFORE_MS before expiry) to show a modal.
 * - Sets an expiry timer to auto-logout when the token expires.
 * - Provides extendSession() to silently refresh the token and reset timers.
 */
import { ref } from 'vue';
import axios from 'axios';
import { store } from '@/store';
import router from '@/router';

const WARNING_BEFORE_MS = 5 * 60 * 1000; // show warning 5 minutes before expiry

// Module-level state so a single watcher runs regardless of how many
// components call useSessionTimeout().
const showWarning = ref(false);
const secondsRemaining = ref(0);

let warningTimer = null;
let expiryTimer = null;
let countdownInterval = null;

function getTokenExpiry(token) {
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    return typeof payload.exp === 'number' ? payload.exp * 1000 : null;
  } catch {
    return null;
  }
}

function clearTimers() {
  clearTimeout(warningTimer);
  clearTimeout(expiryTimer);
  clearInterval(countdownInterval);
  warningTimer = null;
  expiryTimer = null;
  countdownInterval = null;
}

function startCountdown(ms) {
  clearInterval(countdownInterval);
  secondsRemaining.value = Math.max(0, Math.floor(ms / 1000));
  countdownInterval = setInterval(() => {
    if (secondsRemaining.value > 0) {
      secondsRemaining.value--;
    } else {
      clearInterval(countdownInterval);
    }
  }, 1000);
}

function performLogout() {
  clearTimers();
  showWarning.value = false;
  store.setUser(null);
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('isAuthenticated');
  delete axios.defaults.headers.common['Authorization'];
  router.push('/login');
}

function startWatcher() {
  clearTimers();

  const token = localStorage.getItem('access_token');
  if (!token) return;

  const expiry = getTokenExpiry(token);
  if (!expiry) return;

  const now = Date.now();
  const msUntilExpiry = expiry - now;

  if (msUntilExpiry <= 0) {
    performLogout();
    return;
  }

  const msUntilWarning = msUntilExpiry - WARNING_BEFORE_MS;

  if (msUntilWarning > 0) {
    // Token still has plenty of time; schedule warning for later
    warningTimer = setTimeout(() => {
      showWarning.value = true;
      startCountdown(WARNING_BEFORE_MS);
    }, msUntilWarning);
  } else {
    // Already within the warning window
    showWarning.value = true;
    startCountdown(msUntilExpiry);
  }

  expiryTimer = setTimeout(() => {
    performLogout();
  }, msUntilExpiry);
}

function stopWatcher() {
  clearTimers();
  showWarning.value = false;
}

async function extendSession() {
  const refreshToken = localStorage.getItem('refresh_token');
  if (!refreshToken) {
    performLogout();
    return;
  }
  try {
    const resp = await axios.post('/api/users/refresh', {}, {
      headers: { Authorization: `Bearer ${refreshToken}` }
    });
    const newToken = resp.data.access_token;
    localStorage.setItem('access_token', newToken);
    axios.defaults.headers.common['Authorization'] = `Bearer ${newToken}`;
    showWarning.value = false;
    startWatcher();
  } catch {
    performLogout();
  }
}

export function useSessionTimeout() {
  return {
    showWarning,
    secondsRemaining,
    startWatcher,
    stopWatcher,
    extendSession,
    performLogout,
  };
}
