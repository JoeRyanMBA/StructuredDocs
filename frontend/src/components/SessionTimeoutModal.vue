<template>
  <teleport to="body">
    <transition name="modal-fade">
      <div v-if="show" class="session-modal-backdrop" role="dialog" aria-modal="true" aria-labelledby="session-timeout-title">
        <div class="session-modal">
          <div class="session-modal-header">
            <span class="session-icon"><i class="bi bi-clock-history"></i></span>
            <h5 id="session-timeout-title">Session Expiring Soon</h5>
          </div>
          <div class="session-modal-body">
            <p>Your session will expire in</p>
            <div class="session-countdown">{{ formattedTime }}</div>
            <p class="session-hint">Would you like to stay logged in?</p>
          </div>
          <div class="session-modal-footer">
            <button class="btn btn-primary" @click="$emit('extend')">Stay Logged In</button>
            <button class="btn btn-outline-secondary" @click="$emit('logout')">Log Out Now</button>
          </div>
        </div>
      </div>
    </transition>
  </teleport>
</template>

<script>
export default {
  name: 'SessionTimeoutModal',
  props: {
    show: {
      type: Boolean,
      default: false,
    },
    secondsRemaining: {
      type: Number,
      default: 0,
    },
  },
  emits: ['extend', 'logout'],
  computed: {
    formattedTime() {
      const s = Math.max(0, this.secondsRemaining);
      const minutes = Math.floor(s / 60);
      const seconds = s % 60;
      return `${minutes}:${String(seconds).padStart(2, '0')}`;
    },
  },
};
</script>

<style scoped>
.session-modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 2000;
  display: flex;
  align-items: center;
  justify-content: center;
}

.session-modal {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  width: 100%;
  max-width: 380px;
  padding: 2rem;
  text-align: center;
}

.session-modal-header {
  margin-bottom: 1rem;
}

.session-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: #fff3cd;
  color: #e67e22;
  font-size: 1.6rem;
  margin-bottom: 0.75rem;
}

.session-modal-header h5 {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 600;
  color: #343a40;
}

.session-modal-body p {
  margin: 0;
  color: #6c757d;
  font-size: 0.95rem;
}

.session-countdown {
  font-size: 2.8rem;
  font-weight: 700;
  color: #e67e22;
  letter-spacing: 0.05em;
  margin: 0.5rem 0;
}

.session-hint {
  margin-top: 0.25rem;
  font-size: 0.9rem;
  color: #6c757d;
}

.session-modal-footer {
  display: flex;
  gap: 0.75rem;
  justify-content: center;
  margin-top: 1.5rem;
}

.session-modal-footer .btn {
  min-width: 130px;
}

/* Transition */
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 200ms ease;
}
.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}
</style>
