# ADR 0002: Vite + Alpine.js + Tailwind (no Handlebars runtime)

## Status

Accepted

## Context

The SPA should stay vanilla JS (no React/Vue compiler) while still having a fast dev server, utility CSS, and page-sized templates.

## Decision

- Vite builds `frontend/src` and, in production, emits into `backend/static/`.
- Alpine.js owns client state. Page HTML lives in `.hbs` files as static fragments imported with `?raw`.
- Tailwind 3 + PostCSS in the frontend package (not a root `package.json`).
- No Handlebars runtime, no `vite-plugin-handlebars`.

## Consequences

- Biome lints JS and JSON only; it does not lint `.hbs` templates.
- `frontend/src/styles/main.css` stays on Vite/PostCSS (Biome ignores that file).
- New pages register in `frontend/src/js/pages.js`.
