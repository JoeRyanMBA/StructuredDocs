<template>
  <div class="login-container">
    <div class="login-card">
      <!-- Shared header identical to LoginView -->
      <div class="login-header">
        <div class="census-logo">
          <span class="logo-wrapper">
            <span v-show="!symbolLogoLoaded" class="logo-skeleton" aria-hidden="true"></span>
            <img
              class="logo-image"
              :src="symbolLogoSrc"
              alt="StructuredDocs logo"
              decoding="async"
              @load="onSymbolLoad"
              @error="onSymbolError"
            />
          </span>
          <h1>Structured Docs</h1>
          <p class="system-title">Elevated content creation and delivery</p>
        </div>
      </div>

      <div class="login-form-container">
        <!-- Loading state -->
        <div v-if="loading" class="loading-state">
          <div class="spinner"></div>
          <p class="login-subtitle">Validating your setup link...</p>
        </div>

        <!-- Token error state -->
        <div v-else-if="tokenError" class="error-state">
          <div class="error-icon">⚠️</div>
          <h2>Setup Link Invalid</h2>
            <p class="login-subtitle">{{ tokenError }}</p>
            <div class="error-actions">
              <p>Please contact your system administrator for a new setup link.</p>
              <router-link to="/login" class="login-btn alt-btn">Back to Login</router-link>
            </div>
        </div>

        <!-- Success state -->
        <div v-else-if="success" class="success-state">
          <div class="success-icon">✅</div>
          <h2>Password Set Successfully!</h2>
          <p class="login-subtitle">Your password has been created and your account is now ready.</p>
          <div class="success-actions">
            <router-link to="/login" class="login-btn">Continue to Login</router-link>
          </div>
        </div>

        <!-- Form state -->
        <div v-else class="auth-form-wrapper">
          <h2>{{ tokenData?.token_type === 'setup' ? 'Account Setup' : 'Reset Password' }}</h2>
          <p class="login-subtitle" v-if="tokenData">
            <span v-if="tokenData.token_type === 'setup'">Complete your account setup by creating a secure password.</span>
            <span v-else>Create a new password for your account.</span>
          </p>
          <div v-if="tokenData" class="user-info">
            <p>Welcome, <strong>{{ tokenData.user_name }}</strong></p>
            <p class="email">{{ tokenData.user_email }}</p>
            <div class="expires-info">
              <small>This link expires {{ formatExpiryTime(tokenData.expires_at) }}</small>
            </div>
          </div>

          <form @submit.prevent="submitPassword" class="login-form password-form">
            <div class="form-group">
              <label for="password">New Password</label>
              <div class="password-input-container">
                <input
                  id="password"
                  v-model="passwordForm.password"
                  :type="showPassword ? 'text' : 'password'"
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
                  :disabled="submitting"
                  :aria-label="showPassword ? 'Hide password' : 'Show password'"
                  :aria-pressed="showPassword.toString()"
                >
                  <svg
                    v-if="showPassword"
                    class="toggle-icon"
                    width="20"
                    height="20"
                    viewBox="0 0 24 24"
                    fill="none"
                    xmlns="http://www.w3.org/2000/svg"
                    aria-hidden="true"
                  >
                    <path d="M3 3l18 18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M9.88 9.88A3.5 3.5 0 0012 8.5c1.93 0 3.5 1.57 3.5 3.5 0 .77-.25 1.49-.68 2.06" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M10.73 5.08A10.53 10.53 0 0121 12c-2.1 3.5-5.5 6-9 6-1.22 0-2.4-.27-3.5-.77" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M6.53 6.53A10.53 10.53 0 003 12c2.1 3.5 5.5 6 9 6 .96 0 1.9-.16 2.8-.46" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                  <svg
                    v-else
                    class="toggle-icon"
                    width="20"
                    height="20"
                    viewBox="0 0 24 24"
                    fill="none"
                    xmlns="http://www.w3.org/2000/svg"
                    aria-hidden="true"
                  >
                    <path d="M1 12s4-7 11-7 11 7 11 7-4 7-11 7S1 12 1 12z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
                    <circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="2" fill="none"/>
                  </svg>
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
                  id="confirmPassword"
                  v-model="passwordForm.confirmPassword"
                  :type="showConfirmPassword ? 'text' : 'password'"
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
                  :disabled="submitting"
                  :aria-label="showConfirmPassword ? 'Hide password' : 'Show password'"
                  :aria-pressed="showConfirmPassword.toString()"
                >
                  <svg
                    v-if="showConfirmPassword"
                    class="toggle-icon"
                    width="20"
                    height="20"
                    viewBox="0 0 24 24"
                    fill="none"
                    xmlns="http://www.w3.org/2000/svg"
                    aria-hidden="true"
                  >
                    <path d="M3 3l18 18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M9.88 9.88A3.5 3.5 0 0012 8.5c1.93 0 3.5 1.57 3.5 3.5 0 .77-.25 1.49-.68 2.06" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M10.73 5.08A10.53 10.53 0 0121 12c-2.1 3.5-5.5 6-9 6-1.22 0-2.4-.27-3.5-.77" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M6.53 6.53A10.53 10.53 0 003 12c2.1 3.5 5.5 6 9 6 .96 0 1.9-.16 2.8-.46" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                  <svg
                    v-else
                    class="toggle-icon"
                    width="20"
                    height="20"
                    viewBox="0 0 24 24"
                    fill="none"
                    xmlns="http://www.w3.org/2000/svg"
                    aria-hidden="true"
                  >
                    <path d="M1 12s4-7 11-7 11 7 11 7-4 7-11 7S1 12 1 12z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
                    <circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="2" fill="none"/>
                  </svg>
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

            <button type="submit" class="login-btn" :disabled="!isFormValid || submitting">
              <span v-if="submitting">Setting Password...</span>
              <span v-else>Set Password</span>
            </button>

            <div v-if="error" class="error-message">{{ error }}</div>
          </form>
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
      },
      symbolLogoLoaded: false
    }
  },
  computed: {
    symbolLogoSrc() {
      return `${import.meta.env.BASE_URL}assets/StructuredDocsLogoSymbol.svg`
    },
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
    onSymbolLoad() { this.symbolLogoLoaded = true },
    onSymbolError(e) {
      const fallback = `${import.meta.env.BASE_URL}assets/StructuredDocs_logo.svg`
      if (e && e.target && e.target.src !== fallback) {
        e.target.src = fallback
      }
    },
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
/* Copied core styling from LoginView for identical look */
.login-container { min-height: 100vh; display:flex; align-items:center; justify-content:center; padding:2rem; }
.login-card { background:#fff; border-radius:12px; box-shadow:0 20px 40px rgba(0,0,0,0.1); overflow:hidden; max-width:400px; width:100%; }
.login-header { background: var(--primary-deep-teal); color:#fff; padding:2rem; text-align:center; }
.census-logo { display:flex; flex-direction:column; align-items:center; }
.census-logo .logo-image { display:block; width:160px; height:160px; object-fit:contain; margin-bottom:0; }
.census-logo .logo-wrapper { position:relative; display:block; width:160px; height:160px; margin-bottom:0.5rem; }
.census-logo .logo-skeleton { position:absolute; inset:0; border-radius:4px; background:linear-gradient(90deg,#f2f4f7 25%,#e9eef3 37%,#f2f4f7 63%); background-size:400% 100%; animation:logo-shimmer 1.2s ease-in-out infinite; }
@keyframes logo-shimmer { 0%{background-position:100% 0;} 100%{background-position:0 0;} }
.census-logo h1 { margin:0 0 .5rem 0; font-size:1.5rem; font-weight:600; color:#fff; text-shadow:0 1px 8px rgba(0,0,0,0.18); }
.system-title { margin:0; font-size:.9rem; opacity:.9; }
.login-form-container { padding:2rem; }
.login-form-container h2 { margin:0 0 .5rem 0; color:var(--primary-deep-teal); font-size:1.5rem; font-weight:600; }
.login-subtitle { color:var(--text-secondary-cool-gray); margin:0 0 1.5rem 0; font-size:.9rem; line-height:1.4; }
.login-form .form-group { margin-bottom:1.5rem; }
.form-group label { display:block; margin-bottom:.5rem; font-weight:600; color:var(--primary-deep-teal); font-size:.9rem; }
.form-group input { width:100%; padding:.75rem; border:1px solid var(--extended-lavender-gray); border-radius:6px; font-size:.9rem; box-sizing:border-box; transition:border-color .2s ease; }
.form-group input:focus { outline:none; border-color:var(--primary-deep-teal); box-shadow:0 0 0 3px rgba(0,90,156,0.1); }
.login-btn { width:100%; background:var(--primary-deep-teal); color:#fff; padding:.85rem 1rem; border:none; border-radius:6px; font-weight:600; cursor:pointer; font-size:.95rem; transition:background .2s, transform .15s; display:inline-flex; align-items:center; justify-content:center; }
.login-btn:hover:not(:disabled) { background:var(--primary-medium-teal); }
.login-btn:active:not(:disabled) { transform:translateY(1px); }
.login-btn:disabled { opacity:.6; cursor:not-allowed; }
.alt-btn { background: var(--text-secondary-cool-gray); }
.alt-btn:hover:not(:disabled){ background: var(--text-primary-charcoal); }

/* Reuse password toggle styling from LoginView */
.password-input-container { position:relative; display:flex; align-items:center; }
.password-input { flex:1; padding-right:50px; -webkit-appearance:none; appearance:none; }
.password-input::-ms-reveal, .password-input::-ms-clear { display:none; }
.password-toggle { position:absolute; right:12px; top:50%; transform:translateY(-50%); background:none; border:none; cursor:pointer; padding:8px; border-radius:4px; color:var(--text-secondary-cool-gray); font-size:18px; transition:all .2s ease; z-index:10; display:flex; align-items:center; justify-content:center; min-width:32px; min-height:32px; }
.password-toggle:hover { color:var(--primary-medium-teal); background-color:rgba(0,123,191,0.1); }
.password-toggle:disabled { opacity:.5; cursor:not-allowed; }
.password-toggle:focus { outline:2px solid var(--primary-light-teal-t); outline-offset:2px; background-color:rgba(0,123,191,0.1); }

/* Additional password-specific UI */
.password-strength { margin-top:10px; }
.strength-meter { height:6px; background:var(--extended-lavender-gray); border-radius:3px; overflow:hidden; margin-bottom:5px; }
.strength-fill { height:100%; transition:all .3s; border-radius:3px; }
.strength-meter.weak .strength-fill { background: var(--error-coral-red); }
.strength-meter.fair .strength-fill { background: var(--warning-amber); }
.strength-meter.good .strength-fill { background: var(--primary-light-teal); }
.strength-meter.strong .strength-fill { background: var(--success-mint-green); }
.password-strength small { font-weight:500; }
.password-strength small.weak { color: var(--error-coral-red); }
.password-strength small.fair { color: var(--warning-amber); }
.password-strength small.good { color: var(--primary-light-teal); }
.password-strength small.strong { color: var(--success-mint-green); }

.password-requirements { background: var(--bg-light-mist-gray); padding:1rem; border-radius:8px; margin:1.25rem 0 1.75rem 0; }
.password-requirements h4 { margin:0 0 .75rem 0; font-size:.8rem; letter-spacing:.5px; text-transform:uppercase; color:var(--text-primary-charcoal); }
.password-requirements ul { list-style:none; padding:0; margin:0; }
.password-requirements li { padding:.35rem 0 .35rem 25px; font-size:.75rem; color:var(--text-secondary-cool-gray); position:relative; }
.password-requirements li:before { content:'✗'; position:absolute; left:0; color:var(--error-coral-red); font-weight:bold; }
.password-requirements li.valid { color:var(--success-mint-green); }
.password-requirements li.valid:before { content:'✓'; color:var(--success-mint-green); }

.user-info { margin:0 0 1rem 0; text-align:center; }
.user-info p { margin:.25rem 0; font-size:.8rem; }
.user-info .email { font-size:.75rem; opacity:.85; }
.expires-info { margin-top:.5rem; background:var(--extended-warm-taupe); padding:.5rem .75rem; border-radius:6px; border-left:4px solid var(--warning-amber); }

.loading-state, .error-state, .success-state { text-align:center; }
.error-icon, .success-icon { font-size:2.5rem; margin-bottom:1rem; }
.error-actions, .success-actions { margin-top:1.5rem; }

.error-message { background: var(--extended-dusty-rose); color: var(--error-coral-red); padding:.75rem; border-radius:6px; font-size:.85rem; margin-top:1rem; text-align:center; }
.error-text { color: var(--error-coral-red); font-size:.7rem; margin-top:.25rem; display:block; }

@media (max-width: 768px) {
  .login-container { padding:1rem; }
  .census-logo .logo-image, .census-logo .logo-wrapper { width:120px; height:120px; }
}
</style>
