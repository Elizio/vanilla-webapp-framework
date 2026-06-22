/**
 * Login Controller
 * Handles user authentication and login functionality
 */

/** API module for handling login */
export const api = {
    /**
     * @param {string} username
     * @param {string} password
     * @returns {Promise<object>}
     */
    async loginApi(username, password) {
        const response = await fetch('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password }),
        });

        const data = await response.json().catch(() => ({}));
        if (!response.ok) {
            const err = new Error(data.code || 'LOGIN_FAILED');
            err.code = data.code;
            throw err;
        }

        return data;
    },
};

/**
 * View Controller for login functionality.
 *
 * NOTE: this controller must NOT store a reference to the spaApp object as a
 * property. loginController lives directly on the Alpine root scope; storing
 * app as a property creates a circular reference (app → loginController →
 * appContext → app) that causes Alpine's initInterceptors to blow the stack.
 * Access the app via ``window.spaApp`` inside methods instead.
 */
export const loginController = {
    username: '',
    password: '',
    isLoading: false,
    error: null,
    response: null,
    isLoggedIn: false,
    token: null,

    init() {
        this.isLoggedIn = !!localStorage.getItem('token');
        this.token = localStorage.getItem('token');
    },

    async login() {
        const app = window.spaApp;
        this.isLoading = true;
        this.error = null;

        if (!this.username || !this.username.trim()) {
            this.error = app.t('errors.USERNAME_REQUIRED');
            this.isLoading = false;
            return;
        }

        if (!this.password || !this.password.trim()) {
            this.error = app.t('errors.PASSWORD_REQUIRED');
            this.isLoading = false;
            return;
        }

        try {
            const data = await api.loginApi(this.username, this.password);

            if (data.token) {
                this.token = data.token;
                localStorage.setItem('token', data.token);
                this.isLoggedIn = true;
                window.location.href = '/';
            } else {
                this.error = app.tError(data.code || 'LOGIN_FAILED');
            }
        } catch (err) {
            console.error('Login error:', err);
            this.error = app.tError(err.code || 'LOGIN_FAILED');
        } finally {
            this.isLoading = false;
        }
    },
};
