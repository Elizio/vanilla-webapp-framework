/**
 * Login Controller
 * Handles user authentication and login functionality
 */

// API module for handling login
export const api = {
    async loginApi(username, password) {
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

// View Controller for login functionality
export const loginController = {
    // Add properties that match the template bindings
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
        this.isLoggedIn = false;
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
            // Use the api object directly
            const data = await api.loginApi(this.username, this.password);
            
            if (data.token) {
                // Store the token
                this.token = data.token;
                localStorage.setItem('token', data.token);
                this.isLoggedIn = true;
                
                // Redirect to home page
                window.location.href = '/';
            } else {
                this.error = data.message || 'Login failed. Please try again.';
            }
        } catch (err) {
            console.error('Login error:', err);
            this.error = 'Login failed. Please try again.';
        } finally {
            this.isLoading = false;
        }
    },
}; 
