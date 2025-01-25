import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
// import vueDevTools from 'vite-plugin-vue-devtools'
import dotenv from 'dotenv';
import dotenvExpand from 'dotenv-expand';

const dotenvEnv = dotenv.config({ path: "../.env", override: true });
dotenvExpand.expand(dotenvEnv);

const subPath = process.env.JWDJ_SUBPATH || "/";

// https://vite.dev/config/
export default defineConfig({
  base: subPath,
  envDir: '..',
  envPrefix: 'JWDJ',
  plugins: [
    vue(),
    // vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  css: {
    preprocessorOptions: {
      scss: {
        api: "modern",
        silenceDeprecations: ['mixed-decls', 'color-functions', 'global-builtin', 'import'],
      },
    },
  },
  server: {
    port: 8080,
    host: '127.0.0.1',
    proxy: {
      [`${subPath}api/`]: {
        target: "http://127.0.0.1:8000/",
        changeOrigin: false,
        ws: true,
      },
    },
  },
})
