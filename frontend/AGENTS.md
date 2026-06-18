# Frontend Agent Guide

Vite-powered SPA with Alpine.js state, controller modules, and `.hbs` view fragments. Global context: [../AGENTS.md](../AGENTS.md). Standards: [../.cursor/rules/frontend-rules.mdc](../.cursor/rules/frontend-rules.mdc).

## Directory map

```
frontend/
├── vite.config.js
├── tailwind.config.js
├── package.json
└── src/
    ├── index.html              # Shell: x-data="spaApp", x-init loadPage calls
    ├── js/
    │   ├── main.js             # Entry: Alpine.start(), imports CSS
    │   ├── pages.js            # Page registry (bundled templates + controllers)
    │   ├── app.js              # createSpaApp(), loadPage() router
    │   └── controllers/        # One named export per page/partial
    ├── templates/
    │   ├── pages/              # Main view (#view-container)
    │   └── partials/           # menu, login, shared regions
    └── styles/
        └── main.css            # @tailwind directives only
```

## Boot sequence

```
index.html
  └─ <script type="module" src="/js/main.js">
       └─ main.js
            ├─ import Alpine, main.css
            ├─ window.spaApp = createSpaApp()
            └─ Alpine.start()
                 └─ x-init on root div:
                      isLoggedIn = !!localStorage.getItem('token')
                      loadPage(...) × 3  (menu, login, landing page)
```

**Canonical references:** `@frontend/src/index.html`, `@frontend/src/js/main.js`, `@frontend/src/js/app.js`

## Page registry (`pages.js`)

All controllers and templates are statically imported in `frontend/src/js/pages.js` (Vite bundles them):

```javascript
import landingTpl from '../templates/pages/landingpage.hbs?raw';
import { landingPageController } from './controllers/landingpage.js';

export const pages = {
  landingpage: { template: landingTpl, controller: landingPageController },
  // ...
};
```

## SPA router: `loadPage()`

Defined in `app.js`:

```javascript
loadPage(elementIdTarget, pageKey)
```

| Step | Action |
|------|--------|
| 1 | Lookup `pages[pageKey]` |
| 2 | Set `innerHTML` on target element |
| 3 | Shallow-copy controller to `this.currentPage` |
| 4 | Call `currentPage.init(this)` if present |
| 5 | Call `Alpine.initTree(targetEl)` |

Navigation example from `menu.hbs`:

```html
<a href="#" @click.prevent="loadPage('view-container', 'landingpage')">
```

## Controller types

### Persistent partials

Always mounted; bound directly in templates:

| Controller | Export | Template binding |
|------------|--------|------------------|
| Login | `loginController` | `loginController.username`, `loginController.login()` |
| Menu | `menuController` | `menuController.sidebarOpen`, `menuController.toggleDarkMode()` |

Also exposed on `window` for Alpine access.

### Page controllers

Loaded into `#view-container`; bound as `currentPage.*`:

```html
<button @click="currentPage.fetchProtectedData()">Fetch Protected Data</button>
<pre x-text="JSON.stringify(currentPage.response, null, 2)"></pre>
```

**Canonical references:** `@frontend/src/js/controllers/login.js`, `@frontend/src/js/controllers/menu.js`, `@frontend/src/js/controllers/landingpage.js`

## Recipe: add a SPA page

1. **Create template** — `frontend/src/templates/pages/myfeature.hbs`

   Use Alpine directives only (`x-show`, `x-model`, `@click`, `x-text`). No `{{handlebars}}` syntax at runtime.

2. **Create controller** — `frontend/src/js/controllers/myfeature.js`

```javascript
export const myFeatureController = {
    appContext: null,
    isLoading: false,
    data: null,
    error: null,

    init(appContext) {
        this.appContext = appContext;
    },

    async fetchData() {
        this.isLoading = true;
        this.error = null;
        try {
            const token = localStorage.getItem('token');
            const response = await fetch('/api/myfeature', {
                headers: { Authorization: `Bearer ${token}` }
            });
            if (!response.ok) throw new Error('Request failed');
            this.data = await response.json();
        } catch (err) {
            this.error = err.message;
        } finally {
            this.isLoading = false;
        }
    }
};
```

