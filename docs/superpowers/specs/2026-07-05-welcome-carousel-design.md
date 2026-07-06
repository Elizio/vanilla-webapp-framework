# Welcome Page Carousel Refresh — Design Spec

**Date:** 2026-07-05  
**Status:** Approved  
**Scope:** Public welcome page (`welcome.hbs`, `welcomeController`, locale files, Vitest)

## Problem

The public welcome page carousel was built before billing, i18n, and cookie-session auth shipped. It has four slides that partially showcase the framework but:

- Omits **billing** (Lemon Squeezy) and **i18n** (EN / pt-BR), two major fork differentiators.
- Shows an **outdated auth mockup** that implies JWT / localStorage rather than cookie sessions + CSRF.
- Uses **inconsistent slide layout** — only slide 1 has a caption panel (tag / title / description); slides 2–4 are mostly visual with minimal copy.
- Hardcodes four dot buttons and four `carouselSlideNLabel` keys, making expansion brittle.

The hero trust badges and features grid (3 cards) also lag behind what the framework actually ships.

## Goals

1. **Attract developers to fork/clone** by showing breadth of included features — not changelog marketing or sign-up conversion.
2. Expand the carousel to **6 slides**, adding **billing** and **i18n** without removing existing topics.
3. **Full welcome page sync:** hero subtitle, trust badges, features grid, and refreshed auth slide — not carousel-only.
4. Refactor carousel navigation to a **data-driven** pattern so slide count scales without duplicating dot markup.
5. Preserve existing i18n, dark mode, SEO (single `h1`), and accessibility patterns.

## Non-goals

- Adding SEO or cookie-auth as separate carousel slides (out of scope for this pass).
- Replacing static HTML mockups with screenshots or animated GIFs.
- Extracting slide mockups into separate `.hbs` partial files (deferred unless slide count grows again).
- README or `.env.example` updates (no setup/run/config change).
- Live interactive demos on the welcome page (mockups remain decorative).

## Decisions (approved)

| Decision | Choice |
|----------|--------|
| Primary audience goal | **A** — Attract developers to fork; show what's in the box |
| Carousel size | **Expand** — 6 slides total (4 kept + 2 new) |
| New slides | **Billing** + **i18n** |
| Scope | **C** — Full welcome sync (carousel + hero + features grid + slide polish) |
| Implementation approach | **Data-driven carousel** (Approach 2) — `slides[]` in controller; static mockup HTML per slide in template |
| Slide order | 1 Dev workflow · 2 Auth/OAuth (refresh) · 3 Swagger · 4 Docker · 5 Billing · 6 i18n |

## Carousel structure

### Unified slide layout

Every slide uses the same chrome:

```
┌─ browser bar (context-specific URL) ─────────────┐
│  ┌ mockup (left ~50%) ─┐ ┌ caption panel (right) ┐ │
│  │ terminal / UI       │ │ tag · title · desc    │ │
│  └─────────────────────┘ └───────────────────────┘ │
└─ prev · ●●●●●● · next ─────────────────────────────┘
```

Inactive slides get `opacity-0 pointer-events-none aria-hidden="true"` so they are not focusable.

### Slide content

| # | Topic | Action | Chrome URL (mock) | Caption (EN) |
|---|--------|--------|-------------------|--------------|
| 1 | Dev workflow | Keep | `localhost:5173 → /api → :5000` | Dual-server, one origin — Vite proxies /api to Flask |
| 2 | Auth & OAuth | **Refresh** | `/api/auth/google/login` | Cookie sessions + OAuth — secure by default (HttpOnly cookie, CSRF; Google + Facebook) |
| 3 | Swagger | **Polish** | `localhost:5000/docs` | Interactive Swagger UI — every route documented |
| 4 | Docker production | **Polish** | `docker build · APP_PROFILE=production` | Single Docker image — Flask serves SPA + /api from :5000 |
| 5 | Billing | **New** | `localhost:5173/app/billing` | Payments included — Lemon Squeezy adapter, checkout, webhooks, entitlements |
| 6 | i18n | **New** | `localhost:5173 · locale: pt-BR` | i18n built-in — locale JSON files, `t()` everywhere, EN \| PT switcher |

### Slide 2 refresh detail

Replace JWT/localStorage implication with:

- Small **HttpOnly cookie** badge or label on the mockup.
- Brief CSRF mention in caption (`slide2Desc`).
- Keep Google + Facebook social buttons (still accurate).

### Slide 5 mockup (billing)

Mirror real `billing.hbs` at a simplified scale:

- Status panel with credit balance line.
- One plan card (“Supporter”) with custom amount input.
- “Continue to checkout” CTA button.
- Optional small “Lemon Squeezy” provider label in chrome or caption.

### Slide 6 mockup (i18n)

- Left pane: monospace JSON snippet from `en.json` / `pt-BR.json` (e.g. `"billing.title"`, `"menu.billing"`).
- Right pane: UI fragment showing EN \| PT toggle and sample translated strings.
- Caption emphasizes: add a locale file, wire `t()`, done.

## Controller refactor

**File:** `frontend/src/js/controllers/welcome.js`

```javascript
slides: [
  { tagKey: 'welcome.slide1Tag', titleKey: 'welcome.slide1Title', descKey: 'welcome.slide1Desc' },
  { tagKey: 'welcome.slide2Tag', titleKey: 'welcome.slide2Title', descKey: 'welcome.slide2Desc' },
  { tagKey: 'welcome.slide3Tag', titleKey: 'welcome.slide3Title', descKey: 'welcome.slide3Desc' },
  { tagKey: 'welcome.slide4Tag', titleKey: 'welcome.slide4Title', descKey: 'welcome.slide4Desc' },
  { tagKey: 'welcome.slide5Tag', titleKey: 'welcome.slide5Title', descKey: 'welcome.slide5Desc' },
  { tagKey: 'welcome.slide6Tag', titleKey: 'welcome.slide6Title', descKey: 'welcome.slide6Desc' },
],
```

