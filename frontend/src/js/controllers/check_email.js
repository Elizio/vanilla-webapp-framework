/**
 * Post-sign-up "check your email" screen with a resend action.
 * @module controllers/check_email
 */
import { apiFetch } from '../api.js';
import { getLocale } from '../i18n.js';

/**
 * @param {string} email
 * @returns {Promise<object>}
 */
export async function resendVerificationApi(email) {
    const response = await apiFetch('/api/auth/verify-email/resend', {
        method: 'POST',
        body: JSON.stringify({ email, locale: getLocale() }),
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
        const err = new Error(data.code || 'EMAIL_NOT_CONFIGURED');
        err.code = data.code;
        throw err;
    }
    return data;
}

/** View controller bound as ``currentPage.*``. */
export const checkEmailController = {
    appContext: null,
    email: '',
    isLoading: false,
    error: null,
    success: null,

    /** @param {object} appContext */
    init(appContext) {
        this.appContext = appContext;
        this.email = appContext?.pendingVerifyEmail || '';
        this.isLoading = false;
        this.error = null;
        this.success = null;
    },

    async resend() {
        this.isLoading = true;
        this.error = null;
        this.success = null;
        const address = (this.email || '').trim();
        if (!address) {
            this.error = this.appContext.t('errors.EMAIL_REQUIRED');
            this.isLoading = false;
            return;
        }
        try {
            await resendVerificationApi(address);
            this.success = this.appContext.t('verify.resent');
        } catch (err) {
            this.error = this.appContext.tError(err.code || 'REQUEST_FAILED');
        } finally {
            this.isLoading = false;
        }
    },
};
