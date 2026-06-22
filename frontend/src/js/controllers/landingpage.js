/**
 * Landing page: fetches public and protected API samples for demo.
 * Bound in templates as ``currentPage.*`` after loadPage().
 */
export const landingPageController = {
    appContext: null,
    isLoading: false,
    error: null,
    response: null,
    token: null,

    /** @param {object} appContext - Root spaApp from createSpaApp(). */
    init(appContext) {
        this.appContext = appContext;
        this.isLoading = false;
        this.error = null;
        this.response = null;
        this.token = localStorage.getItem('token');
    },

    async fetchProtectedData() {
        if (!this.appContext || !this.token) {
            this.error = this.appContext?.t('errors.NOT_LOGGED_IN') ?? 'Not logged in';
            this.appContext?.logout();
            return;
        }

        this.isLoading = true;
        this.error = null;
        try {
            const response = await fetch('/api/data', {
                headers: { Authorization: `Bearer ${this.token}` },
            });
            if (!response.ok) {
                if (response.status === 401) {
                    this.error = this.appContext.t('errors.UNAUTHORIZED');
                    this.appContext.logout();
                } else {
                    this.error = this.appContext.t('errors.HTTP_ERROR', { status: response.status });
                }
                this.response = null;
            } else {
                this.response = await response.json();
            }
        } catch (err) {
            this.error = this.appContext.t('errors.FETCH_FAILED');
            this.appContext.logout();
        } finally {
            this.isLoading = false;
        }
    },

    async fetchPublicData() {
        this.isLoading = true;
        this.error = null;
        try {
            const response = await fetch('/api/public');
            if (!response.ok) {
                this.error = this.appContext.t('errors.HTTP_ERROR', { status: response.status });
                this.response = null;
            } else {
                this.response = await response.json();
            }
        } catch (err) {
            this.error = this.appContext.t('errors.FETCH_FAILED');
        } finally {
            this.isLoading = false;
        }
    },
};
