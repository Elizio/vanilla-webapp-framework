/**
 * Login Controller
 * Handles user authentication and login functionality
 */
// API module for handling login
export const api = {
    async login(username, password) {
        try {
            const response = await fetch('/api/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (err) {
            console.error('Login failed:', err);
            throw err;
        }
    }
};

// Controller for login functionality
export const loginController = {
    init() {
        this.isLoggingIn = true;
    },

    async login() {
        this.isLoading = true;
        this.error = null;
        
        // Validation
        if (!this.username || !this.username.trim()) {
            this.error = 'Username is required';
            this.isLoading = false;
            return;
        }
        
        if (!this.password || !this.password.trim()) {
            this.error = 'Password is required';
            this.isLoading = false;
            return;
        }
        
        try {
            const data = await api.login(this.username, this.password);
            
            if (data.token) {
                // Store the token
                localStorage.setItem('token', data.token);
                
                // Redirect to home page
                window.location.href = '/';
            } else {
                this.error = data.message || 'Login failed. Please try again.';
            }
        } catch (err) {
            this.error = 'Login failed. Please try again.';
        } finally {
            this.isLoading = false;
        }
    },

    showRegisterForm() {
        this.isLoggingIn = false;
    }
}; 