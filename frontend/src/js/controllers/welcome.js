/** Public welcome page controller: clone command, clipboard copy, and carousel. */

const CAROUSEL_INTERVAL_MS = 5000;

/**
 * Welcome page controller for the public marketing landing.
 * Bound in templates as ``welcomeController.*`` (root scope, not ``currentPage``).
 *
 * Note: this controller must NOT store a reference to the app object as a property,
 * because Alpine's ``initInterceptors`` recursively walks component data and a
 * circular reference (controller → app → controller) causes a stack overflow.
 */
export const welcomeController = {
    cloneCommand: 'git clone https://github.com/you/vanilla-webapp-framework.git',
    copyFeedback: '',
    carouselCurrent: 0,
    carouselTimer: null,

    slides: [
        { tagKey: 'welcome.slide1Tag', titleKey: 'welcome.slide1Title', descKey: 'welcome.slide1Desc' },
        { tagKey: 'welcome.slide2Tag', titleKey: 'welcome.slide2Title', descKey: 'welcome.slide2Desc' },
        { tagKey: 'welcome.slide3Tag', titleKey: 'welcome.slide3Title', descKey: 'welcome.slide3Desc' },
        { tagKey: 'welcome.slide4Tag', titleKey: 'welcome.slide4Title', descKey: 'welcome.slide4Desc' },
        { tagKey: 'welcome.slide5Tag', titleKey: 'welcome.slide5Title', descKey: 'welcome.slide5Desc' },
        { tagKey: 'welcome.slide6Tag', titleKey: 'welcome.slide6Title', descKey: 'welcome.slide6Desc' },
    ],

    /** Reset transient state. */
    init() {
        this.copyFeedback = '';
    },

    /** Whether carousel auto-advance should run. */
    shouldAutoAdvance() {
        return !window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    },

    /** Start or restart the carousel auto-advance timer. */
    initCarousel() {
        this.stopCarousel();
        this.carouselCurrent = 0;
        if (this.shouldAutoAdvance()) {
            this.carouselTimer = setInterval(() => {
                this.goSlide(this.carouselCurrent + 1);
            }, CAROUSEL_INTERVAL_MS);
        }
    },

    /** Clear the carousel auto-advance timer. */
    stopCarousel() {
        if (this.carouselTimer) {
            clearInterval(this.carouselTimer);
            this.carouselTimer = null;
        }
    },

    /**
     * @param {number} index - Zero-based slide index.
     */
    goSlide(index) {
        const total = this.slides.length;
        this.carouselCurrent = ((index % total) + total) % total;
    },

    /** Show the previous carousel slide. */
    prevSlide() {
        this.goSlide(this.carouselCurrent - 1);
        this.restartCarousel();
    },

    /** Show the next carousel slide. */
    nextSlide() {
        this.goSlide(this.carouselCurrent + 1);
        this.restartCarousel();
    },

    /** Reset auto-advance after manual navigation. */
    restartCarousel() {
        this.stopCarousel();
        if (this.shouldAutoAdvance()) {
            this.carouselTimer = setInterval(() => {
                this.goSlide(this.carouselCurrent + 1);
            }, CAROUSEL_INTERVAL_MS);
        }
    },

    /** Copy the git clone command to the clipboard. */
    async copyCloneCommand() {
        const translate = window.spaApp?.t?.bind(window.spaApp) ?? ((key) => key);
        try {
            if (navigator.clipboard?.writeText) {
                await navigator.clipboard.writeText(this.cloneCommand);
                this.copyFeedback = translate('welcome.copied');
            } else {
                this.copyFeedback = translate('welcome.copyUnavailable');
            }
        } catch {
            this.copyFeedback = translate('welcome.copyFailed');
        }

        setTimeout(() => {
            this.copyFeedback = '';
        }, 2000);
    },
};
