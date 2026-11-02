import { describe, it, expect, vi, beforeEach } from 'vitest';
import { apiFetch, initCsrf } from '../src/js/api.js';
import { createSpaApp } from '../src/js/app.js';

describe('loadPage', () => {
    beforeEach(() => {
        document.body.innerHTML = '<div id="view-container"></div>';
        window.Alpine = { initTree: vi.fn(), mutateDom: (cb) => cb() };
        localStorage.clear();
        fetch.mockReset();
        fetch.mockImplementation(async (input) => {
            const url = typeof input === 'string' ? input : input.url;
            if (url.endsWith('/api/auth/providers')) {
                return { ok: true, json: async () => [] };
            }
            if (url.endsWith('/api/auth/capabilities')) {
                return {
                    ok: true,
                    json: async () => ({
                        email_configured: false,
                        password_reset: false,
                        email_verification: false,
                    }),
                };
            }
            if (url.endsWith('/api/csrf')) {
                return { ok: true, json: async () => ({ csrf_token: 'csrf' }) };
            }
            throw new Error(`Unmocked fetch in tests: ${url}`);
        });
    });

    it('loads landingpage template and controller into currentPage', () => {
        const app = createSpaApp();
        app.loadPage('view-container', 'landingpage');

        const container = document.getElementById('view-container');
        expect(container.innerHTML.length).toBeGreaterThan(0);
        expect(typeof app.currentPage.fetchProtectedData).toBe('function');
        expect(window.Alpine.initTree).toHaveBeenCalledWith(
            container.firstElementChild,
        );
    });

    it('logs error for unknown page key without throwing', () => {
        const app = createSpaApp();
        const spy = vi.spyOn(console, 'error').mockImplementation(() => {});

        expect(() =>
            app.loadPage('view-container', 'nonexistent'),
        ).not.toThrow();
        expect(spy).toHaveBeenCalled();

        spy.mockRestore();
    });

    it('loads welcome template into public-container', () => {
        document.body.innerHTML = '<div id="public-container"></div>';
        const app = createSpaApp();
        app.loadPage('public-container', 'welcome');

        const container = document.getElementById('public-container');
        expect(container.innerHTML.length).toBeGreaterThan(0);
        expect(container.innerHTML).toContain("t('welcome.heroTitle')");
    });

    it('showLoginPage toggles showLogin and loads login template', () => {
        document.body.innerHTML =
            '<div id="login-register-container"></div><div id="public-container"></div>';
        const app = createSpaApp();

        expect(app.showLogin).toBe(false);

        app.showLoginPage();
        expect(app.showLogin).toBe(true);
        expect(
            document.getElementById('login-register-container').innerHTML
                .length,
        ).toBeGreaterThan(0);

        app.showWelcomePage();
        expect(app.showLogin).toBe(false);
        expect(
            document.getElementById('public-container').innerHTML.length,
        ).toBeGreaterThan(0);
    });

    it('enterAuthenticatedApp mounts app shell and routes to /app', async () => {
        document.body.innerHTML = `
            <div id="menu-container"></div>
            <div id="view-container"></div>
        `;
        window.Alpine.nextTick = (cb) => cb();

        const app = createSpaApp();
        window.history.replaceState(null, '', '/');

        app.enterAuthenticatedApp();

        expect(app.isLoggedIn).toBe(true);
        expect(app.showLogin).toBe(false);
        expect(app.activeViewPageKey).toBe('landingpage');
        expect(
            document.getElementById('view-container').innerHTML.length,
        ).toBeGreaterThan(0);
        expect(
            document.getElementById('menu-container').innerHTML.length,
        ).toBeGreaterThan(0);
        expect(window.location.pathname).toBe('/app');
    });

    it('logout posts to /api/auth/logout and leaves the welcome page', async () => {
        document.body.innerHTML = `
            <div id="public-container"></div>
            <div id="login-register-container"></div>
            <div id="menu-container"></div>
            <div id="view-container"></div>
        `;
        fetch.mockImplementation(async (input) => {
            const url = typeof input === 'string' ? input : input.url;
            if (url.endsWith('/api/csrf')) {
                return { ok: true, json: async () => ({ csrf_token: 'csrf' }) };
            }
            if (url.endsWith('/api/auth/logout')) {
                return {
                    ok: true,
                    json: async () => ({ authenticated: false }),
                };
            }
            if (url.endsWith('/api/auth/providers')) {
                return { ok: true, json: async () => [] };
            }
            if (url.endsWith('/api/auth/capabilities')) {
                return {
                    ok: true,
                    json: async () => ({
                        email_configured: false,
                        password_reset: false,
                        email_verification: false,
                    }),
                };
            }
            throw new Error(`Unmocked fetch in tests: ${url}`);
        });

        const app = createSpaApp();
        app.isLoggedIn = true;
        await app.logout();

        expect(app.isLoggedIn).toBe(false);
        expect(app.showLogin).toBe(false);
        const urls = fetch.mock.calls.map(([input]) =>
            typeof input === 'string' ? input : input.url,
        );
        expect(urls.some((url) => url.endsWith('/api/auth/logout'))).toBe(true);
    });

    it('auth:expired shows the login page', async () => {
        document.body.innerHTML = `
            <div id="public-container"></div>
            <div id="login-register-container"></div>
            <div id="menu-container"></div>
            <div id="view-container"></div>
        `;
        const app = createSpaApp();
        app.isLoggedIn = true;
        window.dispatchEvent(new Event('auth:expired'));
        await Promise.resolve();
        await Promise.resolve();

        expect(app.isLoggedIn).toBe(false);
        expect(app.showLogin).toBe(true);
    });

    it('destroy removes the auth:expired listener', async () => {
        const app = createSpaApp();
        app.destroy();
        app.isLoggedIn = true;
        app.showLogin = false;
        window.dispatchEvent(new Event('auth:expired'));
        await Promise.resolve();
        await Promise.resolve();
        expect(app.isLoggedIn).toBe(true);
        expect(app.showLogin).toBe(false);
    });

    it('destroy removes the pageshow listener', async () => {
        fetch.mockImplementation(async (input) => {
            const url = typeof input === 'string' ? input : input.url;
            if (url.endsWith('/api/csrf')) {
                return {
                    ok: true,
                    json: async () => ({ csrf_token: 'csrf-1' }),
                };
            }
            if (url.endsWith('/api/data')) {
                return { ok: true, json: async () => ({ message: 'ok' }) };
            }
            throw new Error(`Unmocked fetch in tests: ${url}`);
        });
        const app = createSpaApp();
        await initCsrf();
        app.destroy();
        const event = new Event('pageshow');
        Object.defineProperty(event, 'persisted', { value: true });
        window.dispatchEvent(event);
        fetch.mockClear();
        await apiFetch('/api/data', { method: 'POST' });
        const urls = fetch.mock.calls.map(([input]) =>
            typeof input === 'string' ? input : input.url,
        );
        expect(urls.filter((url) => url.endsWith('/api/csrf'))).toHaveLength(0);
        expect(fetch.mock.calls[0][1].headers['X-CSRF-Token']).toBe('csrf-1');
    });
});
