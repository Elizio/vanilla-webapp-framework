# Welcome Page Carousel Refresh — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expand the public welcome page carousel to six slides (billing + i18n), unify slide layouts, sync hero/features copy, and refactor carousel navigation to a data-driven pattern.

**Architecture:** Static mockup HTML remains in `welcome.hbs` (one block per slide). `welcomeController.slides[]` drives dot count and `goSlide()` bounds. All user-facing strings live in `en.json` / `pt-BR.json`. Auth marketing copy uses “Cookie auth + OAuth” (JWT stays inside the HttpOnly cookie — not SPA localStorage).

**Tech Stack:** Alpine.js, Handlebars template (static HTML), Tailwind CSS, Vitest. No new dependencies.

**Spec:** [docs/superpowers/specs/2026-07-05-welcome-carousel-design.md](../specs/2026-07-05-welcome-carousel-design.md)

---

## File map

| File | Action | Responsibility |
|------|--------|----------------|
| `frontend/tests/welcome.test.js` | Modify | Assert 6 slides, billing/i18n markers, `slides` array |
| `frontend/src/js/controllers/welcome.js` | Modify | `slides[]`, dynamic dot length, reduced-motion |
| `frontend/src/locales/en.json` | Modify | New/updated `welcome.*` keys |
| `frontend/src/locales/pt-BR.json` | Modify | Mirror EN welcome keys |
| `frontend/src/templates/pages/welcome.hbs` | Modify | 6 slides, unified layouts, 5 feature cards, 6 trust badges |

---

### Task 1: Failing welcome tests

**Files:**
- Modify: `frontend/tests/welcome.test.js`

- [ ] **Step 1: Add failing tests**

Replace the test file contents with:

```javascript
import { describe, it, expect } from 'vitest';
import { pages } from '../src/js/pages.js';
import { welcomeController } from '../src/js/controllers/welcome.js';
import welcomeTpl from '../src/templates/pages/welcome.hbs?raw';

describe('welcome page', () => {
    it('is registered with public SEO visibility', () => {
        expect(pages.welcome).toBeDefined();
        expect(pages.welcome.seo.visibility).toBe('public');
    });

    it('template contains exactly one h1 for SEO', () => {
        const h1Matches = welcomeTpl.match(/<h1[\s>]/g);
        expect(h1Matches).toHaveLength(1);
    });

    it('has a welcomeController with copyCloneCommand', () => {
        expect(typeof welcomeController.copyCloneCommand).toBe('function');
    });

    it('defines six carousel slides', () => {
        expect(welcomeController.slides).toHaveLength(6);
    });

    it('template includes billing and i18n carousel slides', () => {
        expect(welcomeTpl).toContain('id="carousel-slide-billing"');
        expect(welcomeTpl).toContain('id="carousel-slide-i18n"');
    });

    it('uses dynamic carousel dot loop', () => {
        expect(welcomeTpl).toContain('welcomeController.slides');
        expect(welcomeTpl).toContain('carouselSlideLabel');
    });
});
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd frontend && npm run test -- welcome.test.js`  
Expected: FAIL — `slides` undefined, missing `carousel-slide-billing`, etc.

- [ ] **Step 3: Commit**

```bash
git add frontend/tests/welcome.test.js
git commit -m "test: add welcome carousel expansion assertions"
```

---

### Task 2: Controller refactor

**Files:**
- Modify: `frontend/src/js/controllers/welcome.js`

- [ ] **Step 1: Replace hardcoded carousel state with slides array**

Update `welcome.js`:

