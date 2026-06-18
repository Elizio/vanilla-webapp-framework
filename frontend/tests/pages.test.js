import { describe, it, expect } from 'vitest';
import { pages } from '../src/js/pages.js';

const expectedKeys = ['menu', 'login', 'user_registry', 'landingpage', 'testpage'];

describe('pages registry', () => {
  it('contains all expected page keys', () => {
    expectedKeys.forEach((key) => {
      expect(pages[key]).toBeDefined();
    });
  });

  it('each page has a template string and controller object', () => {
    expectedKeys.forEach((key) => {
      expect(typeof pages[key].template).toBe('string');
      expect(pages[key].template.length).toBeGreaterThan(0);
      expect(typeof pages[key].controller).toBe('object');
    });
  });
});
