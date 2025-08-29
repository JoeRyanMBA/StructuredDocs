import { reactive } from 'vue';

export const store = reactive({
  user: null,
  
  setUser(userData) {
    this.user = userData;
    if (userData) {
      localStorage.setItem('user', JSON.stringify(userData));
    } else {
      localStorage.removeItem('user');
    }
  },
  
  loadUser() {
    try {
      const userStr = localStorage.getItem('user');
      if (userStr) {
        this.user = JSON.parse(userStr);
      }
    } catch (e) {
      console.error('Error loading user from localStorage', e);
      this.user = null;
    }
  }
});

// Initial load
store.loadUser();
