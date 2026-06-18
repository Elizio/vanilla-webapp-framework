import { loginController } from './controllers/login.js';
import { menuController } from './controllers/menu.js';
import { pages } from './pages.js';

export const createSpaApp = () => {
    const app = {
        currentPage: {},
        menuController: menuController,
        loginController: loginController,

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

            targetEl.innerHTML = page.template;
            this.currentPage = Object.assign({}, page.controller);

            if (typeof this.currentPage.init === 'function') {
                this.currentPage.init(this);
            }

            if (window.Alpine && typeof window.Alpine.initTree === 'function') {
                window.Alpine.initTree(targetEl);
            }
        },

        logout() {
            localStorage.removeItem('token');
            window.location.href = '/';
        }
    };

    app.menuController.init();
    app.loginController.init();

    window.menuController = app.menuController;
    window.loginController = app.loginController;
    return app;
};
