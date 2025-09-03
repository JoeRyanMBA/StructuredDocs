<template>
  <div class="password-setup">
    <div class="setup-container">
      <div class="setup-card">
        <div class="setup-header">
          <h1>Set Your Password</h1>
          <div v-if="tokenData" class="user-info">
            <p>Welcome, <strong>{{ tokenData.user_name }}</strong>!</p>
            <p class="email">{{ tokenData.user_email }}</p>
          </div>
        </div>

        <!-- Loading state -->
        <div v-if="loading" class="loading-state">
          <div class="spinner"></div>
          <p>Validating your setup link...</p>
        </div>

        <!-- Token validation error -->
        <div v-else-if="tokenError" class="error-state">
          <div class="error-icon">⚠️</div>
          <h2>Setup Link Invalid</h2>
          <p>{{ tokenError }}</p>
          <div class="error-actions">
            <p>Please contact your system administrator for a new setup link.</p>
            <router-link to="/login" class="btn btn-secondary">Back to Login</router-link>
          </div>
        </div>

        <!-- Password setup form -->
        <div v-else-if="tokenData && !success" class="setup-form">
          <div class="setup-info">
            <p v-if="tokenData.token_type === 'setup'">
              Complete your account setup by creating a secure password.
            </p>
            <p v-else>
              Create a new password for your account.
            </p>
            <div class="expires-info">
              <small>This link expires {{ formatExpiryTime(tokenData.expires_at) }}</small>
            </div>
          </div>

          <form @submit.prevent="submitPassword" class="password-form">
            <div class="form-group">
              <label for="password">New Password</label>
              <div class="password-input-container">
                <input
                  :type="showPassword ? 'text' : 'password'"
                  id="password"
                  v-model="passwordForm.password"
                  required
                  minlength="8"
                  :disabled="submitting"
                  placeholder="Enter your new password"
                  autocomplete="new-password"
                  class="password-input"
                  @input="validatePassword"
                />
                <button
                  type="button"
                  class="password-toggle"
                  @click="showPassword = !showPassword"
                  :aria-label="showPassword ? 'Hide password' : 'Show password'"
                  :aria-pressed="showPassword.toString()"
                >
                  <span v-if="showPassword" class="toggle-icon">🙈</span>
                  <span v-else class="toggle-icon">👁️</span>
                </button>
              </div>
              <div class="password-strength">
                <div class="strength-meter" :class="passwordStrength.class">
                  <div class="strength-fill" :style="{ width: passwordStrength.width }"></div>
                </div>
                <small :class="passwordStrength.class">{{ passwordStrength.text }}</small>
              </div>
            </div>

            <div class="form-group">
              <label for="confirmPassword">Confirm Password</label>
              <div class="password-input-container">
                <input
                  :type="showConfirmPassword ? 'text' : 'password'"
                  id="confirmPassword"
                  v-model="passwordForm.confirmPassword"
                  required
                  :disabled="submitting"
                  placeholder="Confirm your new password"
                  autocomplete="new-password"
                  class="password-input"
                  @input="validatePasswordMatch"
                />
                <button
                  type="button"
                  class="password-toggle"
                  @click="showConfirmPassword = !showConfirmPassword"
                  :aria-label="showConfirmPassword ? 'Hide password' : 'Show password'"
                  :aria-pressed="showConfirmPassword.toString()"
                >
                  <span v-if="showConfirmPassword" class="toggle-icon">🙈</span>
                  <span v-else class="toggle-icon">👁️</span>
                </button>
              </div>
              <small v-if="confirmPasswordError" class="error-text">{{ confirmPasswordError }}</small>
            </div>

            <div class="password-requirements">
              <h4>Password Requirements:</h4>
              <ul>
                <li :class="{ valid: passwordChecks.length }">At least 8 characters long</li>
                <li :class="{ valid: passwordChecks.uppercase }">Contains uppercase letter</li>
                <li :class="{ valid: passwordChecks.lowercase }">Contains lowercase letter</li>
                <li :class="{ valid: passwordChecks.number }">Contains a number</li>
                <li :class="{ valid: passwordChecks.special }">Contains special character</li>
              </ul>
            </div>

            <div class="form-actions">
              <button
                type="submit"
                class="btn btn-primary btn-large"
                :disabled="!isFormValid || submitting"
              >
                {{ submitting ? 'Setting Password...' : 'Set Password' }}
              </button>
            </div>

            <div v-if="error" class="error-message">
              {{ error }}
            </div>
          </form>
        </div>

        <!-- Success state -->
        <div v-else-if="success" class="success-state">
          <div class="success-icon">✅</div>
          <h2>Password Set Successfully!</h2>
          <p>Your password has been created and your account is now ready to use.</p>
          <div class="success-actions">
            <router-link to="/login" class="btn btn-primary btn-large">
              Continue to Login
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { apiGet, apiPost } from '../api/base';