```javascript
/** Public welcome page controller: clone command, clipboard copy, and carousel. */

const CAROUSEL_INTERVAL_MS = 5000;

/**
 * Welcome page controller for the public marketing landing.
 * Bound in templates as ``welcomeController.*`` (root scope, not ``currentPage``).
 */
export const welcomeController = {
    cloneCommand: 'git clone https://github.com/you/vanilla-webapp-framework.git',
    copyFeedback: '',
    carouselCurrent: 0,
    carouselTimer: null,

    slides: [
        { tagKey: 'welcome.slide1Tag', titleKey: 'welcome.slide1Title', descKey: 'welcome.slide1Desc' },
        { tagKey: 'welcome.slide2Tag', titleKey: 'welcome.slide2Title', descKey: 'welcome.slide2Desc' },
        { tagKey: 'welcome.slide3Tag', titleKey: 'welcome.slide3Title', descKey: 'welcome.slide3Desc' },
        { tagKey: 'welcome.slide4Tag', titleKey: 'welcome.slide4Title', descKey: 'welcome.slide4Desc' },
        { tagKey: 'welcome.slide5Tag', titleKey: 'welcome.slide5Title', descKey: 'welcome.slide5Desc' },
        { tagKey: 'welcome.slide6Tag', titleKey: 'welcome.slide6Title', descKey: 'welcome.slide6Desc' },
    ],

    /** Reset transient state. */
    init() {
        this.copyFeedback = '';
    },

    /** Whether carousel auto-advance should run. */
    shouldAutoAdvance() {
        return !window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    },

    /** Start or restart the carousel auto-advance timer. */
    initCarousel() {
        this.stopCarousel();
        this.carouselCurrent = 0;
        if (this.shouldAutoAdvance()) {
            this.carouselTimer = setInterval(() => {
                this.goSlide(this.carouselCurrent + 1);
            }, CAROUSEL_INTERVAL_MS);
        }
    },

    /** Clear the carousel auto-advance timer. */
    stopCarousel() {
        if (this.carouselTimer) {
            clearInterval(this.carouselTimer);
            this.carouselTimer = null;
        }
    },

    /**
     * @param {number} index - Zero-based slide index.
     */
    goSlide(index) {
        const total = this.slides.length;
        this.carouselCurrent = ((index % total) + total) % total;
    },

    /** Show the previous carousel slide. */
    prevSlide() {
        this.goSlide(this.carouselCurrent - 1);
        this.restartCarousel();
    },

    /** Show the next carousel slide. */
    nextSlide() {
        this.goSlide(this.carouselCurrent + 1);
        this.restartCarousel();
    },

    /** Reset auto-advance after manual navigation. */
    restartCarousel() {
        this.stopCarousel();
        if (this.shouldAutoAdvance()) {
            this.carouselTimer = setInterval(() => {
                this.goSlide(this.carouselCurrent + 1);
            }, CAROUSEL_INTERVAL_MS);
        }
    },

    /** Copy the git clone command to the clipboard. */
    async copyCloneCommand() {
        const translate = window.spaApp?.t?.bind(window.spaApp) ?? ((key) => key);
        try {
            if (navigator.clipboard?.writeText) {
                await navigator.clipboard.writeText(this.cloneCommand);
                this.copyFeedback = translate('welcome.copied');
            } else {
                this.copyFeedback = translate('welcome.copyUnavailable');
            }
        } catch {
            this.copyFeedback = translate('welcome.copyFailed');
        }

        setTimeout(() => {
            this.copyFeedback = '';
        }, 2000);
    },
};
```

- [ ] **Step 2: Run tests**

