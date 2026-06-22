/** Public welcome page controller: clone command, clipboard copy, and carousel. */

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
    carouselDots: [0, 1, 2, 3],
    carouselTimer: null,

    /** Reset transient state. */
    init() {
        this.copyFeedback = '';
    },

    /** Start or restart the carousel auto-advance timer. */
    initCarousel() {
        this.stopCarousel();
        this.carouselCurrent = 0;
        this.carouselTimer = setInterval(() => {
            this.goSlide(this.carouselCurrent + 1);
        }, 5000);
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
        const total = this.carouselDots.length;
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
        this.carouselTimer = setInterval(() => {
            this.goSlide(this.carouselCurrent + 1);
        }, 5000);
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
