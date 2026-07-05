/**
 * Central fetch wrapper: credentials, CSRF double-submit, JSON helpers.
 * @module api
 */

let csrfToken = null;

/**
 * Fetch and cache a CSRF token (sets readable cookie server-side).
 * @returns {Promise<void>}
 */
export async function initCsrf() {
    const response = await fetch('/api/csrf', { credentials: 'include' });
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
 * Fetch with session cookies and CSRF header on mutating methods.
 * @param {string} url
 * @param {RequestInit} [options]
 * @returns {Promise<Response>}
 */
export async function apiFetch(url, options = {}) {
    const method = (options.method || 'GET').toUpperCase();
    const headers = { ...(options.headers || {}) };

    if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(method)) {
        if (!csrfToken) {
            await initCsrf();
        }
        if (csrfToken) {
            headers[CSRF_HEADER_NAME] = csrfToken;
        }
    }

    if (options.body && !headers['Content-Type']) {
        headers['Content-Type'] = 'application/json';
    }

    return fetch(url, {
        ...options,
        headers,
        credentials: 'include',
    });
}

/** Header name sent with CSRF token (for tests). */
export const CSRF_HEADER_NAME = 'X-CSRF-Token';

/**
 * Read current session state from the API.
 * @returns {Promise<{authenticated: boolean, username?: string}>}
 */
export async function fetchSession() {
    const response = await apiFetch('/api/auth/session');
    if (!response.ok) {
        return { authenticated: false };
    }
    return response.json();
}
