/**
 * Vitest config: jsdom tests plus the src/js coverage ratchet.
 * Thresholds are floor(measured) minus ~1 point. Raise them when a PR
 * adds at least 1 point of coverage; do not lower them without a PR note.
 */
import { defineConfig } from 'vitest/config';
import { resolve } from 'path';

export default defineConfig({
    root: __dirname,
    test: {
        environment: 'jsdom',
        include: ['tests/**/*.test.js'],
        setupFiles: ['tests/setup.js'],
        coverage: {
            provider: 'v8',
            include: ['src/js/**/*.js'],
            reporter: ['text', 'text-summary'],
            thresholds: {
                // Measured 2026-11-01 over src/js: 64.60 / 79.69 / 45.95 / 64.60.
                lines: 63,
                statements: 63,
                functions: 44,
                branches: 78,
            },
        },
    },
    resolve: {
        alias: {
            '@': resolve(__dirname, 'src'),
        },
    },
});
