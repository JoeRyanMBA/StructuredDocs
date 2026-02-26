<template>
  <div class="login-container">
    <div class="login-card">
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
        <h2>Author Login</h2>
        <p class="login-subtitle">Sign in to access documentation projects</p>

        <form @submit.prevent="handleLogin" class="login-form">
          <div class="form-group">
            <label for="email">Email Address</label>
            <input
              id="email"
              v-model="loginForm.email"
              type="email"
              required
              placeholder="your.email@example.com"
              autocomplete="username"
              autocapitalize="none"
              autocorrect="off"
              spellcheck="false"
              inputmode="email"
              :disabled="loading"
            />
          </div>

          <div class="form-group">
            <label for="password">Password</label>
            <div class="password-input-container">
              <input
                id="password"
                v-model="loginForm.password"
                :type="showPassword ? 'text' : 'password'"
                required
                placeholder="Enter your password"
                autocomplete="current-password"
                :disabled="loading"
                class="password-input"
              />
              <button
                type="button"
                class="password-toggle"
                @click="showPassword = !showPassword"
                :disabled="loading"
                :aria-label="showPassword ? 'Hide password' : 'Show password'"
                :aria-pressed="showPassword.toString()"
                tabindex="0"
              >
                <!-- Eye-off icon when showing password -->
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
                <!-- Eye icon when hiding password -->
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
          </div>

          <div class="form-options">
            <label class="checkbox-container">
              <input type="checkbox" v-model="loginForm.rememberMe" :disabled="loading">
              <span class="checkmark"></span>
              Remember me
            </label>
            <a href="#" @click.prevent="showForgotPassword = true" class="forgot-link">
              Forgot password?
            </a>
          </div>

          <button type="submit" class="login-btn" :disabled="loading">
            <span v-if="loading">Signing in...</span>
            <span v-else>Sign In</span>
          </button>

          <div v-if="error" class="error-message">
            {{ error }}
          </div>
        </form>

        <div class="login-footer">
          <p>Need access? <a href="#" @click.prevent="showRequestAccess = true">Request author account</a></p>
        </div>
      </div>
    </div>

    <!-- Request Access Modal -->
  <div v-if="showRequestAccess" class="login-modal-overlay" @click.self="showRequestAccess = false">
      <div class="modal" @click.stop>
        <div class="modal-header-row modal-header">
          <div class="modal-logo">
            <img class="modal-logo-image" :src="symbolLogoSrc" alt="StructuredDocs logo" decoding="async" @error="onSymbolError" />
            <h2>Request Author Access</h2>
          </div>
          <button @click="showRequestAccess = false" class="plain-close close-btn">×</button>
        </div>
        <form @submit.prevent="submitAccessRequest" class="modal-body">
          <div class="form-group">
            <label for="requestName">Full Name</label>
            <input
              id="requestName"
              v-model="accessRequest.name"
              type="text"
              required
              placeholder="Enter your full name"
            />
          </div>
          
          <div class="form-group">
            <label for="requestEmail">Email Address</label>
            <input
              id="requestEmail"
              v-model="accessRequest.email"
              type="email"
              required
              placeholder="your.email@census.gov"
            />
          </div>
          
          <div class="form-group">
            <label for="requestDepartment">Department</label>
            <select id="requestDepartment" v-model="accessRequest.department" required>
              <option value="">Select your department</option>
              <option value="Economic Indicators">Economic Indicators</option>
              <option value="Population Studies">Population Studies</option>
              <option value="Information Technology">Information Technology</option>
              <option value="Communications">Communications</option>
              <option value="Data Management">Data Management</option>
              <option value="Other">Other</option>
            </select>
          </div>
          
          <div class="form-group">
            <label for="requestReason">Reason for Access</label>
            <textarea
              id="requestReason"
              v-model="accessRequest.reason"
              rows="4"
              required
              placeholder="Please describe why you need author access and what projects you'll be working on"
            ></textarea>
          </div>
          
          <div class="modal-footer modal-actions">
            <button type="button" @click="showRequestAccess = false" class="btn btn-secondary cancel-btn">
              Cancel
            </button>
            <button type="submit" class="btn btn-primary submit-btn">Submit Request</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Forgot Password Modal -->
  <div v-if="showForgotPassword" class="login-modal-overlay" @click.self="showForgotPassword = false">
      <div class="modal" @click.stop>
        <div class="modal-header-row modal-header">
          <div class="modal-logo">
            <img class="modal-logo-image" :src="symbolLogoSrc" alt="StructuredDocs logo" decoding="async" @error="onSymbolError" />
            <h2>Reset Password</h2>
          </div>
          <button @click="showForgotPassword = false" class="plain-close close-btn">×</button>
        </div>
        <form @submit.prevent="submitPasswordReset" class="modal-body">
          <p class="modal-description">
            Enter your email address and we'll send you a link to reset your password.
          </p>
          
          <div class="form-group">
            <label for="resetEmail">Email Address</label>
            <input
              id="resetEmail"
              v-model="passwordReset.email"
              type="email"
              required
              placeholder="your.email@census.gov"
            />
          </div>
          
          <div class="modal-footer modal-actions">
            <button type="button" @click="showForgotPassword = false" class="btn btn-secondary cancel-btn">
              Cancel
            </button>
            <button type="submit" class="btn btn-primary submit-btn">Send Reset Link</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { store } from '../store';
