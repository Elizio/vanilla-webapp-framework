import { describe, it, expect, beforeEach } from 'vitest';
import { resolveVisibility, applySeo } from '../src/js/seo.js';

describe('resolveVisibility', () => {
    it('returns explicit visibility when set', () => {
        expect(resolveVisibility({ visibility: 'public' }, 'auth-first')).toBe('public');
        expect(resolveVisibility({ visibility: 'auth' }, 'public-first')).toBe('auth');
    });

    it('inherits auth-first default as app', () => {
        expect(resolveVisibility({}, 'auth-first')).toBe('app');
    });

    it('inherits public-first default as public', () => {
        expect(resolveVisibility({}, 'public-first')).toBe('public');
    });

    it('falls back to auth-first for invalid mode', () => {
        expect(resolveVisibility({}, 'invalid')).toBe('app');
    });
});

describe('applySeo', () => {
    beforeEach(() => {
        document.head.innerHTML = '';
        document.title = '';
    });

    it('sets indexable metadata for public pages', () => {
        applySeo(
            {
                visibility: 'public',
                title: 'Public Page',
                description: 'Public description',
            },
            'auth-first',
        );

        expect(document.title).toBe('Public Page');
        expect(document.querySelector('meta[name="description"]').content).toBe('Public description');
        expect(document.querySelector('meta[name="robots"]').content).toBe('index, follow');
        expect(document.querySelector('link[rel="canonical"]').href).toContain('http');
    });

    it('sets noindex for app pages', () => {
        applySeo(
            {
                visibility: 'app',
                title: 'App Page',
            },
            'public-first',
        );

        expect(document.title).toBe('App Page');
        expect(document.querySelector('meta[name="robots"]').content).toBe('noindex, nofollow');
        expect(document.querySelector('link[rel="canonical"]')).toBeNull();
    });

    it('inherits public-first mode as indexable when visibility omitted', () => {
        applySeo(
            {
                title: 'Inherited Public',
                description: 'Inherited description',
            },
            'public-first',
        );

        expect(document.querySelector('meta[name="robots"]').content).toBe('index, follow');
    });

    it('inherits auth-first mode as noindex when visibility omitted', () => {
        applySeo(
            {
                title: 'Inherited App',
            },
            'auth-first',
        );

        expect(document.querySelector('meta[name="robots"]').content).toBe('noindex, nofollow');
    });
});
