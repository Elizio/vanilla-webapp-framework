# Frontend Agent Guide

Vite SPA with Alpine.js, controller modules, and `.hbs` view fragments. Global: [../AGENTS.md](../AGENTS.md). Recipes: [../ARCHITECTURE.md](../ARCHITECTURE.md). Standards: [../.cursor/rules/frontend-rules.mdc](../.cursor/rules/frontend-rules.mdc).

## Directory map

```
frontend/
├── vite.config.js
├── tailwind.config.js
├── package.json
└── src/
    ├── index.html              # x-data="spaApp"
    ├── js/                     # main.js, pages.js, app.js, controllers/
    ├── templates/pages|partials
    └── styles/main.css         # @tailwind directives only
```

## Boot

`index.html` → `main.js` (Alpine + CSS) → `window.spaApp = createSpaApp()` → `Alpine.start()` → `x-init` loads menu, login, and the landing page.

**Canonical:** `@frontend/src/index.html`, `@frontend/src/js/main.js`, `@frontend/src/js/app.js`

## Page registry and router

Controllers and templates are statically imported in `frontend/src/js/pages.js` (`?raw`). `loadPage(elementIdTarget, pageKey)` looks up the registry, sets `innerHTML`, copies the controller to `this.currentPage`, calls `init`, then `Alpine.initTree`.

Persistent partials (`loginController`, `menuController`) bind directly. Page controllers bind as `currentPage.*`.

Add a page: [ARCHITECTURE.md](../ARCHITECTURE.md#add-a-spa-page). Classify `seo.visibility` (`public` | `app` | `auth`) before finishing.

## Templates

`.hbs` files are **static HTML + Alpine**. They are not Handlebars-rendered. No `handlebars` package, no import in `main.js`, no `vite-plugin-handlebars`. Display API data with `x-text`.

## Alpine and API

Root `x-data="spaApp"`: `isLoggedIn`, `loadPage`, `logout`, `currentPage`. Dark mode: `class="dark"` on `<html>`, initialized in `menu.js`.

Fetch `/api/*` with credentials. 401 → `this.appContext.logout()`. Session cookie is httpOnly; CSRF token comes from `GET /api/csrf` via `api.js` (not `document.cookie`).

**Canonical:** `@frontend/src/js/controllers/landingpage.js`, `@frontend/src/js/api.js`

## Vite, Tailwind, Biome

- Dev: port `5173`, root `frontend/src`, proxy `/api` → `:5000`.
- Build: `backend/static/` with `emptyOutDir: true`.
- Tailwind scans `./src/**/*.{html,js,hbs}`; plugin `@tailwindcss/forms`.
- `npm run lint` / `format:check` = Biome (JS + JSON). Biome does **not** lint `.hbs`. `main.css` is excluded.

```bash
cd frontend
npm run dev
npm run build
npm run test          # Vitest + jsdom
npm run test:coverage # CI / make test (thresholds)
```

From the repo root, `make lint-frontend` / `make test` wrap these. Flask must be on `:5000` for API calls during `npm run dev`.

## i18n and SEO

Locales: `en`, `pt-BR` in `frontend/src/locales/`. Use `t(key)` / `tError(code)`. Add keys to **both** files. API errors map under `errors.*`.

`SEO_MODE` (`auth-first` default, or `public-first`) is a build-time Vite env (`VITE_SEO_MODE`) and also drives Flask `/robots.txt`. `applySeo()` runs inside `loadPage()` for `view-container`. History API routing and prerender are optional fork recipes — see [ARCHITECTURE.md](../ARCHITECTURE.md#add-a-spa-page).

## Debt

| Issue | Detail |
|-------|--------|
| Controller binding | Partials use `loginController.*`; pages use `currentPage.*` |
| SSR/prerender | Optional for SEO-heavy forks |

Resolved: cookie session via `api.js`, Vitest coverage, `Alpine.initTree()`, History API paths.

## Code documentation

File-level JSDoc on exported modules; `@param` / `@returns` when not obvious. [../.cursor/rules/documentation.mdc](../.cursor/rules/documentation.mdc).

## See also

- [../AGENTS.md](../AGENTS.md)
- [../ARCHITECTURE.md](../ARCHITECTURE.md)
- [../backend/AGENTS.md](../backend/AGENTS.md)
- [../.cursor/rules/frontend-rules.mdc](../.cursor/rules/frontend-rules.mdc)
