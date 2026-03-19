import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import path from 'path';

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src')
    }
  },
  server: {
    port: 5173,
    host: '0.0.0.0',
    logLevel: 'info',
    // Disable HMR in CI to prevent WebSocket connections from interfering with Cypress
    hmr: process.env.CI ? false : { port: 5173 },
    proxy: {
      '/api': {
        // Proxy API calls to local Flask backend
        target: 'http://localhost:8080',
        changeOrigin: true,
        secure: false,
        configure: (proxy, options) => {
          proxy.on('error', (err, req, res) => {
            console.log('Proxy error:', err);
          });
          proxy.on('proxyReq', (proxyReq, req, res) => {
            console.log('Sending Request to the Target:', req.method, req.url);
          });
          proxy.on('proxyRes', (proxyRes, req, res) => {
            console.log('Received Response from the Target:', proxyRes.statusCode, req.url);
          });
        }
      },
      '/static': {
        // Proxy static asset requests to local Flask backend if needed
        target: 'http://localhost:8080',
        changeOrigin: true,
        secure: false
      }
    }
  }
  ,
  build: {
    sourcemap: true
  }
});