/**
 * Landing page: fetches public and protected API samples for demo.
 * Bound in templates as ``currentPage.*`` after loadPage().
 */
import { apiFetch } from '../api.js';

export const landingPageController = {
    appContext: null,
    isLoading: false,
    error: null,
    response: null,
    newEmail: '',
    emailSuccess: null,

    /** @param {object} appContext - Root spaApp from createSpaApp(). */
    init(appContext) {
        this.appContext = appContext;
        this.isLoading = false;
        this.error = null;
        this.response = null;
        this.newEmail = '';
        this.emailSuccess = null;
    },

    async submitEmail() {
        const address = (this.newEmail || '').trim();
        if (!address) {
            this.error = this.appContext.t('errors.EMAIL_REQUIRED');
            return;
        }
        this.isLoading = true;
        this.error = null;
        this.emailSuccess = null;
        try {
            const response = await apiFetch('/api/auth/email', {
                method: 'POST',
                body: JSON.stringify({ email: address }),
            });
            const data = await response.json().catch(() => ({}));
            if (!response.ok) {
                this.error = this.appContext.tError(
                    data.code || 'REQUEST_FAILED',
                );
                return;
            }
            this.emailSuccess = this.appContext.t('landing.addEmailSent');
            this.appContext.needsEmail = false;
        } catch (_err) {
            this.error = this.appContext.t('errors.FETCH_FAILED');
        } finally {
            this.isLoading = false;
        }
    },

    async fetchProtectedData() {
        if (!this.appContext?.isLoggedIn) {
            this.error =
                this.appContext?.t('errors.NOT_LOGGED_IN') ?? 'Not logged in';
            this.appContext?.logout();
            return;
        }

        this.isLoading = true;
        this.error = null;
        try {
            const response = await apiFetch('/api/data');
            if (!response.ok) {
                if (response.status === 401) {
                    this.error = this.appContext.t('errors.UNAUTHORIZED');
                } else {
                    this.error = this.appContext.t('errors.HTTP_ERROR', {
                        status: response.status,
                    });
                }
                this.response = null;
            } else {
                this.response = await response.json();
            }
        } catch (_err) {
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
            const response = await apiFetch('/api/public');
            if (!response.ok) {
                this.error = this.appContext.t('errors.HTTP_ERROR', {
                    status: response.status,
                });
                this.response = null;
            } else {
                this.response = await response.json();
            }
        } catch (_err) {
            this.error = this.appContext.t('errors.FETCH_FAILED');
        } finally {
            this.isLoading = false;
        }
    },
};
