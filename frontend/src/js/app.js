/**
 * SPA shell: page registry router, OAuth query handler, Alpine root state.
 * @module app
 */
import { withBase, stripBase } from './basepath.js';
import { loginController } from './controllers/login.js';
import { menuController } from './controllers/menu.js';
import { welcomeController } from './controllers/welcome.js';
import { pages, PAGE_ROUTES, PATH_TO_PAGE } from './pages.js';
import { applySeo, resolveVisibility, SEO_MODE } from './seo.js';
import {
    initLocale,
    setLocale as applyLocale,
    getLocale,
    t as translate,
    tError as translateError,
} from './i18n.js';
import {
    AUTH_EXPIRED_EVENT,
    apiFetch,
    fetchSession,
    initCsrf,
    resetCsrf,
} from './api.js';

/**
 * Resolve a page key from the current pathname.
 * @returns {string|null}
 */
function pageKeyFromPath() {
    const path = stripBase(window.location.pathname).replace(/\/$/, '') || '/';
    if (PATH_TO_PAGE[path]) {
        return PATH_TO_PAGE[path];
    }
    const match = Object.entries(PAGE_ROUTES)
        .sort((a, b) => b[1].length - a[1].length)
        .find(
            ([, routePath]) => path.startsWith(routePath) && routePath !== '/',
        );
    return match ? match[0] : null;
}

/**
 * Pick the in-app page for an authenticated session from the current URL.
 * Public/auth paths (e.g. `/`) fall back to the default app home.
 * @returns {string}
 */
function resolveLoggedInPageKey() {
    const routedPage = pageKeyFromPath();
    if (routedPage && pages[routedPage]) {
        const visibility = resolveVisibility(pages[routedPage].seo, SEO_MODE);
        if (visibility === 'app') {
            return routedPage;
        }
    }
    return 'landingpage';
}

/**
 * Sync the browser URL to a registered app page route.
 * @param {string} pageKey
 * @param {{ replace?: boolean }} [options]
 */
function syncUrlForPage(pageKey, { replace = false } = {}) {
    const targetPath = PAGE_ROUTES[pageKey];
    if (!targetPath || stripBase(window.location.pathname) === targetPath) {
        return;
    }
    const state = { pageKey };
    const fullPath = withBase(targetPath);
    if (replace) {
        window.history.replaceState(state, '', fullPath);
    } else {
        window.history.pushState(state, '', fullPath);
    }
}

/**
 * Run callback after Alpine applies pending DOM updates (fallback: microtask).
 * @param {() => void} callback
 */
function afterAlpineUpdate(callback) {
    if (typeof window.Alpine?.nextTick === 'function') {
        window.Alpine.nextTick(callback);
    } else {
        queueMicrotask(callback);
    }
}

/**
 * Set the login-form error on Alpine's reactive controller copy.
 * Writes to ``app.loginController`` (not the imported module object) so ``x-show`` updates.
 * @param {object} app - Root spaApp instance (Alpine reactive proxy).
 * @param {string} message - User-facing error text.
 */
function setLoginError(app, message) {
    app.loginController.error = message;
}

/**
 * @param {object} app - Root spaApp instance.
 */
