import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import {
    AUTH_EXPIRED_EVENT,
    AUTH_REFRESH_LOCK,
    apiFetch,
    fetchSession,
    refreshAccessToken,
    resetAuthRefresh,
    resetCsrf,
} from '../src/js/api.js';

function jsonResponse(body, { status = 200 } = {}) {
    return {
        ok: status >= 200 && status < 300,
        status,
        json: async () => body,
    };
}

describe('apiFetch refresh-on-401', () => {
    beforeEach(() => {
        resetCsrf();
        resetAuthRefresh();
        vi.stubGlobal(
            'fetch',
            vi.fn(async () => {
                throw new Error('Unmocked fetch');
            }),
        );
    });

    afterEach(() => {
        vi.unstubAllGlobals();
        resetCsrf();
        resetAuthRefresh();
    });

    it('retries the original request once after a successful refresh', async () => {
        fetch
            .mockResolvedValueOnce(
                jsonResponse({ code: 'TOKEN_EXPIRED' }, { status: 401 }),
            )
            .mockResolvedValueOnce(jsonResponse({ csrf_token: 'csrf-1' }))
            .mockResolvedValueOnce(jsonResponse({ authenticated: true }))
            .mockResolvedValueOnce(jsonResponse({ message: 'ok' }));

        const response = await apiFetch('/api/data');
        expect(response.status).toBe(200);
        expect(await response.json()).toEqual({ message: 'ok' });

        const urls = fetch.mock.calls.map(([url]) => url);
        expect(urls.filter((url) => url.endsWith('/api/data'))).toHaveLength(2);
        expect(
            urls.filter((url) => url.endsWith('/api/auth/refresh')),
        ).toHaveLength(1);
    });

    it('shares one in-flight refresh across parallel 401s', async () => {
        fetch
            .mockResolvedValueOnce(
                jsonResponse({ code: 'TOKEN_EXPIRED' }, { status: 401 }),
            )
            .mockResolvedValueOnce(
                jsonResponse({ code: 'TOKEN_EXPIRED' }, { status: 401 }),
            )
            .mockResolvedValueOnce(jsonResponse({ csrf_token: 'csrf-1' }))
            .mockResolvedValueOnce(jsonResponse({ authenticated: true }))
            .mockResolvedValueOnce(jsonResponse({ a: 1 }))
            .mockResolvedValueOnce(jsonResponse({ b: 2 }));

        const [first, second] = await Promise.all([
            apiFetch('/api/data'),
            apiFetch('/api/public'),
        ]);
        expect(first.status).toBe(200);
        expect(second.status).toBe(200);

        const urls = fetch.mock.calls.map(([url]) => url);
        expect(
            urls.filter((url) => url.endsWith('/api/auth/refresh')),
        ).toHaveLength(1);
    });

    it('dispatches auth:expired when refresh fails', async () => {
        const expired = vi.fn();
        window.addEventListener(AUTH_EXPIRED_EVENT, expired);

        fetch
            .mockResolvedValueOnce(
                jsonResponse({ code: 'TOKEN_EXPIRED' }, { status: 401 }),
            )
            .mockResolvedValueOnce(jsonResponse({ csrf_token: 'csrf-1' }))
            .mockResolvedValueOnce(
                jsonResponse({ code: 'INVALID_TOKEN' }, { status: 401 }),
            );

        const response = await apiFetch('/api/data');
        expect(response.status).toBe(401);
        expect(expired).toHaveBeenCalledTimes(1);

        const urls = fetch.mock.calls.map(([url]) => url);
        expect(urls.filter((url) => url.endsWith('/api/data'))).toHaveLength(1);
        window.removeEventListener(AUTH_EXPIRED_EVENT, expired);
    });

    it('does not refresh auth routes', async () => {
        fetch
            .mockResolvedValueOnce(jsonResponse({ csrf_token: 'csrf-1' }))
            .mockResolvedValueOnce(
                jsonResponse({ code: 'INVALID_CREDENTIALS' }, { status: 401 }),
            );

        const response = await apiFetch('/api/login', {
            method: 'POST',
            body: JSON.stringify({ username: 'a', password: 'b' }),
        });
        expect(response.status).toBe(401);
        const urls = fetch.mock.calls.map(([url]) => url);
        expect(urls.some((url) => url.endsWith('/api/auth/refresh'))).toBe(
            false,
        );
    });

    it('does not loop when the retried request is still 401', async () => {
        fetch
            .mockResolvedValueOnce(
                jsonResponse({ code: 'TOKEN_EXPIRED' }, { status: 401 }),
            )
            .mockResolvedValueOnce(jsonResponse({ csrf_token: 'csrf-1' }))
            .mockResolvedValueOnce(jsonResponse({ authenticated: true }))
            .mockResolvedValueOnce(
                jsonResponse({ code: 'INVALID_TOKEN' }, { status: 401 }),
            );

        const expired = vi.fn();
        window.addEventListener(AUTH_EXPIRED_EVENT, expired);
        const response = await apiFetch('/api/data');
        expect(response.status).toBe(401);
        expect(expired).not.toHaveBeenCalled();
        const urls = fetch.mock.calls.map(([url]) => url);
        expect(
            urls.filter((url) => url.endsWith('/api/auth/refresh')),
        ).toHaveLength(1);
        expect(urls.filter((url) => url.endsWith('/api/data'))).toHaveLength(2);
        window.removeEventListener(AUTH_EXPIRED_EVENT, expired);
    });

    it('uses navigator.locks when available', async () => {
        const request = vi.fn(async (_name, callback) => callback());
        Object.defineProperty(navigator, 'locks', {
            configurable: true,
            value: { request },
        });

        fetch
            .mockResolvedValueOnce(jsonResponse({ csrf_token: 'csrf-1' }))
            .mockResolvedValueOnce(jsonResponse({ authenticated: true }));

        await refreshAccessToken();
        expect(request).toHaveBeenCalledWith(
            AUTH_REFRESH_LOCK,
            expect.any(Function),
        );
    });
});

