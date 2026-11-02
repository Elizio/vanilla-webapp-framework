/**
 * Email verification and password-reset SPA behaviour.
 */
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { createSpaApp, handleEmailQuery } from '../src/js/app.js';
import { pages } from '../src/js/pages.js';
import { userRegistryController } from '../src/js/controllers/user_registry.js';
import { forgotPasswordController } from '../src/js/controllers/forgot_password.js';
import { resetPasswordController } from '../src/js/controllers/reset_password.js';
import { checkEmailController } from '../src/js/controllers/check_email.js';
import { landingPageController } from '../src/js/controllers/landingpage.js';
import loginTpl from '../src/templates/partials/login.hbs?raw';

describe('email auth UI', () => {
    /** @type {object[]} */
    const spaApps = [];

    /**
     * @returns {object}
     */
    function spaApp() {
        const app = createSpaApp();
        spaApps.push(app);
        return app;
    }

    afterEach(() => {
        while (spaApps.length) {
            const app = spaApps.pop();
            app.destroy();
        }
    });

    beforeEach(() => {
        document.body.innerHTML = `
            <div id="login-register-container"></div>
            <div id="public-container"></div>
            <div id="view-container"></div>
            <div id="menu-container"></div>
        `;
        window.Alpine = { initTree: vi.fn(), mutateDom: (cb) => cb() };
        fetch.mockReset();
        fetch.mockImplementation(async (input) => {
            const url = typeof input === 'string' ? input : input.url;
            if (url.endsWith('/api/csrf')) {
                return { ok: true, json: async () => ({ csrf_token: 'csrf' }) };
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
    });

    it('registers forgot, reset, and check-email pages', () => {
        expect(pages.forgot_password).toBeDefined();
        expect(pages.reset_password).toBeDefined();
        expect(pages.check_email).toBeDefined();
        expect(pages.forgot_password.seo.visibility).toBe('auth');
    });

    it('hides the forgot-password link when reset is not configured', () => {
        expect(loginTpl).toContain('emailCapabilities.password_reset');
        expect(loginTpl).toContain('forgot_password');
    });

    it('handleEmailQuery posts verify_token then enters the app', async () => {
        fetch.mockImplementation(async (input, options = {}) => {
            const url = typeof input === 'string' ? input : input.url;
            if (url.endsWith('/api/csrf')) {
                return { ok: true, json: async () => ({ csrf_token: 'csrf' }) };
            }
            if (
                url.endsWith('/api/auth/verify-email') &&
                options.method === 'POST'
            ) {
                return {
                    ok: true,
                    json: async () => ({
                        authenticated: true,
                        code: 'EMAIL_VERIFIED',
                    }),
                };
            }
            throw new Error(`Unmocked fetch in tests: ${url}`);
        });
        window.history.replaceState(null, '', '/?verify_token=raw-token-value');
        const app = spaApp();
        window.spaApp = app;
        const enter = vi.spyOn(app, 'enterAuthenticatedApp');
        await handleEmailQuery(app);
        expect(enter).toHaveBeenCalled();
        expect(window.location.search).toBe('');
    });

    it('handleEmailQuery stashes reset_token and shows the reset page', async () => {
        window.history.replaceState(null, '', '/?reset_token=reset-raw');
        const app = spaApp();
        await handleEmailQuery(app);
        expect(app.pendingResetToken).toBe('reset-raw');
        expect(app.showLogin).toBe(true);
        expect(app.activeAuthPageKey).toBe('reset_password');
        expect(window.location.search).toBe('');
    });

    it('register requires email only when email sending is configured', async () => {
        const app = {
            t: (key) => key,
            tError: (code) => code,
            emailCapabilities: { email_configured: true },
            enterAuthenticatedApp: vi.fn(),
            loadPage: vi.fn(),
        };
        userRegistryController.init(app);
        userRegistryController.username = 'ada';
        userRegistryController.password = 'testpass8';
        userRegistryController.confirmPassword = 'testpass8';
        userRegistryController.email = '';
        await userRegistryController.register();
        expect(userRegistryController.error).toBe('errors.EMAIL_REQUIRED');

        app.emailCapabilities.email_configured = false;
        userRegistryController.init(app);
        userRegistryController.username = 'ada';
        userRegistryController.password = 'testpass8';
        userRegistryController.confirmPassword = 'testpass8';
        fetch.mockImplementation(async (input) => {
            const url = typeof input === 'string' ? input : input.url;
            if (url.endsWith('/api/csrf')) {
                return { ok: true, json: async () => ({ csrf_token: 'csrf' }) };
            }
            if (url.endsWith('/api/register')) {
                return {
                    ok: true,
                    json: async () => ({
                        authenticated: true,
                        code: 'USER_CREATED',
                    }),
                };
            }
            throw new Error(`Unmocked fetch in tests: ${url}`);
        });
        await userRegistryController.register();
        expect(app.enterAuthenticatedApp).toHaveBeenCalled();
    });

    it('forgot-password submit is unavailable without SMTP', async () => {
        const app = {
            t: (key) => key,
            tError: (code) => code,
            emailCapabilities: { password_reset: false },
        };
        forgotPasswordController.init(app);
        await forgotPasswordController.submit();
        expect(forgotPasswordController.error).toBe('EMAIL_NOT_CONFIGURED');
    });

    it('forgot-password submit sends when reset is configured', async () => {
        fetch.mockImplementation(async (input) => {
            const url = typeof input === 'string' ? input : input.url;
            if (url.endsWith('/api/csrf')) {
                return { ok: true, json: async () => ({ csrf_token: 'csrf' }) };
            }
            if (url.endsWith('/api/auth/password/forgot')) {
                return {
                    ok: true,
                    json: async () => ({ code: 'EMAIL_ACCEPTED' }),
                };
            }
            throw new Error(`Unmocked fetch in tests: ${url}`);
        });
        const app = {
            t: (key) => key,
            tError: (code) => code,
            emailCapabilities: { password_reset: true },
        };
        forgotPasswordController.init(app);
        forgotPasswordController.email = 'ada@example.com';
        await forgotPasswordController.submit();
        expect(forgotPasswordController.success).toBe('forgot.checkEmail');
        expect(forgotPasswordController.error).toBeNull();
    });

    it('reset-password submit requires a token and matching password', async () => {
        const app = {
            t: (key) => key,
            tError: (code) => code,
            pendingResetToken: null,
        };
        resetPasswordController.init(app);
        await resetPasswordController.submit();
        expect(resetPasswordController.error).toBe('TOKEN_INVALID_OR_EXPIRED');

        app.pendingResetToken = 'raw-token';
        resetPasswordController.init(app);
        resetPasswordController.password = 'short';
        resetPasswordController.confirmPassword = 'short';
        await resetPasswordController.submit();
        expect(resetPasswordController.error).toBe('errors.PASSWORD_TOO_SHORT');

        resetPasswordController.password = 'newpass88';
        resetPasswordController.confirmPassword = 'otherpass';
        await resetPasswordController.submit();
        expect(resetPasswordController.error).toBe(
            'errors.PASSWORDS_DO_NOT_MATCH',
        );

        resetPasswordController.confirmPassword = 'newpass88';
        fetch.mockImplementation(async (input) => {
            const url = typeof input === 'string' ? input : input.url;
            if (url.endsWith('/api/csrf')) {
                return { ok: true, json: async () => ({ csrf_token: 'csrf' }) };
            }
            if (url.endsWith('/api/auth/password/reset')) {
                return {
                    ok: true,
                    json: async () => ({ code: 'PASSWORD_RESET' }),
                };
            }
            throw new Error(`Unmocked fetch in tests: ${url}`);
        });
        await resetPasswordController.submit();
        expect(resetPasswordController.success).toBe('reset.success');
        expect(app.pendingResetToken).toBeNull();
    });

    it('check-email resend posts the pending address', async () => {
        const app = {
            t: (key) => key,
            tError: (code) => code,
            pendingVerifyEmail: 'ada@example.com',
        };
        checkEmailController.init(app);
        fetch.mockImplementation(async (input) => {
            const url = typeof input === 'string' ? input : input.url;
            if (url.endsWith('/api/csrf')) {
                return { ok: true, json: async () => ({ csrf_token: 'csrf' }) };
            }
            if (url.endsWith('/api/auth/verify-email/resend')) {
                return {
                    ok: true,
                    json: async () => ({ code: 'EMAIL_ACCEPTED' }),
                };
            }
            throw new Error(`Unmocked fetch in tests: ${url}`);
        });
        await checkEmailController.resend();
        expect(checkEmailController.success).toBe('verify.resent');
    });

    it('landing add-email posts and clears the banner', async () => {
        const app = {
            t: (key) => key,
            tError: (code) => code,
            needsEmail: true,
        };
        landingPageController.init(app);
        await landingPageController.submitEmail();
        expect(landingPageController.error).toBe('errors.EMAIL_REQUIRED');

        landingPageController.newEmail = 'ada@example.com';
        fetch.mockImplementation(async (input) => {
            const url = typeof input === 'string' ? input : input.url;
            if (url.endsWith('/api/csrf')) {
                return { ok: true, json: async () => ({ csrf_token: 'csrf' }) };
            }
            if (url.endsWith('/api/auth/email')) {
                return {
                    ok: true,
                    json: async () => ({ code: 'EMAIL_ACCEPTED' }),
                };
            }
            throw new Error(`Unmocked fetch in tests: ${url}`);
        });
        await landingPageController.submitEmail();
        expect(landingPageController.emailSuccess).toBe('landing.addEmailSent');
        expect(app.needsEmail).toBe(false);
    });

    it('register without a session cookie shows the check-email page', async () => {
        const app = {
            t: (key) => key,
            tError: (code) => code,
            emailCapabilities: { email_configured: true },
            enterAuthenticatedApp: vi.fn(),
            loadPage: vi.fn(),
            pendingVerifyEmail: '',
        };
        userRegistryController.init(app);
        userRegistryController.username = 'ada';
        userRegistryController.email = 'ada@example.com';
        userRegistryController.password = 'testpass8';
        userRegistryController.confirmPassword = 'testpass8';
        fetch.mockImplementation(async (input) => {
            const url = typeof input === 'string' ? input : input.url;
            if (url.endsWith('/api/csrf')) {
                return { ok: true, json: async () => ({ csrf_token: 'csrf' }) };
            }
            if (url.endsWith('/api/register')) {
                return {
                    ok: true,
                    json: async () => ({
                        authenticated: false,
                        code: 'USER_CREATED',
                    }),
                };
            }
            throw new Error(`Unmocked fetch in tests: ${url}`);
        });
        await userRegistryController.register();
        expect(app.pendingVerifyEmail).toBe('ada@example.com');
        expect(app.loadPage).toHaveBeenCalledWith(
            'login-register-container',
            'check_email',
        );
        expect(app.enterAuthenticatedApp).not.toHaveBeenCalled();
    });

    it('forgot-password requires an address and surfaces API errors', async () => {
        const app = {
            t: (key) => key,
            tError: (code) => code,
            emailCapabilities: { password_reset: true },
        };
        forgotPasswordController.init(app);
        await forgotPasswordController.submit();
        expect(forgotPasswordController.error).toBe('errors.EMAIL_REQUIRED');

        forgotPasswordController.email = 'ada@example.com';
        fetch.mockImplementation(async (input) => {
            const url = typeof input === 'string' ? input : input.url;
            if (url.endsWith('/api/csrf')) {
                return { ok: true, json: async () => ({ csrf_token: 'csrf' }) };
            }
            if (url.endsWith('/api/auth/password/forgot')) {
                return {
                    ok: false,
                    json: async () => ({ code: 'EMAIL_NOT_CONFIGURED' }),
                };
            }
            throw new Error(`Unmocked fetch in tests: ${url}`);
        });
        await forgotPasswordController.submit();
        expect(forgotPasswordController.error).toBe('EMAIL_NOT_CONFIGURED');
    });

    it('reset-password and check-email surface API errors', async () => {
        fetch.mockImplementation(async (input) => {
            const url = typeof input === 'string' ? input : input.url;
            if (url.endsWith('/api/csrf')) {
                return { ok: true, json: async () => ({ csrf_token: 'csrf' }) };
            }
            if (
                url.endsWith('/api/auth/password/reset') ||
                url.endsWith('/api/auth/verify-email/resend')
            ) {
                return {
                    ok: false,
                    json: async () => ({ code: 'TOKEN_INVALID_OR_EXPIRED' }),
                };
            }
            throw new Error(`Unmocked fetch in tests: ${url}`);
        });
        const resetApp = {
            t: (key) => key,
            tError: (code) => code,
            pendingResetToken: 'raw-token',
        };
        resetPasswordController.init(resetApp);
        resetPasswordController.password = 'newpass88';
        resetPasswordController.confirmPassword = 'newpass88';
        await resetPasswordController.submit();
        expect(resetPasswordController.error).toBe('TOKEN_INVALID_OR_EXPIRED');

        const checkApp = {
            t: (key) => key,
            tError: (code) => code,
            pendingVerifyEmail: '',
        };
        checkEmailController.init(checkApp);
        await checkEmailController.resend();
        expect(checkEmailController.error).toBe('errors.EMAIL_REQUIRED');
        checkEmailController.email = 'ada@example.com';
        await checkEmailController.resend();
        expect(checkEmailController.error).toBe('TOKEN_INVALID_OR_EXPIRED');
    });

    it('handleEmailQuery shows login when verify fails', async () => {
        fetch.mockImplementation(async (input) => {
            const url = typeof input === 'string' ? input : input.url;
            if (url.endsWith('/api/csrf')) {
                return { ok: true, json: async () => ({ csrf_token: 'csrf' }) };
            }
            if (url.endsWith('/api/auth/verify-email')) {
                return {
                    ok: false,
                    json: async () => ({ code: 'TOKEN_INVALID_OR_EXPIRED' }),
                };
            }
            throw new Error(`Unmocked fetch in tests: ${url}`);
        });
        window.history.replaceState(null, '', '/?verify_token=bad');
        const app = spaApp();
        await handleEmailQuery(app);
        expect(app.showLogin).toBe(true);
    });

    it('landing add-email and register show API errors', async () => {
        fetch.mockImplementation(async (input) => {
            const url = typeof input === 'string' ? input : input.url;
            if (url.endsWith('/api/csrf')) {
                return { ok: true, json: async () => ({ csrf_token: 'csrf' }) };
            }
            if (url.endsWith('/api/auth/email')) {
                return {
                    ok: false,
                    json: async () => ({ code: 'EMAIL_EXISTS' }),
                };
            }
            if (url.endsWith('/api/register')) {
                return {
                    ok: false,
                    json: async () => ({ code: 'USERNAME_EXISTS' }),
                };
            }
            throw new Error(`Unmocked fetch in tests: ${url}`);
        });
        const landingApp = {
            t: (key) => key,
            tError: (code) => code,
            needsEmail: true,
        };
        landingPageController.init(landingApp);
        landingPageController.newEmail = 'ada@example.com';
        await landingPageController.submitEmail();
        expect(landingPageController.error).toBe('EMAIL_EXISTS');

        const registerApp = {
            t: (key) => key,
            tError: (code) => code,
            emailCapabilities: { email_configured: true },
            enterAuthenticatedApp: vi.fn(),
            loadPage: vi.fn(),
        };
        userRegistryController.init(registerApp);
        userRegistryController.username = 'ada';
        userRegistryController.email = 'ada@example.com';
        userRegistryController.password = 'testpass8';
        userRegistryController.confirmPassword = 'testpass8';
        await userRegistryController.register();
        expect(registerApp.enterAuthenticatedApp).not.toHaveBeenCalled();
        expect(userRegistryController.error).toBe('USERNAME_EXISTS');
    });
});
