import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    // forwards /api/* to the local Flask server during `npm run dev`,
    // so the frontend can always call a relative '/api/...' URL
    proxy: {
      '/api': 'http://localhost:5000',
    },
  },
})
