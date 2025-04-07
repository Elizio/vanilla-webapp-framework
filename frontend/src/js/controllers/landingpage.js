
export const landingPageController = {
    async fetchProtectedData() {
        this.isLoading = true;
        this.error = null;
        try {
            const response = await fetch('/api/data', {
                headers: { 'Authorization': `Bearer ${this.token}` }
            });
            this.response = await response.json();
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
            const response = await fetch('/api/public');
            this.response = await response.json();
        } catch (err) {
            this.error = 'Failed to fetch data';
        } finally {
            this.isLoading = false;
        }
    },


};