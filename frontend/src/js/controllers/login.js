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

/** View Controller for login functionality */
export const loginController = {
    appContext: null,
    username: '',
    password: '',
    isLoading: false,
    error: null,
    response: null,
    isLoggedIn: false,
    token: null,

    /** @param {object} [appContext] - Root spaApp from createSpaApp(). */
    init(appContext) {
        this.appContext = appContext;
        this.isLoggedIn = !!localStorage.getItem('token');
        this.token = localStorage.getItem('token');
    },

    async login() {
        this.isLoading = true;
        this.error = null;

        if (!this.username || !this.username.trim()) {
            this.error = this.appContext.t('errors.USERNAME_REQUIRED');
            this.isLoading = false;
            return;
        }

        if (!this.password || !this.password.trim()) {
            this.error = this.appContext.t('errors.PASSWORD_REQUIRED');
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
                this.error = this.appContext.tError(data.code || 'LOGIN_FAILED');
            }
        } catch (err) {
            console.error('Login error:', err);
            this.error = this.appContext.tError(err.code || 'LOGIN_FAILED');
        } finally {
            this.isLoading = false;
        }
    },
};