- Remove hardcoded `carouselDots: [0, 1, 2, 3]`.
- Derive dot indices from `slides.length` (getter or computed in `initCarousel`).
- Template dot row: `x-for="(slide, i) in welcomeController.slides"` with `@click="welcomeController.goSlide(i); welcomeController.restartCarousel()"`.
- `goSlide(index)` unchanged — modulo wrap over `slides.length`.

### Reduced motion

In `initCarousel()`, check `window.matchMedia('(prefers-reduced-motion: reduce)').matches`. When true, **do not** start the auto-advance interval; manual prev/next/dots still work.

## Hero + features grid sync

### Hero subtitle

| Locale | Update |
|--------|--------|
| EN | Mention cookie auth + OAuth, billing, i18n, SEO modes, Docker (drop standalone “JWT” emphasis) |
| pt-BR | Same additions in Portuguese |

### Trust badges (4 → 6)

| Key | EN label |
|-----|----------|
| `trustAuth` | Cookie auth + OAuth *(reword)* |
| `trustVite` | Vite + Tailwind *(unchanged)* |
| `trustAlembic` | Alembic migrations *(unchanged)* |
| `trustDocker` | CI + Docker *(unchanged)* |
| `trustBilling` | Billing ready *(new)* |
| `trustI18n` | EN + pt-BR i18n *(new)* |

Keep `flex-wrap` on the trust row — six badges wrap naturally on small screens.

### Features grid (3 → 5 cards)

Layout: `sm:grid-cols-2 lg:grid-cols-3`; fifth card centered on large screens (`lg:col-start-2` on the last item or equivalent 3+2 visual balance).

| Key | EN title | EN description (summary) |
|-----|----------|--------------------------|
| `featureBackend*` | Backend-first | Unchanged |
| `featureFrontend*` | Vanilla frontend | Unchanged |
| `featureSeo*` | SEO fork-ready | Unchanged |
| `featureBilling*` | Payments included | Lemon Squeezy adapter, checkout, webhooks, entitlements; swap via `BILLING_PROVIDER` |
| `featureI18n*` | i18n built-in | Locale JSON, `t()` in templates/controllers, EN \| PT switcher |

**Unchanged:** partners sidebar, ad slot placeholders, footer.

## Locale keys

Add or update in **both** `frontend/src/locales/en.json` and `pt-BR.json`:

### Carousel

- `slide2Tag`, `slide2Title`, `slide2Desc` — cookie auth refresh
- `slide3Tag`, `slide3Title`, `slide3Desc` — Swagger caption panel
- `slide4Tag`, `slide4Title`, `slide4Desc` — Docker caption panel
- `slide5Tag`, `slide5Title`, `slide5Desc` — billing caption
- `slide5*` UI strings — billing mockup labels (plan name, checkout CTA, balance label as needed)
- `slide6Tag`, `slide6Title`, `slide6Desc` — i18n caption
- `slide6*` UI strings — i18n mockup sample strings
- Replace per-slide dot labels with one parameterized key: `carouselSlideLabel` accepting `{ n }` (removes `carouselSlide1Label` … `carouselSlide4Label` in favor of a single key used in the dot `x-for` loop)

### Hero + features

- Updated `heroSubtitle`
- Updated `trustAuth`; new `trustBilling`, `trustI18n`
- New `featureBillingTitle`, `featureBillingDesc`, `featureI18nTitle`, `featureI18nDesc`

## Accessibility

| Concern | Handling |
|---------|----------|
| Inactive slides focusable | `pointer-events-none` + `aria-hidden="true"` when not active |
| Dot buttons | Dynamic `aria-label` from locale (`carouselSlideLabel` or numbered keys) |
| Auto-advance | 5s interval; manual nav resets timer (existing); **paused** when `prefers-reduced-motion: reduce` |
| Prev/next | Existing `aria-label` keys (`carouselPrev`, `carouselNext`) |
| Locale switch on welcome | Existing EN \| PT buttons unchanged |

## Testing

**File:** `frontend/tests/welcome.test.js`

Existing tests preserved:

- `pages.welcome.seo.visibility === 'public'`
- Template contains exactly one `<h1>`
- `copyCloneCommand` is a function

New assertions:

- `welcomeController.slides.length === 6`
- Template references billing slide (e.g. `carouselCurrent === 4` or stable `id="carousel-slide-billing"`)
- Template references i18n slide (e.g. `carouselCurrent === 5` or `id="carousel-slide-i18n"`)

Run as part of verification: `cd frontend && npm run test`.

## Files touched

| File | Change |
|------|--------|
| `frontend/src/templates/pages/welcome.hbs` | 2 new slides, unified layouts on slides 2–4, 5 feature cards, 6 hero badges |
| `frontend/src/js/controllers/welcome.js` | `slides[]`, dynamic dots, reduced-motion check |
| `frontend/src/locales/en.json` | New/updated `welcome.*` keys |
| `frontend/src/locales/pt-BR.json` | Mirror |
| `frontend/tests/welcome.test.js` | Slide count + slide content markers |

## Verification checklist (implementation)

- [ ] `cd frontend && npm run build && npm run test`
- [ ] Manual check at `http://localhost:5173` — all 6 slides render, dots work, auto-advance pauses with reduced motion
- [ ] EN and pt-BR locale switch updates all new strings
- [ ] Single `h1` preserved for SEO