Run: `cd frontend && npm run test -- welcome.test.js`  
Expected: `defines six carousel slides` PASS; template tests still FAIL.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/js/controllers/welcome.js
git commit -m "feat: data-driven welcome carousel controller with reduced motion"
```

---

### Task 3: English locale keys

**Files:**
- Modify: `frontend/src/locales/en.json`

- [ ] **Step 1: Update `welcome` section**

Apply these changes inside `"welcome": { ... }`:

**Replace** `heroSubtitle`:
```json
"heroSubtitle": "Flask REST API, Alpine.js SPA, cookie auth + OAuth, billing, i18n, SEO modes, and Docker — a production-ready starter so you focus on your idea, not boilerplate.",
```

**Replace** `trustAuth`:
```json
"trustAuth": "Cookie auth + OAuth",
```

**Add** after `trustDocker`:
```json
"trustBilling": "Billing ready",
"trustI18n": "EN + pt-BR i18n",
```

**Replace** carousel dot labels — remove `carouselSlide1Label` … `carouselSlide4Label`, add:
```json
"carouselSlideLabel": "Go to slide {n}",
```

**Add** slide caption keys (after existing `slide1Desc` / slide UI keys):
```json
"slide2Tag": "Authentication",
"slide2Title": "Cookie sessions + OAuth",
"slide2Desc": "HttpOnly session cookie and CSRF on mutating requests — Google and Facebook OAuth included.",
"slide2CookieBadge": "HttpOnly cookie",
"slide3Tag": "API docs",
"slide3Title": "Swagger out of the box",
"slide3Desc": "Interactive Swagger UI — every route documented.",
"slide4Tag": "Production",
"slide4Title": "Single-server deploy",
"slide4Desc": "Vite build lands in backend/static/ — Flask serves /api and the SPA from one Docker image.",
"slide5Tag": "Billing",
"slide5Title": "Payments included",
"slide5Desc": "Lemon Squeezy adapter with checkout, webhooks, and entitlements — swap providers via BILLING_PROVIDER.",
"slide5Balance": "Credit balance",
"slide5BalanceValue": "$0.00",
"slide5PlanName": "Supporter",
"slide5PlanDesc": "One-time donation — choose any amount.",
"slide5AmountLabel": "Amount",
"slide5Checkout": "Continue to checkout",
"slide5Provider": "Lemon Squeezy",
"slide6Tag": "Internationalization",
"slide6Title": "i18n built-in",
"slide6Desc": "Add a locale JSON file, wire t() in templates and controllers — EN | PT switcher on day one.",
"slide6SampleKey1": "\"billing.title\"",
"slide6SampleKey2": "\"menu.billing\"",
"slide6SampleUiTitle": "Billing",
"slide6SampleUiSubtitle": "Manage plans and checkout",
```

**Add** feature cards after `featureSeoDesc`:
```json
"featureBillingTitle": "Payments included",
"featureBillingDesc": "Lemon Squeezy adapter, checkout, webhooks, and entitlements — swap providers via BILLING_PROVIDER.",
"featureI18nTitle": "i18n built-in",
"featureI18nDesc": "Locale JSON files, t() in templates and controllers, EN | PT switcher included.",
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/locales/en.json
git commit -m "feat: add welcome carousel and hero locale strings (en)"
```

---

### Task 4: Carousel template — dots, accessibility, slides 2–4 polish

**Files:**
- Modify: `frontend/src/templates/pages/welcome.hbs`

- [ ] **Step 1: Add shared slide visibility classes**

On **each** of the six slide wrapper divs (`absolute inset-0 transition-opacity duration-500`), use:

```html
:class="[
  welcomeController.carouselCurrent === N ? 'opacity-100' : 'opacity-0 pointer-events-none',
]"
:aria-hidden="welcomeController.carouselCurrent !== N"
```

Replace `N` with 0–5 per slide.

- [ ] **Step 2: Replace hardcoded dot buttons with x-for loop**

Replace the four static dot `<button>` elements with:

```html
<template x-for="(slide, i) in welcomeController.slides" :key="i">
    <button type="button"
            @click="welcomeController.goSlide(i); welcomeController.restartCarousel()"
            :class="welcomeController.carouselCurrent === i ? 'w-5 bg-indigo-600' : 'w-2 bg-gray-300 dark:bg-gray-600'"
            class="h-2 rounded-full transition-all"
            :aria-label="t('welcome.carouselSlideLabel', { n: i + 1 })"></button>
