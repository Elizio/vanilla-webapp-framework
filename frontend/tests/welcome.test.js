import { describe, it, expect } from 'vitest';
import { pages } from '../src/js/pages.js';
import { welcomeController } from '../src/js/controllers/welcome.js';
import welcomeTpl from '../src/templates/pages/welcome.hbs?raw';

describe('welcome page', () => {
    it('is registered with public SEO visibility', () => {
        expect(pages.welcome).toBeDefined();
        expect(pages.welcome.seo.visibility).toBe('public');
    });

    it('template contains exactly one h1 for SEO', () => {
        const h1Matches = welcomeTpl.match(/<h1[\s>]/g);
        expect(h1Matches).toHaveLength(1);
    });

    it('has a welcomeController with copyCloneCommand', () => {
        expect(typeof welcomeController.copyCloneCommand).toBe('function');
    });

    it('defines six carousel slides', () => {
        expect(welcomeController.slides).toHaveLength(6);
    });

    it('template includes billing and i18n carousel slides', () => {
        expect(welcomeTpl).toContain('id="carousel-slide-billing"');
        expect(welcomeTpl).toContain('id="carousel-slide-i18n"');
    });

    it('uses dynamic carousel dot loop', () => {
        expect(welcomeTpl).toContain('welcomeController.slides');
        expect(welcomeTpl).toContain('carouselSlideLabel');
    });
});
