import { vi } from 'vitest';

vi.stubGlobal('fetch', vi.fn(async (input) => {
    const url = typeof input === 'string' ? input : input.url;
    if (url.endsWith('/api/auth/providers')) {
        return {
            ok: true,
            json: async () => [],
        };
    }
    throw new Error(`Unmocked fetch in tests: ${url}`);
}));

Object.defineProperty(window, 'matchMedia', {
    writable: true,
    value: vi.fn().mockImplementation((query) => ({
        matches: false,
        media: query,
        onchange: null,
        addListener: vi.fn(),
        removeListener: vi.fn(),
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
        dispatchEvent: vi.fn(),
    })),
});