</template>
```

- [ ] **Step 3: Polish slide 2 — split layout + cookie badge**

Restructure slide 2 (`carouselCurrent === 1`) to match slide 1's `grid grid-cols-2` pattern:
- Left: login mockup (existing form UI) + small badge using `t('welcome.slide2CookieBadge')`
- Right: caption panel with `slide2Tag`, `slide2Title`, `slide2Desc`

- [ ] **Step 4: Polish slides 3 and 4 — add caption panels**

For Swagger (index 2) and Docker (index 3), add right-side caption panels using `slide3Tag/Title/Desc` and `slide4Tag/Title/Desc`. Keep existing left mockup content.

- [ ] **Step 5: Run tests (partial pass expected)**

Run: `cd frontend && npm run test -- welcome.test.js`  
Expected: dot loop test may PASS; billing/i18n slide id tests still FAIL.

---

### Task 5: New carousel slides — billing and i18n

**Files:**
- Modify: `frontend/src/templates/pages/welcome.hbs`

- [ ] **Step 1: Add slide 5 (billing) after slide 4**

```html
<div id="carousel-slide-billing"
     class="absolute inset-0 transition-opacity duration-500"
     :class="[
       welcomeController.carouselCurrent === 4 ? 'opacity-100' : 'opacity-0 pointer-events-none',
     ]"
     :aria-hidden="welcomeController.carouselCurrent !== 4">
    <div class="h-full flex flex-col">
        <div class="flex items-center gap-1.5 px-4 py-2.5 bg-slate-800 border-b border-slate-700">
            <span class="w-2.5 h-2.5 rounded-full bg-red-400" aria-hidden="true"></span>
            <span class="w-2.5 h-2.5 rounded-full bg-amber-400" aria-hidden="true"></span>
            <span class="w-2.5 h-2.5 rounded-full bg-emerald-400" aria-hidden="true"></span>
            <span class="ml-3 text-[11px] text-slate-400 font-mono">localhost:5173/app/billing</span>
        </div>
        <div class="flex-1 grid grid-cols-2">
            <div class="bg-slate-50 dark:bg-slate-900 p-5 space-y-3 overflow-hidden">
                <p class="text-xs text-slate-500 dark:text-slate-400">
                    <span x-text="t('welcome.slide5Balance')"></span>:
                    <span class="font-semibold text-slate-700 dark:text-slate-200" x-text="t('welcome.slide5BalanceValue')"></span>
                </p>
                <div class="rounded-lg border border-slate-200 dark:border-slate-700 p-3 bg-white dark:bg-slate-800">
                    <p class="text-sm font-semibold text-slate-800 dark:text-white" x-text="t('welcome.slide5PlanName')"></p>
                    <p class="text-xs text-slate-500 dark:text-slate-400 mt-1" x-text="t('welcome.slide5PlanDesc')"></p>
                    <p class="text-[10px] text-slate-400 mt-2" x-text="t('welcome.slide5AmountLabel')"></p>
                    <div class="mt-1 h-8 rounded border border-slate-200 dark:border-slate-600 bg-slate-50 dark:bg-slate-700"></div>
                    <div class="mt-2 h-8 rounded-md bg-indigo-600 flex items-center justify-center text-white text-xs font-semibold"
                         x-text="t('welcome.slide5Checkout')"></div>
                </div>
                <p class="text-[10px] text-slate-400" x-text="t('welcome.slide5Provider')"></p>
            </div>
            <div class="bg-gradient-to-br from-indigo-600 to-violet-700 p-6 flex flex-col justify-center text-white">
                <span class="text-xs uppercase tracking-widest text-indigo-200" x-text="t('welcome.slide5Tag')"></span>
                <p class="mt-1 text-xl sm:text-2xl font-bold leading-snug" x-text="t('welcome.slide5Title')"></p>
                <p class="mt-2 text-sm text-indigo-100" x-text="t('welcome.slide5Desc')"></p>
            </div>
        </div>
    </div>
</div>
```

- [ ] **Step 2: Add slide 6 (i18n)**

```html
<div id="carousel-slide-i18n"
     class="absolute inset-0 transition-opacity duration-500"
     :class="[
       welcomeController.carouselCurrent === 5 ? 'opacity-100' : 'opacity-0 pointer-events-none',
     ]"
     :aria-hidden="welcomeController.carouselCurrent !== 5">
    <div class="h-full flex flex-col">
        <div class="flex items-center gap-1.5 px-4 py-2.5 bg-slate-800 border-b border-slate-700">
            <span class="w-2.5 h-2.5 rounded-full bg-red-400" aria-hidden="true"></span>
            <span class="w-2.5 h-2.5 rounded-full bg-amber-400" aria-hidden="true"></span>
            <span class="w-2.5 h-2.5 rounded-full bg-emerald-400" aria-hidden="true"></span>
            <span class="ml-3 text-[11px] text-slate-400 font-mono">localhost:5173 · locale: pt-BR</span>
        </div>
        <div class="flex-1 grid grid-cols-2">
            <div class="bg-slate-900 p-5 font-mono text-[11px] sm:text-xs leading-relaxed text-slate-300 overflow-hidden">
                <p><span class="text-amber-300" x-text="t('welcome.slide6SampleKey1')"></span>: "Billing",</p>
                <p><span class="text-amber-300" x-text="t('welcome.slide6SampleKey2')"></span>: "Billing",</p>
                <p class="text-slate-500 mt-2">// pt-BR.json</p>
                <p><span class="text-amber-300" x-text="t('welcome.slide6SampleKey1')"></span>: "Cobrança",</p>
            </div>
            <div class="bg-gradient-to-br from-indigo-600 to-violet-700 p-6 flex flex-col justify-center text-white">
                <div class="flex gap-2 text-xs mb-4">
                    <span class="px-2 py-0.5 rounded bg-white/20">EN</span>
                    <span class="px-2 py-0.5 rounded bg-white/10 text-indigo-200">PT</span>
                </div>
                <p class="text-lg font-bold" x-text="t('welcome.slide6SampleUiTitle')"></p>
                <p class="text-sm text-indigo-100" x-text="t('welcome.slide6SampleUiSubtitle')"></p>
                <span class="mt-4 text-xs uppercase tracking-widest text-indigo-200" x-text="t('welcome.slide6Tag')"></span>
                <p class="mt-1 text-xl sm:text-2xl font-bold leading-snug" x-text="t('welcome.slide6Title')"></p>
                <p class="mt-2 text-sm text-indigo-100" x-text="t('welcome.slide6Desc')"></p>
            </div>
        </div>
    </div>
