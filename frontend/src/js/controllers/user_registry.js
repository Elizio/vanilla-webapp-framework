/**
 * User Registration Controller
 * Handles new user registration functionality
 */

// API module for handling user registration
export const api = {
    async registerApi(username, password) {
        try {
            const response = await fetch('/api/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (err) {
            console.error('Registration failed:', err);
            throw err;
        }
    }
};

// View Controller for user registration
export const userRegistryController = {
    // Add app context reference
    appContext: null,
    username: '',
    password: '',
    confirmPassword: '',
    isLoading: false,
    error: null,
    success: null,
    
    init(appContext) {
        // Store app reference when initialized
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
        
        // Validation
        if (!this.username || !this.username.trim()) {
            this.error = 'Username is required';
            this.isLoading = false;
            return;
        }
        
        if (!this.password || this.password.length < 6) {
            this.error = 'Password must be at least 6 characters';
            this.isLoading = false;
            return;
        }
        
        if (this.password !== this.confirmPassword) {
            this.error = 'Passwords do not match';
            this.isLoading = false;
            return;
        }
        
        try {
            const data = await api.registerApi(this.username, this.password);
            
            if (data.message === 'User created successfully') {
                this.success = 'Account created successfully! You can now login.';
                
                // Reset form
                this.username = '';
                this.password = '';
                this.confirmPassword = '';
                
                // Use app.loadPage instead of this.loadPage
                setTimeout(() => {
                    this.appContext.loadPage('login-register-container', '/templates/partials/login.hbs', '/js/controllers/login.js', 'loginController');
                }, 2000);
            } else {
                this.error = data.message || 'Registration failed. Please try again.';
            }
        } catch (err) {
            this.error = 'Registration failed. Please try again.';
        } finally {
            this.isLoading = false;
        }
    }
};