export default {
  name: 'PasswordSetupView',
  data() {
    return {
      token: null,
      tokenData: null,
      tokenError: null,
      loading: true,
      submitting: false,
      success: false,
      error: '',
  showPassword: false,
  showConfirmPassword: false,
      passwordForm: {
        password: '',
        confirmPassword: ''
      },
      confirmPasswordError: '',
      passwordChecks: {
        length: false,
        uppercase: false,
        lowercase: false,
        number: false,
        special: false
      }
    }
  },
  computed: {
    passwordStrength() {
      const checks = Object.values(this.passwordChecks)
      const score = checks.filter(Boolean).length
      
      if (score === 0) return { class: '', width: '0%', text: '' }
      if (score <= 2) return { class: 'weak', width: '25%', text: 'Weak' }
      if (score <= 3) return { class: 'fair', width: '50%', text: 'Fair' }
      if (score <= 4) return { class: 'good', width: '75%', text: 'Good' }
      return { class: 'strong', width: '100%', text: 'Strong' }
    },
    isFormValid() {
      return this.passwordForm.password &&
             this.passwordForm.confirmPassword &&
             this.passwordForm.password === this.passwordForm.confirmPassword &&
             this.passwordChecks.length &&
             !this.confirmPasswordError
    }
  },
  async mounted() {
    this.token = this.$route.params.token
    if (this.token) {
      await this.validateToken()
    } else {
      this.tokenError = 'No setup token provided'
      this.loading = false
    }
  },
  methods: {
    async validateToken() {
      try {
        const data = await apiGet(`/api/users/validate-reset-token/${this.token}`);
        this.tokenData = data;
        console.log('Token validation successful:', this.tokenData);
      } catch (error) {
        console.error('Token validation failed:', error);
        this.tokenError = 'Invalid or expired setup link. Please contact your administrator.';
      } finally {
        this.loading = false;
      }
    },
    
    validatePassword() {
      const password = this.passwordForm.password
      
      this.passwordChecks = {
        length: password.length >= 8,
        uppercase: /[A-Z]/.test(password),
        lowercase: /[a-z]/.test(password),
        number: /\d/.test(password),
        special: /[!@#$%^&*(),.?":{}|<>]/.test(password)
      }
      
      this.validatePasswordMatch()
    },
    
    validatePasswordMatch() {
      if (this.passwordForm.confirmPassword) {
        if (this.passwordForm.password !== this.passwordForm.confirmPassword) {
          this.confirmPasswordError = 'Passwords do not match'
        } else {
          this.confirmPasswordError = ''
        }
      } else {
        this.confirmPasswordError = ''
      }
    },
    
    async submitPassword() {
      if (!this.isFormValid) return;
      
      this.submitting = true;
      this.error = '';
      
      try {
        const response = await apiPost(`/api/users/reset-password/${this.token}`, {
          password: this.passwordForm.password
        });
        
        console.log('Password setup successful:', response);
        this.success = true;
        
      } catch (error) {
        console.error('Password setup failed:', error);
        this.error = 'Failed to set password. The link may have expired or been used already.';
      } finally {
        this.submitting = false;
      }
    },
    
    formatExpiryTime(expiresAt) {
      const now = new Date()
      const expiry = new Date(expiresAt)
      const diffMs = expiry - now
      
      if (diffMs <= 0) return 'soon'
      
      const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
      const diffMinutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60))
      
      if (diffHours > 0) {
        return `in ${diffHours} hour${diffHours > 1 ? 's' : ''}`
      } else {
        return `in ${diffMinutes} minute${diffMinutes > 1 ? 's' : ''}`
      }
    }
  }
}
</script>