</div>
```

- [ ] **Step 3: Run tests**

Run: `cd frontend && npm run test -- welcome.test.js`  
Expected: all welcome tests PASS.

- [ ] **Step 4: Commit**

```bash
git add frontend/src/templates/pages/welcome.hbs
git commit -m "feat: expand welcome carousel with billing and i18n slides"
```

---

### Task 6: Hero trust badges and features grid

**Files:**
- Modify: `frontend/src/templates/pages/welcome.hbs`

- [ ] **Step 1: Add two trust badges in hero**

After the existing four `<span class="inline-flex items-center gap-1.5">` trust items, add:

```html
<span class="inline-flex items-center gap-1.5">
    <svg class="w-4 h-4 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
    <span x-text="t('welcome.trustBilling')"></span>
</span>
<span class="inline-flex items-center gap-1.5">
    <svg class="w-4 h-4 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
    <span x-text="t('welcome.trustI18n')"></span>
</span>
```

- [ ] **Step 2: Expand features grid to 5 cards**

Add two `<article>` blocks after the SEO card. Use a credit-card icon for billing and a globe/translate icon for i18n (match existing article structure with `featureBillingTitle/Desc` and `featureI18nTitle/Desc`).

On the **fifth** article, add `class="... lg:col-start-2"` so the last row centers on large screens (3+2 layout).

- [ ] **Step 3: Commit**

```bash
git add frontend/src/templates/pages/welcome.hbs
git commit -m "feat: sync welcome hero badges and features grid"
```

---

### Task 7: Portuguese locale mirror

**Files:**
- Modify: `frontend/src/locales/pt-BR.json`

- [ ] **Step 1: Mirror all new/updated welcome keys**

Update `heroSubtitle`, `trustAuth`, add `trustBilling`, `trustI18n`, replace dot labels with `carouselSlideLabel`, add all `slide2*`–`slide6*` keys and `featureBilling*` / `featureI18n*` with natural Brazilian Portuguese.

Example `heroSubtitle`:
```json
"heroSubtitle": "API REST Flask, SPA Alpine.js, cookie auth + OAuth, billing, i18n, modos SEO e Docker — um starter pronto para produção para você focar na sua ideia, não em boilerplate.",
```

Example `trustAuth`:
```json
"trustAuth": "Cookie auth + OAuth",
```

Example `carouselSlideLabel`:
```json
"carouselSlideLabel": "Ir para slide {n}",
```

Translate remaining new keys consistently with existing pt-BR tone in the file.

- [ ] **Step 2: Run full frontend tests**

Run: `cd frontend && npm run test`  
Expected: PASS (including i18n tests — ensure no missing keys break resolution).

- [ ] **Step 3: Commit**

```bash
git add frontend/src/locales/pt-BR.json
git commit -m "feat: add welcome carousel locale strings (pt-BR)"
```

---

### Task 8: Build verification

**Files:** (none — verification only)

- [ ] **Step 1: Production build**

Run: `cd frontend && npm run build`  
Expected: PASS, no template errors.

- [ ] **Step 2: Manual smoke check (optional)**

Run dev servers and open `http://localhost:5173`:
- All 6 slides visible via dots/prev/next
- EN | PT toggles new strings
- Single h1 in page source

- [ ] **Step 3: Final commit if any fixups needed**

---

## Spec coverage checklist

| Spec requirement | Task |
|------------------|------|
| 6 slides (billing + i18n) | Tasks 2, 5 |
| Unified split layout | Tasks 4, 5 |
| Slide 2 cookie auth refresh | Task 4 |
| Data-driven dots | Tasks 2, 4 |
| Reduced motion | Task 2 |
| Hero subtitle + trust badges | Tasks 3, 6 |
| 5 feature cards | Tasks 3, 6 |
| Locale keys EN + pt-BR | Tasks 3, 7 |
| Accessibility (aria-hidden, pointer-events) | Task 4 |
| Vitest coverage | Tasks 1, 5 |
