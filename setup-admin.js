// Quick setup script to simulate admin login
// Run this in browser console to test admin functionality

// Set admin user in localStorage
const adminUser = {
  id: 1,
  name: "Admin User",
  email: "admin@example.com",
  role: "admin",
  active: true
};

localStorage.setItem('user', JSON.stringify(adminUser));
console.log('✅ Admin user set in localStorage');
console.log('🔄 Reloading page...');
window.location.reload();