<style scoped>
.password-setup {
  min-height: 100vh;
  background: linear-gradient(135deg, var(--primary-deep-teal) 0%, var(--extended-slate-purple) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.setup-container {
  width: 100%;
  max-width: 500px;
}

.setup-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.setup-header {
  background: linear-gradient(135deg, var(--primary-deep-teal) 0%, var(--extended-slate-purple) 100%);
  color: white;
  padding: 30px;
  text-align: center;
}

.setup-header h1 {
  margin: 0 0 15px 0;
  font-size: 28px;
  font-weight: 600;
}

.user-info p {
  margin: 5px 0;
  opacity: 0.9;
}

.user-info .email {
  font-size: 14px;
  opacity: 0.8;
}

.loading-state,
.error-state,
.success-state {
  padding: 40px 30px;
  text-align: center;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid var(--bg-light-mist-gray);
  border-top: 4px solid var(--primary-deep-teal);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-icon,
.success-icon {
  font-size: 48px;
  margin-bottom: 20px;
}

.error-state h2,
.success-state h2 {
  color: var(--text-primary-charcoal);
  margin-bottom: 15px;
}

.setup-form {
  padding: 30px;
}

.setup-info {
  margin-bottom: 30px;
  text-align: center;
}

.setup-info p {
  color: var(--text-secondary-cool-gray);
  margin-bottom: 10px;
}

.expires-info {
  padding: 10px;
  background: var(--extended-warm-taupe);
  border-radius: 6px;
  border-left: 4px solid var(--warning-amber);
}

.password-form {
  max-width: 100%;
}

.form-group {
  margin-bottom: 25px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: var(--text-primary-charcoal);
}

.form-group input {
  width: 100%;
  padding: 12px;
  border: 2px solid var(--extended-lavender-gray);
  border-radius: 8px;
  font-size: 16px;
  transition: border-color 0.3s;
  box-sizing: border-box;
}

.form-group input:focus {
  outline: none;
  border-color: var(--primary-deep-teal);
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.password-strength {
  margin-top: 10px;
}

.strength-meter {
  height: 6px;
  background: var(--extended-lavender-gray);
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 5px;
}

.strength-fill {
  height: 100%;
  transition: all 0.3s;
  border-radius: 3px;
}

.strength-meter.weak .strength-fill { background: var(--error-coral-red); }
.strength-meter.fair .strength-fill { background: var(--warning-amber); }
.strength-meter.good .strength-fill { background: var(--primary-light-teal); }
.strength-meter.strong .strength-fill { background: var(--success-mint-green); }

.password-strength small {
  font-weight: 500;
}

.password-strength small.weak { color: var(--error-coral-red); }
.password-strength small.fair { color: var(--warning-amber); }
.password-strength small.good { color: var(--primary-light-teal); }
.password-strength small.strong { color: var(--success-mint-green); }

.password-requirements {
  background: var(--bg-light-mist-gray);
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 25px;
}

.password-requirements h4 {
  margin: 0 0 15px 0;
  color: var(--text-primary-charcoal);
  font-size: 14px;
}

.password-requirements ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.password-requirements li {
  padding: 5px 0;
  font-size: 14px;
  color: var(--text-secondary-cool-gray);
  position: relative;
  padding-left: 25px;
}

.password-requirements li:before {
  content: '✗';
  position: absolute;
  left: 0;
  color: var(--error-coral-red);
  font-weight: bold;
}

.password-requirements li.valid {
  color: var(--success-mint-green);
}

.password-requirements li.valid:before {
  content: '✓';
  color: var(--success-mint-green);
}

.btn {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  text-decoration: none;
  display: inline-block;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-large {
  padding: 15px 30px;
  font-size: 18px;
  width: 100%;
}

.btn-primary {
  background: linear-gradient(135deg, var(--primary-deep-teal) 0%, var(--extended-slate-purple) 100%);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: linear-gradient(135deg, var(--primary-medium-teal) 0%, #5a3a7a 100%);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.btn-secondary {
  background: var(--text-secondary-cool-gray);
  color: white;
}

.btn-secondary:hover {
  background: var(--text-primary-charcoal);
  text-decoration: none;
  color: white;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.form-actions {
  text-align: center;
  margin-top: 30px;
}

.error-message {
  background: var(--extended-dusty-rose);
  color: var(--error-coral-red);
  padding: 12px;
  border-radius: 6px;
  margin-top: 15px;
  text-align: center;
}

.error-text {
  color: var(--error-coral-red);
  font-size: 14px;
  margin-top: 5px;
  display: block;
}

.error-actions,
.success-actions {
  margin-top: 30px;
}

/* Password input with toggle (match LoginView) */
.password-input-container {
  position: relative;
  display: flex;
  align-items: center;
}

.password-input-container .password-input {
  flex: 1;
  padding-right: 50px;
  -webkit-appearance: none;
  -moz-appearance: none;
  appearance: none;
}

.password-toggle {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  cursor: pointer;
  padding: 8px;
  border-radius: 4px;
  color: var(--text-secondary-cool-gray);
  font-size: 18px;
  transition: all 0.2s ease;
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 32px;
  min-height: 32px;
}

.toggle-icon {
  display: inline-block;
  line-height: 1;
  font-size: 18px;
}

.password-toggle:hover {
  color: var(--primary-medium-teal);
  background-color: rgba(0, 123, 191, 0.1);
}

.password-toggle:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.password-toggle:focus {
  outline: 2px solid var(--primary-light-teal-t);
  outline-offset: 2px;
  background-color: rgba(0, 123, 191, 0.1);
}

/* Ensure our toggle appears above any browser-native elements */
.password-input-container {
  isolation: isolate;
}

/* Hide Edge/IE native reveal (prevents double toggles) */
.password-input::-ms-reveal {
  display: none;
}
.password-input::-ms-clear {
  display: none;
}

@media (max-width: 768px) {
  .password-setup {
    padding: 10px;
  }
  
  .setup-header {
    padding: 20px;
  }
  
  .setup-header h1 {
    font-size: 24px;
  }
  
  .setup-form {
    padding: 20px;
  }
}
</style>
