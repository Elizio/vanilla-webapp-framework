/**
 * Request a password-reset email, or show that reset is unavailable.
 * @module controllers/forgot_password
 */
import { apiFetch } from '../api.js';
import { getLocale } from '../i18n.js';

/**
 * @param {string} email
 * @returns {Promise<object>}
 */
export async function forgotPasswordApi(email) {
    const response = await apiFetch('/api/auth/password/forgot', {
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
export const forgotPasswordController = {
    appContext: null,
    email: '',
    isLoading: false,
    error: null,
    success: null,

    /** @param {object} appContext */
    init(appContext) {
        this.appContext = appContext;
        this.email = '';
        this.isLoading = false;
        this.error = null;
        this.success = null;
    },

    async submit() {
        this.isLoading = true;
        this.error = null;
        this.success = null;
        if (!this.appContext?.emailCapabilities?.password_reset) {
            this.error = this.appContext.tError('EMAIL_NOT_CONFIGURED');
            this.isLoading = false;
            return;
        }
        if (!this.email || !this.email.trim()) {
            this.error = this.appContext.t('errors.EMAIL_REQUIRED');
            this.isLoading = false;
            return;
        }
        try {
            await forgotPasswordApi(this.email.trim());
            this.success = this.appContext.t('forgot.checkEmail');
        } catch (err) {
            this.error = this.appContext.tError(
                err.code || 'EMAIL_NOT_CONFIGURED',
            );
        } finally {
            this.isLoading = false;
        }
    },
};
