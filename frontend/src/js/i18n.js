/**
 * Lightweight i18n: locale resolution, JSON lookups, and interpolation.
 * @module i18n
 */
import en from '../locales/en.json';
import ptBR from '../locales/pt-BR.json';

/** @type {string[]} */
export const SUPPORTED_LOCALES = ['en', 'pt-BR'];

const LOCALE_STORAGE_KEY = 'locale';

/** @type {Record<string, object>} */
const catalogs = {
    en,
    'pt-BR': ptBR,
};

/** @type {string} */
let activeLocale = 'en';

/**
 * Map a BCP 47 language tag to a supported locale.
 * @param {string} [tag='en'] - Browser or explicit language tag.
 * @returns {'en' | 'pt-BR'}
 */
export function resolveLocale(tag = 'en') {
    const normalized = (tag || 'en').toLowerCase();
    if (normalized === 'pt-br' || normalized === 'pt' || normalized.startsWith('pt-')) {
        return 'pt-BR';
    }
    return 'en';
}

/** @returns {string} Active locale code. */
export function getLocale() {
    return activeLocale;
}

/**
 * @param {string} locale
 */
function applyHtmlLang(locale) {
    document.documentElement.lang = locale === 'pt-BR' ? 'pt-BR' : 'en';
}

/**
 * Initialize locale from localStorage or navigator; set html lang.
 * @returns {string} Resolved locale.
 */
export function initLocale() {
    const stored = localStorage.getItem(LOCALE_STORAGE_KEY);
    if (stored && SUPPORTED_LOCALES.includes(stored)) {
        activeLocale = stored;
    } else {
        activeLocale = resolveLocale(typeof navigator !== 'undefined' ? navigator.language : 'en');
    }
    applyHtmlLang(activeLocale);
    return activeLocale;
}

/**
 * Switch active locale and persist preference.
 * @param {string} locale - ``en`` or ``pt-BR``.
 */
export function setLocale(locale) {
    if (!SUPPORTED_LOCALES.includes(locale)) {
        return;
    }
    activeLocale = locale;
    localStorage.setItem(LOCALE_STORAGE_KEY, locale);
    applyHtmlLang(locale);
    window.dispatchEvent(new CustomEvent('localechange', { detail: { locale } }));
}

/**
 * @param {object} obj
 * @param {string} keyPath
 * @returns {string|undefined}
 */
function lookup(obj, keyPath) {
    return keyPath.split('.').reduce((acc, part) => {
        if (acc && typeof acc === 'object' && part in acc) {
            return acc[part];
        }
        return undefined;
    }, obj);
}

/**
 * Translate a dot-notation key for the active locale.
 * @param {string} key - e.g. ``login.title``.
 * @param {Record<string, string|number>} [params] - Interpolation placeholders.
 * @returns {string}
 */
export function t(key, params = {}) {
    let value = lookup(catalogs[activeLocale], key);
    if (value === undefined && activeLocale !== 'en') {
        value = lookup(catalogs.en, key);
    }
    if (typeof value !== 'string') {
        return key;
    }
    return Object.entries(params).reduce(
        (str, [name, val]) => str.replaceAll(`{${name}}`, String(val)),
        value,
    );
}

/**
 * Map an API error code to a localized message.
 * @param {string} code - API error code.
 * @returns {string}
 */
export function tError(code) {
    const msg = lookup(catalogs[activeLocale], `errors.${code}`)
        ?? lookup(catalogs.en, `errors.${code}`);
    if (typeof msg === 'string') {
        return msg;
    }
    return t('errors.UNKNOWN_ERROR');
}
