import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  // For development, configure environment variables
  define: {
    'import.meta.env.VITE_API_BASE_URL': JSON.stringify(''),
    // Google OAuth Client ID
    'import.meta.env.VITE_GOOGLE_CLIENT_ID': JSON.stringify('918431758586-bpmp3he6jum82j38ja46jal7aa2636c3.apps.googleusercontent.com'),
    // Dev auth disabled - use real authentication only
    'import.meta.env.VITE_DEV_AUTH': JSON.stringify('false'),
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
      '/debug': {
        target: 'http://localhost:8080',
        changeOrigin: true,
      },
    }
  }
})

