// Test script to simulate different user roles
// Run these in browser console to test role-based visibility

// Test 1: Author User (should NOT see Admin tab)
console.log('🧪 Testing Author User - Admin tab should be HIDDEN');
const authorUser = {
  id: 2,
  name: "John Author",
  email: "john@example.com", 
  role: "author",
  active: true
};
localStorage.setItem('user', JSON.stringify(authorUser));
console.log('✅ Author user set in localStorage');
window.location.reload();

// Test 2: Admin User (should see Admin tab)
/*
console.log('🧪 Testing Admin User - Admin tab should be VISIBLE');
const adminUser = {
  id: 1,
  name: "Admin User",
  email: "admin@example.com",
  role: "admin", 
  active: true
};
localStorage.setItem('user', JSON.stringify(adminUser));
console.log('✅ Admin user set in localStorage');
window.location.reload();
*/

// Test 3: Reviewer User (should NOT see Admin tab)
/*
console.log('🧪 Testing Reviewer User - Admin tab should be HIDDEN');
const reviewerUser = {
  id: 3,
  name: "Jane Reviewer", 
  email: "jane@example.com",
  role: "reviewer",
  active: true
};
localStorage.setItem('user', JSON.stringify(reviewerUser));
console.log('✅ Reviewer user set in localStorage');
window.location.reload();
*/
