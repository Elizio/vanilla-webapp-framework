import { api } from './controllers/login.js';
import './controllers/menu.js'; // Import early for dark mode initialization

export const createSpaApp = () => ({
    isLoggedIn: false,
    token: localStorage.getItem('token'),
    username: '',
    password: '',
    confirmPassword: '',
    response: null,
    error: null,
    success: null,
    isLoading: false,
    isRegistering: false,
    sidebarOpen: window.innerWidth >= 1024, // Desktop should have sidebar open by default

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

    async loadPage(elementIdTarget, templatePath, controllerPath = null) {
        // Load template
        const response = await fetch(templatePath);
        const template = await response.text();
        document.getElementById(elementIdTarget).innerHTML = template;

        // Load controller if specified
        if (controllerPath) {
            try {
                const module = await import(controllerPath);
                // Get the first exported object from the module
                const controller = Object.values(module)[0];
                if (controller && typeof controller === 'object') {
                    // Merge controller methods with current app instance
                    Object.assign(this, controller);
                    
                    // Call init method if it exists
                    if (typeof this.init === 'function') {
                        this.init();
                    }
                }
            } catch (err) {
                console.error('Failed to load controller:', err);
            }
        }
    }
}); 