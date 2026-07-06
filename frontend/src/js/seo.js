/**
 * Client-side SEO metadata for SPA pages.
 * @module seo
 */
import { t } from './i18n.js';

/** @type {'auth-first' | 'public-first'} Fork SEO mode from build env. */
export const SEO_MODE = import.meta.env.VITE_SEO_MODE || 'auth-first';

const VALID_MODES = new Set(['auth-first', 'public-first']);
const VALID_VISIBILITIES = new Set(['public', 'app', 'auth']);

/**
 * Resolve effective page visibility from explicit registry setting or fork SEO_MODE.
 * @param {object} [seo] - Page ``seo`` block from ``pages.js``.
 * @param {string} [mode=SEO_MODE] - Fork ``SEO_MODE`` (``auth-first`` | ``public-first``).
 * @returns {'public' | 'app' | 'auth'} Effective visibility for the page.
 */
export function resolveVisibility(seo = {}, mode = SEO_MODE) {
    const safeMode = VALID_MODES.has(mode) ? mode : 'auth-first';

    if (seo.visibility && VALID_VISIBILITIES.has(seo.visibility)) {
        return seo.visibility;
    }

    return safeMode === 'public-first' ? 'public' : 'app';
}

/**
 * @param {'public' | 'app' | 'auth'} visibility
 * @returns {boolean}
 */
function isIndexable(visibility) {
    return visibility === 'public';
}

/**
 * @param {string} name
 * @param {string} content
 */
function upsertMeta(name, content) {
    if (content == null || content === '') {
        return;
    }

    let element = document.querySelector(`meta[name="${name}"]`);
    if (!element) {
        element = document.createElement('meta');
        element.setAttribute('name', name);
        document.head.appendChild(element);
    }
    element.setAttribute('content', content);
}

/**
 * @param {string} rel
 * @param {string} href
 */
function upsertLink(rel, href) {
    if (!href) {
        return;
    }

    let element = document.querySelector(`link[rel="${rel}"]`);
    if (!element) {
        element = document.createElement('link');
        element.setAttribute('rel', rel);
        document.head.appendChild(element);
    }
    element.setAttribute('href', href);
}

/**
 * Apply page SEO metadata to ``document.head``.
 * @param {object} [seo] - Page ``seo`` block from ``pages.js``.
 * @param {string} [mode=SEO_MODE] - Fork ``SEO_MODE`` (``auth-first`` | ``public-first``).
 */
export function applySeo(seo = {}, mode = SEO_MODE) {
    const visibility = resolveVisibility(seo, mode);
    const indexable = isIndexable(visibility);

    const title = seo.titleKey ? t(seo.titleKey) : seo.title;
    const description = seo.descriptionKey ? t(seo.descriptionKey) : seo.description;

    if (title) {
        document.title = title;
    }

    if (description) {
        upsertMeta('description', description);
    }

    upsertMeta('robots', indexable ? 'index, follow' : 'noindex, nofollow');

    if (seo.canonical) {
        upsertLink('canonical', seo.canonical);
    } else if (indexable) {
        upsertLink('canonical', window.location.href.split('#')[0]);
    }
}
