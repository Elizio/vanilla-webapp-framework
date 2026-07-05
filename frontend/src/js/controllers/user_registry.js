/**
 * User Registration Controller
 * Handles new user registration functionality
 */
import { apiFetch } from '../api.js';

/** API module for handling user registration */
export const api = {
    /**
     * @param {string} username
     * @param {string} password
     * @returns {Promise<object>}
     */
    async registerApi(username, password) {
        const response = await apiFetch('/api/register', {
            method: 'POST',
            body: JSON.stringify({ username, password }),
        });

        const data = await response.json().catch(() => ({}));
        if (!response.ok) {
            const err = new Error(data.code || 'REGISTRATION_FAILED');
            err.code = data.code;
            throw err;
        }

        return data;
    },
};

/** View Controller for user registration */
export const userRegistryController = {
    appContext: null,
    username: '',
    password: '',
    confirmPassword: '',
    isLoading: false,
    error: null,
    success: null,

    /** @param {object} appContext - Root spaApp from createSpaApp(). */
    init(appContext) {
        this.appContext = appContext;
        this.username = '';
        this.password = '';
        this.confirmPassword = '';
        this.isLoading = false;
        this.error = null;
        this.success = null;
    },

    async register() {
        this.isLoading = true;
        this.error = null;
        this.success = null;

        if (!this.username || !this.username.trim()) {
            this.error = this.appContext.t('errors.USERNAME_REQUIRED');
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
            const data = await api.registerApi(this.username, this.password);

            if (data.authenticated || data.code === 'USER_CREATED') {
                this.success = this.appContext.t('register.success');
                this.appContext.isLoggedIn = true;
                this.appContext.showLogin = false;
                this.appContext.refreshMountedPages();
            } else {
                this.error = this.appContext.tError(data.code || 'REGISTRATION_FAILED');
            }
        } catch (err) {
            console.error('Registration failed:', err);
            this.error = this.appContext.tError(err.code || 'REGISTRATION_FAILED');
        } finally {
            this.isLoading = false;
        }
    },
};
