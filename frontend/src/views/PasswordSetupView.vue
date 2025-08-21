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
              <input
                type="password"
                id="password"
                v-model="passwordForm.password"
                required
                minlength="8"
                :disabled="submitting"
                placeholder="Enter your new password"
                @input="validatePassword"
              />
              <div class="password-strength">
                <div class="strength-meter" :class="passwordStrength.class">
                  <div class="strength-fill" :style="{ width: passwordStrength.width }"></div>
                </div>
                <small :class="passwordStrength.class">{{ passwordStrength.text }}</small>
              </div>
            </div>

            <div class="form-group">
              <label for="confirmPassword">Confirm Password</label>
              <input
                type="password"
                id="confirmPassword"
                v-model="passwordForm.confirmPassword"
                required
                :disabled="submitting"
                placeholder="Confirm your new password"
                @input="validatePasswordMatch"
              />
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
import axios from 'axios'

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
        const response = await axios.get(`/api/users/validate-reset-token/${this.token}`)
        this.tokenData = response.data
        console.log('Token validation successful:', this.tokenData)
      } catch (error) {
        console.error('Token validation failed:', error)
        if (error.response?.data?.error) {
          this.tokenError = error.response.data.error
        } else {
          this.tokenError = 'Invalid or expired setup link'
        }
      } finally {
        this.loading = false
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
      if (!this.isFormValid) return
      
      this.submitting = true
      this.error = ''
      
      try {
        const response = await axios.post(`/api/users/reset-password/${this.token}`, {
          password: this.passwordForm.password
        })
        
        console.log('Password setup successful:', response.data)
        this.success = true
        
      } catch (error) {
        console.error('Password setup failed:', error)
        if (error.response?.data?.error) {
          this.error = error.response.data.error
        } else {
          this.error = 'Failed to set password. Please try again.'
        }
      } finally {
        this.submitting = false
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
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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
  border: 4px solid #f3f3f3;
  border-top: 4px solid #667eea;
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
  color: #333;
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
  color: #666;
  margin-bottom: 10px;
}

.expires-info {
  padding: 10px;
  background: #fff3cd;
  border-radius: 6px;
  border-left: 4px solid #ffc107;
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
  color: #333;
}

.form-group input {
  width: 100%;
  padding: 12px;
  border: 2px solid #e1e5e9;
  border-radius: 8px;
  font-size: 16px;
  transition: border-color 0.3s;
  box-sizing: border-box;
}

.form-group input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.password-strength {
  margin-top: 10px;
}

.strength-meter {
  height: 6px;
  background: #e1e5e9;
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 5px;
}

.strength-fill {
  height: 100%;
  transition: all 0.3s;
  border-radius: 3px;
}

.strength-meter.weak .strength-fill { background: #dc3545; }
.strength-meter.fair .strength-fill { background: #ffc107; }
.strength-meter.good .strength-fill { background: #17a2b8; }
.strength-meter.strong .strength-fill { background: #28a745; }

.password-strength small {
  font-weight: 500;
}

.password-strength small.weak { color: #dc3545; }
.password-strength small.fair { color: #ffc107; }
.password-strength small.good { color: #17a2b8; }
.password-strength small.strong { color: #28a745; }

.password-requirements {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 25px;
}

.password-requirements h4 {
  margin: 0 0 15px 0;
  color: #333;
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
  color: #666;
  position: relative;
  padding-left: 25px;
}

.password-requirements li:before {
  content: '✗';
  position: absolute;
  left: 0;
  color: #dc3545;
  font-weight: bold;
}

.password-requirements li.valid {
  color: #28a745;
}

.password-requirements li.valid:before {
  content: '✓';
  color: #28a745;
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
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background: #545b62;
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
  background: #f8d7da;
  color: #721c24;
  padding: 12px;
  border-radius: 6px;
  margin-top: 15px;
  text-align: center;
}

.error-text {
  color: #dc3545;
  font-size: 14px;
  margin-top: 5px;
  display: block;
}

.error-actions,
.success-actions {
  margin-top: 30px;
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
