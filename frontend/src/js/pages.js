import { menuController } from './controllers/menu.js';
import { loginController } from './controllers/login.js';
import { welcomeController } from './controllers/welcome.js';
import { landingPageController } from './controllers/landingpage.js';
import { testPageController } from './controllers/testpage.js';
import { userRegistryController } from './controllers/user_registry.js';

import menuTpl from '../templates/partials/menu.hbs?raw';
import loginTpl from '../templates/partials/login.hbs?raw';
import userRegistryTpl from '../templates/partials/user_registry.hbs?raw';
import welcomeTpl from '../templates/pages/welcome.hbs?raw';
import landingTpl from '../templates/pages/landingpage.hbs?raw';
import testTpl from '../templates/pages/testpage.hbs?raw';

const frameworkDescription =
    'Vanilla WebApp Framework — lightweight Flask and Alpine.js starter for entrepreneur solutions.';

export const pages = {
    menu: {
        template: menuTpl,
        controller: menuController,
        seo: {
            visibility: 'app',
            title: 'Menu — Vanilla WebApp Demo',
        },
    },
    login: {
        template: loginTpl,
        controller: loginController,
        seo: {
            visibility: 'auth',
            title: 'Login — Vanilla WebApp Demo',
            description: frameworkDescription,
        },
    },
    user_registry: {
        template: userRegistryTpl,
        controller: userRegistryController,
        seo: {
            visibility: 'auth',
            title: 'Register — Vanilla WebApp Demo',
            description: frameworkDescription,
        },
    },
    welcome: {
        template: welcomeTpl,
        controller: welcomeController,
        seo: {
            visibility: 'public',
            title: 'Vanilla WebApp Framework — Ship your SaaS faster',
            description: frameworkDescription,
        },
    },
    landingpage: {
        template: landingTpl,
        controller: landingPageController,
        seo: {
            visibility: 'app',
            title: 'Vanilla WebApp Demo',
            description: frameworkDescription,
        },
    },
    testpage: {
        template: testTpl,
        controller: testPageController,
        seo: {
            visibility: 'app',
            title: 'Test Page — Vanilla WebApp Demo',
        },
    },
};
