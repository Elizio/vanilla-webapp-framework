export const testPageController = {
    abc: 0, // Define the abc variable
    isLoading: false, // Add isLoading state
    appContext: null,

    init(appContext) {
        this.appContext = appContext;
        console.log('Test page controller initialized');
        this.isLoading = false; // Ensure it's reset on load
    },

    async ttt() {
        this.isLoading = true;
        console.log('ttt called, abc is:', this.abc);
        // Simulate work
        await new Promise(resolve => setTimeout(resolve, 500)); 
        console.log('ttt finished');
        this.isLoading = false;
    },

};
