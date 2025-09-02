<template>
  <div class="admin-user-management">
    <HeaderBar />
    <div class="page-content">
      <div class="page-header">
        <h2>User Management</h2>
        <p class="page-description">Manage user accounts, roles, and permissions</p>
      </div>
      
      <UserManagement />
    </div>
  </div>
</template>

<script>
import HeaderBar from '../components/HeaderBar.vue'
import UserManagement from '../components/UserManagement.vue'

export default {
  name: 'AdminUserManagement',
  components: {
    HeaderBar,
    UserManagement
  },
  mounted() {
    this.checkAdminAccess()
  },
  methods: {
    checkAdminAccess() {
      const user = JSON.parse(localStorage.getItem('user') || '{}')
      if (!user.role || user.role !== 'admin') {
        this.$router.push('/dashboard')
        return
      }
    }
  }
}
</script>

<style scoped>
.admin-user-management {
  min-height: 100vh;
  background: #f8f9fa;
}

.page-content {
  padding: 30px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 30px;
}

.breadcrumb {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
  font-size: 14px;
}

.breadcrumb-link {
  color: var(--primary-deep-teal);
  text-decoration: none;
}

.breadcrumb-link:hover {
  text-decoration: underline;
}

.breadcrumb-separator {
  margin: 0 10px;
  color: #6c757d;
}

.breadcrumb-current {
  color: #6c757d;
}

h1 {
  color: #333;
  margin: 0 0 10px 0;
  font-size: 32px;
  font-weight: 700;
}

.page-description {
  color: #666;
  margin: 0;
  font-size: 16px;
}

.tabs button.active {
  color: var(--primary-deep-teal);
  border-bottom: 2px solid var(--primary-deep-teal);
}

@media (max-width: 768px) {
  .page-content {
    padding: 20px 15px;
  }
  
  h1 {
    font-size: 24px;
  }
  
  .breadcrumb {
    font-size: 12px;
  }
}
</style>
