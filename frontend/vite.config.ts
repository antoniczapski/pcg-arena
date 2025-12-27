import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  // For development, use empty string so requests go through the proxy
  define: {
    'import.meta.env.VITE_API_BASE_URL': JSON.stringify(''),
  },
  server: {
    port: 3000,
    proxy: {
      '/health': {
        target: 'http://localhost:8080',
        changeOrigin: true,
      },
      '/v1': {
        target: 'http://localhost:8080',
        changeOrigin: true,
        // Ensure cookies are properly forwarded
        cookieDomainRewrite: 'localhost',
      },
      '/admin': {
        target: 'http://localhost:8080',
        changeOrigin: true,
      },
      '/debug': {
        target: 'http://localhost:8080',
        changeOrigin: true,
      },
    }
  }
})

