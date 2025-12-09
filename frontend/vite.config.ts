import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    host: '0.0.0.0', // Permite acesso externo
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://192.168.31.175:8000', // IP da sua máquina
        changeOrigin: true,
      },
      '/ws': {
        target: 'ws://192.168.31.175:8000', // IP da sua máquina
        ws: true,
      },
    },
  },
})
