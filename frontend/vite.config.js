import { defineConfig, loadEnv } from 'vite';
import { resolve } from 'path';
import tailwindcss from 'tailwindcss';
import autoprefixer from 'autoprefixer';

export default defineConfig(({ mode }) => {
  const projectRoot = resolve(__dirname, '..');
  const env = loadEnv(mode, projectRoot, '');
  const seoMode = env.SEO_MODE || env.VITE_SEO_MODE || 'auth-first';

  return {
    root: 'src',
    envDir: projectRoot,
    define: {
      'import.meta.env.VITE_SEO_MODE': JSON.stringify(seoMode),
    },
    css: {
      postcss: {
        plugins: [
          tailwindcss(),
          autoprefixer(),
        ],
      },
    },
    build: {
      outDir: '../backend/static',
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
  };
});
