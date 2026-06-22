import { loginController } from './controllers/login.js';
import { menuController } from './controllers/menu.js';
import { welcomeController } from './controllers/welcome.js';
import { pages } from './pages.js';
import { applySeo, SEO_MODE } from './seo.js';

function handleOAuthFragment(app) {
    const hash = window.location.hash.slice(1);
    if (!hash) {
        return;
    }

    const params = new URLSearchParams(hash);
    const token = params.get('token');
    const authError = params.get('auth_error');

    window.history.replaceState(null, '', window.location.pathname + window.location.search);

    if (token) {
        localStorage.setItem('token', token);
        app.isLoggedIn = true;
    } else if (authError) {
        loginController.error = decodeURIComponent(authError);
        app.showLogin = true;
        applySeo(pages.login.seo, SEO_MODE);
    }
}

export const createSpaApp = () => {
    const app = {
        isLoggedIn: !!localStorage.getItem('token'),
        showLogin: false,
        oauthProviders: [],
        currentPage: {},
        menuController: menuController,
        loginController: loginController,
        welcomeController: welcomeController,

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
                applySeo(pages.landingpage.seo, SEO_MODE);
            } else {
                applySeo(pages.welcome.seo, SEO_MODE);
            }
        },

        async refreshOAuthProviders() {
            try {
                const response = await fetch('/api/auth/providers');
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
                const envPrefix = provider.toUpperCase();
                loginController.error =
                    `${provider.charAt(0).toUpperCase()}${provider.slice(1)} login is not configured. ` +
                    `Add ${envPrefix}_CLIENT_ID and ${envPrefix}_CLIENT_SECRET to .env, then restart Flask.`;
                return;
            }
            window.location.href = `/api/auth/${provider}/login`;
        },

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

            if (pageKey === 'login') {
                this.refreshOAuthProviders();
            }

            if (pageKey === 'welcome') {
                welcomeController.initCarousel();
            }
        },

        /** Load shell partials and initial page content after Alpine.start(). */
        bootApp() {
            this.loadPage('menu-container', 'menu');
            this.loadPage('login-register-container', 'login');
            this.loadPage('public-container', 'welcome');
            this.loadPage('view-container', 'landingpage');
            this.applyInitialSeo();
        },

        logout() {
            localStorage.removeItem('token');
            window.location.href = '/';
        }
    };

    app.menuController.init();
    app.loginController.init();
    app.welcomeController.init();
    app.refreshOAuthProviders();

    handleOAuthFragment(app);

    window.menuController = app.menuController;
    window.loginController = app.loginController;
    window.welcomeController = app.welcomeController;
    return app;
};
