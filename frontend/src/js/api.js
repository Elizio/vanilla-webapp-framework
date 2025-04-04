// API module for handling all fetch requests
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
            return response.json();
        } catch (err) {
            console.error('Login failed:', err);
            throw err;
        }
    },

    async fetchProtectedData(token) {
        const response = await fetch('/api/data', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        return response.json();
    },

    async fetchPublicData() {
        const response = await fetch('/api/public');
        return response.json();
    }
}; 