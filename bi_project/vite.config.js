import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  base: '/powerbi/',
  server: {
    proxy: {
      '/api': {
        target: 'https://order.xxwyc.cn',
        changeOrigin: true,
        rewrite: (path) => path
        },
    },
  },
  build: {
    outDir: 'powerbi' // 将输出目录更改为powerbi
  }
})
