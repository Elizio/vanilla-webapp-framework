/**
 * Central fetch wrapper: credentials, CSRF double-submit, refresh-on-401.
 * @module api
 */
import { stripBase, withBase } from './basepath.js';

let csrfToken = null;
/** @type {Promise<boolean> | null} */
let inFlightRefresh = null;

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
 * Fetch with session cookies and CSRF header on mutating methods.
 * On 401 from a non-auth route, refresh once and retry the original request.
 * @param {string} url
 * @param {RequestInit & { skipRefresh?: boolean }} [options]
 * @returns {Promise<Response>}
 */
export async function apiFetch(url, options = {}) {
    const { skipRefresh = false, ...fetchOptions } = options;
    const method = (fetchOptions.method || 'GET').toUpperCase();
    const headers = { ...(fetchOptions.headers || {}) };

    if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(method)) {
        if (!csrfToken) {
            await initCsrf();
        }
        if (csrfToken) {
            headers[CSRF_HEADER_NAME] = csrfToken;
        }
    }

    if (fetchOptions.body && !headers['Content-Type']) {
        headers['Content-Type'] = 'application/json';
    }

    const fullUrl = url.startsWith('/') ? withBase(url) : url;
    const response = await fetch(fullUrl, {
        ...fetchOptions,
        headers,
        credentials: 'include',
    });

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
