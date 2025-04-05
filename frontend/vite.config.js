import { defineConfig } from 'vite';
import { resolve } from 'path';
import handlebars from 'vite-plugin-handlebars';

export default defineConfig({
  root: 'src',
  css: {
    postcss: './postcss.config.js',
  },
  build: {
    outDir: '../backend/templates',
    emptyOutDir: true,
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'src/index.html'),
      },
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        secure: false,
      },
    },
  },
  plugins: [
    handlebars({
      partialDirectory: resolve(__dirname, 'src/templates/partials'),
      helpers: {
        json: (context) => JSON.stringify(context, null, 2),
        eq: (v1, v2) => v1 === v2
      }
    }),
  ],
}); 