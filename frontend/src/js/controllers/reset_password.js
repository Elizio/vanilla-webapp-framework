/**
 * Set a new password from an email reset token.
 * @module controllers/reset_password
 */
import { apiFetch } from '../api.js';

/**
 * @param {string} token
 * @param {string} password
 * @returns {Promise<object>}
 */
export async function resetPasswordApi(token, password) {
    const response = await apiFetch('/api/auth/password/reset', {
        method: 'POST',
        body: JSON.stringify({ token, password }),
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
        const err = new Error(data.code || 'TOKEN_INVALID_OR_EXPIRED');
        err.code = data.code;
        throw err;
    }
    return data;
}

/** View controller bound as ``currentPage.*``. */
export const resetPasswordController = {
    appContext: null,
    password: '',
    confirmPassword: '',
    isLoading: false,
    error: null,
    success: null,

    /** @param {object} appContext */
    init(appContext) {
        this.appContext = appContext;
        this.password = '';
        this.confirmPassword = '';
        this.isLoading = false;
        this.error = null;
        this.success = null;
    },

    async submit() {
        this.isLoading = true;
        this.error = null;
        this.success = null;
        const token = this.appContext?.pendingResetToken;
        if (!token) {
            this.error = this.appContext.tError('TOKEN_INVALID_OR_EXPIRED');
            this.isLoading = false;
            return;
        }
        if (!this.password || this.password.length < 8) {
            this.error = this.appContext.t('errors.PASSWORD_TOO_SHORT');
            this.isLoading = false;
            return;
        }
        if (this.password !== this.confirmPassword) {
            this.error = this.appContext.t('errors.PASSWORDS_DO_NOT_MATCH');
            this.isLoading = false;
            return;
        }
        try {
            await resetPasswordApi(token, this.password);
            this.success = this.appContext.t('reset.success');
            this.appContext.pendingResetToken = null;
        } catch (err) {
            this.error = this.appContext.tError(
                err.code || 'TOKEN_INVALID_OR_EXPIRED',
            );
        } finally {
            this.isLoading = false;
        }
    },
};
