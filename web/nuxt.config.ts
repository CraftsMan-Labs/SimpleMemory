import tailwindcss from '@tailwindcss/vite'

export default defineNuxtConfig({
  compatibilityDate: '2025-11-01',
  future: { compatibilityVersion: 4 },
  devtools: { enabled: true },
  modules: [
    '@vueuse/nuxt',
    '@pinia/nuxt',
  ],
  css: [
    '~/assets/css/main.css',
  ],
  vite: {
    plugins: [tailwindcss()],
  },
  runtimeConfig: {
    apiBaseUrl: process.env.KMG_API_BASE_URL || 'http://localhost:8000',
    apiKey: process.env.KMG_API_KEY || '',
    public: {
      appName: 'Knowledge Memory Graph',
    },
  },
  typescript: {
    strict: true,
    typeCheck: false,
  },
  app: {
    head: {
      title: 'KMG — Knowledge Memory Graph',
      meta: [
        { name: 'description', content: 'Your AI-generated Obsidian-style vault.' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
      ],
    },
  },
})
