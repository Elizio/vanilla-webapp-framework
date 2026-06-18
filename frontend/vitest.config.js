import { defineConfig } from 'vitest/config';
import { resolve } from 'path';

export default defineConfig({
  root: __dirname,
  test: {
    environment: 'jsdom',
    include: ['tests/**/*.test.js'],
    setupFiles: ['tests/setup.js'],
  },
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
});