3. **Wire navigation** in `frontend/src/templates/partials/menu.hbs`:

```html
<a href="#" @click.prevent="loadPage('view-container', '/templates/pages/myfeature.hbs', '/js/controllers/myfeature.js', 'myFeatureController')">
  My Feature
</a>
```

4. **Verify** via `cd frontend && npm run dev` at `http://localhost:5173`

## Templates (.hbs)

**Actual pattern:** `.hbs` files are **static HTML + Alpine directives** fetched at runtime. They are **not** Handlebars-rendered.

- Handlebars is imported in `main.js` but only a `json` helper is registered
- `vite-plugin-handlebars` is configured for compile-time use in `index.html` (currently unused)
- Display API data with Alpine: `x-text="JSON.stringify(currentPage.response, null, 2)"`

Cursor rule 2.2 (render with Handlebars) is aspirational — follow the Alpine pattern above until migrated.

## Alpine.js conventions

Root scope (`x-data="spaApp"`):

| Property / method | Purpose |
|-------------------|---------|
| `isLoggedIn` | Set from `localStorage.token` in `x-init` |
| `loadPage(...)` | SPA navigation |
| `logout()` | Clears token, reloads to `/` |
| `currentPage` | Active page controller copy |

Common directives: `x-show`, `x-model`, `x-text`, `@click.prevent`, `:class`, `:disabled`, `x-cloak`.

Dark mode: `class="dark"` on `<html>`, Tailwind `darkMode: 'class'` in `tailwind.config.js`. Initialized in `menu.js` before Alpine starts.

## API integration

All calls use Fetch to `/api/*`:

| Endpoint | Method | Auth | Controller |
|----------|--------|------|------------|
| `/api/login` | POST | No | `login.js` |
| `/api/register` | POST | No | `user_registry.js` |
| `/api/public` | GET | No | `landingpage.js` |
| `/api/data` | GET | Bearer token | `landingpage.js` |

**Auth pattern:**

```javascript
const response = await fetch('/api/data', {
    headers: { Authorization: `Bearer ${token}` }
});
if (response.status === 401) {
    this.appContext.logout();
}
```

Token stored in `localStorage.setItem('token', ...)`.

**Canonical reference:** `@frontend/src/js/controllers/landingpage.js`

## Vite configuration

Dev server (`npm run dev`):

- Port: `5173`
- Root: `frontend/src`
- Proxy: `/api` → `http://localhost:5000`

Build (`npm run build`):

- Output: `backend/templates/` (with `emptyOutDir: true`)
- Flask does **not** read this path today — production alignment is pending

PostCSS runs Tailwind + Autoprefixer inline in `vite.config.js`.

## Tailwind CSS

- Config: `frontend/tailwind.config.js` — scans `./src/**/*.{html,js,hbs}`
- Entry: `frontend/src/styles/main.css` (`@tailwind base/components/utilities`)
- Plugin: `@tailwindcss/forms`
- Use utility classes; avoid custom CSS except `[x-cloak]` in `index.html`

## Development commands

```bash
cd frontend
npm install
npm run dev      # Development — use :5173 in browser
npm run build    # Production bundle → backend/templates/
npm run preview  # Preview production build
```

Flask must be running on `:5000` for API calls during dev.

## Testing

```bash
cd frontend && npm run test   # Vitest + jsdom
```

## Frontend debt register

| Issue | Detail |
|-------|--------|
| Full page reloads | Login success and logout use `window.location.href = '/'` |
| No `Alpine.initTree()` | Dynamic innerHTML may not reliably init nested Alpine directives |
| Controller binding inconsistency | Partials use `loginController.*`; pages use `currentPage.*` |
| No frontend tests | No lint/test CI for JS |
| Dead menu links | Settings / Profile nav items have no handlers |

## See also

- [../AGENTS.md](../AGENTS.md) — global setup and verification
- [../backend/AGENTS.md](../backend/AGENTS.md) — API and auth patterns
- [../.cursor/rules/frontend-rules.mdc](../.cursor/rules/frontend-rules.mdc) — coding standards
