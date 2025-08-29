import { createApp, reactive } from 'vue'
import App from './App.vue'
import router from './router'
import '@fortawesome/fontawesome-free/css/all.css'
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap-icons/font/bootstrap-icons.css'
// Import global styles last so they override Bootstrap defaults
import './assets/style.css'
import * as bootstrap from 'bootstrap/dist/js/bootstrap.bundle.min.js'
import { store } from './store';

// Make Bootstrap available globally
window.bootstrap = bootstrap

const app = createApp(App);

app.config.globalProperties.$store = store;

app.use(router)
  .mount('#app');
