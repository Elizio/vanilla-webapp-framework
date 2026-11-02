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
                // Measured 2026-11-02 over src/js after refresh tokens + #68:
                // 71.16 / 82.18 / 62.19 / 71.16. Floors are floor(measured) minus ~1.
                lines: 70,
                statements: 70,
                functions: 61,
                branches: 81,
            },
        },
    },
    resolve: {
        alias: {
            '@': resolve(__dirname, 'src'),
        },
    },
});
