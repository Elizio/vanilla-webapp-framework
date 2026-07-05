/**
 * SPA shell: page registry router, OAuth query handler, Alpine root state.
 * @module app
 */
import { loginController } from './controllers/login.js';
import { menuController } from './controllers/menu.js';
import { welcomeController } from './controllers/welcome.js';
import { pages, PAGE_ROUTES, PATH_TO_PAGE } from './pages.js';
import { applySeo, SEO_MODE } from './seo.js';
import {
    initLocale,
    setLocale as applyLocale,
    getLocale,
    t as translate,
    tError as translateError,
} from './i18n.js';
import { apiFetch, fetchSession, initCsrf, resetCsrf } from './api.js';

/**
 * Resolve a page key from the current pathname.
 * @returns {string|null}
 */
function pageKeyFromPath() {
    const path = window.location.pathname.replace(/\/$/, '') || '/';
    if (PATH_TO_PAGE[path]) {
        return PATH_TO_PAGE[path];
    }
    const match = Object.entries(PAGE_ROUTES)
        .sort((a, b) => b[1].length - a[1].length)
        .find(([, routePath]) => path.startsWith(routePath) && routePath !== '/');
    return match ? match[0] : null;
}

/**
 * @param {object} app - Root spaApp instance.
 */
function handleOAuthQuery(app) {
    const params = new URLSearchParams(window.location.search);
    const authSuccess = params.get('auth');
    const authError = params.get('auth_error');

    if (!authSuccess && !authError) {
        return;
    }

    window.history.replaceState(null, '', window.location.pathname);

    if (authSuccess === 'success') {
        app.isLoggedIn = true;
    } else if (authError) {
        loginController.error = app.tError(authError);
        app.showLogin = true;
        applySeo(pages.login.seo, SEO_MODE);
    }
}

/**
 * Create the Alpine root application object.
 * @returns {object} Alpine x-data root (isLoggedIn, loadPage, controllers, …)
 */
