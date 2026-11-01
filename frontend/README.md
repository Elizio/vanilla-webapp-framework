# Frontend

Vite + Alpine.js + Tailwind SPA. **Do not add a second `package.json` at the repo root** — Tailwind and Vite live here (this package uses Tailwind 3).

| Task | Where |
|------|--------|
| Commands | `npm run dev` / `build` / `test` / `lint` — or `make` from the repo root |
| Agent map | [AGENTS.md](AGENTS.md) |
| Recipes (add a page, SEO, i18n) | [../ARCHITECTURE.md](../ARCHITECTURE.md) |
| Human how-to | [../README.md](../README.md) |

Dev server: `http://localhost:5173` (proxies `/api` to Flask `:5000`). Production build writes `backend/static/`.
