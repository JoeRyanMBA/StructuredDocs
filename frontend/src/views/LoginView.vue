<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <div class="census-logo">
          <div class="logo-icon">🏛️</div>
          <h1>Structured Docs</h1>
          <p class="system-title">Structured Documentation System</p>
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
              placeholder="your.email@census.gov"
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
    <div v-if="showRequestAccess" class="modal-overlay" @click="showRequestAccess = false">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h2>Request Author Access</h2>
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
    <div v-if="showForgotPassword" class="modal-overlay" @click="showForgotPassword = false">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h2>Reset Password</h2>
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
      this.loading = true
      this.error = ''
      
      try {
        // Mock authentication - replace with real API call
        const authenticatedUser = await this.mockAuthentication()
        
        // Store user session
        const userData = {
          id: authenticatedUser.role === 'admin' ? 1 : 2,
          name: authenticatedUser.name || 'John Smith',
          email: this.loginForm.email,
          department: 'Economic Indicators',
          role: authenticatedUser.role || 'author',
          loginTime: new Date().toISOString()
        }
        
        console.log('🔍 Login - Storing user data:', userData)
        console.log('🔍 Login - User role:', userData.role)
        
        localStorage.setItem('isAuthenticated', 'true')
        localStorage.setItem('user', JSON.stringify(userData))
        
        console.log('🔍 Login - Stored in localStorage:', JSON.parse(localStorage.getItem('user')))
        
        // Emit custom event to notify components of user update
        window.dispatchEvent(new CustomEvent('userUpdated'))
        console.log('🔍 Login - Dispatched userUpdated event')
        
        // Redirect to dashboard
        this.$router.push('/')
        
      } catch (error) {
        this.error = error.message
      } finally {
        this.loading = false
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
        // Mock API call
        await new Promise(resolve => setTimeout(resolve, 500))
        
        alert(`Password reset link sent to ${this.passwordReset.email}`)
        
        // Reset form
        this.passwordReset.email = ''
        this.showForgotPassword = false
        
      } catch (error) {
        console.error('Failed to send password reset:', error)
      }
    }
  },
  
  mounted() {
    // Check if user is already logged in
    const isAuthenticated = localStorage.getItem('isAuthenticated')
    if (isAuthenticated) {
      this.$router.push('/')
    }
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  background:radial-gradient( #e6e2e2ff 0%, #ffffff 100%);
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
  background: #205493;
  color: white;
  padding: 2rem;
  text-align: center;
}

.census-logo .logo-icon {
  font-size: 3rem;
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
  color: #205493;
  font-size: 1.5rem;
  font-weight: 600;
}

.login-subtitle {
  color: #6c757d;
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
  color: #205493;
  font-size: 0.9rem;
}

.form-group input, .form-group select, .form-group textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.9rem;
  box-sizing: border-box;
  transition: border-color 0.2s ease;
}

.form-group input:focus, .form-group select:focus, .form-group textarea:focus {
  outline: none;
  border-color: #205493;
  box-shadow: 0 0 0 3px rgba(0, 90, 156, 0.1);
}

.form-group input:disabled {
  background: #f3f4f6;
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
  color: #374151;
  cursor: pointer;
}

.checkbox-container input {
  margin-right: 0.5rem;
}

.forgot-link {
  color: #205493;
  text-decoration: none;
  font-size: 0.9rem;
}

.forgot-link:hover {
  text-decoration: underline;
}

.login-btn {
  width: 100%;
  background: #205493;
  color: white;
  border: none;
  padding: 0.75rem;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s ease;
  margin-bottom: 1rem;
}

.login-btn:hover:not(:disabled) {
  background: #005E7B;
}

.login-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.error-message {
  background: #fee2e2;
  color: #dc2626;
  padding: 0.75rem;
  border-radius: 6px;
  font-size: 0.9rem;
  margin-top: 1rem;
}

.login-footer {
  text-align: center;
  color: #6c757d;
  font-size: 0.9rem;
}

.login-footer a {
  color: #205493;
  text-decoration: none;
}

.login-footer a:hover {
  text-decoration: underline;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: white;
  border-radius: 12px;
  min-width: 500px;
  max-width: 90vw;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h2 {
  margin: 0;
  color: #205493;
  font-size: 1.5rem;
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #9ca3af;
  padding: 0.25rem;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.close-btn:hover {
  color: #205493;
  background: #f3f4f6;
}

.modal-body {
  padding: 1.5rem;
}

.modal-description {
  color: #6c757d;
  margin-bottom: 1.5rem;
  line-height: 1.5;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid #e5e7eb;
}

.cancel-btn, .submit-btn {
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  border: none;
  transition: all 0.2s ease;
}

.cancel-btn {
  background: #f3f4f6;
  color: #374151;
}

.cancel-btn:hover {
  background: #e5e7eb;
}

.submit-btn {
  background: #205493;
  color: white;
}

.submit-btn:hover {
  background: #005E7B;
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
