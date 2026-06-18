import { describe, it, expect, vi, beforeEach } from 'vitest';
import { createSpaApp } from '../src/js/app.js';

describe('loadPage', () => {
    beforeEach(() => {
        document.body.innerHTML = '<div id="view-container"></div>';
        window.Alpine = { initTree: vi.fn() };
        localStorage.clear();
    });

    it('loads landingpage template and controller into currentPage', () => {
        const app = createSpaApp();
        app.loadPage('view-container', 'landingpage');

        const container = document.getElementById('view-container');
        expect(container.innerHTML.length).toBeGreaterThan(0);
        expect(typeof app.currentPage.fetchProtectedData).toBe('function');
        expect(window.Alpine.initTree).toHaveBeenCalledWith(container);
    });

    it('logs error for unknown page key without throwing', () => {
        const app = createSpaApp();
        const spy = vi.spyOn(console, 'error').mockImplementation(() => {});

        expect(() => app.loadPage('view-container', 'nonexistent')).not.toThrow();
        expect(spy).toHaveBeenCalled();

        spy.mockRestore();
    });
});
