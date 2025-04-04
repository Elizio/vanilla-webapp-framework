import { api } from './api.js';

export const createAppState = () => ({
    isLoggedIn: false,
    token: localStorage.getItem('token'),
    username: '',
    password: '',
    response: null,
    error: null,
    isLoading: false,

    async login() {
        this.isLoading = true;
        this.error = null;
        try {
            const data = await api.login(this.username, this.password);
            this.token = data.token;
            localStorage.setItem('token', data.token);
            this.isLoggedIn = true;
        } catch (err) {
            this.error = 'Login failed';
        } finally {
            this.isLoading = false;
        }
    },

    logout() {
        this.token = null;
        localStorage.removeItem('token');
        this.isLoggedIn = false;
        this.response = null;
    },

    async fetchProtectedData() {
        this.isLoading = true;
        this.error = null;
        try {
            const data = await api.fetchProtectedData(this.token);
            this.response = data;
        } catch (err) {
            this.error = 'Failed to fetch data';
            if (err.status === 401) {
                this.logout();
            }
        } finally {
            this.isLoading = false;
        }
    },

    async fetchPublicData() {
        this.isLoading = true;
        this.error = null;
        try {
            const data = await api.fetchPublicData();
            this.response = data;
        } catch (err) {
            this.error = 'Failed to fetch data';
        } finally {
            this.isLoading = false;
        }
    }
}); 