describe('fetchSession', () => {
    beforeEach(() => {
        resetCsrf();
        resetAuthRefresh();
        vi.stubGlobal(
            'fetch',
            vi.fn(async () => {
                throw new Error('Unmocked fetch');
            }),
        );
    });

    afterEach(() => {
        vi.unstubAllGlobals();
        resetCsrf();
        resetAuthRefresh();
    });

    it('tries refresh once when the session is unauthenticated', async () => {
        fetch
            .mockResolvedValueOnce(jsonResponse({ authenticated: false }))
            .mockResolvedValueOnce(jsonResponse({ csrf_token: 'csrf-1' }))
            .mockResolvedValueOnce(jsonResponse({ authenticated: true }))
            .mockResolvedValueOnce(
                jsonResponse({ authenticated: true, username: 'ada' }),
            );

        const session = await fetchSession();
        expect(session).toEqual({ authenticated: true, username: 'ada' });
        const urls = fetch.mock.calls.map(([url]) => url);
        expect(
            urls.filter((url) => url.endsWith('/api/auth/refresh')),
        ).toHaveLength(1);
    });

    it('does not dispatch auth:expired when opportunistic refresh fails', async () => {
        const expired = vi.fn();
        window.addEventListener(AUTH_EXPIRED_EVENT, expired);
        fetch
            .mockResolvedValueOnce(jsonResponse({ authenticated: false }))
            .mockResolvedValueOnce(jsonResponse({ csrf_token: 'csrf-1' }))
            .mockResolvedValueOnce(
                jsonResponse({ code: 'INVALID_TOKEN' }, { status: 401 }),
            );

        const session = await fetchSession();
        expect(session).toEqual({ authenticated: false });
        expect(expired).not.toHaveBeenCalled();
        window.removeEventListener(AUTH_EXPIRED_EVENT, expired);
    });
});
