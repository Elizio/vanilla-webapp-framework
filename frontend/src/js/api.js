/**
 * Central fetch wrapper: credentials, CSRF double-submit, refresh-on-401.
 * @module api
 */
import { stripBase, withBase } from './basepath.js';

let csrfToken = null;
/** @type {Promise<boolean> | null} */
let inFlightRefresh = null;

const FRESH_CSRF_PATHS = new Set(['/api/login', '/api/register']);

/** Event name dispatched when refresh fails after a 401. */
export const AUTH_EXPIRED_EVENT = 'auth:expired';

/** Web Lock name shared across tabs when `navigator.locks` exists. */
export const AUTH_REFRESH_LOCK = 'vwf-auth-refresh';

const NO_REFRESH_PATHS = new Set([
    '/api/auth/refresh',
    '/api/auth/logout',
    '/api/auth/logout-all',
    '/api/logout',
    '/api/login',
    '/api/register',
    '/api/auth/verify-email',
    '/api/auth/verify-email/resend',
    '/api/auth/password/forgot',
    '/api/auth/password/reset',
    '/api/auth/capabilities',
]);

/**
 * Fetch and cache a CSRF token from the JSON body (cookie is HttpOnly).
 * @returns {Promise<void>}
 */
export async function initCsrf() {
    const response = await fetch(withBase('/api/csrf'), {
        credentials: 'include',
    });
    if (response.ok) {
        const data = await response.json();
        csrfToken = data.csrf_token;
    }
}

/**
 * Reset cached CSRF token (e.g. after logout).
 */
export function resetCsrf() {
    csrfToken = null;
}

/**
 * Reset in-flight refresh state (tests).
 */
export function resetAuthRefresh() {
    inFlightRefresh = null;
}

/**
 * Drop the in-memory CSRF token after a bfcache restore.
 * @param {PageTransitionEvent | Event} event
 */
function onPageShow(event) {
    if ('persisted' in event && event.persisted) {
        csrfToken = null;
    }
}

let pageShowBound = false;

/**
 * Listen for bfcache restores so a stale in-memory CSRF token is dropped.
 */
export function bindCsrfPageShow() {
    if (typeof window === 'undefined' || pageShowBound) {
        return;
    }
    window.addEventListener('pageshow', onPageShow);
    pageShowBound = true;
}

/**
 * Remove the bfcache pageshow listener (SPA teardown).
 */
export function unbindCsrfPageShow() {
    if (typeof window === 'undefined' || !pageShowBound) {
        return;
    }
    window.removeEventListener('pageshow', onPageShow);
    pageShowBound = false;
}

bindCsrfPageShow();

/**
 * @param {string} url
 * @returns {string}
 */
function requestPath(url) {
    try {
        const parsed = new URL(url, 'http://localhost');
        return stripBase(parsed.pathname);
    } catch {
        return url;
    }
}

/**
 * @param {string} url
 * @returns {boolean}
 */
function shouldSkipRefresh(url) {
    return NO_REFRESH_PATHS.has(requestPath(url));
}

/**
 * POST /api/auth/refresh once. Shared in-tab promise; Web Locks across tabs.
 * @returns {Promise<boolean>}
 */
export async function refreshAccessToken() {
    if (inFlightRefresh) {
        return inFlightRefresh;
    }

    const execute = () =>
        apiFetch('/api/auth/refresh', {
            method: 'POST',
            skipRefresh: true,
        }).then((response) => response.ok);

    const run = () => {
        const locks = globalThis.navigator?.locks;
        if (locks && typeof locks.request === 'function') {
            return locks.request(AUTH_REFRESH_LOCK, execute);
        }
        return execute();
    };

    inFlightRefresh = run().finally(() => {
        inFlightRefresh = null;
    });
    return inFlightRefresh;
}

/**
 * Read an error ``code`` without consuming the original response body.
 * @param {Response} response
 * @returns {Promise<string | undefined>}
 */
async function readErrorCode(response) {
    try {
        const source =
            typeof response.clone === 'function' ? response.clone() : response;
        const data = await source.json();
        return data && data.code;
    } catch {
        return undefined;
    }
}

/**
 * Fetch with session cookies and CSRF header on mutating methods.
 * On 403 CSRF_INVALID, refetch GET /api/csrf (via withBase) and retry once.
 * On 401 from a non-auth route, refresh once and retry the original request.
 * Login and register always fetch a fresh CSRF token first.
 * @param {string} url
 * @param {RequestInit & { skipRefresh?: boolean, skipCsrfRetry?: boolean }} [options]
 * @returns {Promise<Response>}
 */
export async function apiFetch(url, options = {}) {
    const {
        skipRefresh = false,
        skipCsrfRetry = false,
        ...fetchOptions
    } = options;
    const method = (fetchOptions.method || 'GET').toUpperCase();
    const headers = { ...(fetchOptions.headers || {}) };
    const fullUrl = url.startsWith('/') ? withBase(url) : url;
    const path = requestPath(fullUrl);
    const mutating = ['POST', 'PUT', 'PATCH', 'DELETE'].includes(method);

    if (mutating) {
        if (!csrfToken || FRESH_CSRF_PATHS.has(path)) {
            await initCsrf();
        }
        if (csrfToken) {
            headers[CSRF_HEADER_NAME] = csrfToken;
        }
    }

    if (fetchOptions.body && !headers['Content-Type']) {
        headers['Content-Type'] = 'application/json';
    }

    const response = await fetch(fullUrl, {
        ...fetchOptions,
        headers,
        credentials: 'include',
    });

    if (
        mutating &&
        response.status === 403 &&
        !skipCsrfRetry &&
        (await readErrorCode(response)) === 'CSRF_INVALID'
    ) {
        csrfToken = null;
        await initCsrf();
        return apiFetch(url, { ...options, skipCsrfRetry: true });
    }

    if (
        response.status === 401 &&
        !skipRefresh &&
        !shouldSkipRefresh(fullUrl)
    ) {
        const refreshed = await refreshAccessToken();
        if (!refreshed) {
            window.dispatchEvent(new Event(AUTH_EXPIRED_EVENT));
            return response;
        }
        return apiFetch(url, { ...options, skipRefresh: true });
    }

    return response;
}

/** Header name sent with CSRF token (for tests). */
export const CSRF_HEADER_NAME = 'X-CSRF-Token';

/**
 * Read current session state from the API.
 * When the access cookie has expired, try one refresh so a reload after
 * 15 minutes stays logged in. A failed opportunistic refresh does not
 * dispatch ``auth:expired`` (logged-out visitors would always see login).
 * @returns {Promise<{authenticated: boolean, username?: string}>}
 */
export async function fetchSession() {
    const response = await apiFetch('/api/auth/session', {
        skipRefresh: true,
    });
    if (!response.ok) {
        return { authenticated: false };
    }
    const data = await response.json();
    if (data.authenticated === true) {
        return data;
    }
    const refreshed = await refreshAccessToken();
    if (!refreshed) {
        return { authenticated: false };
    }
    const retry = await apiFetch('/api/auth/session', { skipRefresh: true });
    if (!retry.ok) {
        return { authenticated: false };
    }
    return retry.json();
}
