export const landingPageController = {
    appContext: null, // To store the main app context
    isLoading: false, // Initialize isLoading state
    error: null,      // Initialize error state
    response: null,   // Initialize response state
    token: null,
    
    init(appContext) {
        this.appContext = appContext; // Store the context
        // Reset state on init
        this.isLoading = false;
        this.error = null;
        this.response = null;
        this.token = localStorage.getItem('token');

    },

    async fetchProtectedData() {
        // Access global state/methods via appContext
        if (!this.appContext || !this.token) {
            this.error = 'Not logged in';
            this.appContext?.logout(); // Use optional chaining
            return;
        }

        this.isLoading = true;
        this.error = null;
        try {
            const response = await fetch('/api/data', {
                headers: { 'Authorization': `Bearer ${this.token}` }
            });
            if (!response.ok) {
                if (response.status === 401) {
                    this.error = 'Unauthorized';
                    this.appContext.logout();
                } else {
                    this.error = `Error: ${response.status}`;
                }
                this.response = null;
            } else {
                this.response = await response.json();
            }
        } catch (err) {
            this.error = 'Failed to fetch data';
            // Optional: Check error type if needed before logging out
            this.appContext.logout(); 
        } finally {
            this.isLoading = false;
        }
    },

    async fetchPublicData() {
        this.isLoading = true;
        this.error = null;
        try {
            const response = await fetch('/api/public');
             if (!response.ok) {
                this.error = `Error: ${response.status}`;
                this.response = null;
            } else {
                this.response = await response.json();
            }
        } catch (err) {
            this.error = 'Failed to fetch data';
        } finally {
            this.isLoading = false;
        }
    },

};