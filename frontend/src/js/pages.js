import { menuController } from './controllers/menu.js';
import { loginController } from './controllers/login.js';
import { welcomeController } from './controllers/welcome.js';
import { landingPageController } from './controllers/landingpage.js';
import { testPageController } from './controllers/testpage.js';
import { userRegistryController } from './controllers/user_registry.js';
import { billingController } from './controllers/billing.js';
import { settingsController } from './controllers/settings.js';
import { profileController } from './controllers/profile.js';

import menuTpl from '../templates/partials/menu.hbs?raw';
import loginTpl from '../templates/partials/login.hbs?raw';
import userRegistryTpl from '../templates/partials/user_registry.hbs?raw';
import welcomeTpl from '../templates/pages/welcome.hbs?raw';
import landingTpl from '../templates/pages/landingpage.hbs?raw';
import testTpl from '../templates/pages/testpage.hbs?raw';
import billingTpl from '../templates/pages/billing.hbs?raw';
import settingsTpl from '../templates/pages/settings.hbs?raw';
import profileTpl from '../templates/pages/profile.hbs?raw';

/** Map page keys to browser paths for History API routing. */
export const PAGE_ROUTES = {
    welcome: '/',
    landingpage: '/app',
    testpage: '/app/analytics',
    billing: '/app/billing',
    settings: '/app/settings',
    profile: '/app/profile',
};

/** Reverse lookup: pathname → page key (longest prefix wins). */
export const PATH_TO_PAGE = Object.fromEntries(
    Object.entries(PAGE_ROUTES).map(([key, path]) => [path, key]),
);

export const pages = {
    menu: {
        template: menuTpl,
        controller: menuController,
        seo: {
            visibility: 'app',
            titleKey: 'seo.menu.title',
        },
    },
    login: {
        template: loginTpl,
        controller: loginController,
        seo: {
            visibility: 'auth',
            titleKey: 'seo.login.title',
            descriptionKey: 'seo.frameworkDescription',
        },
    },
    user_registry: {
        template: userRegistryTpl,
        controller: userRegistryController,
        seo: {
            visibility: 'auth',
            titleKey: 'seo.register.title',
            descriptionKey: 'seo.frameworkDescription',
        },
    },
    welcome: {
        template: welcomeTpl,
        controller: welcomeController,
        seo: {
            visibility: 'public',
            titleKey: 'seo.welcome.title',
            descriptionKey: 'seo.welcome.description',
        },
    },
    landingpage: {
        template: landingTpl,
        controller: landingPageController,
        seo: {
            visibility: 'app',
            titleKey: 'seo.landing.title',
            descriptionKey: 'seo.frameworkDescription',
        },
    },
    testpage: {
        template: testTpl,
        controller: testPageController,
        seo: {
            visibility: 'app',
            titleKey: 'seo.testpage.title',
        },
    },
    billing: {
        template: billingTpl,
        controller: billingController,
        seo: {
            visibility: 'app',
            titleKey: 'seo.billing.title',
        },
    },
    settings: {
        template: settingsTpl,
        controller: settingsController,
        seo: {
            visibility: 'app',
            titleKey: 'seo.settings.title',
        },
    },
    profile: {
        template: profileTpl,
        controller: profileController,
        seo: {
            visibility: 'app',
            titleKey: 'seo.profile.title',
        },
    },
};
