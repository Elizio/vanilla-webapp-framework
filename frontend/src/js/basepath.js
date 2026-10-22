/**
 * Base path utilities for subpath deployments.
 * @module basepath
 */

/**
 * The configured base path from Vite build config (default '/').
 * Trailing slash is normalized away for consistent joining.
 * @type {string}
 */
export const BASE_PATH = (import.meta.env.BASE_URL || '/').replace(/\/$/, '');

/**
 * Prefix a path with the configured base path.
 * @param {string} path - Absolute path starting with '/'.
 * @returns {string} Path prefixed with BASE_PATH.
 */
export function withBase(path) {
    if (!path.startsWith('/')) {
        console.warn(`withBase() expects absolute paths starting with '/', got: ${path}`);
    }
    return BASE_PATH === '' ? path : BASE_PATH + path;
}

/**
 * Strip the configured base path from a pathname (e.g. from window.location.pathname).
 * @param {string} pathname - Full pathname including base.
 * @returns {string} Pathname with base removed.
 */
export function stripBase(pathname) {
    if (BASE_PATH === '' || !pathname.startsWith(BASE_PATH)) {
        return pathname;
    }
    return pathname.slice(BASE_PATH.length) || '/';
}
