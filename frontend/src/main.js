import { createApp, reactive } from 'vue'
import App from './App.vue'
import router from './router'
// Font Awesome removed to reduce bundle size; using Bootstrap Icons / inline SVG instead.
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap-icons/font/bootstrap-icons.css'
// Import global styles last so they override Bootstrap defaults
import './assets/style.css'
// Import additional global layout overrides
import './style.css'
import * as bootstrap from 'bootstrap/dist/js/bootstrap.bundle.min.js'
import { store } from './store';
import { toast } from './composables/useToast'

// Make Bootstrap available globally
window.bootstrap = bootstrap

const app = createApp(App);

app.config.globalProperties.$store = store;
app.config.globalProperties.$toast = toast;

app.use(router)
  .mount('#app');