import { toast } from '@/composables/useToast'

export default {
  name: 'LoginView',
  data() {
    return {
      loading: false,
      error: '',
      showRequestAccess: false,
      showForgotPassword: false,
      showPassword: false,
      loginForm: {
        email: '',
        password: '',
        rememberMe: false
      },
      accessRequest: {
        name: '',
        email: '',
        department: '',
        reason: ''
      },
      passwordReset: {
        email: ''
      },
      // Track when the top-of-card logo has loaded to hide shimmer
      symbolLogoLoaded: false,
      
    }
  },
  computed: {
    symbolLogoSrc() {
  return `${import.meta.env.BASE_URL}assets/StructuredDocsLogoSymbol.svg`
    }
  },
  methods: {
    onSymbolLoad() {
      this.symbolLogoLoaded = true
    },
    onSymbolError(e) {
  const fallback = `${import.meta.env.BASE_URL}assets/StructuredDocs_logo.svg`
      if (e && e.target && e.target.src !== fallback) {
        e.target.src = fallback
      }
    },
    async handleLogin() {
      this.loading = true;
      this.error = '';
      try {
        const normalizedEmail = (this.loginForm.email || '').trim().toLowerCase();
        const password = this.loginForm.password;
        const response = await axios.post('/api/users/login', {
          email: normalizedEmail,
          password: password,
        });

        const { access_token, user } = response.data;

        // Store token and user data
        localStorage.setItem('access_token', access_token);
        store.setUser(user);
        localStorage.setItem('isAuthenticated', 'true');

        // Set axios default header
        axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;

        // Emit custom event to notify components of user update
        window.dispatchEvent(new CustomEvent('userUpdated'));

        // Redirect to dashboard
        this.$router.push('/');
      } catch (error) {
        this.error = error.response?.data?.error || 'Invalid email or password';
        // Clear stored data on login failure
        localStorage.removeItem('access_token');
        store.setUser(null);
        localStorage.removeItem('isAuthenticated');
        delete axios.defaults.headers.common['Authorization'];
      } finally {
        this.loading = false;
      }
    },
    
    async mockAuthentication() {
      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      // Mock valid credentials
      const validCredentials = [
        { email: 'admin@example.com', password: 'admin123', role: 'admin', name: 'Admin User' },
        { email: 'john.smith@census.gov', password: 'demo123' },
        { email: 'sarah.johnson@census.gov', password: 'demo123' },
        { email: 'mike.chen@census.gov', password: 'demo123' },
        { email: 'lisa.park@census.gov', password: 'demo123' },
        { email: 'alex.rodriguez@census.gov', password: 'demo123' }
      ]
      
      const matchedUser = validCredentials.find(cred => 
        cred.email === this.loginForm.email && cred.password === this.loginForm.password
      )
      
      if (!matchedUser) {
        throw new Error('Invalid email or password')
      }
      
      return matchedUser
    },
    
    async submitAccessRequest() {
      try {
        // Mock API call - in real implementation, this would send to backend
        await new Promise(resolve => setTimeout(resolve, 500))
        
        toast.success(`Access request submitted for ${this.accessRequest.name}. You will receive an email notification once your request is reviewed.`)
        
        // Reset form
        this.accessRequest = {
          name: '',
          email: '',
          department: '',
          reason: ''
        }
        
        this.showRequestAccess = false
        
      } catch (error) {
        console.error('Failed to submit access request:', error)
      }
    },
    
    async submitPasswordReset() {
      try {
        await axios.post('/api/users/reset-password', { email: this.passwordReset.email });
        toast.success(`Password reset link sent to ${this.passwordReset.email}`);
        this.passwordReset.email = '';
        this.showForgotPassword = false;
      } catch (error) {
        console.error('Failed to send password reset:', error);
        toast.error(error.response?.data?.error || 'Failed to send password reset link.');
      }
    }
  },
  
  mounted() {
    // Check if user is already logged in
    const token = localStorage.getItem('access_token');
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      this.$router.push('/');
    }
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
/*  background:radial-gradient( var(--bg-light-mist-gray) 0%, #ffffff 100%); */
  display: flex;
  align-items: center;
  justify-content: center; /* horizontal centering */
  margin: 0 auto;          /* ensure block is centered if it ever gets intrinsic width */
  width: 100%;             /* allow taking full width for proper centering */
  padding: 2rem;
}

.login-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  max-width: 400px;
  width: 100%;
}

.login-header {
  background: var(--primary-deep-teal);
  color: white;
  padding: 2rem;
  text-align: center;
}

