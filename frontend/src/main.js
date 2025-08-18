import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './style.css'
import '@fortawesome/fontawesome-free/css/all.css'
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap-icons/font/bootstrap-icons.css'
import * as bootstrap from 'bootstrap/dist/js/bootstrap.bundle.min.js'

// Make Bootstrap available globally
window.bootstrap = bootstrap

createApp(App)
  .use(router)
  .mount('#app')