export const createSpaApp = () => {
    const app = {
        isLoggedIn: false,
        showLogin: false,
        oauthProviders: [],
        currentPage: {},
        activeViewPageKey: 'landingpage',
        activeAuthPageKey: 'login',
        locale: initLocale(),
        menuController: menuController,
        loginController: loginController,
        welcomeController: welcomeController,

        /**
         * @param {string} key
         * @param {Record<string, string|number>} [params]
         * @returns {string}
         */
        t(key, params) {
            return translate(key, params);
        },

        /**
         * @param {string} code
         * @returns {string}
         */
        tError(code) {
            return translateError(code);
        },

        /**
         * @param {string} locale
         */
        setLocale(locale) {
            applyLocale(locale);
            this.locale = getLocale();
            this.refreshMountedPages();
        },

        refreshMountedPages() {
            if (this.isLoggedIn) {
                this.loadPage('menu-container', 'menu');
                this.loadPage('view-container', this.activeViewPageKey);
            } else if (this.showLogin) {
                this.loadPage('login-register-container', this.activeAuthPageKey);
            } else {
                this.loadPage('public-container', 'welcome');
            }
            this.applyInitialSeo();
        },

        showLoginPage() {
            this.showLogin = true;
            this.refreshOAuthProviders();
            applySeo(pages.login.seo, SEO_MODE);
        },

        showWelcomePage() {
            this.showLogin = false;
            applySeo(pages.welcome.seo, SEO_MODE);
        },

        applyInitialSeo() {
            if (this.isLoggedIn) {
                applySeo(pages[this.activeViewPageKey]?.seo ?? pages.landingpage.seo, SEO_MODE);
            } else if (this.showLogin) {
                applySeo(pages[this.activeAuthPageKey]?.seo ?? pages.login.seo, SEO_MODE);
            } else {
                applySeo(pages.welcome.seo, SEO_MODE);
            }
        },

        async refreshOAuthProviders() {
            try {
                const response = await apiFetch('/api/auth/providers');
                if (response.ok) {
                    this.oauthProviders = await response.json();
                }
            } catch (err) {
                console.error('Failed to load OAuth providers:', err);
            }
        },

        isOAuthEnabled(provider) {
            return this.oauthProviders.includes(provider);
        },

        startSocialLogin(provider) {
            if (!this.isOAuthEnabled(provider)) {
                const label = provider.charAt(0).toUpperCase() + provider.slice(1);
                loginController.error = this.t('errors.OAUTH_NOT_CONFIGURED', {
                    provider: label,
                    envPrefix: provider.toUpperCase(),
                });
                return;
            }
            window.location.href = `/api/auth/${provider}/login`;
        },

        /**
         * Load a registered page into a DOM target and init Alpine on it.
         * @param {string} elementIdTarget - DOM id of the mount point.
         * @param {string} pageKey - Key in pages.js registry.
         */
        loadPage(elementIdTarget, pageKey) {
            const page = pages[pageKey];
            if (!page) {
                console.error(`Unknown page: ${pageKey}`);
                return;
            }

            const targetEl = document.getElementById(elementIdTarget);
            if (!targetEl) {
                console.error(`Element not found: ${elementIdTarget}`);
                return;
            }

            if (elementIdTarget === 'view-container') {
                this.activeViewPageKey = pageKey;
            }
            if (elementIdTarget === 'login-register-container') {
                this.activeAuthPageKey = pageKey;
            }

            window.Alpine.mutateDom(() => {
                targetEl.innerHTML = page.template;
            });
            this.currentPage = Object.assign({}, page.controller);

            if (typeof this.currentPage.init === 'function') {
                this.currentPage.init(this);
            }

            Array.from(targetEl.children).forEach((child) => {
                window.Alpine.initTree(child);
            });

            if (elementIdTarget === 'view-container' && page.seo) {
                applySeo(page.seo, SEO_MODE);
            }

            if (elementIdTarget === 'view-container' && PAGE_ROUTES[pageKey]) {
                const targetPath = PAGE_ROUTES[pageKey];
                if (window.location.pathname !== targetPath) {
                    window.history.pushState({ pageKey }, '', targetPath);
                }
            }

            if (pageKey === 'login') {
                this.refreshOAuthProviders();
            }

            if (pageKey === 'welcome') {
                welcomeController.initCarousel();
            }
        },

        /** Load shell partials and initial page content after Alpine.start(). */
        async bootApp() {
            await initCsrf();
            const session = await fetchSession();
            this.isLoggedIn = session.authenticated === true;
            handleOAuthQuery(this);

            const routedPage = pageKeyFromPath();
            if (this.isLoggedIn && routedPage && pages[routedPage]) {
                this.activeViewPageKey = routedPage;
            }

            window.addEventListener('popstate', () => {
                const key = pageKeyFromPath();
                if (this.isLoggedIn && key && pages[key]) {
                    this.activeViewPageKey = key;
                    this.loadPage('view-container', key);
                }
            });

            if (this.isLoggedIn) {
                this.loadPage('menu-container', 'menu');
                this.loadPage('view-container', this.activeViewPageKey);
            } else if (this.showLogin) {
                this.loadPage('login-register-container', this.activeAuthPageKey);
            } else {
                this.loadPage('public-container', 'welcome');
            }
            this.applyInitialSeo();
        },

        async logout() {
            try {
                await apiFetch('/api/logout', { method: 'POST' });
            } catch (err) {
                console.error('Logout failed:', err);
            }
            resetCsrf();
            this.isLoggedIn = false;
            this.showLogin = false;
            await initCsrf();
            this.refreshMountedPages();
        },
    };

    app.menuController.init();
    app.loginController.init();
    app.welcomeController.init();

    window.menuController = app.menuController;
    window.loginController = app.loginController;
    window.welcomeController = app.welcomeController;
    return app;
};