/* Center the logo and force 160x160 */
.census-logo {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.census-logo .logo-image {
  display: block;
  width: 160px;
  height: 160px;
  object-fit: contain;
  margin-bottom: 0.5rem;
}

/* Shimmer wrapper for login logo */
.census-logo .logo-wrapper {
  position: relative;
  display: block;
  width: 160px;
  height: 160px;
  margin-bottom: 0.5rem;
}

.census-logo .logo-skeleton {
  position: absolute;
  inset: 0;
  border-radius: 4px;
  background: linear-gradient(90deg, #f2f4f7 25%, #e9eef3 37%, #f2f4f7 63%);
  background-size: 400% 100%;
  animation: logo-shimmer 1.2s ease-in-out infinite;
}

@keyframes logo-shimmer {
  0% { background-position: 100% 0; }
  100% { background-position: 0 0; }
}

/* Ensure image doesn't add extra internal gap; spacing handled by wrapper */
.census-logo .logo-image {
  margin-bottom: 0;
  display: block;
}

.census-logo h1 {
  margin: 0 0 0.5rem 0;
  font-size: 1.5rem;
  font-weight: 600;
  /* Ensure contrast on deep teal header */
  color: #fff;
  text-shadow: 0 1px 8px rgba(0,0,0,0.18);
}

.system-title {
  margin: 0;
  font-size: 0.9rem;
  opacity: 0.9;
}

.login-form-container {
  padding: 2rem;
}

.login-form-container h2 {
  margin: 0 0 0.5rem 0;
  color: var(--primary-deep-teal);
  font-size: 1.5rem;
  font-weight: 600;
}

.login-subtitle {
  color: var(--text-secondary-cool-gray);
  margin: 0 0 2rem 0;
  font-size: 0.9rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: var(--primary-deep-teal);
  font-size: 0.9rem;
}

.form-group input, .form-group select, .form-group textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid var(--extended-lavender-gray);
  border-radius: 6px;
  font-size: 0.9rem;
  box-sizing: border-box;
  transition: border-color 0.2s ease;
}

.form-group input:focus, .form-group select:focus, .form-group textarea:focus {
  outline: none;
  border-color: var(--primary-deep-teal);
  box-shadow: 0 0 0 3px rgba(0, 90, 156, 0.1);
}

.form-group input:disabled {
  background: var(--bg-light-mist-gray);
  opacity: 0.7;
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.checkbox-container {
  display: flex;
  align-items: center;
  font-size: 0.9rem;
  color: var(--text-primary-charcoal);
  cursor: pointer;
  white-space: nowrap; /* keep label text on one line */
}

.checkbox-container input {
  margin-right: 0.5rem;
}

.forgot-link {
  color: var(--primary-deep-teal);
  text-decoration: none;
  font-size: 0.9rem;
}

.forgot-link:hover {
  text-decoration: underline;
}

.error-message {
  background: var(--extended-dusty-rose);
  color: var(--error-coral-red);
  padding: 0.75rem;
  border-radius: 6px;
  font-size: 0.9rem;
  margin-top: 1rem;
}

.login-footer {
  text-align: center;
  color: var(--text-secondary-cool-gray);
  font-size: 0.9rem;
}

.login-footer a {
  color: var(--primary-deep-teal);
  text-decoration: none;
}

.login-footer a:hover {
  text-decoration: underline;
}

/* Modal Styles - using global .modal-overlay and .modal utilities; keep header/body below */

.login-modal-overlay {
  position: fixed !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  width: 100vw !important;
  height: 100vh !important;
  background: rgba(0, 0, 0, 0.7) !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  z-index: 9999 !important;
  backdrop-filter: blur(2px);
}

.modal {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
  margin: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid var(--extended-lavender-gray);
}

.modal-logo {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.modal-logo-image {
  width: auto;
  height: 40px;
  max-width: 120px;
}

.modal-header h2 {
  margin: 0;
  color: var(--primary-deep-teal);
  font-size: 1.5rem;
  font-weight: 600;
}

.modal-body {
  padding: 1.5rem;
}

.modal-description {
  color: var(--text-secondary-cool-gray);
  margin-bottom: 1.5rem;
  line-height: 1.5;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid var(--extended-lavender-gray);
}

/* Responsive Design */
@media (max-width: 768px) {
  .login-container {
    padding: 1rem;
  }
  
  .modal {
    min-width: auto;
    margin: 1rem;
  }
  
  .form-options {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }
}

/* Password input with toggle */
.password-input-container {
  position: relative;
  display: flex;
  align-items: center;
}

.password-input-container .password-input {
  flex: 1;
  padding-right: 50px; /* Make room for the toggle button */
  /* Disable browser-native password reveal to avoid conflicts */
  -webkit-appearance: none;
  -moz-appearance: none;
  appearance: none;
}

/* Hide Edge/IE native reveal (prevents double toggles) */
.password-input::-ms-reveal {
  display: none;
}
.password-input::-ms-clear {
  display: none;
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
</style>