export function handleOAuthQuery(app) {
    const params = new URLSearchParams(window.location.search);
    const authSuccess = params.get('auth');
    const authError = params.get('auth_error');

    if (!authSuccess && !authError) {
        return;
    }

    window.history.replaceState(null, '', window.location.pathname);

    if (authSuccess === 'success') {
        app.isLoggedIn = true;
        app.showLogin = false;
    } else if (authError) {
        setLoginError(app, app.tError(authError));
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
        sidebarOpen: typeof window !== 'undefined' && window.innerWidth >= 1024,
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
                this.loadPage(
                    'login-register-container',
                    this.activeAuthPageKey,
                );
            } else {
                this.loadPage('public-container', 'welcome');
            }
            this.applyInitialSeo();
        },

        /**
         * Transition from auth UI to the authenticated app shell and route.
         * @param {string} [pageKey='landingpage'] - App page to show after login.
         */
        enterAuthenticatedApp(pageKey = 'landingpage') {
            this.isLoggedIn = true;
            this.showLogin = false;
            this.sidebarOpen = true;
            this.activeViewPageKey = pages[pageKey] ? pageKey : 'landingpage';

            afterAlpineUpdate(() => {
                this.refreshMountedPages();
                syncUrlForPage(this.activeViewPageKey, { replace: true });
            });
        },

        showLoginPage() {
            this.showLogin = true;
            this.refreshMountedPages();
        },

        showWelcomePage() {
            this.showLogin = false;
            this.refreshMountedPages();
        },

        applyInitialSeo() {
            if (this.isLoggedIn) {
                applySeo(
                    pages[this.activeViewPageKey]?.seo ?? pages.landingpage.seo,
                    SEO_MODE,
                );
            } else if (this.showLogin) {
                applySeo(
                    pages[this.activeAuthPageKey]?.seo ?? pages.login.seo,
                    SEO_MODE,
                );
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
                const label =
                    provider.charAt(0).toUpperCase() + provider.slice(1);
                console.warn(
                    `${label} login is not configured. Add ${provider.toUpperCase()}_CLIENT_ID and ${provider.toUpperCase()}_CLIENT_SECRET to .env, then restart Flask.`,
                );
                setLoginError(
                    this,
                    this.t('errors.OAUTH_NOT_CONFIGURED', {
                        provider: label,
                    }),
                );
                return;
            }
            window.location.href = withBase(`/api/auth/${provider}/login`);
        },

        toggleSidebar() {
            this.sidebarOpen = !this.sidebarOpen;
        },

        /**
         * Get the full URL for a page key (including base path).
         * @param {string} pageKey - Key in pages.js registry.
         * @returns {string} Full URL path with base.
         */
        getPageUrl(pageKey) {
            const route = PAGE_ROUTES[pageKey];
            return route ? withBase(route) : '#';
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
                syncUrlForPage(pageKey);
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

            if (this.isLoggedIn) {
                this.sidebarOpen = true;
                this.activeViewPageKey = resolveLoggedInPageKey();
            }

            window.addEventListener('popstate', () => {
                if (!this.isLoggedIn) {
                    return;
                }
                const key = resolveLoggedInPageKey();
                this.activeViewPageKey = key;
                this.loadPage('view-container', key);
            });

            if (this.isLoggedIn) {
                this.loadPage('menu-container', 'menu');
                this.loadPage('view-container', this.activeViewPageKey);
                syncUrlForPage(this.activeViewPageKey, { replace: true });
            } else if (this.showLogin) {
                this.loadPage(
                    'login-register-container',
                    this.activeAuthPageKey,
                );
            } else {
                this.loadPage('public-container', 'welcome');
            }
            this.applyInitialSeo();
        },

        /**
         * Clear local auth UI without calling the logout API.
         * @param {{ showLogin?: boolean }} [options]
         */
        async clearLocalSession({ showLogin = false } = {}) {
            resetCsrf();
            this.isLoggedIn = false;
            this.showLogin = showLogin;
            await initCsrf();
            const strippedPath = stripBase(window.location.pathname);
            if (strippedPath !== '/') {
                window.history.replaceState(null, '', withBase('/'));
            }
            this.refreshMountedPages();
        },

        async logout() {
            try {
                await apiFetch('/api/auth/logout', { method: 'POST' });
            } catch (err) {
                console.error('Logout failed:', err);
            }
            await this.clearLocalSession({ showLogin: false });
        },
    };

    app.menuController.init();
    app.loginController.init();
    app.welcomeController.init();

    window.menuController = app.menuController;
    window.loginController = app.loginController;
    window.welcomeController = app.welcomeController;

    if (typeof window.addEventListener === 'function') {
        window.addEventListener(AUTH_EXPIRED_EVENT, () => {
            app.clearLocalSession({ showLogin: true });
        });
    }

    return app;
};
