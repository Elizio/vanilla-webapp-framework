import { menuController } from './controllers/menu.js';
import { loginController } from './controllers/login.js';
import { landingPageController } from './controllers/landingpage.js';
import { testPageController } from './controllers/testpage.js';
import { userRegistryController } from './controllers/user_registry.js';

import menuTpl from '../templates/partials/menu.hbs?raw';
import loginTpl from '../templates/partials/login.hbs?raw';
import userRegistryTpl from '../templates/partials/user_registry.hbs?raw';
import landingTpl from '../templates/pages/landingpage.hbs?raw';
import testTpl from '../templates/pages/testpage.hbs?raw';

export const pages = {
    menu:          { template: menuTpl,         controller: menuController },
    login:         { template: loginTpl,        controller: loginController },
    user_registry: { template: userRegistryTpl, controller: userRegistryController },
    landingpage:   { template: landingTpl,      controller: landingPageController },
    testpage:      { template: testTpl,         controller: testPageController },
};
