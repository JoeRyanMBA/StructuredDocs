/**
 * Composable for inactivity-based session timeout handling.
 *
 * - Shows a warning after INACTIVITY_TIMEOUT_MS of no user activity.
 * - Auto-logs out WARNING_BEFORE_MS after the warning if no action is taken.
 * - Any user activity (mouse, keyboard, touch, scroll) resets the inactivity timer.
 * - Also enforces a hard logout when the JWT token itself expires (shows warning first).
 * - extendSession() refreshes the token and resets all timers.
 * - Listens for the global 'auth:logout' event dispatched by API interceptors so
 *   token-refresh failures also surface as the modal rather than a raw page redirect.
 */
import { ref } from 'vue';
import axios from 'axios';
import { store } from '@/store';
import router from '@/router';

const INACTIVITY_TIMEOUT_MS  = 30 * 60 * 1000; // 30 min idle → show warning
const WARNING_BEFORE_MS      =  5 * 60 * 1000; // 5 min grace after warning
const EXPIRED_GRACE_MS       = 30 * 1000;       // 30 s grace when token already expired

// Module-level state so a single watcher runs regardless of how many
// components call useSessionTimeout().
const showWarning = ref(false);
const secondsRemaining = ref(0);
const sessionExpired = ref(false); // true when triggered by token expiry / API failure

let warningTimer        = null;
let expiryTimer         = null;
let tokenExpiryTimer    = null;
let countdownInterval   = null;
let activityAttached    = false;
let expiredListenerAdded = false; // guard against double-registration

const ACTIVITY_EVENTS = ['mousemove', 'keydown', 'mousedown', 'touchstart', 'scroll'];

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
  clearTimeout(tokenExpiryTimer);
  clearInterval(countdownInterval);
  warningTimer = expiryTimer = tokenExpiryTimer = countdownInterval = null;
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
  detachActivityListeners();
  showWarning.value = false;
  sessionExpired.value = false;
  store.setUser(null);
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('isAuthenticated');
  delete axios.defaults.headers.common['Authorization'];
  router.push('/login');
}

/**
 * Show the warning modal then auto-logout after gracePeriodMs.
 * expired=true switches the modal title to "Session Expired".
 */
function showWarningThenLogout(gracePeriodMs, expired = false) {
  if (showWarning.value) return;
  clearTimeout(expiryTimer);
  clearInterval(countdownInterval);
  sessionExpired.value = expired;
  showWarning.value = true;
  startCountdown(gracePeriodMs);
  expiryTimer = setTimeout(() => performLogout(), gracePeriodMs);
}

/** Schedule the inactivity warning + auto-logout timers from NOW. */
function scheduleInactivityTimers() {
  clearTimeout(warningTimer);
  clearTimeout(expiryTimer);
  clearInterval(countdownInterval);

  warningTimer = setTimeout(() => {
    showWarningThenLogout(WARNING_BEFORE_MS);
  }, INACTIVITY_TIMEOUT_MS);
}

/** Called on every user activity event; resets the inactivity clock. */
function onActivity() {
  if (showWarning.value) return;
  scheduleInactivityTimers();
}

function attachActivityListeners() {
  if (activityAttached) return;
  ACTIVITY_EVENTS.forEach(e => document.addEventListener(e, onActivity, { passive: true }));
  activityAttached = true;
}

function detachActivityListeners() {
  if (!activityAttached) return;
  ACTIVITY_EVENTS.forEach(e => document.removeEventListener(e, onActivity));
  activityAttached = false;
}

function startWatcher() {
  clearTimers();
  detachActivityListeners();

  const token = localStorage.getItem('access_token');
  if (!token) return;

  // Show warning (then hard-logout) at JWT expiry instead of silently logging out
  const expiry = getTokenExpiry(token);
  if (expiry) {
    const msUntilExpiry = expiry - Date.now();
    if (msUntilExpiry <= 0) {
      showWarningThenLogout(EXPIRED_GRACE_MS, true);
      return;
    }
    tokenExpiryTimer = setTimeout(() => showWarningThenLogout(EXPIRED_GRACE_MS, true), msUntilExpiry);
  }

  // Register global event listener for API-interceptor-triggered logouts (once only)
  if (!expiredListenerAdded) {
    window.addEventListener('auth:logout', () => showWarningThenLogout(EXPIRED_GRACE_MS, true));
    expiredListenerAdded = true;
  }

  // Start inactivity tracking
  attachActivityListeners();
  scheduleInactivityTimers();
}

function stopWatcher() {
  clearTimers();
  detachActivityListeners();
  showWarning.value = false;
}

async function extendSession() {
  const refreshToken = localStorage.getItem('refresh_token');
  if (!refreshToken) { performLogout(); return; }
  try {
    const resp = await axios.post('/api/users/refresh', {}, {
      headers: { Authorization: `Bearer ${refreshToken}` }
    });
    const newToken = resp.data.access_token;
    localStorage.setItem('access_token', newToken);
    axios.defaults.headers.common['Authorization'] = `Bearer ${newToken}`;
    showWarning.value = false;
    startWatcher(); // restart with fresh token expiry + fresh inactivity clock
  } catch {
    performLogout();
  }
}

export function useSessionTimeout() {
  return {
    showWarning,
    secondsRemaining,
    sessionExpired,
    startWatcher,
    stopWatcher,
    extendSession,
    performLogout,
  };
}

