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
                // Re-measured after rebase onto master (#67/#68) + refresh tokens.
                // Floors are floor(measured) minus ~1; tests re-measure before ship.
                lines: 68,
                statements: 68,
                functions: 54,
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
