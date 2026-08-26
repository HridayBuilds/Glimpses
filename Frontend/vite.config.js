import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  // amazon-cognito-identity-js (via its crypto deps) references the Node
  // `global`, which doesn't exist in the browser.
  define: {
    global: 'globalThis',
  },
})
