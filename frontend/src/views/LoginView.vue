<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <div class="census-logo">
          <img class="logo-image" src="/StructuredDocsLogoSymbol.svg" alt="Structured Docs logo" />
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
              :disabled="loading"
            />
          </div>

          <div class="form-group">
            <label for="password">Password</label>
            <input
              id="password"
              v-model="loginForm.password"
              type="password"
              required
              placeholder="Enter your password"
              autocomplete="current-password"
              :disabled="loading"
            />
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
    <div v-if="showRequestAccess" class="login-modal-overlay" @click="showRequestAccess = false">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <div class="modal-logo">
            <img class="modal-logo-image" src="/StructuredDocsLogoSymbol.svg" alt="Structured Docs logo" />
            <h2>Request Author Access</h2>
          </div>
          <button @click="showRequestAccess = false" class="close-btn">×</button>
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
          
          <div class="modal-actions">
            <button type="button" @click="showRequestAccess = false" class="cancel-btn">
              Cancel
            </button>
            <button type="submit" class="submit-btn">Submit Request</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Forgot Password Modal -->
    <div v-if="showForgotPassword" class="login-modal-overlay" @click="showForgotPassword = false">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <div class="modal-logo">
            <img class="modal-logo-image" src="/StructuredDocsLogoSymbol.svg" alt="Structured Docs logo" />
            <h2>Reset Password</h2>
          </div>
          <button @click="showForgotPassword = false" class="close-btn">×</button>
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
          
          <div class="modal-actions">
            <button type="button" @click="showForgotPassword = false" class="cancel-btn">
              Cancel
            </button>
            <button type="submit" class="submit-btn">Send Reset Link</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { store } from '../store';

export default {
  name: 'LoginView',
  data() {
    return {
      loading: false,
      error: '',
      showRequestAccess: false,
      showForgotPassword: false,
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
      }
    }
  },
  methods: {
    async handleLogin() {
      this.loading = true;
      this.error = '';
      try {
        const response = await axios.post('/api/users/login', {
          email: this.loginForm.email,
          password: this.loginForm.password,
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
        
        alert(`Access request submitted for ${this.accessRequest.name}. You will receive an email notification once your request is reviewed.`)
        
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
        alert(`Password reset link sent to ${this.passwordReset.email}`);
        this.passwordReset.email = '';
        this.showForgotPassword = false;
      } catch (error) {
        console.error('Failed to send password reset:', error);
        alert(error.response?.data?.error || 'Failed to send password reset link.');
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
  justify-content: center;
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

.census-logo .logo-image {
  display: inline-block;
  width: auto;
  height: auto;
  max-width: 160px; /* keep within modal/card width */
  max-height: 80px; /* visually balanced with header padding */
  margin-bottom: 0.5rem;
}

.census-logo h1 {
  margin: 0 0 0.5rem 0;
  font-size: 1.5rem;
  font-weight: 600;
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
</style>
