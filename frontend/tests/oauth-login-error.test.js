/**
 * OAuth login errors must render in the login error box (Alpine reactive state).
 */
import {
    afterEach,
    beforeAll,
    beforeEach,
    describe,
    expect,
    it,
    vi,
} from 'vitest';
import Alpine from 'alpinejs';
import { createSpaApp, handleOAuthQuery } from '../src/js/app.js';
import { loginController } from '../src/js/controllers/login.js';
import { setLocale } from '../src/js/i18n.js';
import loginTpl from '../src/templates/partials/login.hbs?raw';

/**
 * Flush Alpine effects and x-show's setTimeout reveal.
 * @returns {Promise<void>}
 */
async function flushShow() {
    await new Promise((resolve) => Alpine.nextTick(resolve));
    await new Promise((resolve) => setTimeout(resolve, 20));
}

/**
 * @returns {HTMLElement|null}
 */
function errorBox() {
    return document.querySelector('[x-show="loginController.error"]');
}

/**
 * @param {HTMLElement|null} el
 * @returns {boolean}
 */
function isShown(el) {
    return Boolean(el) && el.style.display !== 'none';
}

/**
 * Mount the login form under a real Alpine spaApp root.
 * @returns {Promise<object>} Reactive Alpine app instance.
 */
async function mountLoginApp() {
    document.body.innerHTML = `
        <div x-data="spaApp">
            <div id="login-register-container">${loginTpl}</div>
            <div id="public-container"></div>
        </div>
    `;
    const root = document.querySelector('[x-data]');
    Alpine.initTree(root);
    const app = root._x_dataStack[0];
    window.spaApp = app;
    await flushShow();
    return app;
}

/**
 * @param {string} provider
 * @returns {HTMLButtonElement|undefined}
 */
function providerButton(provider) {
    const label = provider.charAt(0).toUpperCase() + provider.slice(1);
    return [...document.querySelectorAll('button')].find((el) =>
        el.textContent.includes(label),
    );
}

describe('unconfigured OAuth login errors', () => {
    beforeAll(() => {
        window.Alpine = Alpine;
        Alpine.data('spaApp', () => createSpaApp());
    });

    beforeEach(() => {
        setLocale('en');
        loginController.error = null;
        loginController.response = null;
        vi.spyOn(console, 'warn').mockImplementation(() => {});
        fetch.mockImplementation(async (input) => {
            const url = typeof input === 'string' ? input : input.url;
            if (url.includes('/api/auth/providers')) {
                return { ok: true, json: async () => [] };
            }
            if (url.includes('/api/csrf')) {
                return {
                    ok: true,
                    json: async () => ({ csrf_token: 'test-csrf' }),
                };
            }
            if (url.includes('/api/auth/session')) {
                return {
                    ok: true,
                    json: async () => ({ authenticated: false }),
                };
            }
            if (url.includes('/api/auth/capabilities')) {
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
    });

    afterEach(() => {
        const root = document.querySelector('[x-data]');
        if (root) {
            Alpine.destroyTree(root);
        }
        loginController.error = null;
        document.body.innerHTML = '';
        window.history.replaceState(null, '', '/');
        console.warn.mockRestore?.();
    });

    it.each(['google', 'facebook'])(
        'shows a generic error when clicking an unconfigured %s button',
        async (provider) => {
            await mountLoginApp();

            const box = errorBox();
            expect(box).toBeTruthy();
            expect(isShown(box)).toBe(false);

            const button = providerButton(provider);
            expect(button).toBeTruthy();
            expect(button.className).toContain('opacity-60');
            expect(button.className).toContain('cursor-not-allowed');

            button.click();
            await flushShow();

            expect(isShown(box)).toBe(true);
            const label = provider.charAt(0).toUpperCase() + provider.slice(1);
            expect(box.textContent).toContain(label);
            expect(box.textContent).not.toMatch(
                /\.env|CLIENT_ID|CLIENT_SECRET|Flask/i,
            );
        },
    );

    it('shows the auth_error query on the login error box', async () => {
        const app = await mountLoginApp();

        const box = errorBox();
        expect(isShown(box)).toBe(false);

        window.history.replaceState(null, '', '/?auth_error=AUTH_FAILED');
        handleOAuthQuery(app);
        await flushShow();

        expect(isShown(box)).toBe(true);
        expect(box.textContent).toBe('Authentication failed');
        expect(box.textContent).not.toMatch(
            /\.env|CLIENT_ID|CLIENT_SECRET|Flask/i,
        );
    });
});
