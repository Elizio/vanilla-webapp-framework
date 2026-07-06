import { describe, it, expect, beforeEach } from 'vitest';
import {
    resolveLocale,
    t,
    tError,
    getLocale,
    setLocale,
    initLocale,
    SUPPORTED_LOCALES,
} from '../src/js/i18n.js';

describe('resolveLocale', () => {
    it('maps Portuguese variants to pt-BR', () => {
        expect(resolveLocale('pt-BR')).toBe('pt-BR');
        expect(resolveLocale('pt')).toBe('pt-BR');
        expect(resolveLocale('pt-PT')).toBe('pt-BR');
    });

    it('maps unknown tags to en', () => {
        expect(resolveLocale('en')).toBe('en');
        expect(resolveLocale('en-US')).toBe('en');
        expect(resolveLocale('fr')).toBe('en');
    });
});

describe('t', () => {
    beforeEach(() => {
        setLocale('en');
    });

    it('looks up nested keys', () => {
        expect(t('login.title')).toBe('Vanilla WebApp Demo');
    });

    it('interpolates params', () => {
        expect(t('errors.OAUTH_NOT_CONFIGURED', { provider: 'Google' }))
            .toContain('Google');
    });

    it('falls back to en for missing pt-BR key', () => {
        setLocale('pt-BR');
        expect(t('login.title')).toBeTruthy();
    });

    it('returns key for unknown lookup', () => {
        expect(t('does.not.exist')).toBe('does.not.exist');
    });
});

describe('tError', () => {
    beforeEach(() => setLocale('en'));

    it('maps known API codes', () => {
        expect(tError('INVALID_CREDENTIALS')).toBe('Invalid credentials');
    });

    it('falls back for unknown codes', () => {
        expect(tError('MADE_UP_CODE')).toBe('An unexpected error occurred');
    });
});

describe('locale persistence', () => {
    beforeEach(() => {
        localStorage.clear();
        document.documentElement.lang = 'en';
    });

    it('initLocale reads localStorage override', () => {
        localStorage.setItem('locale', 'pt-BR');
        expect(initLocale()).toBe('pt-BR');
        expect(document.documentElement.lang).toBe('pt-BR');
    });

    it('setLocale persists and updates html lang', () => {
        setLocale('pt-BR');
        expect(getLocale()).toBe('pt-BR');
        expect(localStorage.getItem('locale')).toBe('pt-BR');
        expect(document.documentElement.lang).toBe('pt-BR');
    });
});

describe('SUPPORTED_LOCALES', () => {
    it('includes en and pt-BR', () => {
        expect(SUPPORTED_LOCALES).toContain('en');
        expect(SUPPORTED_LOCALES).toContain('pt-BR');
    });
});
