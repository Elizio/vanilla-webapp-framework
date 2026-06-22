import { describe, it, expect } from 'vitest';
import { pages } from '../src/js/pages.js';
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
        expect(typeof pages.welcome.controller.copyCloneCommand).toBe('function');
    });
});
