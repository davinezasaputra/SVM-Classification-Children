import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { VitePWA } from 'vite-plugin-pwa';

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,png,svg}'],
        navigateFallback: '/index.html' 
      },
      manifest: {
        name: 'Sistem Klasifikasi Gizi Balita',
        short_name: 'Gizi SVM',
        description: 'Sistem pakar klasifikasi stunting menggunakan SVM',
        theme_color: '#0d9488',
        background_color: '#ffffff',
        display: 'standalone',
        icons: [
          {
            src: '/favicon.svg',
            sizes: '192x192',
            type: 'image/svg+xml'
          },
          {
            src: '/Kabupaten-Bangka-Barat.png',
            sizes: '512x512',
            type: 'image/png'
          }
        ]
      }
    })
  ]
});